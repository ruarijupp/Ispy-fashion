import sqlite3

DB_PATH = "products.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            title TEXT,
            image_url TEXT,
            price TEXT,
            link TEXT,
            brand TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_product(product):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO products (id, title, image_url, price, link, brand)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        product["id"],
        product["title"],
        product["image_url"],
        product["price"],
        product["link"],
        product["brand"]
    ))
    conn.commit()
    conn.close()
