import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

# =========================================================
# قراءة الإعدادات من ملف config.json
# =========================================================
def load_settings():
    config_path = "config.json"
    settings = {
        "company_name": "Mahmoud Ali Trading & Warehouses Management",
        "logo_path": "",
        "rights": "All Rights Reserved © Mahmoud Ali ~ 01000551634"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings.update({k: v for k, v in data.items() if v})
        except Exception:
            pass
    return settings

COLOR_MAIN = colors.HexColor("#0A3D91")
REPORTS_DIR = "reports"

# =========================================================
# إنشاء تقرير عام
# =========================================================
def generate_pdf(title, table_data, columns, filename_prefix="report"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = os.path.join(REPORTS_DIR, f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # تحميل الإعدادات
    cfg = load_settings()
    logo = cfg.get("logo_path", "")
    company = cfg.get("company_name", "")
    rights = cfg.get("rights", "")

    # رأس الصفحة (اللوجو + الشركة)
    if logo and os.path.exists(logo):
        try:
            c.drawImage(logo, 40, height - 90, width=80, height=50, preserveAspectRatio=True)
        except Exception:
            pass
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_MAIN)
        c.drawString(140, height - 60, company)
    else:
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(COLOR_MAIN)
        c.drawString(40, height - 60, company)

    # العنوان
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawString(40, height - 100, title)

    # التاريخ
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 115, f"تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # رسم الجدول
    y = height - 140
    x = 40
    row_height = 20
    col_widths = [90] * len(columns)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COLOR_MAIN)
    c.rect(x - 3, y, sum(col_widths), row_height, fill=1)
    c.setFillColor(colors.white)
    for i, col in enumerate(columns):
        c.drawString(x + i * col_widths[i] + 3, y + 5, str(col))
    y -= row_height

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    for row in table_data:
        for i, value in enumerate(row):
            c.drawString(x + i * col_widths[i] + 3, y + 5, str(value))
        y -= row_height
        if y < 100:
            c.showPage()
            y = height - 100

    # حقوق الطباعة
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.gray)
    c.drawString(150, 40, rights)

    c.save()
    return filename

# =========================================================
# تقارير جاهزة
# =========================================================
def generate_stock_report(items):
    columns = ["الاسم", "الكود", "الكمية", "الحد الأدنى", "المخزن"]
    data = [[i["name"], i["sku"], i["quantity"], i["min_quantity"], i["warehouse"]] for i in items]
    return generate_pdf("تقرير جرد المخزون", data, columns, "stock_report")

def generate_low_stock_report(items):
    columns = ["الاسم", "الكود", "الكمية الحالية", "الحد الأدنى"]
    data = [[i["name"], i["sku"], i["quantity"], i["min_quantity"]] for i in items]
    return generate_pdf("تقرير الأصناف الأقل من الحد الأدنى", data, columns, "low_stock")

def generate_transaction_report(transactions):
    columns = ["النوع", "الصنف", "الكمية", "من مخزن", "إلى مخزن", "المستخدم", "التاريخ"]
    data = [
        [t["type"], t["item"], t["quantity"], t["from_wh"], t["to_wh"], t["user"], t["date"]]
        for t in transactions
    ]
    return generate_pdf("تقرير حركة الأذونات", data, columns, "transactions")
