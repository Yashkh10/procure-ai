from sqlalchemy.orm import Session
from models import Product, Inventory, Forecast, Supplier, PurchaseOrder, Constraint


def get_product(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    return {"id": product.id,"sku": product.sku,"name": product.name}


def get_inventory(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    inventory = db.query(Inventory).filter(Inventory.product_id==product.id).first()

    if not inventory:
        return {"error": "Inventory not found"}

    return {
        "node": inventory.node,
        "quantity": inventory.quantity,
        "reserved_quantity": inventory.reserved_quantity
    }


def get_forecast(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    forecast = db.query(Forecast).filter(Forecast.product_id==product.id).first()

    if not forecast:
        return {"error": "Forecast not found"}

    return {"expected_demand": forecast.expected_demand}


def get_suppliers(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        return {"error": "Product not found"}

    suppliers = db.query(Supplier).filter(Supplier.product_id == product.id).all()

    if not suppliers:
        return {"error": "No suppliers found"}

    return [
        {
            "id": supplier.id,
            "name": supplier.name,
            "moq": supplier.moq,
            "lead_time_days": supplier.lead_time_days,
            "unit_price": supplier.unit_price,
            "available_quantity": supplier.available_quantity
        }
        for supplier in suppliers
    ]


def get_open_purchase_orders(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    orders = db.query(PurchaseOrder).filter(PurchaseOrder.product_id==product.id,PurchaseOrder.status=="OPEN").all()

    return [
        {
            "id": order.id,
            "quantity": order.quantity,
            "node": order.node,
            "status": order.status
        }
        for order in orders
    ]


def get_constraints(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    inventory = db.query(Inventory).filter(Inventory.product_id==product.id).first()

    if not inventory:
        return {"error": "Inventory not found"}

    constraint = db.query(Constraint).filter(Constraint.node==inventory.node).first()

    if not constraint:
        return {"error": "Constraints not found"}

    return {
        "node": constraint.node,
        "budget": constraint.budget,
        "storage_capacity": constraint.storage_capacity
    }