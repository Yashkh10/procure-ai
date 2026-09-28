def validate_purchase(
    purchase_quantity,
    demand,
    inventory,
    incoming_po,
    supplier_moq,
    supplier_available_quantity,
    unit_price,
    budget,
    storage_capacity
):
    available_stock = inventory + incoming_po
    required_quantity = max(0, demand - available_stock)

    projected_inventory = inventory + incoming_po + purchase_quantity
    total_cost = purchase_quantity * unit_price

    errors = []

    if purchase_quantity < 0:
        errors.append("Purchase quantity cannot be negative")

    if purchase_quantity > 0 and purchase_quantity < supplier_moq:
        errors.append("Purchase quantity is below supplier MOQ")

    if purchase_quantity > supplier_available_quantity:
        errors.append("Supplier does not have enough available quantity")

    if total_cost > budget:
        errors.append("Purchase exceeds available budget")

    if projected_inventory > storage_capacity:
        errors.append("Purchase exceeds warehouse storage capacity")

    if purchase_quantity < required_quantity:
        errors.append("Purchase quantity is insufficient to meet expected demand")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "required_quantity": required_quantity,
        "projected_inventory": projected_inventory,
        "storage_capacity": storage_capacity,
        "total_cost": total_cost
    }
