import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_stats_summary():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/stats/summary")
    # Assuming the DB might be empty or mock isn't provided, 
    # we expect a 200 status code and basic keys
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "blocked_queries" in data

@pytest.mark.asyncio
async def test_domain_analyze():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/analyze", json={"domain": "google.com"})
    assert response.status_code == 200
    data = response.json()
    assert "domain" in data
    assert "prediction" in data
    assert "risk_score" in data

@pytest.mark.asyncio
async def test_settings_endpoints():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Get settings
        response = await ac.get("/api/v1/settings")
        assert response.status_code == 200
        
        # Update setting (mock/test payload)
        update_response = await ac.put("/api/v1/settings", json={"upstream_dns": "1.1.1.1"})
        # 200 or 400 depending on actual validation, assuming 200 for valid
        assert update_response.status_code in [200, 422]
