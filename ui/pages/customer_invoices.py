from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar

    

# هينزل الشاشة والقائمة المنسدلة تلقائياً في قمة الصفحة
    
    # باقي كود الصفحة الخاص بـ POS
def render_customer_invoices_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    with ui.column().classes('w-full p-6 gap-6'):
        
        with ui.card().classes('w-full p-6 bg-white shadow-sm rounded-lg gap-4'):
            ui.label('🔍 بحث وفلترة فواتير العملاء').classes('text-xl font-bold text-gray-800')

            customers = crud.get_all_customers()
            if not customers:
                ui.label('لا توجد عملاء مسجلين حالياً.').classes('text-red-500 font-bold')
                return

            cust_options = {c['id']: c['name'] for c in customers}
            invoices_container = ui.column().classes('w-full gap-4 mt-4')

            # متغير لتخزين العميل المختار حالياً عشان نعيد تحميل الفواتير بعد الحذف
            selected_customer_id = {'id': None}

            def load_customer_invoices(cust_id):
                invoices_container.clear()
                if not cust_id:
                    return

                try:
                    conn = crud.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT * FROM invoices 
                        WHERE customer_id = ? 
                        ORDER BY id DESC
                    ''', (cust_id,))
                    invoices = [dict(row) for row in cursor.fetchall()]
                    conn.close()

                    if not invoices:
                        with invoices_container:
                            ui.label('لا توجد فواتير مسجلة لهذا العميل حتى الآن.').classes('text-gray-500 italic')
                        return

                    with invoices_container:
                        ui.label(f'📋 عدد الفواتير المسجلة: {len(invoices)}').classes('font-bold text-blue-600')
                        
                        for inv in invoices:
                            inv_id = inv.get('id', 0)
                            inv_total = inv.get('total_amount', 0.0)
                            inv_payment = inv.get('payment_type', 'كاش')
                            inv_cust_id = inv.get('customer_id')

                            with ui.card().classes('w-full p-4 bg-gray-50 border border-gray-200 shadow-xs rounded-lg gap-2'):
                                with ui.row().classes('w-full justify-between items-center'):
                                    ui.label(f"فاتورة رقم #{inv_id}").classes('font-bold text-gray-800 text-lg')
                                    ui.label(f"التاريخ والوقت: {inv.get('created_at', 'غير متوفر')}").classes('text-sm text-gray-500')
                                
                                with ui.row().classes('w-full justify-between items-center'):
                                    ui.label(f"إجمالي الفاتورة: {inv_total:,.2f} ج.م").classes('font-bold text-green-700')
                                    ui.label(f"طريقة الدفع: {inv_payment}").classes('text-sm font-semibold text-blue-600')

                                # جلب تفاصيل أصناف الفاتورة
                                try:
                                    conn_items = crud.get_connection()
                                    cursor_items = conn_items.cursor()
                                    cursor_items.execute('''
                                        SELECT invoice_items.*, products.name as product_name 
                                        FROM invoice_items 
                                        LEFT JOIN products ON invoice_items.product_id = products.id 
                                        WHERE invoice_items.invoice_id = ?
                                    ''', (inv_id,))
                                    items = [dict(row) for row in cursor_items.fetchall()]
                                    conn_items.close()

                                    if items:
                                        ui.separator().classes('my-1')
                                        ui.label('الأصناف في الفاتورة:').classes('text-xs font-bold text-gray-600')
                                        for item in items:
                                            p_name = item.get('product_name') or 'صنف محذوف'
                                            qty = item.get('quantity', 0)
                                            u_price = item.get('unit_price', 0.0)
                                            ui.label(f"- {p_name} | الكمية: {qty} | السعر: {u_price} ج.م | الإجمالي: {qty * u_price:,.2f} ج.م").classes('text-xs text-gray-700 mr-4')
                                except Exception as item_err:
                                    print(f"Error loading invoice items: {item_err}")

                                # زر حذف الفاتورة
                                def delete_invoice(i_id=inv_id, total=inv_total, c_id=inv_cust_id, p_type=inv_payment):
                                    try:
                                        conn_del = crud.get_connection()
                                        cursor_del = conn_del.cursor()
                                        
                                        # 1. استرجاع الكميات للمخزن الخاصة بهذه الفاتورة
                                        cursor_del.execute("SELECT product_id, quantity FROM invoice_items WHERE invoice_id = ?", (i_id,))
                                        inv_items_to_restore = cursor_del.fetchall()
                                        for itm in inv_items_to_restore:
                                            cursor_del.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (itm['quantity'], itm['product_id']))
                                        
                                        # 2. إذا كانت الفاتورة آجل، يتم خصم قيمتها من دين العميل
                                        if p_type == 'آجل (دين)' or p_type == 'آجل':
                                            cursor_del.execute("UPDATE customers SET balance = balance - ? WHERE id = ?", (total, c_id))
                                        
                                        # 3. حذف عناصر الفاتورة ثم الفاتورة نفسها
                                        cursor_del.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (i_id,))
                                        cursor_del.execute("DELETE FROM invoices WHERE id = ?", (i_id,))
                                        
                                        conn_del.commit()
                                        conn_del.close()
                                        
                                        ui.notify(f'تم حذف الفاتورة #{i_id} بنجاح وتم تعديل المخزن والحسابات 🗑️', color='positive')
                                        # إعادة تحميل فواتير نفس العميل
                                        load_customer_invoices(selected_customer_id['id'])
                                    except Exception as del_err:
                                        ui.notify(f'خطأ أثناء الحذف: {str(del_err)}', color='negative')

                                with ui.row().classes('w-full justify-end mt-2'):
                                    ui.button('حذف الفاتورة 🗑️', on_click=delete_invoice, icon='delete').classes('bg-red-600 text-white text-xs py-1')

                except Exception as db_err:
                    with invoices_container:
                        ui.label(f'حدث خطأ أثناء جلب الفواتير: {str(db_err)}').classes('text-red-500 font-bold')

            def on_select_change(e):
                selected_customer_id['id'] = e.value
                load_customer_invoices(e.value)

            cust_filter_select = ui.select(cust_options, label='اختر العميل لعرض فواتيره المؤرخة', on_change=on_select_change).classes('w-full')