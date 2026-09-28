from sqlalchemy.orm import Session

from agent.agent import run_agent
from validator import validate_purchase
from services.purchase_orders import create_purchase_order
from services.execution_validator import validate_execution
from models import Product, Inventory, Forecast, Supplier, PurchaseOrder, Constraint


def get_purchase_data(db: Session, sku: str):
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        return None

    inventory = db.query(Inventory).filter(
        Inventory.product_id == product.id
    ).first()

    forecast = db.query(Forecast).filter(
        Forecast.product_id == product.id
    ).first()

    suppliers = db.query(Supplier).filter(
        Supplier.product_id == product.id
    ).all()

    open_orders = db.query(PurchaseOrder).filter(
        PurchaseOrder.product_id == product.id,
        PurchaseOrder.status == "OPEN"
    ).all()

    constraint = db.query(Constraint).filter(
        Constraint.node == inventory.node
    ).first()

    return {
        "inventory": inventory,
        "forecast": forecast,
        "suppliers": suppliers,
        "open_orders": open_orders,
        "constraint": constraint
    }


def execute_purchase_workflow(
    db: Session,
    sku: str,
    proposed_quantity: int
):
    data = get_purchase_data(db, sku)

    if not data:
        return {
            "status": "ESCALATE",
            "reason": "Product not found"
        }

    decision = run_agent(
        db=db,
        sku=sku,
        proposed_quantity=proposed_quantity
    )

    if decision["decision"] in ["REJECT", "ESCALATE"]:
        return {
            "status": decision["decision"],
            "decision": decision
        }

    quantity = decision["recommended_quantity"]
    supplier_id = decision.get("supplier_id")

    supplier = None

    for item in data["suppliers"]:
        if item.id == supplier_id:
            supplier = item
            break

    if not supplier:
        return {
            "status": "ESCALATE",
            "decision": decision,
            "reason": "AI selected an invalid supplier"
        }

    if supplier_id and len(data["open_orders"]) == 1:
        existing_po = data["open_orders"][0]

        original_supplier = None

        for item in data["suppliers"]:
            if item.id == existing_po.supplier_id:
                original_supplier = item
                break

        if (
            original_supplier
            and existing_po.quantity > original_supplier.available_quantity
        ):
            shortfall = (
                existing_po.quantity
                - original_supplier.available_quantity
            )

            if quantity == shortfall:
                total_cost = (
                    original_supplier.available_quantity
                    * original_supplier.unit_price
                    + quantity * supplier.unit_price
                )

                projected_inventory = (
                    data["inventory"].quantity
                    + existing_po.quantity
                )

                errors = []

                if quantity < supplier.moq:
                    errors.append("Recovery quantity is below supplier MOQ")

                if quantity > supplier.available_quantity:
                    errors.append(
                        "Recovery supplier does not have enough available quantity"
                    )

                if total_cost > data["constraint"].budget:
                    errors.append("Recovery purchase exceeds available budget")

                if projected_inventory > data["constraint"].storage_capacity:
                    errors.append(
                        "Recovery purchase exceeds warehouse storage capacity"
                    )

                if errors:
                    return {
                        "status": "ESCALATE",
                        "decision": decision,
                        "validation": {
                            "valid": False,
                            "errors": errors
                        },
                        "reason": "Supplier recovery failed business validation"
                    }

                execution = create_purchase_order(
                    db=db,
                    sku=sku,
                    quantity=quantity,
                    supplier_id=supplier_id
                )

                if not execution["success"]:
                    return {
                        "status": "ESCALATE",
                        "decision": decision,
                        "execution": execution,
                        "reason": "Recovery purchase execution failed"
                    }

                post_validation = validate_execution(
                    db=db,
                    order_id=execution["purchase_order_id"],
                    expected_quantity=quantity
                )

                return {
                    "status": post_validation["status"],
                    "decision": decision,
                    "validation": {
                        "valid": True,
                        "errors": [],
                        "shortfall": shortfall,
                        "projected_inventory": projected_inventory,
                        "storage_capacity": data["constraint"].storage_capacity,
                        "total_cost": total_cost
                    },
                    "execution": execution,
                    "post_validation": post_validation
                }

    incoming_po = sum(
        order.quantity for order in data["open_orders"]
    )

    validation = validate_purchase(
        purchase_quantity=quantity,
        demand=data["forecast"].expected_demand,
        inventory=data["inventory"].quantity,
        incoming_po=incoming_po,
        supplier_moq=supplier.moq,
        supplier_available_quantity=supplier.available_quantity,
        unit_price=supplier.unit_price,
        budget=data["constraint"].budget,
        storage_capacity=data["constraint"].storage_capacity
    )

    if not validation["valid"]:
        return {
            "status": "ESCALATE",
            "decision": decision,
            "validation": validation,
            "reason": "AI decision failed business validation"
        }

    execution = create_purchase_order(
        db=db,
        sku=sku,
        quantity=quantity,
        supplier_id=supplier_id
    )

    if not execution["success"]:
        return {
            "status": "ESCALATE",
            "decision": decision,
            "validation": validation,
            "execution": execution,
            "reason": "Purchase execution failed"
        }

    post_validation = validate_execution(
        db=db,
        order_id=execution["purchase_order_id"],
        expected_quantity=quantity
    )

    return {
        "status": post_validation["status"],
        "decision": decision,
        "validation": validation,
        "execution": execution,
        "post_validation": post_validation
    }
