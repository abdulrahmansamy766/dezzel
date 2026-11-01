from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar


def render_returns_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    return_items_list = []

    with ui.column().classes('w-full p-6 gap-6'):
        with ui.card().classes('w-full p-6 bg-white shadow-sm rounded-lg gap-4'):
            ui.label('تسجيل مرتجع مبيعات من عميل').classes('text-xl font-bold text-gray-800')
            
            customers = crud.get_all_customers()
            cust_options = {c['id']: f"{c['name']} (رصيد: {c['balance']} ج.م)" for c in customers} if customers else {0: "عميل نقدي"}
            
            customer_select = ui.select(cust_options, label='اختر العميل').classes('w-full')
            if customers:
                customer_select.value = customers[0]['id']

            reason_input = ui.input('سبب المرتجع (مثلاً: بضاعة تالفة، زيادة عن الحاجة)').classes('w-full')

            # اختيار المنتج المرتجع
            ui.label('اختر المنتج المراد إرجاعه:').classes('font-bold mt-2')
            products = crud.get_all_products()
            
            if not products:
                ui.label('لا توجد منتجات مسجلة.').classes('text-red-500')
            else:
                # دعم جلب سعر المنتج (سواء الافتراضي أو المخصص للعميل)
                prod_options = {p['id']: f"{p['name']} - (السعر الأساسي: {p['sell_price']} ج.م)" for p in products}
                prod_select = ui.select(prod_options, label='المنتج').classes('flex-1 min-w-[250px]')
                qty_input = ui.number('الكمية المرتجعة', value=1).classes('w-28')

                # جدول سلة المرتجعات المؤقتة
                return_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'اسم المنتج', 'field': 'name', 'align': 'right'},
                        {'name': 'quantity', 'label': 'الكمية', 'field': 'quantity', 'align': 'center'},
                        {'name': 'unit_price', 'label': 'السعر', 'field': 'unit_price', 'align': 'center'},
                        {'name': 'total', 'label': 'الإجمالي', 'field': 'total', 'align': 'center'},
                    ],
                    rows=[], row_key='product_id'
                ).classes('w-full')

                total_label = ui.label('إجمالي قيمة المرتجع: 0.00 ج.م').classes('text-xl font-bold text-red-700 mt-2')

                def add_to_return_cart():
                    selected_prod_id = prod_select.value
                    if not selected_prod_id:
                        return
                    
                    prod = next((p for p in products if p['id'] == selected_prod_id), None)
                    if not prod:
                        return
                    
                    qty = int(qty_input.value or 1)
                    
                    # جلب السعر المناسب للعميل (المخصص أو الافتراضي)
                    cust_id = customer_select.value if customer_select.value != 0 else None
                    unit_price = crud.get_product_price_for_customer(prod['id'], cust_id)
                    
                    existing = next((item for item in return_items_list if item['product_id'] == prod['id']), None)
                    if existing:
                        existing['quantity'] += qty
                        existing['total'] = existing['quantity'] * existing['unit_price']
                    else:
                        return_items_list.append({
                            'product_id': prod['id'],
                            'name': prod['name'],
                            'quantity': qty,
                            'unit_price': unit_price,
                            'total': qty * unit_price
                        })
                    
                    return_table.rows = list(return_items_list)
                    return_table.update()
                    
                    tot = sum(i['total'] for i in return_items_list)
                    total_label.text = f"إجمالي قيمة المرتجع: {tot:,.2f} ج.م"

                ui.button('إضافة لقائمة المرتجعات', on_click=add_to_return_cart, icon='add').classes('bg-amber-600 text-white')

                def submit_return():
                    if not return_items_list:
                        ui.notify('قائمة المرتجعات فارغة!', color='negative')
                        return
                    
                    cust_id = customer_select.value if customer_select.value != 0 else None
                    tot = sum(i['total'] for i in return_items_list)
                    
                    success, msg = crud.create_sales_return(cust_id, return_items_list, tot, reason_input.value or "مرتجع مبيعات")
                    if success:
                        ui.notify(msg, color='positive')
                        ui.navigate.reload()
                    else:
                        ui.notify(f'خطأ: {msg}', color='negative')

                ui.button('تأكيد وحفظ المرتجع 🔄', on_click=submit_return, icon='check_circle').classes('bg-red-600 text-white w-full py-3 mt-4 text-lg')