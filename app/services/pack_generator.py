from typing import List, Optional
from datetime import datetime
import logging

from app.models.anime import Anime
from app.schemas.osu import Beatmapset
from app.schemas.pack import Pack
from app.services.animethemes import get_anime_metadata
from app.services.chimu import search_for_beatmaps

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
    
    def __init__(self):
        self.pack_id_counter = 1  # TODO: Replace with database auto-increment
    
    def generate_pack_from_anime(
        self,
        anime_name: str,
        status: int = 1,  # 1 = ranked, 2 = loved
        mode: Optional[int] = None  # None = all modes, 0 = standard, 1 = taiko, 2 = catch, 3 = mania
    ) -> Pack:
        """
        Generate a beatmap pack for a given anime name.
        
        Args:
            anime_name: The name of the anime (e.g., "Bakemonogatari", "Steins;Gate")
            status: Beatmap status filter (1=ranked, 2=loved)
            mode: Game mode filter (None=all, 0=standard, 1=taiko, 2=catch, 3=mania)
        
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
            pack = self._create_pack(
                anime_title=anime_metadata.name,
                anime_slug=anime_metadata.slug,
                anime_synopsis=anime_metadata.synopsis,
                beatmapset_ids=beatmapset_ids
            )
            logger.info(f"Pack created successfully: {pack.name}")
            
            return pack
            
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
        mode: Optional[int]
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
            
            # Search with specified filters
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
        beatmapset_ids.sort()  # Sort for consistency
        return beatmapset_ids
    
    def _create_pack(
        self,
        anime_title: str,
        anime_slug: str,
        anime_synopsis: Optional[str],
        beatmapset_ids: List[int],
    ) -> Pack:
        """
        Create a Pack object with the collected data.
        
        Args:
            anime_title: The anime title
            anime_slug: The anime slug
            beatmapset_ids: List of beatmapset IDs
            anime_metadata: Full anime metadata object
        
        Returns:
            Pack: Newly created Pack object
        """
        current_time = datetime.now(datetime.timezone.utc).isoformat()
        
        # Generate pack name (e.g., "Bakemonogatari - Ranked Maps")
        pack_name = self._generate_pack_name(anime_title, len(beatmapset_ids))
        
        pack = Pack(
            id=self.pack_id_counter,
            name=pack_name,
            anime_title=anime_title,
            anime_slug=anime_slug,
            synopsis=anime_synopsis,
            beatmapset_ids=beatmapset_ids,
            beatmapset_count=len(beatmapset_ids),
            downloads=0,
            created_at=current_time,
            updated_at=current_time
        )
        
        # TODO: Save to database instead of incrementing in-memory counter
        self.pack_id_counter += 1
        
        return pack
    
    def _generate_pack_name(self, anime_title: str, beatmapset_count: int) -> str:
        """
        Generate a descriptive pack name.
        
        Args:
            anime_title: The anime title
            beatmapset_count: Number of beatmapsets in the pack
        
        Returns:
            str: Generated pack name
        """
        return f"{anime_title} - Ranked Maps ({beatmapset_count} beatmapsets)"
    
    # i think we have to assume here that the titles are found exactly from animethemes.moe. in this regard, perhaps we can implement a search for anime title connected to animethemes and fetch the metadata if user selects it.
    def generate_packs_batch(
        self,
        anime_names: List[str],
        status: int = 1,
        mode: Optional[int] = None
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
