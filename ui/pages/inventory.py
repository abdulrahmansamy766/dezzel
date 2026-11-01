from nicegui import ui
from ui.components import render_header
import backend.crud as crud
from ui.navbar import render_navbar


def render_inventory_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')

    with ui.column().classes('w-full p-6 gap-6'):
        
        # --- قسم إضافة صنف جديد ---
        with ui.expansion('➕ إضافة صنف جديد للمخزن', icon='add_box').classes('w-full bg-white shadow-sm rounded-lg'):
            with ui.column().classes('w-full p-4 gap-4'):
                with ui.row().classes('w-full gap-4 items-center flex-wrap'):
                    barcode_input = ui.input('الباركود').classes('flex-1 min-w-[130px]')
                    name_input = ui.input('اسم المنتج').classes('flex-2 min-w-[180px]')
                    unit_input = ui.select(['قطعة',  'كرتونة'], value='قطعة', label='الوحدة').classes('w-28')
                    buy_input = ui.number('سعر التكلفة', format='%.2f').classes('w-32')
                    sell_input = ui.number('سعر البيع الافتراضي', format='%.2f').classes('w-36')
                    qty_input = ui.number('الكمية', value=1).classes('w-24')
                    min_limit_input = ui.number('حد الأمان', value=5).classes('w-24')

                def save_product():
                    if not name_input.value or buy_input.value is None or sell_input.value is None:
                        ui.notify('من فضلك ادخل اسم المنتج وسعر التكلفة وسعر البيع!', color='negative')
                        return
                    
                    success, msg = crud.add_product(
                        barcode_input.value or f"BAR-{qty_input.id}",
                        name_input.value,
                        unit_input.value,
                        float(buy_input.value),
                        float(sell_input.value),
                        int(qty_input.value or 0),
                        int(min_limit_input.value or 5)
                    )
                    
                    if success:
                        ui.notify(msg, color='positive')
                        ui.navigate.reload()
                    else:
                        ui.notify(f'خطأ: {msg}', color='negative')

                ui.button('حفظ الصنف 💾', on_click=save_product, icon='save').classes('bg-blue-600 text-white w-full py-3 text-lg')

        # --- تعريف متغيرات التعديل (داخل نافذة منبثقة Dialog) ---
        selected_prod_id = ui.label().classes('hidden')
        
        with ui.dialog() as edit_dialog, ui.card().classes('p-6 gap-4 min-w-[400px] bg-white'):
            ui.label('✏️ تعديل بيانات الصنف').classes('text-xl font-bold text-gray-800')
            
            e_barcode = ui.input('الباركود').classes('w-full')
            e_name = ui.input('اسم المنتج').classes('w-full')
            e_unit = ui.select(['قطعة', 'كرتونة'], label='الوحدة').classes('w-full')
            e_buy = ui.number('سعر التكلفة', format='%.2f').classes('w-full')
            e_sell = ui.number('سعر البيع', format='%.2f').classes('w-full')
            e_qty = ui.number('الكمية').classes('w-full')
            e_min = ui.number('حد الأمان').classes('w-full')

            def update_prod_action():
                success, msg = crud.update_product(
                    int(selected_prod_id.text),
                    e_barcode.value,
                    e_name.value,
                    e_unit.value,
                    float(e_buy.value or 0),
                    float(e_sell.value or 0),
                    int(e_qty.value or 0),
                    int(e_min.value or 0)
                )
                if success:
                    ui.notify(msg, color='positive')
                    edit_dialog.close()
                    ui.navigate.reload()
                else:
                    ui.notify(f'خطأ: {msg}', color='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('إلغاء', on_click=edit_dialog.close).props('flat')
                ui.button('حفظ التعديلات', on_click=update_prod_action).classes('bg-green-600 text-white')

        # --- جدول الأصناف مع أزرار التعديل والحذف ---
        ui.label('📋 الأصناف المسجلة في المخزن').classes('text-lg font-bold text-gray-800 mt-4')
        
        columns = [
            {'name': 'barcode', 'label': 'الباركود', 'field': 'barcode', 'align': 'right'},
            {'name': 'name', 'label': 'اسم المنتج', 'field': 'name', 'align': 'right'},
            {'name': 'unit', 'label': 'الوحدة', 'field': 'unit', 'align': 'center'},
            {'name': 'buy_price', 'label': 'التكلفة', 'field': 'buy_price', 'align': 'center'},
            {'name': 'sell_price', 'label': 'سعر البيع', 'field': 'sell_price', 'align': 'center'},
            {'name': 'quantity', 'label': 'الكمية', 'field': 'quantity', 'align': 'center'},
            {'name': 'min_limit', 'label': 'حد الأمان', 'field': 'min_limit', 'align': 'center'},
            {'name': 'actions', 'label': 'إجراءات', 'field': 'id', 'align': 'center'},
        ]
       
        products = crud.get_all_products()
        table = ui.table(columns=columns, rows=products, row_key='id').classes('w-full bg-white shadow-sm rounded-lg')

        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <div class="flex gap-1 justify-center">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit_prod', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('delete_prod', props.row.id)" />
                </div>
            </q-td>
        ''')

        def open_edit_dialog(e):
            row = e.args
            selected_prod_id.text = str(row['id'])
            e_barcode.value = row['barcode']
            e_name.value = row['name']
            e_unit.value = row['unit']
            e_buy.value = row['buy_price']
            e_sell.value = row['sell_price']
            e_qty.value = row['quantity']
            e_min.value = row['min_limit']
            edit_dialog.open()

        def remove_product(e):
            prod_id = e.args
            success, msg = crud.delete_product(prod_id)
            if success:
                ui.notify(msg, color='positive')
                ui.navigate.reload()
            else:
                ui.notify(f'خطأ: {msg}', color='negative')

        table.on('edit_prod', open_edit_dialog)
        table.on('delete_prod', remove_product)