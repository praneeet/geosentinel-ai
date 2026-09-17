import pytest
from app.deduplication.exact_sha256 import calculate_sha256, normalize_text_for_hash
from app.deduplication.minhash_lsh import MinHashLSHDeduplicator

def test_exact_sha256_duplicate_detection():
    text1 = "Military forces conducted border surveillance patrols across the northern ridge."
    text2 = "  Military forces conducted   border surveillance patrols across the northern ridge.  "
    text3 = "<b>Military forces</b> conducted border surveillance patrols across the northern ridge."

    hash1 = calculate_sha256(text1)
    hash2 = calculate_sha256(text2)
    hash3 = calculate_sha256(text3)

    assert hash1 == hash2
    assert hash1 == hash3
    assert len(hash1) == 64

def test_minhash_lsh_near_duplicate_detection():
    dedup = MinHashLSHDeduplicator(threshold=0.82, num_perm=128, shingle_size=2)

    original_text = (
        "Defense ministries confirmed joint naval maneuvers involving guided missile destroyers "
        "and amphibious transport vessels navigating through designated maritime corridors. "
        "Surveillance aircraft monitored high-speed interception drills along international territorial waters. "
        "Allied commanders reiterated their commitment to maintaining navigational freedom and regional stability across the region."
    )
    # Syndicated wire re-release with slight variation in wording (Jaccard > 0.82)
    syndicated_text = (
        "Defense ministries confirmed joint naval maneuvers involving guided missile destroyers "
        "and amphibious transport vessels navigating through designated maritime corridors. "
        "Surveillance aircraft monitored high-speed interception drills along international territorial waters. "
        "Allied commanders reiterated their commitment to maintaining navigational freedom and stability across the region."
    )
    # Completely distinct article
    different_text = (
        "Central bankers announced sudden interest rate hikes following energy inflation figures "
        "sparking bond yield inversions across agricultural commodities markets and treasury securities."
    )

    # Insert original
    status1, canon1, sim1 = dedup.check_and_insert("art_orig", original_text)
    assert status1 == "unique"
    assert canon1 is None

    # Check syndicated wire article -> should be identified as near_duplicate
    status2, canon2, sim2 = dedup.check_and_insert("art_synd", syndicated_text)
    assert status2 == "near_duplicate"
    assert canon2 == "art_orig"
    assert sim2 >= 0.82

    # Check distinct article -> should be unique
    status3, canon3, sim3 = dedup.check_and_insert("art_diff", different_text)
    assert status3 == "unique"
    assert canon3 is None
