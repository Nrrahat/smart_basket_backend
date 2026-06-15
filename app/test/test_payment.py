# app/test/test_payment.py
import pytest
from decimal import Decimal
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_successful_checkout_lifecycle(client: AsyncClient):
    """Tests the full payment checkout lifecycle.
    
    Seeds a product, creates an order, adds the item to the order, 
    and verifies that checkout locks the order and returns a valid bill with a QR code.
    """
    
    # 1. Seed a mock product into the test database
    product_payload = {
        "rfid_uid": "rfid_coffee_99",
        "name": "Latte Macchiato",
        "price": 5.25,
        "weight": 350.0,
        "category": "Beverages"
    }
    prod_resp = await client.post("/products", json=product_payload)
    assert prod_resp.status_code == 201

    # 2. Create a brand new pending order session
    order_resp = await client.post("/orders")
    assert order_resp.status_code == 201
    order_id = order_resp.json()["id"]

    # 3. Scan the product via RFID to add it to our basket session
    scan_resp = await client.post(f"/orders/{order_id}/add-item?rfid_uid=rfid_coffee_99")
    assert scan_resp.status_code == 200
    
    # 4. Trigger the checkout endpoint process
    checkout_payload = {"order_id": order_id}
    checkout_resp = await client.post("/payments/checkout", json=checkout_payload)
    
    # Assert HTTP response success
    assert checkout_resp.status_code == 201
    
    bill_data = checkout_resp.json()
    
    # 5. Assert Billing Structural Fields
    assert bill_data["bill_id"] is not None
    assert bill_data["order_id"] == order_id
    assert bill_data["status"] == "pending"
    assert Decimal(str(bill_data["total_price"])) == Decimal("5.25")
    
    # 6. Assert Itemized Breakdown Receipt Array
    assert len(bill_data["items"]) == 1
    receipt_item = bill_data["items"][0]
    assert receipt_item["product_name"] == "Latte Macchiato"
    assert receipt_item["quantity"] == 1
    assert Decimal(str(receipt_item["unit_price"])) == Decimal("5.25")
    assert Decimal(str(receipt_item["subtotal"])) == Decimal("5.25")
    
    # 7. Assert Image Data Verification Rules
    assert "qr_code_base64" in bill_data
    assert bill_data["qr_code_base64"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_checkout_fails_for_empty_basket(client: AsyncClient):
    """Verifies that the checkout system prevents building invoices for empty baskets."""
    # Create an order session but do not scan any products into it
    order_resp = await client.post("/orders")
    assert order_resp.status_code == 201
    order_id = order_resp.json()["id"]

    # Trigger checkout immediately
    checkout_payload = {"order_id": order_id}
    checkout_resp = await client.post("/payments/checkout", json=checkout_payload)
    
    # Should fail validation because the basket has 0 items
    assert checkout_resp.status_code == 400
    assert checkout_resp.json()["detail"] == "Cannot checkout an empty basket"


@pytest.mark.asyncio
async def test_cannot_checkout_twice(client: AsyncClient):
    """Ensures an order cannot undergo processing twice once its state has shifted to completed."""
    # Seed a product and an order
    await client.post("/products", json={
        "rfid_uid": "rfid_snack_12", "name": "Chips", "price": 2.00, "weight": 150.0, "category": "Snacks"
    })
    order_resp = await client.post("/orders")
    order_id = order_resp.json()["id"]
    await client.post(f"/orders/{order_id}/add-item?rfid_uid=rfid_snack_12")

    # First checkout (Succeeds)
    first_checkout = await client.post("/payments/checkout", json={"order_id": order_id})
    assert first_checkout.status_code == 201

    # Second checkout attempt (Should fail since status changed from PENDING to COMPLETED)
    second_checkout = await client.post("/payments/checkout", json={"order_id": order_id})
    assert second_checkout.status_code == 400
    assert "already checked out" in second_checkout.json()["detail"]