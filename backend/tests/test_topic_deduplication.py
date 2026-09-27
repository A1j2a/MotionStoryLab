import pytest
from httpx import AsyncClient
from ai.topic_researcher import (
    discover_kids_topics,
    normalize_topic_signature,
    is_topic_duplicate_or_excluded,
    save_discovered_topics_history,
)


def test_normalize_signature():
    sig1 = normalize_topic_signature("Chanda Mama 🌙 Kids Nursery Rhyme & Song")
    sig2 = normalize_topic_signature("Chanda Mama 🎶 3D Toddler Balgeet")
    assert "chanda" in sig1 and "mama" in sig1
    assert sig1 == sig2


def test_is_duplicate_detection():
    exc_sigs = {normalize_topic_signature("Bella the Blue Bus")}
    curr_sigs = set()
    
    cand_dup = {
        "suggested_title": "Bella the Blue Bus | Fun Sing Along 🎶",
        "topic": "Bella the Blue Bus & Friends",
    }
    cand_novel = {
        "suggested_title": "Orby the Night Owl | Sleepy Star Song ✨",
        "topic": "Orby the Night Owl Lullaby",
    }
    
    assert is_topic_duplicate_or_excluded(cand_dup, exc_sigs, curr_sigs) is True
    assert is_topic_duplicate_or_excluded(cand_novel, exc_sigs, curr_sigs) is False


def test_discover_kids_topics_zero_repeats_and_exclusions():
    excluded = ["Chanda Mama", "Titli Rani", "Bella the Blue Bus"]
    
    batch1 = discover_kids_topics(limit=6, excluded_topics=excluded, seed=12345)
    assert len(batch1) == 6
    
    # Check no duplicate titles within batch1
    titles1 = [b["suggested_title"].strip().lower() for b in batch1]
    assert len(titles1) == len(set(titles1))
    
    # Check that excluded topics are not present
    for b in batch1:
        t_lower = (b["suggested_title"] + " " + b["topic"]).lower()
        for exc in excluded:
            assert exc.lower() not in t_lower or "episode" in t_lower

    # Second batch should not repeat batch1
    batch2 = discover_kids_topics(limit=6, excluded_topics=excluded + [b["topic"] for b in batch1], seed=67890)
    assert len(batch2) == 6
    titles2 = [b["suggested_title"].strip().lower() for b in batch2]
    
    # Zero intersection between batch1 and batch2
    intersection = set(titles1) & set(titles2)
    assert len(intersection) == 0


@pytest.mark.asyncio
async def test_api_topic_discovery_excludes_existing_project(client: AsyncClient):
    # 1. Create a project with a specific topic
    custom_topic = "Unique Dino Dan Exploring Crystal Caves"
    sel_res = await client.post("/api/v1/topics/select", json={
        "topic": custom_topic,
        "title": f"{custom_topic} 🎶✨",
        "category": "Vehicles & Animals",
        "target_age": "2–5 Years",
        "content_angle": "Fun cave adventure hook",
        "why_worth_considering": "Popular dino theme",
        "opportunity_signals": "High search volume",
        "suggested_characters": ["Dino Dan"],
        "suggested_story_concept": "Exploring sparkling caves",
    })
    assert sel_res.status_code == 201

    # 2. Discover topics — should NEVER include custom_topic
    disc_res = await client.get("/api/v1/topics/discover?limit=8")
    assert disc_res.status_code == 200
    disc_topics = disc_res.json()
    assert len(disc_topics) >= 4

    for t in disc_topics:
        assert custom_topic.lower() not in t["suggested_title"].lower()
        assert custom_topic.lower() not in t["topic"].lower()
