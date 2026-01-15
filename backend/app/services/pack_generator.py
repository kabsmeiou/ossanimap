import json
from typing import List
import logging
from sqlalchemy.exc import SQLAlchemyError
from httpx import RequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.anime import Anime
from app.schemas.osu import Beatmapset
from app.schemas.pack import Pack, PackCreate
from app.services.animethemes import get_anime_metadata, AnimeThemesInvalidResponse, AnimeThemesThrottleError, AnimeThemesDown
from app.services.osu import handle_beatmapset_search
from app.db.services import save_pack
from app.utils.format import packdb_to_packschema

logger = logging.getLogger("uvicorn.error")

# -4 database save error
# -3 json decode error from animethemes
# -2 animethemes api fetch error
# -1 beatmapset search error
# 0 no beatmapsets found
class PackGenerationError(Exception):
    """Raised when pack generation fails"""
    def __init__(
        self,
        *,
        anime_name: str | None = None,
        code: int = 0,
        message: str = "Pack generation failed",
    ):
        self.anime_name = anime_name
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"[code={self.code}] {self.message} (anime={self.anime_name})"


class PackGenerator:
    """
    Service responsible for generating beatmap packs from anime names.
    
    Process:
    1. Fetch anime metadata from AnimeThemes API
    2. Search for beatmapsets using the anime title
    3. Filter and collect beatmapset IDs
    4. Create Pack object with metadata
    """
    async def generate_pack_from_anime(
        self,
        session: AsyncSession,
        anime: Anime,
        status: List[int] = [1],
        mode: List[int] = [0],
    ) -> Pack:
        """
        Orchestrator for generating a beatmap pack for a given anime name.
        
        Args:
            anime_name: The name of the anime (e.g., "Bakemonogatari", "Steins;Gate")
            status: Beatmap status filter (1=ranked)
            mode: Game mode filter (-1=all, 0=standard)
        
        Returns:
            Pack: A Pack object containing anime info and beatmapset IDs
        
        Raises:
            PackGenerationError: If pack generation fails at any stage
        """
        try:
            # step 1 is to fetch anime metadata but the creation process
            # already obtains the needed info so we just pass it directly
            # from the client
            # Step 2: Search for beatmapsets
            beatmapset_ids = await self._search_beatmapsets(anime.name)

            # Step 3: Create Pack object
            pack: PackCreate = self._create_pack(
                anime=anime,
                beatmapset_ids=beatmapset_ids,
                mode=mode,
                status=status,
            )
            
            # save to databse after successful creation then convert to schema
            try:
                p = await save_pack(session, anime, pack)
                await session.commit()
                # calls refresh on the pack_db object
                # this is to reload and get database generated fields and etc.
                await session.refresh(p)
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database save error for pack {pack.name}: {str(e)}")
                raise PackGenerationError(anime_name=anime.name, code=-4, message="Database save error") from e
            p_schema = packdb_to_packschema(p)
            return p_schema
        except PackGenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating pack for {anime.name}: {str(e)}")
            raise PackGenerationError(anime_name=anime.name, code=-1, message=str(e)) from e
    
    async def _fetch_anime_metadata(self, anime_name: str) -> Anime:
        """
        Fetch anime metadata from AnimeThemes API.
        
        Args:
            anime_name: The anime name to search for
        
        Returns:
            Anime: Anime metadata object
        
        Raises:
            PackGenerationError: If anime metadata cannot be fetched
        """
        try:
            return await get_anime_metadata(anime_name)
        except json.JSONDecodeError as e:
            raise PackGenerationError(anime_name=anime_name, code=-3, message="Invalid response from AnimeThemes API") from e
        except (AnimeThemesInvalidResponse, AnimeThemesThrottleError, AnimeThemesDown) as e:
            logger.error(f"AnimeThemes API error for '{anime_name}': {str(e)}")
            raise PackGenerationError(anime_name=anime_name, code=-2, message="Failed to fetch anime metadata") from e
    
    async def _search_beatmapsets(
        self,
        anime_title: str,
        status: List[int] = [1],
        mode: List[int] = [0]
    ) -> List[Beatmapset]:
        """
        Search for beatmapsets using the anime title.
        Uses quoted search to ensure exact matching.
        
        Args:
            anime_title: The anime title to search for
            status: Beatmap status filter
            mode: Game mode filter
        
        Returns:
            List[Beatmapset]: List of matching beatmapsets
        
        Raises:
            PackGenerationError: If search fails
        """
        try:
            beatmapsets = await handle_beatmapset_search(anime_title)
            if not beatmapsets:
                raise PackGenerationError(anime_name=anime_title, code=0, message="No beatmapsets found")
            return beatmapsets
        except PackGenerationError:
            raise
        except Exception as e:
            raise PackGenerationError(anime_name=anime_title, message=f"Failed to search beatmapsets: {str(e)}", code=-1) from e
    
    def _create_pack(
        self,
        anime: Anime,
        beatmapset_ids: List[int],
        mode: List[int] = [0],
        status: List[int] = [1],
    ) -> PackCreate:
        """
        Create a Pack object with the collected data.
        
        Args:
            anime_title: The anime title
            anime_slug: The anime slug
            beatmapset_ids: List of beatmapset IDs
            anime_metadata: Full anime metadata object
        
        Returns:
            PackCreate: Newly created PackCreate object
        """
        # Generate pack name (e.g., "Bakemonogatari - Ranked Maps")
        pack_name = self._generate_pack_name(anime.name)
        
        pack = PackCreate(
            name=pack_name,
            anime_id=anime.id,
            anime_title=anime.name,
            anime_slug=anime.slug,
            anime_synopsis=anime.synopsis,
            image_link=anime.image_link,
            status=status,
            mode=mode,
            beatmapset_ids=beatmapset_ids
        )
    
        return pack
    
    def _generate_pack_name(self, anime_title: str) -> str:
        """
        Generate a descriptive pack name.
        
        Args:
            anime_title: The anime title
            beatmapset_count: Number of beatmapsets in the pack
        
        Returns:
            str: Generated pack name
        """
        return f"{anime_title} - Beatmap Pack"
    
    # def generate_packs_batch(
    #     self,
    #     anime_names: List[str],
    #     status: List[int] = [1],
    #     mode: List[int] = [0]
    # ) -> List[Pack]:
    #     """
    #     Generate multiple packs from a list of anime names.
        
    #     Args:
    #         anime_names: List of anime names
    #         status: Beatmap status filter
    #         mode: Game mode filter
        
    #     Returns:
    #         List[Pack]: List of successfully generated packs
    #     """
    #     packs = []
    #     failed = []
        
    #     for anime_name in anime_names:
    #         try:
    #             pack = self.generate_pack_from_anime(anime_name, status, mode)
    #             packs.append(pack)
    #         except PackGenerationError as e:
    #             logger.error(f"Failed to generate pack for {anime_name}: {str(e)}")
    #             failed.append(anime_name)
        
    #     if failed:
    #         logger.warning(f"Failed to generate packs for: {', '.join(failed)}")
        
    #     logger.info(f"Successfully generated {len(packs)} out of {len(anime_names)} packs")
    #     return packs

pack_generator = PackGenerator()
