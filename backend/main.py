from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_db, Base, engine
from models import Product, Inventory, Forecast, Supplier, PurchaseOrder, Constraint
from validator import validate_purchase
from scenarios import reset_scenario_1, reset_scenario_2
from agent.agent import run_agent
from agent.workflow import execute_purchase_workflow
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="ProcureAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "ProcureAI backend is running"}


@app.get("/purchasing/{sku}")
def get_purchasing_data(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    inventory = db.query(Inventory).filter(Inventory.product_id==product.id).first()
    forecast = db.query(Forecast).filter(Forecast.product_id==product.id).first()
    suppliers = db.query(Supplier).filter(Supplier.product_id==product.id).all()
    open_po = db.query(PurchaseOrder).filter(PurchaseOrder.product_id==product.id,PurchaseOrder.status=="OPEN").first()
    constraint = db.query(Constraint).filter(Constraint.node==inventory.node).first()

    return {
        "product": {"sku": product.sku,"name": product.name},
        "inventory": {"node": inventory.node,"quantity": inventory.quantity,"reserved_quantity": inventory.reserved_quantity},
        "forecast": {"expected_demand": forecast.expected_demand},
        "suppliers": [
            {
                "id": supplier.id,
                "name": supplier.name,
                "moq": supplier.moq,
                "lead_time_days": supplier.lead_time_days,
                "unit_price": supplier.unit_price,
                "available_quantity": supplier.available_quantity
            }
            for supplier in suppliers
        ],
        "open_po": {"quantity": open_po.quantity,"status": open_po.status
        } if open_po else None,
        "constraints": {
            "budget": constraint.budget,
            "storage_capacity": constraint.storage_capacity
        }
    }


@app.post("/purchasing/{sku}/validate")
def validate_purchase_request(sku: str,purchase_quantity: int,db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku==sku).first()

    if not product:
        return {"error": "Product not found"}

    inventory = db.query(Inventory).filter(Inventory.product_id==product.id).first()
    forecast = db.query(Forecast).filter(Forecast.product_id==product.id).first()
    supplier = db.query(Supplier).filter(Supplier.product_id==product.id).first()
    open_po = db.query(PurchaseOrder).filter(PurchaseOrder.product_id==product.id,PurchaseOrder.status=="OPEN").first()
    constraint = db.query(Constraint).filter(Constraint.node==inventory.node).first()

    result = validate_purchase(
        purchase_quantity=purchase_quantity,
        demand=forecast.expected_demand,
        inventory=inventory.quantity,
        incoming_po=open_po.quantity if open_po else 0,
        supplier_moq=supplier.moq,
        supplier_available_quantity=supplier.available_quantity,
        unit_price=supplier.unit_price,
        budget=constraint.budget,
        storage_capacity=constraint.storage_capacity
    )

    return result


@app.post("/agent/review/{sku}")
def review_purchase(sku: str,purchase_quantity: int,db: Session = Depends(get_db)):
    decision = run_agent(db=db,sku=sku,proposed_quantity=purchase_quantity)

    return {
        "sku": sku,
        "proposed_quantity": purchase_quantity,
        "agent_decision": decision
    }


@app.post("/agent/purchase/{sku}")
def agent_purchase(sku: str,purchase_quantity: int,db: Session = Depends(get_db)):
    return execute_purchase_workflow(db=db,sku=sku,proposed_quantity=purchase_quantity)


@app.post("/scenarios/reset/1")
def reset_scenario_one(db: Session = Depends(get_db)):
    return reset_scenario_1(db)


@app.post("/scenarios/reset/2")
def reset_scenario_two(db: Session = Depends(get_db)):
    return reset_scenario_2(db)
