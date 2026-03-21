import sqlite3
from datetime import datetime
from config import DB_NAME


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS machine_status (
        machine_id TEXT PRIMARY KEY,
        state TEXT,
        temperature REAL,
        humidity REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item_code TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        cost REAL,
        stock INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code TEXT,
        item_name TEXT,
        category TEXT,
        price REAL,
        cost REAL,
        profit REAL,
        sold_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_inventory(items):
    conn = connect()
    cur = conn.cursor()

    for code, item in items.items():
        cur.execute("""
        INSERT OR IGNORE INTO inventory (item_code, name, category, price, cost, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            code,
            item["name"],
            item["category"],
            item["price"],
            item["cost"],
            item["stock"]
        ))

    conn.commit()
    conn.close()


def reset_inventory_from_data(items):
    conn = connect()
    cur = conn.cursor()

    for code, item in items.items():
        cur.execute("""
        INSERT INTO inventory (item_code, name, category, price, cost, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_code) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            price = excluded.price,
            cost = excluded.cost,
            stock = excluded.stock
        """, (
            code,
            item["name"],
            item["category"],
            item["price"],
            item["cost"],
            item["stock"]
        ))

    conn.commit()
    conn.close()


def load_inventory_into_items(items):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT item_code, stock FROM inventory")
    rows = cur.fetchall()

    conn.close()

    for code, stock in rows:
        if code in items:
            items[code]["stock"] = stock


def restock_item(item_code, amount):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE inventory
    SET stock = stock + ?
    WHERE item_code = ?
    """, (amount, item_code))

    conn.commit()
    success = cur.rowcount > 0
    conn.close()

    return success


def update_machine_status(machine_id, state, temperature, humidity):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO machine_status(machine_id, state, temperature, humidity)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(machine_id) DO UPDATE SET
        state = excluded.state,
        temperature = excluded.temperature,
        humidity = excluded.humidity
    """, (machine_id, state, temperature, humidity))

    conn.commit()
    conn.close()


def record_sale(item_code, item_name, category, price, cost):
    conn = connect()
    cur = conn.cursor()

    profit = price - cost
    sold_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
    INSERT INTO sales (item_code, item_name, category, price, cost, profit, sold_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item_code,
        item_name,
        category,
        price,
        cost,
        profit,
        sold_at
    ))

    conn.commit()
    conn.close()


def get_best_profit_item():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT item_name, SUM(profit) AS total_profit
    FROM sales
    GROUP BY item_code, item_name
    ORDER BY total_profit DESC
    LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return row


def get_most_bought_item():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT item_name, COUNT(*) AS times_bought
    FROM sales
    GROUP BY item_code, item_name
    ORDER BY times_bought DESC
    LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return row


def get_least_bought_item():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT item_name, COUNT(*) AS times_bought
    FROM sales
    GROUP BY item_code, item_name
    ORDER BY times_bought ASC
    LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return row
