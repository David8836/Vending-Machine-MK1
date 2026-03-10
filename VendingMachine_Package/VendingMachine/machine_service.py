from data import itemsMaster, DEFAULT_ITEMS
from db import (
    update_machine_status,
    reduce_stock,
    load_inventory_into_items,
    reset_inventory_from_data,
    record_sale,
    get_best_profit_item,
    get_most_bought_item,
    get_least_bought_item
)
from config import MACHINE_ID

balance = 0.0
cart = []


def refresh_inventory():
    load_inventory_into_items(itemsMaster)


def reset_stock_to_data():
    reset_inventory_from_data(DEFAULT_ITEMS)
    refresh_inventory()


def cart_total():
    return sum(itemsMaster[c]["price"] for c in cart)


def add_to_cart(code):
    refresh_inventory()

    if itemsMaster[code]["stock"] <= 0:
        return False

    cart.append(code)
    return True


def remove_from_cart(code):
    if code in cart:
        cart.remove(code)


def insert_money(amount):
    global balance
    balance += amount


def return_change():
    global balance
    balance = 0.0


def checkout():
    global balance

    refresh_inventory()

    total = cart_total()

    if total == 0:
        return False, "Cart is empty"

    if total > balance:
        return False, f"Not enough balance. Need ${total - balance:.2f} more."

    for code in cart:
        if itemsMaster[code]["stock"] <= 0:
            return False, f"{itemsMaster[code]['name']} is out of stock"

    for code in cart:
        success = reduce_stock(code)
        if not success:
            return False, f"{itemsMaster[code]['name']} is out of stock"

        item = itemsMaster[code]
        record_sale(
            code,
            item["name"],
            item["category"],
            item["price"],
            item["cost"]
        )

    refresh_inventory()

    balance -= total
    cart.clear()

    return True, "Purchase complete"


def update_machine_state(state, temp, hum):
    update_machine_status(MACHINE_ID, state, temp, hum)


def sales_summary():
    return {
        "best_profit": get_best_profit_item(),
        "most_bought": get_most_bought_item(),
        "least_bought": get_least_bought_item()
    }