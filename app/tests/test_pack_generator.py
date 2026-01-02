import logging
from app.services.pack_generator import pack_generator, PackGenerationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_single_pack_generation():
    """Test generating a single pack"""
    print("\n" + "="*60)
    print("Testing Single Pack Generation")
    print("="*60)
    
    try:
        # Test with a popular anime
        anime_name = "Bakemonogatari"
        print(f"\nGenerating pack for: {anime_name}")
        
        pack = pack_generator.generate_pack_from_anime(anime_name)
        
        print(f"\n✅ Pack created successfully!")
        print(f"Pack ID: {pack.id}")
        print(f"Pack Name: {pack.name}")
        print(f"Anime Title: {pack.anime_title}")
        print(f"Anime Slug: {pack.anime_slug}")
        print(f"Anime Synopsis: {pack.synopsis}")
        print(f"Beatmapset Count: {pack.beatmapset_count}")
        print(f"Beatmapset IDs: {pack.beatmapset_ids[:5]}..." if len(pack.beatmapset_ids) > 5 else f"Beatmapset IDs: {pack.beatmapset_ids}")
        print(f"Downloads: {pack.downloads}")
        print(f"Created At: {pack.created_at}")
        
        return pack
        
    except PackGenerationError as e:
        print(f"\n❌ Pack generation failed: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return None


def test_batch_pack_generation():
    """Test generating multiple packs"""
    print("\n" + "="*60)
    print("Testing Batch Pack Generation")
    print("="*60)
    
    anime_list = [
        "Steins;Gate",
        "Death Note",
        "Cowboy Bebop"
    ]
    
    print(f"\nGenerating packs for: {', '.join(anime_list)}")
    
    packs = pack_generator.generate_packs_batch(anime_list)
    
    print(f"\n✅ Successfully generated {len(packs)} pack(s)")
    for pack in packs:
        print(f"  - {pack.name} ({pack.beatmapset_count} beatmapsets)")
    
    return packs


def test_with_filters():
    """Test pack generation with mode filters"""
    print("\n" + "="*60)
    print("Testing Pack Generation with Mode Filter")
    print("="*60)
    
    try:
        anime_name = "K-On!"
        mode = 0  # osu!standard only
        
        print(f"\nGenerating pack for: {anime_name} (osu!standard only)")
        
        pack = pack_generator.generate_pack_from_anime(
            anime_name=anime_name,
            status=1,  # ranked only
            mode=mode
        )
        
        print(f"\n✅ Pack created successfully!")
        print(f"Pack Name: {pack.name}")
        print(f"Beatmapset Count: {pack.beatmapset_count}")
        
        return pack
        
    except PackGenerationError as e:
        print(f"\n❌ Pack generation failed: {e}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Pack Generator Service Tests")
    print("="*60)
    
    # Test 1: Single pack generation
    test_single_pack_generation()
    
    # Test 2: Batch pack generation
    # test_batch_pack_generation()
    
    # Test 3: Pack with filters
    # test_with_filters()
    
    print("\n" + "="*60)
    print("Tests Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
