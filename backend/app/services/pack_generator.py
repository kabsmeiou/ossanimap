import json
from typing import List
import logging
from sqlalchemy.exc import SQLAlchemyError


from app.schemas.anime import Anime
from app.schemas.osu import Beatmapset
from app.schemas.pack import PackCreate
from app.services.osu import handle_beatmapset_search
from app.db.session import AsyncSessionLocal
from app.db.services import save_pack

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

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
    def create_job_id(
        self, 
        anime_id: int, status: List[int], mode: List[int]
    ) -> str:
        """
        Create unique job id depending on anime id, status and mode filters.
        """
        status_str = "".join(map(str, sorted(status)))
        mode_str = "".join(map(str, sorted(mode)))
        return f"{anime_id}-{status_str}-{mode_str}"

    async def generate_pack_from_anime(
        self,
        anime: Anime,
        status: List[int] = [1],
        mode: List[int] = [0],
    ):
        """
        Orchestrator for generating a beatmap pack for a given anime name.
        
        Args:
            anime_name: The name of the anime (e.g., "Bakemonogatari", "Steins;Gate")
            status: Beatmap status filter (1=ranked)
            mode: Game mode filter (-1=all, 0=standard)
        
        Raises:
            PackGenerationError: If pack generation fails at any stage
        """
        try:
            # step 1 is to fetch anime metadata but the creation process
            # already obtains the needed info so we just pass it directly
            # from the client
            # Step 2: Search for beatmapsets
            beatmapset_ids = await self._search_beatmapsets(anime.name, anime.slug)

            # Step 3: Create Pack object
            pack: PackCreate = self._create_pack(
                anime=anime,
                beatmapset_ids=beatmapset_ids,
                mode=mode,
                status=status,
            )
            
            # save to databse after successful creation then convert to schema
            try:
                async with AsyncSessionLocal() as session:
                    p = await save_pack(session, anime, pack)
                    await session.commit()
                    # calls refresh on the pack_db object
                    # this is to reload and get database generated fields and etc.
                    await session.refresh(p)
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database save error for pack {pack.name}: {str(e)}")
                raise PackGenerationError(anime_name=anime.name, code=-4, message="Database save error") from e
            return p.id
        except PackGenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating pack for {anime.name}: {str(e)}")
            raise PackGenerationError(anime_name=anime.name, code=-1, message=str(e)) from e
    
    async def _search_beatmapsets(
        self,
        anime_name: str,
        anime_slug: str,
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
            beatmapsets = await handle_beatmapset_search(anime_name, anime_slug)
            if not beatmapsets:
                raise PackGenerationError(anime_name=anime_name, code=0, message="No beatmapsets found")
            return beatmapsets
        except PackGenerationError:
            raise
        except Exception as e:
            raise PackGenerationError(anime_name=anime_name, message=f"Failed to search beatmapsets: {str(e)}", code=-1) from e
    
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
            anime: Anime metadata
            beatmapset_ids: List of beatmapset IDs
            mode: Game mode filter
            status: Beatmap status filter
        
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
