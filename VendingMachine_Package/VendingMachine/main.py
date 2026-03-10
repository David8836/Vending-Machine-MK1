from db import init_db, seed_inventory
from data import itemsMaster
from vending_ui import start_ui


def main():
    init_db()
    seed_inventory(itemsMaster)
    start_ui()


if __name__ == "__main__":
    main()