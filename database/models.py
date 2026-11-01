import sqlite3

def get_connection():
    conn = sqlite3.connect('warehouse.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. جدول الأصناف والمنتجات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT NOT NULL,
            unit TEXT DEFAULT 'قطعة',
            buy_price REAL NOT NULL,
            sell_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            min_limit INTEGER DEFAULT 5
        )
    ''')

    # 2. جدول العملاء
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')

    # 3. جدول الأسعار المخصصة لكل عميل صنف
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_prices (
            customer_id INTEGER,
            product_id INTEGER,
            price REAL NOT NULL,
            PRIMARY KEY (customer_id, product_id),
            FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    # 4. جدول الفواتير الرئيسية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            payment_type TEXT DEFAULT 'كاش',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL
        )
    ''')

    # 5. جدول عناصر الفاتورة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    # 6. جدول الخزينة والحركات المالية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treasury (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. جدول المرتجعات (تمت إضافته لمنع أي خطأ 500 في التحليلات)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            return_type TEXT DEFAULT 'مرتجع مبيعات',
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()