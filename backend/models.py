from sqlalchemy import Column, Integer, String, Float
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    node = Column(String)
    quantity = Column(Integer)
    reserved_quantity = Column(Integer, default=0)


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    expected_demand = Column(Integer)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    name = Column(String)
    moq = Column(Integer)
    lead_time_days = Column(Integer)
    unit_price = Column(Float)
    available_quantity = Column(Integer)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    supplier_id = Column(Integer)
    quantity = Column(Integer)
    status = Column(String)
    node = Column(String)


class Constraint(Base):
    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True)
    node = Column(String)
    budget = Column(Float)
    storage_capacity = Column(Integer)