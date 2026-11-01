from nicegui import ui, app
from fastapi.responses import FileResponse
from database.models import init_db
from ui.navbar import render_navbar
from ui.pages.pos import render_pos_page
from ui.pages.inventory import render_inventory_page
from ui.pages.dashboard import render_dashboard_page
from ui.pages.returns import render_returns_page
from ui.pages.low_stock import render_low_stock_page
from ui.pages.treasury import render_treasury_page
from ui.pages.customers import render_customers_page
from ui.pages.login import render_login_page
from ui.pages.customer_invoices import render_customer_invoices_page
import os
import uvicorn

# ربط مجلد الملفات الثابتة لكي يتمكن محرك الـ PWA وقارئ المانفست من الوصول للأيقونة والـ manifest
app.add_static_files('/static', 'static')

# جعل ملفات PWA متاحة من جذر النطاق حتى يعمل نطاق الـ Service Worker على كل الصفحات.
@app.get('/sw.js', include_in_schema=False)
def service_worker():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), 'static', 'sw.js'),
        media_type='application/javascript',
        headers={'Service-Worker-Allowed': '/'},
    )

# رأس الصفحة وإعدادات الـ PWA
ui.add_head_html('''
    <link rel="manifest" href="/static/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <link rel="apple-touch-icon" href="/static/appstore-images/ios/180.png">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js', {scope: '/'})
                    .catch((error) => console.error('Service worker registration failed:', error));
            });
        }
    </script>
''', shared=True)

# دالة تغليف عامة تعمل كـ Decorator لإدراج النافبار تلقائياً في قمة أي صفحة
# دالة تغليف عامة تعمل كـ Decorator وتقبل الـ arguments والـ kwargs لتجنب خطأ FastAPI
# دالة تغليف عامة تعمل كـ Decorator لإدراج النافبار تلقائياً
def global_layout(page_func):
    def wrapper():
        render_navbar()
        return page_func()
    return wrapper

# مسار تسجيل الدخول (بدون نافبار)
@ui.page('/login')
def login_page():
    render_login_page()

# الصفحة الرئيسية (نقطة البيع) - محمية ومزودة بالنافبار
@ui.page('/')
@global_layout
def index_page():
    if not app.storage.user.get('authenticated'):
        return ui.navigate.to('/login')
    render_pos_page()

# مسارات لوحة التحكم والمخزن والعملاء (Admin Only) مزودة بالنافبار تلقائياً
@ui.page('/dashboard')
@global_layout
def dashboard_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_dashboard_page()

@ui.page('/inventory')
@global_layout
def inventory_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_inventory_page()

@ui.page('/customers')
@global_layout
def customers_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_customers_page()

@ui.page('/returns')
@global_layout
def returns_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_returns_page()

@ui.page('/low-stock')
@global_layout
def low_stock_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_low_stock_page()

@ui.page('/treasury')
@global_layout
def treasury_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_treasury_page()

@ui.page('/customer_invoices')
@global_layout
def customer_invoices_page():
    if app.storage.user.get('role') != 'admin':
        ui.notify('غير مسموح لك بالدخول لهذه الصفحة!', color='negative')
        return ui.navigate.to('/')
    render_customer_invoices_page()

ui.run(title="نظام إدارة مخازن الجملة", storage_secret='my_secret_key', reload=False)
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port
    )
