from database import engine, SessionLocal, Base
from models import (
    Product,
    Inventory,
    Forecast,
    Supplier,
    PurchaseOrder,
    Constraint
)


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    if db.query(Product).first():
        db.close()
        return

    product = Product(
        sku="MILK-001",
        name="Fresh Milk 1L"
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    inventory = Inventory(
        product_id=product.id,
        node="Delhi-01",
        quantity=300,
        reserved_quantity=0
    )

    forecast = Forecast(
        product_id=product.id,
        expected_demand=1000
    )

    supplier = Supplier(
        product_id=product.id,
        name="FreshFoods Supplier",
        moq=100,
        lead_time_days=3,
        unit_price=40,
        available_quantity=1000
    )

    po = PurchaseOrder(
        product_id=product.id,
        supplier_id=1,
        quantity=400,
        status="OPEN",
        node="Delhi-01"
    )

    constraint = Constraint(
        node="Delhi-01",
        budget=20000,
        storage_capacity=1000
    )

    db.add_all([
        inventory,
        forecast,
        supplier,
        po,
        constraint
    ])

    db.commit()
    db.close()


if __name__ == "__main__":
    seed()