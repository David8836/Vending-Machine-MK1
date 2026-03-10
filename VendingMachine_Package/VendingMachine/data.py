import copy

DEFAULT_ITEMS = {
    "A1": {"name": "Pepsi", "price": 2.00, "cost": 0.80, "stock": 5, "category": "Consumable"},
    "A2": {"name": "Doritos Nacho Cheese", "price": 1.75, "cost": 0.70, "stock": 5, "category": "Consumable"},
    "A3": {"name": "Gatorade Cool Blue", "price": 2.50, "cost": 1.10, "stock": 5, "category": "Consumable"},
    "A4": {"name": "Oreo Cookies", "price": 1.75, "cost": 0.65, "stock": 5, "category": "Consumable"},
    "A5": {"name": "Dasani Water", "price": 1.50, "cost": 0.55, "stock": 5, "category": "Consumable"},

    "B1": {"name": "Band-Aids", "price": 2.00, "cost": 0.75, "stock": 5, "category": "Medical"},
    "B2": {"name": "Gauze Pads", "price": 2.50, "cost": 1.00, "stock": 5, "category": "Medical"},
    "B3": {"name": "Pain Relief Pills", "price": 3.50, "cost": 1.60, "stock": 5, "category": "Medical"},

    "C1": {"name": "USB-C Cable", "price": 7.00, "cost": 3.50, "stock": 5, "category": "Electronics"},
    "C2": {"name": "Wireless Earbuds", "price": 25.00, "cost": 14.00, "stock": 5, "category": "Electronics"}
}

itemsMaster = copy.deepcopy(DEFAULT_ITEMS)

categories = ["Consumable", "Medical", "Electronics"]