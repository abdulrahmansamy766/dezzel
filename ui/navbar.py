from nicegui import ui, app

def render_navbar():
    # 1. القائمة الجانبية (Drawer) للموبايل (تفتح بزر القائمة وتختفي دايماً على الشاشات الكبيرة)
    drawer = ui.left_drawer(value=False).props('overlay elevated behavior=mobile').classes('bg-gray-900 text-white p-4')
    with drawer:
        ui.label('نظام إدارة المخازن').classes('text-xl font-bold mb-4 text-blue-400')
        ui.separator().classes('mb-4 border-gray-700')
        
        ui.link('نقطة البيع (POS)', '/').classes('text-white text-lg py-2 block hover:text-blue-400')
        if app.storage.user.get('role') == 'admin':
            ui.link('لوحة المؤشرات', '/dashboard').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('المخزن', '/inventory').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('العملاء', '/customers').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('المردودات', '/returns').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('النواقص', '/low-stock').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('الخزينة', '/treasury').classes('text-white text-lg py-2 block hover:text-blue-400')
            ui.link('فواتير العملاء', '/customer_invoices').classes('text-white text-lg py-2 block hover:text-blue-400')
        
        ui.separator().classes('my-4 border-gray-700')
        ui.link('تسجيل الخروج', '/login').classes('text-red-400 text-lg py-2 block hover:text-red-300')

    # 2. الشريط العلوي الرئيسي (Header)
    with ui.header().classes('bg-gray-900 text-white flex flex-col px-4 py-2 z-50'):
        
        # الصف الأول: اسم النظام + زر القائمة (يظهر على الموبايل lt-md فقط)
        with ui.row().classes('w-full justify-between items-center'):
            with ui.row().classes('items-center gap-2'):
                # زر القائمة يظهر فقط عند تصغير الشاشة (الموبايل)
                ui.button(icon='menu', on_click=drawer.toggle).props('flat color=white dense').classes('lt-md')
                ui.label('نظام OMAR للجملة').classes('text-lg font-bold')
            
            # زر تسجيل الخروج السريع لو حابب تخليه فوق عالي الشاشة
            ui.link('تسجيل الخروج', '/login').classes('text-red-400 text-sm lt-md')

        # الصف الثاني: الروابط الكاملة (تظهر فقط على الشاشات الكبيرة gt-sm وتختفي تماماً على الموبايل)
        with ui.row().classes('w-full items-center gap-4 py-1 gt-sm border-t border-gray-800'):
            ui.link('🛒 نقطة البيع (POS)', '/').classes('text-white hover:text-blue-400 text-sm')
            if app.storage.user.get('role') == 'admin':
                ui.link('📦 المخزن', '/inventory').classes('text-white hover:text-blue-400 text-sm')
                ui.link('👥 العملاء والديون', '/customers').classes('text-white hover:text-blue-400 text-sm')
                ui.link('📊 لوحة التحكم', '/dashboard').classes('text-white hover:text-blue-400 text-sm')
                ui.link('🔄 المرتجعات', '/returns').classes('text-white hover:text-blue-400 text-sm')
                ui.link('⚠️ النواقص', '/low-stock').classes('text-white hover:text-blue-400 text-sm')
                ui.link('💰 الخزينة', '/treasury').classes('text-white hover:text-blue-400 text-sm')
                ui.link('📜 فواتير العملاء المؤرخة', '/customer_invoices').classes('text-white hover:text-blue-400 text-sm')
            ui.link('🚪 خروج', '/login').classes('text-red-400 hover:text-red-300 text-sm ml-auto')