FROM python:3.10-slim

WORKDIR /app

# تثبيت متطلبات النظام لو لزم الأمر
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# نسخ ملفات المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# منفذ التشغيل الافتراضي
EXPOSE 8080

# أمر تشغيل السيرفر المباشر
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]