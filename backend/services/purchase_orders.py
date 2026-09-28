from sqlalchemy.orm import Session
from models import PurchaseOrder, Product, Supplier


def create_purchase_order(db: Session,sku: str,quantity: int,supplier_id: int):
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        return {"success": False, "error": "Product not found"}

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id,Supplier.product_id == product.id).first()

    if not supplier:
        return {"success": False, "error": "Supplier not found"}

    order = PurchaseOrder(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=quantity,
        status="OPEN",
        node="Delhi-01"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "purchase_order_id": order.id,
        "quantity": order.quantity,
        "supplier": supplier.name,
        "supplier_id": supplier.id,
        "status": order.status
    }


def get_purchase_order(db: Session, order_id: int):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == order_id
    ).first()

    if not order:
        return None

    return {
        "id": order.id,
        "product_id": order.product_id,
        "supplier_id": order.supplier_id,
        "quantity": order.quantity,
        "status": order.status,
        "node": order.node
    }