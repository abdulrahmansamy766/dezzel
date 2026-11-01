from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar

  # هينزل الشاشة والقائمة المنسدلة تلقائياً في قمة الصفحة
    


def render_pos_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    cart_items = []

    with ui.row().classes('w-full p-6 gap-6 items-start'):
        
        # القسم الأيمن: الأصناف المتاحة
        with ui.column().classes('flex-1 gap-4'):
            ui.label('📦 اختر الصنف والعميل المخصص له').classes('text-xl font-bold text-gray-800')
            
            customers = crud.get_all_customers()
            cust_options = {c['id']: c['name'] for c in customers} if customers else {}
            products = crud.get_all_products()
            
            if not products:
                ui.label('لا توجد أصناف مسجلة في المخزن.').classes('text-red-500 font-bold')
            else:
                for prod in products:
                    with ui.card().classes('w-full p-4 bg-white shadow-sm rounded-lg flex flex-col gap-3'):
                        with ui.row().classes('justify-between items-center w-full'):
                            with ui.column().classes('gap-1'):
                                ui.label(prod['name']).classes('text-lg font-bold text-gray-900')
                                ui.label(f"الباركود: {prod['barcode']} | المتاح بالمخزن: {prod['quantity']} {prod['unit']}").classes('text-xs text-gray-500')
                                ui.label(f"السعر الافتراضي العام: {prod['sell_price']} ج.م").classes('text-sm font-bold text-blue-600')

                        if customers:
                            row_cust_select = ui.select(cust_options, label='اختر العميل لهذا الصنف').classes('w-full')
                            row_cust_select.value = customers[0]['id']
                        else:
                            row_cust_select = None
                            ui.label('⚠️ تنبيه: لا يوجد عملاء مسجلين، سيتم البيع بالسعر الافتراضي.').classes('text-xs text-red-500')

                        with ui.row().classes('gap-4 items-center justify-between w-full'):
                            qty_input = ui.number('الكمية', value=1, min=1, max=prod['quantity']).classes('w-32')

                            # ربط الحدث مباشرة بطريقة آمنة
                            def add_item_to_cart(p=prod, q_inp=qty_input, c_sel=row_cust_select):
                                qty = int(q_inp.value or 1)
                                if qty > p['quantity']:
                                    ui.notify('الكمية المطلوبة أكبر من المتاح بالمخزن!', color='negative')
                                    return
                                
                                cust_id = c_sel.value if c_sel else None
                                unit_price = crud.get_product_price_for_customer(p['id'], cust_id)
                                cust_name = cust_options.get(cust_id, 'عميل نقدي/افتراضي')

                                # إضافة عنصر جديد للقائمة
                                cart_items.append({
                                    'id': len(cart_items) + 1,
                                    'product_id': p['id'],
                                    'name': f"{p['name']} ({cust_name})",
                                    'customer_id': cust_id,
                                    'quantity': qty,
                                    'unit_price': unit_price,
                                    'total': qty * unit_price
                                })
                                
                                # تحديث الجدول بالطريقة المباشرة
                                cart_table.rows = list(cart_items)
                                cart_table.update()
                                update_totals()
                                ui.notify(f'تم إضافة {p["name"]} للفاتورة بنجاح 🛒', color='positive')

                            ui.button('إضافة للفاتورة 🛒', on_click=add_item_to_cart, icon='add_shopping_cart').classes('bg-blue-600 text-white')

        # القسم الأيسر: سلة الفاتورة الإجمالية والدفع
        with ui.column().classes('w-full lg:w-[450px] gap-4'):
            with ui.card().classes('w-full p-6 bg-white shadow-sm rounded-lg gap-4 sticky top-4'):
                ui.label('🧾 سلة الفاتورة الشاملة').classes('text-xl font-bold text-gray-800')
                
                customer_debt_display = ui.label('دين العميل الحالي: 0.00 ج.م').classes('text-sm font-semibold text-gray-600')

                # استخدام row_key='id' فريد لكل صف لمنع حدوث تداخل
                cart_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'الصنف والعميل', 'field': 'name', 'align': 'right'},
                        {'name': 'quantity', 'label': 'كمية', 'field': 'quantity', 'align': 'center'},
                        {'name': 'unit_price', 'label': 'السعر', 'field': 'unit_price', 'align': 'center'},
                        {'name': 'total', 'label': 'الإجمالي', 'field': 'total', 'align': 'center'},
                    ],
                    rows=[], row_key='id'
                ).classes('w-full')

                total_amount_label = ui.label('الإجمالي العام: 0.00 ج.م').classes('text-2xl font-bold text-green-700 mt-2')
                
                paid_amount_input = ui.number('المبلغ المدفوع نقداً', value=0.0, format='%.2f').classes('w-full')
                payment_type_select = ui.select(['كاش', 'آجل'], value='كاش', label='طريقة الدفع العامة').classes('w-full')

                def update_totals():
                    tot = sum(i['total'] for i in cart_items)
                    total_amount_label.text = f"الإجمالي العام: {tot:,.2f} ج.م"
                    paid_amount_input.value = tot

                    if cart_items:
                        main_cust_id = cart_items[-1].get('customer_id')
                        if main_cust_id and customers:
                            selected_cust = next((c for c in customers if c['id'] == main_cust_id), None)
                            if selected_cust:
                                debt = selected_cust.get('balance', 0.0)
                                customer_debt_display.text = f"إجمالي ديون العميل الحالية: {debt:,.2f} ج.م"
                                customer_debt_display.classes(remove='text-gray-600', add='text-red-600 font-bold')
                    else:
                        customer_debt_display.text = "دين العميل الحالي: 0.00 ج.م"
                        customer_debt_display.classes(remove='text-red-600 font-bold', add='text-gray-600')

                def checkout():
                    if not cart_items:
                        ui.notify('السلة فارغة!', color='negative')
                        return
                    
                    main_cust_id = cart_items[0].get('customer_id')
                    if not main_cust_id:
                        ui.notify('من فضلك تأكد من اختيار العميل لكل صنف في الفاتورة!', color='negative')
                        return
                    
                    tot = sum(i['total'] for i in cart_items)
                    paid_amt = float(paid_amount_input.value or 0.0)
                    remaining_debt = tot - paid_amt
                    
                    conn = crud.get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO invoices (customer_id, total_amount, payment_type)
                            VALUES (?, ?, ?)
                        ''', (main_cust_id, tot, payment_type_select.value))
                        invoice_id = cursor.lastrowid
                        
                        for item in cart_items:
                            cursor.execute('''
                                INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price)
                                VALUES (?, ?, ?, ?)
                            ''', (invoice_id, item['product_id'], item['quantity'], item['unit_price']))
                            
                            cursor.execute('''
                                UPDATE products SET quantity = quantity - ? WHERE id = ?
                            ''', (item['quantity'], item['product_id']))
                        
                        if paid_amt > 0:
                            cursor.execute('''
                                INSERT INTO treasury (type, amount, description)
                                VALUES ('وارد', ?, ?)
                            ''', (paid_amt, f"تحصيل من فاتورة مبيعات رقم #{invoice_id}"))
                        
                        if remaining_debt > 0:
                            cursor.execute('''
                                UPDATE customers SET balance = balance + ? WHERE id = ?
                            ''', (remaining_debt, main_cust_id))
                            msg_extra = f" | وتم تسجيل مبلغ {remaining_debt:,.2f} ج.م في ديون العميل."
                        else:
                            msg_extra = ""

                        conn.commit()
                        conn.close()
                        
                        ui.notify(f"تم حفظ الفاتورة بنجاح{msg_extra}", color='positive')
                        ui.navigate.reload()
                        
                    except Exception as e:
                        conn.close()
                        ui.notify(f'خطأ في إتمام العملية: {str(e)}', color='negative')

                ui.button('إتمام الدفع وتسجيل الحسابات 💾', on_click=checkout, icon='check_circle').classes('bg-green-600 text-white w-full py-3 text-lg')