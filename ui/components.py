from nicegui import ui, app

def render_header(title_text):
    role = app.storage.user.get('role', 'cashier')
    
    # استخدام sticky top-0 z-50 لتثبيت الهيدر فوق الشاشة دائماً ودون أي اهتزاز عند التنقل
    with ui.row().classes('w-full bg-gray-900 text-white p-4 justify-between items-center shadow-md sticky top-0 z-50').style('direction: rtl;'):
        ui.label(title_text).classes('text-xl font-bold')
        
        with ui.row().classes('gap-4 items-center'):
            # نقطة البيع متاحة للجميع
            ui.link('نقطة البيع (POS) 🛒', '/').classes('text-white underline text-sm font-bold')
            
            # باقي أقسام السيستم تظهر للمدير فقط
            if role == 'admin':
                ui.link('المخزن 📦', '/inventory').classes('text-white underline text-sm font-bold')
                ui.link('العملاء والديون 👥', '/customers').classes('text-white underline text-sm font-bold')
                ui.link('لوحة التحكم 📊', '/dashboard').classes('text-white underline text-sm font-bold')
                ui.link('المرتجعات 🔄', '/returns').classes('text-white underline text-sm font-bold')
                ui.link('النواقص ⚠️', '/low-stock').classes('text-white underline text-sm font-bold')
                ui.link('الخزينة 💰', '/treasury').classes('text-white underline text-sm font-bold')
                ui.link('فواتير العملاء المؤرخة', '/customer_invoices').classes('text-white underline text-sm font-bold')

            def logout():
                app.storage.user.clear()
                ui.navigate.to('/login')

            ui.button('خروج 🚪', on_click=logout, color='red').props('flat dense text-color=white')