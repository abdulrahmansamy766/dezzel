from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar
from ui.navbar import render_navbar



def render_dashboard_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    analytics = crud.get_dashboard_analytics()

    with ui.column().classes('w-full p-6 gap-6'):
        with ui.row().classes('w-full gap-4 flex-wrap'):
            
            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-white shadow-sm rounded-lg'):
                ui.label('إجمالي المبيعات').classes('text-gray-500 text-sm')
                ui.label(f"{analytics.get('total_sales', 0):,.2f} ج.م").classes('text-2xl font-bold text-blue-600')

            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-white shadow-sm rounded-lg'):
                ui.label('إجمالي المرتجعات').classes('text-gray-500 text-sm')
                ui.label(f"{analytics.get('total_returns', 0):,.2f} ج.م").classes('text-2xl font-bold text-red-600')

            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-white shadow-sm rounded-lg'):
                ui.label('صافي المبيعات').classes('text-gray-500 text-sm')
                ui.label(f"{analytics.get('net_sales', 0):,.2f} ج.م").classes('text-2xl font-bold text-green-600')

            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-white shadow-sm rounded-lg'):
                ui.label('رصيد الخزينة الحالي').classes('text-gray-500 text-sm')
                ui.label(f"{analytics.get('treasury_balance', 0):,.2f} ج.م").classes('text-2xl font-bold text-amber-600')

            with ui.card().classes('flex-1 min-w-[200px] p-4 bg-white shadow-sm rounded-lg'):
                ui.label('إجمالي ديون العملاء').classes('text-gray-500 text-sm')
                ui.label(f"{analytics.get('total_debts', 0):,.2f} ج.م").classes('text-2xl font-bold text-purple-600')