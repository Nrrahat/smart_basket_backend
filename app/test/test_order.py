import pytest
from decimal import Decimal

# Apply the asyncio mark to all test functions in this module
pytestmark = pytest.mark.asyncio(loop_scope="function")


async def test_order_lifecycle(client):
    """Tests starting an order session and scanning products via RFID."""
    
    # 1. Seed a product into the test database
    product_payload = {
        "rfid_uid": "rfid_milk_77",
        "name": "Organic Whole Milk",
        "price": 4.50,
        "weight": 1000.0,
        "category": "Dairy"
    }
    prod_resp = await client.post("/products", json=product_payload)
    assert prod_resp.status_code == 201

    # 2. Create a new order session
    order_resp = await client.post("/orders")
    assert order_resp.status_code == 201
    order_data = order_resp.json()
    
    assert order_data["id"] is not None
    assert order_data["status"] == "pending"
    assert Decimal(str(order_data["total_price"])) == Decimal("0.00")
    assert len(order_data["items"]) == 0
    
    order_id = order_data["id"]

    # 3. Scan the product the first time
    scan_1_resp = await client.post(f"/orders/{order_id}/add-item?rfid_uid=rfid_milk_77")
    assert scan_1_resp.status_code == 200
    scan_1_data = scan_1_resp.json()
    
    assert Decimal(str(scan_1_data["total_price"])) == Decimal("4.50")
    assert len(scan_1_data["items"]) == 1
    assert scan_1_data["items"][0]["quantity"] == 1

    # 4. Scan the exact same product a second time (Quantity should increment)
    scan_2_resp = await client.post(f"/orders/{order_id}/add-item?rfid_uid=rfid_milk_77")
    assert scan_2_resp.status_code == 200
    scan_2_data = scan_2_resp.json()
    
    assert Decimal(str(scan_2_data["total_price"])) == Decimal("9.00")
    assert scan_2_data["items"][0]["quantity"] == 2


async def test_scan_non_existent_rfid(client):
    """Verifies that scanning an unrecognized RFID code throws an appropriate 404 error."""
    
    # 1. Initialize an empty order session
    order_resp = await client.post("/orders")
    order_id = order_resp.json()["id"]
    
    # 2. Attempt to scan an invalid RFID tag
    bad_scan_resp = await client.post(f"/orders/{order_id}/add-item?rfid_uid=ghost_rfid_999")
    assert bad_scan_resp.status_code == 404
    assert "linked to rfid" in bad_scan_resp.json()["detail"].lower()