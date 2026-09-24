import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["backend"]["status"] == "connected"
        assert data["backend"]["port"] == 8000
        assert "ollama" in data
        assert "n8n" in data
        assert "comfyui" in data
        assert "tts" in data
        assert "ffmpeg" in data
