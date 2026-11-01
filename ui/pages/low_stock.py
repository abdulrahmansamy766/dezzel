from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar


def render_low_stock_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    with ui.column().classes('w-full p-6 gap-6'):
        ui.label('⚠️ الأصناف التي وصلت إلى حد الأمان أو قربت على النفاد').classes('text-xl font-bold text-red-700')
        
        columns = [
            {'name': 'barcode', 'label': 'الباركود', 'field': 'barcode', 'align': 'right'},
            {'name': 'name', 'label': 'اسم المنتج', 'field': 'name', 'align': 'right'},
            {'name': 'unit', 'label': 'الوحدة', 'field': 'unit', 'align': 'center'},
            {'name': 'quantity', 'label': 'الكمية الحالية', 'field': 'quantity', 'align': 'center'},
            {'name': 'min_limit', 'label': 'حد الأمان', 'field': 'min_limit', 'align': 'center'},
        ]
        
        low_products = crud.get_low_stock_products()
        if not low_products:
            with ui.card().classes('w-full p-6 bg-green-50 border-r-4 border-green-600'):
                ui.label('ممتاز! لا توجد أي نواقص أو منتجات متدنية الكمية حالياً.').classes('text-green-700 font-bold')
        else:
            ui.table(columns=columns, rows=low_products, row_key='id').classes('w-full bg-white shadow-sm rounded-lg')