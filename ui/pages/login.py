from nicegui import ui, app

def render_login_page():
    ui.query('body').style('direction: rtl; font-family: Cairo, sans-serif; background-color: #f4f6f9;')
    
    with ui.column().classes('w-full h-screen justify-center items-center p-4'):
        with ui.card().classes('w-full max-w-md p-8 bg-white shadow-md rounded-lg gap-4 items-center'):
            ui.label('🔐 تسجيل الدخول للنظام').classes('text-2xl font-bold text-gray-800 mb-2')
            
            username_input = ui.input('اسم المستخدم').classes('w-full')
            password_input = ui.input('كلمة المرور', password=True, password_toggle_button=True).classes('w-full')

            def handle_login():
                u = username_input.value.strip() if username_input.value else ""
                p = password_input.value.strip() if password_input.value else ""
                
                # تفريغ الجلسة القديمة لضمان عدم حدوث تداخل
                app.storage.user.clear()

                # تحقق المدير
                if u == "admin" and p == "mora75":
                    app.storage.user['authenticated'] = True
                    app.storage.user['role'] = 'admin'
                    ui.notify('مرحباً بك يا مدير النظام', color='positive')
                    ui.navigate.to('/')
                
                # تحقق الكاشير
                elif u == "cashier" and p == "123":
                    app.storage.user['authenticated'] = True
                    app.storage.user['role'] = 'cashier'
                    ui.notify('مرحباً بك، تم تسجيل الدخول لنقطة البيع', color='positive')
                    ui.navigate.to('/')
                else:
                    ui.notify('خطأ في اسم المستخدم أو كلمة المرور!', color='negative')

            ui.button('دخول', on_click=handle_login).classes('bg-blue-600 text-white w-full py-3 text-lg mt-4')
            
