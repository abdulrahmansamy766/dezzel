from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar


def render_treasury_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    with ui.column().classes('w-full p-6 gap-6'):
        
        # نموذج إضافة حركة يدوية (مصروفات أو إيداع)
        with ui.expansion('➕ تسجيل حركة مالية يدوية (صادر/وارد)', icon='account_balance_wallet').classes('w-full bg-white shadow-sm rounded-lg'):
            with ui.row().classes('w-full p-4 gap-4 items-end'):
                t_type = ui.select(['وارد', 'صادر'], value='صادر', label='نوع الحركة').classes('w-32')
                t_amount = ui.number('المبلغ', format='%.2f').classes('w-32')
                t_desc = ui.input('البيان / السبب (مثل: إيجار، فاتورة كهرباء)').classes('flex-1')

                def save_trans():
                    if t_amount.value is None or t_amount.value <= 0 or not t_desc.value:
                        ui.notify('من فضلك ادخل المبلغ والسبب بشكل صحيح!', color='negative')
                        return
                    
                    success, msg = crud.add_treasury_transaction(t_type.value, float(t_amount.value), t_desc.value)
                    if success:
                        ui.notify(msg, color='positive')
                        ui.navigate.reload()
                    else:
                        ui.notify(f'خطأ: {msg}', color='negative')

                ui.button('حفظ الحركة', on_click=save_trans).classes('bg-green-600 text-white')

        # جدول عرض الحركات المالية
        ui.label('📋 سجل الحركات المالية للخزينة').classes('text-lg font-bold text-gray-800 mt-4')
        
        columns = [
            {'name': 'created_at', 'label': 'التاريخ والوقت', 'field': 'created_at', 'align': 'center'},
            {'name': 'type', 'label': 'النوع', 'field': 'type', 'align': 'center'},
            {'name': 'amount', 'label': 'المبلغ', 'field': 'amount', 'align': 'center'},
            {'name': 'description', 'label': 'البيان والتفاصيل', 'field': 'description', 'align': 'right'},
        ]
        
        transactions = crud.get_treasury_transactions()
        ui.table(columns=columns, rows=transactions, row_key='id').classes('w-full bg-white shadow-sm rounded-lg')