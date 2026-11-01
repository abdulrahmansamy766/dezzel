import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_connection
# --- دوال المنتجات والمخزن ---
def add_product(barcode, name, unit, buy_price, sell_price, quantity, min_limit, custom_prices=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (barcode, name, unit, buy_price, sell_price, quantity, min_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (barcode, name, unit, buy_price, sell_price, quantity, min_limit))
        product_id = cursor.lastrowid
        
        if custom_prices:
            for item in custom_prices:
                cursor.execute('''
                    INSERT INTO customer_prices (customer_id, product_id, price)
                    VALUES (?, ?, ?)
                    ON CONFLICT(customer_id, product_id) DO UPDATE SET price = ?
                ''', (item['customer_id'], product_id, item['price'], item['price']))

        conn.commit()
        conn.close()
        return True, "تم إضافة المنتج وأسعاره المخصصة بنجاح"
    except Exception as e:
        return False, str(e)

def update_product(product_id, barcode, name, unit, buy_price, sell_price, quantity, min_limit):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET barcode = ?, name = ?, unit = ?, buy_price = ?, sell_price = ?, quantity = ?, min_limit = ?
            WHERE id = ?
        ''', (barcode, name, unit, buy_price, sell_price, quantity, min_limit, product_id))
        
        conn.commit()
        conn.close()
        return True, "تم تعديل وصفظ بيانات الصنف بنجاح 💾"
    except Exception as e:
        return False, str(e)    

def update_customer(customer_id, name, phone, balance):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customers 
            SET name = ?, phone = ?, balance = ?
            WHERE id = ?
        ''', (name, phone, balance, customer_id))
        conn.commit()
        conn.close()
        return True, "تم تعديل بيانات العميل بنجاح"
    except Exception as e:
        return False, str(e)

def get_all_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    except:
        return []

# --- دالة النواقص المحمية لمنع خطأ 500 ---
def get_low_stock_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, barcode, name, unit, buy_price, sell_price, quantity, min_limit FROM products WHERE quantity <= min_limit")
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    except Exception as e:
        print(f"Error in get_low_stock: {e}")
        return []

# --- دوال الحذف ---
def delete_product(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customer_prices WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return True, "تم حذف الصنف بنجاح"
    except Exception as e:
        return False, str(e)
    
def get_product_price_for_customer(product_id, customer_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # لو عندك جدول مخصص لأسعار العملاء (مثلا customer_prices)
        cursor.execute('''
            SELECT price FROM customer_prices 
            WHERE customer_id = ? AND product_id = ?
        ''', (customer_id, product_id))
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return row['price']
            
        # لو مفيش سعر مخصص، رجع سعر البيع الافتراضي للصنف
        cursor.execute('SELECT sell_price FROM products WHERE id = ?', (product_id,))
        prod = cursor.fetchone()
        conn.close()
        
        return prod['sell_price'] if prod else 0.0
    except Exception:
        return 0.0    

def get_all_customers():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers
    except:
        return []

def get_treasury_transactions():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treasury ORDER BY created_at DESC")
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    except Exception as e:
        print(f"Treasury Error: {e}")
        return []

# --- دوال التحليلات للوحة التحكم (محمية بالكامل لتفادي خطأ 500) ---
def get_dashboard_analytics():
    # قيم افتراضية آمنة في حال أي خطأ
    analytics = {
        'total_invoices': 0,
        'total_sales': 0.0,
        'total_returns': 0.0,
        'net_sales': 0.0,
        'treasury_balance': 0.0,
        'total_customers': 0,
        'total_debts': 0.0
    }
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. إجمالي الفواتير والمبيعات
        try:
            cursor.execute('SELECT COUNT(id) as total_invoices, SUM(total_amount) as total_sales FROM invoices')
            inv_res = cursor.fetchone()
            if inv_res:
                analytics['total_invoices'] = inv_res['total_invoices'] or 0
                analytics['total_sales'] = inv_res['total_sales'] or 0.0
        except Exception as e:
            print(f"Analytics Invoices Error: {e}")

        # 2. إجمالي المرتجعات
        try:
            cursor.execute("SELECT SUM(total_amount) as total_returns FROM returns WHERE return_type = 'مرتجع مبيعات'")
            ret_res = cursor.fetchone()
            if ret_res:
                analytics['total_returns'] = ret_res['total_returns'] or 0.0
        except Exception as e:
            print(f"Analytics Returns Error: {e}")

        analytics['net_sales'] = analytics['total_sales'] - analytics['total_returns']

        # 3. رصيد الخزينة
        try:
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'وارد' THEN amount ELSE 0 END) as total_in,
                    SUM(CASE WHEN type = 'صادر' THEN amount ELSE 0 END) as total_out
                FROM treasury
            ''')
            treasury_res = cursor.fetchone()
            if treasury_res:
                treasury_in = treasury_res['total_in'] or 0.0
                treasury_out = treasury_res['total_out'] or 0.0
                analytics['treasury_balance'] = treasury_in - treasury_out
        except Exception as e:
            print(f"Analytics Treasury Error: {e}")

        # 4. العملاء والديون
        try:
            cursor.execute('SELECT COUNT(id) as total_customers, SUM(balance) as total_debts FROM customers')
            cust_res = cursor.fetchone()
            if cust_res:
                analytics['total_customers'] = cust_res['total_customers'] or 0
                analytics['total_debts'] = cust_res['total_debts'] or 0.0
        except Exception as e:
            print(f"Analytics Customers Error: {e}")

        conn.close()
    except Exception as e:
        print(f"General Dashboard Connection Error: {e}")
        
    return analytics            
