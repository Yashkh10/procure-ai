from sqlalchemy.orm import Session

from models import (
    Product,
    Inventory,
    Forecast,
    Supplier,
    PurchaseOrder,
    Constraint
)


def reset_scenario_1(db: Session):
    db.query(PurchaseOrder).delete()
    db.query(Inventory).delete()
    db.query(Forecast).delete()
    db.query(Supplier).delete()
    db.query(Constraint).delete()
    db.query(Product).delete()

    db.commit()

    product = Product(sku="MILK-001",name="Fresh Milk 1L")

    db.add(product)
    db.commit()
    db.refresh(product)

    inventory = Inventory(product_id=product.id,node="Delhi-01",quantity=300,reserved_quantity=0)
    forecast = Forecast(product_id=product.id,expected_demand=1000)
    supplier = Supplier(product_id=product.id,name="FreshFoods Supplier",moq=100,lead_time_days=3,unit_price=40,available_quantity=1000)
    constraint = Constraint(node="Delhi-01",budget=20000,storage_capacity=1000)

    db.add(inventory)
    db.add(forecast)
    db.add(supplier)
    db.add(constraint)

    db.commit()
    db.refresh(supplier)

    purchase_order = PurchaseOrder(product_id=product.id,supplier_id=supplier.id,quantity=400,status="OPEN",node="Delhi-01")

    db.add(purchase_order)
    db.commit()

    return {"scenario": 1,"name": "Purchase Recommendation Review","status": "reset","sku": product.sku}



def reset_scenario_2(db: Session):
    db.query(PurchaseOrder).delete()
    db.query(Inventory).delete()
    db.query(Forecast).delete()
    db.query(Supplier).delete()
    db.query(Constraint).delete()
    db.query(Product).delete()

    db.commit()

    product = Product(
        sku="RICE-001",
        name="Basmati Rice 5kg"
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    inventory = Inventory(product_id=product.id,node="Delhi-01",quantity=100,reserved_quantity=0)

    forecast = Forecast(product_id=product.id,expected_demand=600)

    supplier_a = Supplier(
        product_id=product.id,
        name="Reliable Foods",
        moq=100,
        lead_time_days=3,
        unit_price=50,
        available_quantity=250
    )

    supplier_b = Supplier(
        product_id=product.id,
        name="Backup Foods",
        moq=100,
        lead_time_days=4,
        unit_price=55,
        available_quantity=500
    )

    constraint = Constraint(
        node="Delhi-01",
        budget=30000,
        storage_capacity=800
    )

    db.add(inventory)
    db.add(forecast)
    db.add(supplier_a)
    db.add(supplier_b)
    db.add(constraint)

    db.commit()
    db.refresh(supplier_a)

    purchase_order = PurchaseOrder(
        product_id=product.id,
        supplier_id=supplier_a.id,
        quantity=500,
        status="OPEN",
        node="Delhi-01"
    )

    db.add(purchase_order)
    db.commit()

    return {"scenario": 2,"name": "Supplier Cannot Fulfil","status": "reset","sku": product.sku}