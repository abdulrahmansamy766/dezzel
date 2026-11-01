from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar

    
    
def render_customer_prices_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    with ui.column().classes('w-full p-6 gap-6'):
        with ui.card().classes('w-full p-6 bg-white shadow-sm rounded-lg gap-4'):
            ui.label('حدد سعر خاص لصنف معين لعميل معين').classes('text-xl font-bold text-gray-800')
            
            customers = crud.get_all_customers()
            products = crud.get_all_products()
            
            if not customers or not products:
                ui.label('يجب توفر عملاء و منتجات مسجلة أولاً لتخصيص الأسعار.').classes('text-red-500 font-bold')
                return

            cust_options = {c['id']: c['name'] for c in customers}
            prod_options = {p['id']: f"{p['name']} (السعر الافتراضي: {p['sell_price']} ج.م)" for p in products}

            cust_select = ui.select(cust_options, label='اختر العميل').classes('w-full')
            prod_select = ui.select(prod_options, label='اختر المنتج').classes('w-full')
            price_input = ui.number('السعر المخصص لهذا العميل', format='%.2f').classes('w-full')

            def save_custom_price():
                if not cust_select.value or not prod_select.value or price_input.value is None:
                    ui.notify('من فضلك أكمل اختيار العميل والمنتج والسعر!', color='negative')
                    return
                
                success, msg = crud.set_customer_product_price(cust_select.value, prod_select.value, float(price_input.value))
                if success:
                    ui.notify(msg, color='positive')
                    ui.navigate.reload()
                else:
                    ui.notify(f'خطأ: {msg}', color='negative')

            ui.button('حفظ السعر المخصص', on_click=save_custom_price, icon='save').classes('bg-blue-600 text-white w-full py-3')