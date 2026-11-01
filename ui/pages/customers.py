from nicegui import ui
from ui.components import render_header
import backend.crud as crud


def render_customers_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    temp_cust_prices = []

    with ui.column().classes('w-full p-6 gap-6'):
        
        # --- قسم إضافة عميل جديد ---
        with ui.expansion('➕ إضافة عميل جديد (مع الديون وأسعار البيع الخاصة)', icon='person_add').classes('w-full bg-white shadow-sm rounded-lg'):
            with ui.column().classes('w-full p-4 gap-4'):
                
                with ui.row().classes('w-full gap-4 items-end flex-wrap'):
                    name_input = ui.input('اسم العميل / الشركة').classes('flex-2 min-w-[200px]')
                    phone_input = ui.input('رقم الهاتف').classes('flex-1 min-w-[150px]')
                    balance_input = ui.number('الديون السابقة (رصيد افتتاحي)', value=0.0, format='%.2f').classes('w-44')

                ui.separator().classes('my-2')
                ui.label('تخصيص أسعار أصناف لهذا العميل (اختياري قبل الحفظ):').classes('font-bold text-gray-700 text-sm')

                products = crud.get_all_products()
                if products:
                    prod_options = {p['id']: f"{p['name']} (الافتراضي: {p['sell_price']} ج.م)" for p in products}
                    with ui.row().classes('w-full gap-4 items-center flex-wrap'):
                        p_select = ui.select(prod_options, label='اختر الصنف').classes('flex-1 min-w-[220px]')
                        p_price_inp = ui.number('سعر البيع المخصص لهذا العميل', format='%.2f').classes('w-44')

                        prices_table = ui.table(
                            columns=[
                                {'name': 'product_name', 'label': 'اسم الصنف', 'field': 'product_name', 'align': 'right'},
                                {'name': 'price', 'label': 'السعر المخصص', 'field': 'price', 'align': 'center'},
                            ],
                            rows=[], row_key='product_id'
                        ).classes('w-full my-2')

                        def add_price_to_temp():
                            if not p_select.value or p_price_inp.value is None:
                                ui.notify('اختر الصنف وادخل السعر!', color='negative')
                                return
                            
                            p_id = p_select.value
                            p_name = products[[p['id'] for p in products].index(p_id)]['name']
                            val = float(p_price_inp.value)

                            existing = next((i for i in temp_cust_prices if i['product_id'] == p_id), None)
                            if existing:
                                existing['price'] = val
                            else:
                                temp_cust_prices.append({'product_id': p_id, 'product_name': p_name, 'price': val})

                            prices_table.rows = list(temp_cust_prices)
                            prices_table.update()
                            p_price_inp.value = None
                            ui.notify(f'تم إضافة السعر للصنف {p_name}', color='positive')

                        ui.button('إضافة السعر للقائمة', on_click=add_price_to_temp, icon='add').classes('bg-amber-600 text-white')

                def save_customer():
                    if not name_input.value:
                        ui.notify('من فضلك ادخل اسم العميل على الأقل!', color='negative')
                        return
                    
                    conn = crud.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO customers (name, phone, balance) VALUES (?, ?, ?)", 
                                   (name_input.value, phone_input.value or "", float(balance_input.value or 0.0)))
                    cust_id = cursor.lastrowid

                    for item in temp_cust_prices:
                        cursor.execute('''
                            INSERT INTO customer_prices (customer_id, product_id, price)
                            VALUES (?, ?, ?)
                            ON CONFLICT(customer_id, product_id) DO UPDATE SET price = ?
                        ''', (cust_id, item['product_id'], item['price'], item['price']))

                    conn.commit()
                    conn.close()

                    ui.notify('تم حفظ العميل وأسعاره بنجاح', color='positive')
                    ui.navigate.reload()

                ui.button('حفظ العميل بالكامل 💾', on_click=save_customer, icon='save').classes('bg-blue-600 text-white w-full py-3 mt-4 text-lg')

        # --- نافذة منبثقة (Dialog) لتوريد وتحصيل الدفعات من العميل ---
        pay_cust_id = ui.label().classes('hidden')
        pay_cust_name_label = ui.label('').classes('text-lg font-bold text-blue-700')
        pay_cust_current_balance = ui.label('').classes('text-sm font-semibold text-gray-600')
        
        with ui.dialog() as pay_dialog, ui.card().classes('p-6 gap-4 min-w-[400px] bg-white'):
            ui.label('💵 توريد دفعة نقدية وسداد من الدين').classes('text-xl font-bold text-gray-800')
            
            pay_cust_name_label.classes()
            pay_cust_current_balance.classes()

            payment_amount_input = ui.number('المبلغ المراد توريده/سداده', format='%.2f').classes('w-full')
            payment_note_input = ui.input('ملاحظات / بيان (اختياري)', value='سداد دفعة من الدين').classes('w-full')

            def process_payment():
                try:
                    amt = float(payment_amount_input.value or 0.0)
                    if amt <= 0:
                        ui.notify('من فضلك ادخل مبلغ صحيح أكبر من الصفر!', color='negative')
                        return
                    
                    c_id = int(pay_cust_id.text)
                    
                    conn = crud.get_connection()
                    cursor = conn.cursor()
                    
                    # 1. خصم المبلغ المدفوع من دين العميل
                    cursor.execute("UPDATE customers SET balance = balance - ? WHERE id = ?", (amt, c_id))
                    
                    # جلب اسم العميل لتسجيله في وصف الخزينة
                    cursor.execute("SELECT name FROM customers WHERE id = ?", (c_id,))
                    c_row = cursor.fetchone()
                    c_name = c_row['name'] if c_row else "عميل"

                    # 2. تسجيل المبلغ الوارد في الخزينة تلقائياً
                    cursor.execute('''
                        INSERT INTO treasury (type, amount, description)
                        VALUES ('وارد', ?, ?)
                    ''', (amt, f"توريد/سداد دين من العميل: {c_name} - {payment_note_input.value}"))

                    conn.commit()
                    conn.close()

                    ui.notify(f'تم توريد مبلغ {amt:,.2f} ج.م بنجاح وتحديث حساب العميل والخزينة 💰', color='positive')
                    pay_dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    ui.notify(f'حدث خطأ: {str(e)}', color='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('إلغاء', on_click=pay_dialog.close).props('flat')
                ui.button('تأكيد التوريد 💾', on_click=process_payment).classes('bg-green-600 text-white')

        # --- نافذة منبثقة (Dialog) لتعديل العميل وأسعاره الخاصة ---
        selected_cust_id = ui.label().classes('hidden')
        edit_cust_prices_list = []
        
        with ui.dialog() as edit_cust_dialog, ui.card().classes('p-6 gap-4 min-w-[500px] bg-white'):
            ui.label('✏️ تعديل بيانات العميل والأسعار الخاصة').classes('text-xl font-bold text-gray-800')
            
            e_cust_name = ui.input('اسم العميل').classes('w-full')
            e_cust_phone = ui.input('رقم الهاتف').classes('w-full')
            e_cust_balance = ui.number('إجمالي الديون', format='%.2f').classes('w-full')

            ui.separator().classes('my-2')
            ui.label('أسعار الأصناف المخصصة لهذا العميل:').classes('font-bold text-gray-700 text-sm')

            if products:
                e_prod_select = ui.select(prod_options, label='اختر صنف لتخصيص أو تعديل سعره').classes('w-full')
                e_prod_price_inp = ui.number('السعر الجديد للعميل', format='%.2f').classes('w-full')

                edit_prices_table = ui.table(
                    columns=[
                        {'name': 'product_name', 'label': 'اسم الصنف', 'field': 'product_name', 'align': 'right'},
                        {'name': 'price', 'label': 'السعر المخصص', 'field': 'price', 'align': 'center'},
                    ],
                    rows=[], row_key='product_id'
                ).classes('w-full my-2')

                def add_or_update_edit_price():
                    if not e_prod_select.value or e_prod_price_inp.value is None:
                        ui.notify('اختر الصنف وادخل السعر!', color='negative')
                        return
                    
                    p_id = e_prod_select.value
                    p_name = products[[p['id'] for p in products].index(p_id)]['name']
                    val = float(e_prod_price_inp.value)

                    existing = next((i for i in edit_cust_prices_list if i['product_id'] == p_id), None)
                    if existing:
                        existing['price'] = val
                    else:
                        edit_cust_prices_list.append({'product_id': p_id, 'product_name': p_name, 'price': val})

                    edit_prices_table.rows = list(edit_cust_prices_list)
                    edit_prices_table.update()
                    e_prod_price_inp.value = None
                    ui.notify(f'تم تحديث السعر للصنف {p_name} في القائمة', color='positive')

                ui.button('تحديث/إضافة السعر للقائمة', on_click=add_or_update_edit_price, icon='add').classes('bg-amber-600 text-white w-full')

            def update_customer_action():
                c_id = int(selected_cust_id.text)
                success, msg = crud.update_customer(
                    c_id,
                    e_cust_name.value,
                    e_cust_phone.value,
                    float(e_cust_balance.value or 0.0)
                )
                if success:
                    conn = crud.get_connection()
                    cursor = conn.cursor()
                    for item in edit_cust_prices_list:
                        cursor.execute('''
                            INSERT INTO customer_prices (customer_id, product_id, price)
                            VALUES (?, ?, ?)
                            ON CONFLICT(customer_id, product_id) DO UPDATE SET price = ?
                        ''', (c_id, item['product_id'], item['price'], item['price']))
                    conn.commit()
                    conn.close()

                    ui.notify('تم تعديل بيانات العميل وأسعاره بنجاح 💾', color='positive')
                    edit_cust_dialog.close()
                    ui.navigate.reload()
                else:
                    ui.notify(f'خطأ: {msg}', color='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('إلغاء', on_click=edit_cust_dialog.close).props('flat')
                ui.button('حفظ التعديلات', on_click=update_customer_action).classes('bg-green-600 text-white')

        # --- جدول العملاء مع أزرار التعديل، والحذف، وتوريد الدفعات ---
        ui.label('📋 قائمة العملاء والديون الحالية').classes('text-lg font-bold text-gray-800 mt-4')
        
        columns = [
            {'name': 'name', 'label': 'اسم العميل', 'field': 'name', 'align': 'right'},
            {'name': 'phone', 'label': 'رقم الهاتف', 'field': 'phone', 'align': 'center'},
            {'name': 'balance', 'label': 'إجمالي الديون', 'field': 'balance', 'align': 'center'},
            {'name': 'pay_action', 'label': 'توريد دفعة', 'field': 'balance', 'align': 'center'}, # عمود جديد لزرار التوريد
            {'name': 'actions', 'label': 'إجراءات', 'field': 'id', 'align': 'center'},
        ]
   
        customers = crud.get_all_customers()
        table = ui.table(columns=columns, rows=customers, row_key='id').classes('w-full bg-white shadow-sm rounded-lg')
        
        # فتح نافذة توريد الدفعات
        def open_pay_dialog(e):
            row = e.args
            pay_cust_id.text = str(row['id'])
            pay_cust_name_label.text = f"العميل: {row['name']}"
            pay_cust_current_balance.text = f"إجمالي الدين الحالي: {row['balance']:,.2f} ج.م"
            payment_amount_input.value = None
            pay_dialog.open()

        table.add_slot('body-cell-pay_action', '''
            <q-td :props="props">
                <q-btn icon="payments" color="green" label="توريد فلوس" dense size="sm" @click="$parent.$emit('open_pay', props.row)" />
            </q-td>
        ''')

        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <div class="flex gap-1 justify-center">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit_cust', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('delete_cust', props.row.id)" />
                </div>
            </q-td>
        ''')

        def open_edit_cust_dialog(e):
            row = e.args
            c_id = row['id']
            selected_cust_id.text = str(c_id)
            e_cust_name.value = row['name']
            e_cust_phone.value = row.get('phone', '')
            e_cust_balance.value = row['balance']

            edit_cust_prices_list.clear()
            conn = crud.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cp.product_id, p.name as product_name, cp.price 
                FROM customer_prices cp
                JOIN products p ON cp.product_id = p.id
                WHERE cp.customer_id = ?
            ''', (c_id,))
            rows = cursor.fetchall()
            conn.close()

            for r in rows:
                edit_cust_prices_list.append({'product_id': r['product_id'], 'product_name': r['product_name'], 'price': r['price']})

            if products:
                edit_prices_table.rows = list(edit_cust_prices_list)
                edit_prices_table.update()

            edit_cust_dialog.open()

        def remove_customer(e):
            cust_id = e.args
            success, msg = crud.delete_customer(cust_id)
            if success:
                ui.notify(msg, color='positive')
                ui.navigate.reload()
            else:
                ui.notify(f'خطأ: {msg}', color='negative')

        table.on('open_pay', open_pay_dialog)
        table.on('edit_cust', open_edit_cust_dialog)
        table.on('delete_cust', remove_customer)