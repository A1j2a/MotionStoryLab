import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_topic_discovery_endpoint(client: AsyncClient):
    res = await client.get("/api/v1/topics/discover?limit=10")
    assert res.status_code == 200
    topics = res.json()
    assert isinstance(topics, list)
    assert len(topics) >= 5
    first = topics[0]
    assert "topic" in first
    assert "suggested_title" in first
    assert "category" in first
    assert "target_age" in first
    assert "search_keywords" in first
    assert "content_angle" in first
    assert "why_worth_considering" in first
    assert "opportunity_signals" in first
    assert "suggested_characters" in first
    assert "suggested_story_concept" in first


@pytest.mark.asyncio
async def test_topic_selection_and_content_package_flow(client: AsyncClient):
    # 1. Select Topic
    select_payload = {
        "topic": "Toto the Little Train Meets Farm Animals",
        "title": "Toto the Choo-Choo Train & Farm Animals 🚂",
        "category": "Vehicles & Animals",
        "target_age": "1–4 Years",
        "content_angle": "Fun call-and-response animal sounds",
        "why_worth_considering": "High engagement for toddler vehicle rhymes",
        "opportunity_signals": "High search volume on YouTube Kids",
        "suggested_characters": ["Toto the Train", "Daisy Cow"],
        "suggested_story_concept": "Toto visits farm stations.",
    }
    sel_res = await client.post("/api/v1/topics/select", json=select_payload)
    assert sel_res.status_code == 201
    project = sel_res.json()
    project_id = project["id"]

    # 2. Generate Content Package
    pkg_res = await client.post(f"/api/v1/projects/{project_id}/content-package/generate")
    assert pkg_res.status_code == 200
    pkg = pkg_res.json()
    assert "title" in pkg
    assert "lyrics_full" in pkg
    assert "characters" in pkg
    assert "approved_lyrics" in pkg

    # 3. Save Approved Content Package
    save_payload = {
        "title": pkg["title"],
        "approved_lyrics": pkg["approved_lyrics"] + "\n[Extra Verse]\nHappy children sing along!",
        "characters": pkg["characters"],
        "story_concept": pkg.get("story_concept", "Fun train ride"),
    }
    save_res = await client.put(f"/api/v1/projects/{project_id}/content-package", json=save_payload)
    assert save_res.status_code == 200
    saved_pkg = save_res.json()
    assert "Happy children sing along!" in saved_pkg["approved_lyrics"]

    # 4. Generate Storyboard from approved lyrics
    sb_res = await client.post(f"/api/v1/projects/{project_id}/storyboard/generate")
    assert sb_res.status_code == 200
    scenes = sb_res.json()
    assert isinstance(scenes, list)
    assert len(scenes) >= 1

    # 5. Validate Storyboard
    val_res = await client.get(f"/api/v1/projects/{project_id}/storyboard/validate")
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert "is_valid" in val_data

    # 6. Quality Control
    qc_res = await client.post(f"/api/v1/projects/{project_id}/qc/run")
    assert qc_res.status_code == 200
    qc_data = qc_res.json()
    assert "status" in qc_data
    assert "checks" in qc_data

    # 7. YouTube Upload Mock
    yt_res = await client.post(f"/api/v1/projects/{project_id}/youtube/upload", json={"privacy_status": "private"})
    # Note: final.mp4 not rendered yet, returns 400 with clear message
    assert yt_res.status_code in (200, 400)


@pytest.mark.asyncio
async def test_ai_settings_endpoint(client: AsyncClient):
    # 1. Get AI settings
    get_res = await client.get("/api/v1/settings/ai")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "openrouter_enabled" in data
    assert "openrouter_model" in data
    assert "available_models" in data

    # 2. Update AI settings
    update_payload = {
        "openrouter_enabled": True,
        "openrouter_model": "deepseek/deepseek-r1:free",
        "openrouter_api_key": "sk-or-v1-testkey1234567890",
    }
    post_res = await client.post("/api/v1/settings/ai", json=update_payload)
    assert post_res.status_code == 200
    updated_data = post_res.json()
    assert updated_data["openrouter_enabled"] is True
    assert updated_data["openrouter_model"] == "deepseek/deepseek-r1:free"
    assert updated_data["openrouter_api_key_masked"].startswith("sk-or-")
