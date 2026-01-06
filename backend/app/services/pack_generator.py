from typing import List, Optional
import logging

from app.schemas.anime import Anime
from app.schemas.osu import Beatmapset
from app.schemas.pack import Pack, PackCreate
from app.services.animethemes import get_anime_metadata
from app.services.chimu import search_for_beatmaps
from app.db.session import SessionLocal
from app.db.services import save_pack
from app.utils.format import packdb_to_packschema
from app.schemas.osu import MODE_MAP

logger = logging.getLogger(__name__)


class PackGenerationError(Exception):
    """Raised when pack generation fails"""
    pass


class PackGenerator:
    """
    Service responsible for generating beatmap packs from anime names.
    
    Process:
    1. Fetch anime metadata from AnimeThemes API
    2. Search for beatmapsets using the anime title
    3. Filter and collect beatmapset IDs
    4. Create Pack object with metadata
    """
    def generate_pack_from_anime(
        self,
        anime_name: str,
        status: int = 1,
        mode: int = -1,
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
            # Step 1: Fetch anime metadata
            logger.info(f"Fetching anime metadata for: {anime_name}")
            anime_metadata = self._fetch_anime_metadata(anime_name)
            logger.info(f"Found anime: {anime_metadata.name} (ID: {anime_metadata.id})")
            
            # Step 2: Search for beatmapsets
            logger.info(f"Searching for beatmapsets with title: {anime_metadata.name}")
            beatmapsets = self._search_beatmapsets(anime_metadata.name, status, mode)
            logger.info(f"Found {len(beatmapsets)} beatmapsets")
            
            if not beatmapsets:
                raise PackGenerationError(f"No beatmapsets found for anime: {anime_name}")
            
            # Step 3: Extract beatmapset IDs
            beatmapset_ids = self._extract_beatmapset_ids(beatmapsets)
            logger.info(f"Collected {len(beatmapset_ids)} unique beatmapset IDs")
            
            # Step 4: Create Pack object
            pack: PackCreate = self._create_pack(
                anime_title=anime_metadata.name,
                anime_slug=anime_metadata.slug,
                anime_synopsis=anime_metadata.synopsis,
                beatmapset_ids=beatmapset_ids,
                mode=mode
            )

            logger.info(f"Pack created successfully: {pack.name}")
            
            # save to databse after successful creation
            with SessionLocal() as session:
               try:
                   pack_db = save_pack(session, anime_metadata, pack)
                   session.commit()
                   session.refresh(pack_db)
                   logger.info(f"Pack and Anime saved to database successfully")
                   pack_schema = packdb_to_packschema(pack_db)
               except Exception as e:
                   logger.error(f"Failed to save Pack and Anime to database: {str(e)}")
                   session.rollback()
                   raise PackGenerationError(f"Database save error: {str(e)}")
            return pack_schema
            
        except Exception as e:
            logger.error(f"Pack generation failed for {anime_name}: {str(e)}")
            raise PackGenerationError(f"Failed to generate pack for {anime_name}: {str(e)}")
    
    def _fetch_anime_metadata(self, anime_name: str) -> Anime:
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
            return get_anime_metadata(anime_name)
        except Exception as e:
            raise PackGenerationError(f"Failed to fetch anime metadata: {str(e)}")
    
    def _search_beatmapsets(
        self,
        anime_title: str,
        status: int,
        mode: int = -1
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
            # Enclose anime title in quotes for exact search
            search_query = f'"{anime_title}"'
            if mode is not None:
                beatmapsets = search_for_beatmaps(search_query, status=status, mode=mode)
            else:
                # Search all modes if mode is None
                beatmapsets = search_for_beatmaps(search_query, status=status)
            
            return beatmapsets
        except Exception as e:
            raise PackGenerationError(f"Failed to search beatmapsets: {str(e)}")
    
    def _extract_beatmapset_ids(self, beatmapsets: List[Beatmapset]) -> List[int]:
        """
        Extract unique beatmapset IDs from the list of beatmapsets.
        
        Args:
            beatmapsets: List of Beatmapset objects
        
        Returns:
            List[int]: List of unique beatmapset IDs
        """
        # Use set to ensure uniqueness, then convert back to sorted list
        beatmapset_ids = list(set(beatmapset.id for beatmapset in beatmapsets))
        beatmapset_ids.sort()
        return beatmapset_ids
    
    def _create_pack(
        self,
        anime_title: str,
        anime_slug: str,
        anime_synopsis: Optional[str],
        beatmapset_ids: List[int],
        mode: int = -1
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
        pack_name = self._generate_pack_name(anime_title, len(beatmapset_ids), mode=mode)
        
        pack = PackCreate(
            name=pack_name,
            anime_title=anime_title,
            anime_slug=anime_slug,
            synopsis=anime_synopsis,
            beatmapset_ids=beatmapset_ids
        )
    
        return pack
    
    def _generate_pack_name(self, anime_title: str, beatmapset_count: int, mode: int) -> str:
        """
        Generate a descriptive pack name.
        
        Args:
            anime_title: The anime title
            beatmapset_count: Number of beatmapsets in the pack
        
        Returns:
            str: Generated pack name
        """
        return f"{anime_title} - Ranked Maps ({beatmapset_count} beatmapsets) - {MODE_MAP.get(mode, 'All Modes')}"
    
    def generate_packs_batch(
        self,
        anime_names: List[str],
        status: int = 1,
        mode: int = -1
    ) -> List[Pack]:
        """
        Generate multiple packs from a list of anime names.
        
        Args:
            anime_names: List of anime names
            status: Beatmap status filter
            mode: Game mode filter
        
        Returns:
            List[Pack]: List of successfully generated packs
        """
        packs = []
        failed = []
        
        for anime_name in anime_names:
            try:
                pack = self.generate_pack_from_anime(anime_name, status, mode)
                packs.append(pack)
            except PackGenerationError as e:
                logger.error(f"Failed to generate pack for {anime_name}: {str(e)}")
                failed.append(anime_name)
        
        if failed:
            logger.warning(f"Failed to generate packs for: {', '.join(failed)}")
        
        logger.info(f"Successfully generated {len(packs)} out of {len(anime_names)} packs")
        return packs


# Singleton instance for convenience
pack_generator = PackGenerator()
