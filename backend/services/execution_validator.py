from sqlalchemy.orm import Session

from models import PurchaseOrder


def validate_execution(
    db: Session,
    order_id: int,
    expected_quantity: int
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == order_id
    ).first()

    if not order:
        return {
            "valid": False,
            "status": "ESCALATE",
            "reason": "Purchase order was not created"
        }

    if order.status != "OPEN":
        return {
            "valid": False,
            "status": "ESCALATE",
            "reason": f"Unexpected purchase order status: {order.status}"
        }

    if order.quantity != expected_quantity:
        return {
            "valid": False,
            "status": "ESCALATE",
            "reason": (
                f"Expected quantity {expected_quantity}, "
                f"but order contains {order.quantity}"
            )
        }

    return {
        "valid": True,
        "status": "SUCCESS",
        "reason": "Purchase order created correctly"
    }
