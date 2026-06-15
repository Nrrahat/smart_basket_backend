import pytest

# Apply the asyncio mark to all test functions in this module
pytestmark = pytest.mark.asyncio(loop_scope="function")


async def test_health_check(client):
    """Tests the /health route directly."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_create_and_get_product(client):
    """Integration test checking schemas, routes, services, and models altogether."""
    payload = {
        "rfid_uid": "rfid_tag_123",
        "name": "Mechanical Keyboard",
        "price": 89.99,
        "weight": 850.5,
        "category": "Electronics"
    }

    # 1. Test POST /products (Create product)
    post_response = await client.post("/products", json=payload)
    assert post_response.status_code == 201
    data = post_response.json()
    assert data["name"] == "Mechanical Keyboard"
    assert "id" in data

    # 2. Test GET /products/{rfid_uid} (Retrieve product)
    get_response = await client.get(f"/products/{payload['rfid_uid']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Mechanical Keyboard"