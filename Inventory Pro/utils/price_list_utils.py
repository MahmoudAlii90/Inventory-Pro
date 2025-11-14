import os
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from utils.settings_manager import SettingsManager
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display


def fix_text(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))


# ============================================================
# PDF EXPORT
# ============================================================
def export_price_list_pdf(items):
    settings = SettingsManager()

    company = settings.get("company_name", "Company Name")
    phone = settings.get("company_phone", "")
    email = settings.get("company_email", "")
    address = settings.get("company_address", "")
    logo = settings.get("logo_path", "")

    filename = f"price_list_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Logo
    if logo and os.path.exists(logo):
        c.drawImage(logo, 20*mm, height - 40*mm, width=30*mm, height=20*mm, preserveAspectRatio=True)

    # Company Info
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(width - 20*mm, height - 20*mm, fix_text(company))
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20*mm, height - 28*mm, fix_text(address))
    c.drawRightString(width - 20*mm, height - 35*mm, f"📞 {fix_text(phone)}")
    c.drawRightString(width - 20*mm, height - 42*mm, f"✉ {fix_text(email)}")

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 65*mm, fix_text("قائمة الأسعار"))

    # Date
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 75*mm,
                        fix_text(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"))

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    y = height - 100*mm

    headers = ["الصنف", "SKU", "المخزن", "الكمية", "الحد الأدنى"]
    cols = [40*mm, 40*mm, 50*mm, 30*mm, 30*mm]

    x_start = 20*mm

    for i, h in enumerate(headers):
        c.drawString(x_start, y, fix_text(h))
        x_start += cols[i]

    y -= 10*mm
    c.line(20*mm, y, width - 20*mm, y)

    # Rows
    c.setFont("Helvetica", 11)
    for it in items:
        x = 20*mm
        y -= 8*mm

        if y < 20*mm:  # New Page
            c.showPage()
            y = height - 20*mm

        row = [
            it["name"],
            it["sku"],
            it["warehouse"],
            str(it["quantity"]),
            str(it["min_quantity"])
        ]

        for i, val in enumerate(row):
            c.drawString(x, y, fix_text(val))
            x += cols[i]

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    footer = "All Rights Reserved © Mahmoud Ali – 01000551634"
    c.drawCentredString(width / 2, 10*mm, footer)

    c.save()
    return filename


# ============================================================
# EXCEL EXPORT
# ============================================================
def export_price_list_excel(items):
    filename = f"price_list_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet("Price List")

    header_format = workbook.add_format({
        "bold": True, "bg_color": "#0A3D91",
        "color": "white", "font_size": 12,
        "align": "center"
    })

    row_format = workbook.add_format({"font_size": 10, "align": "center"})

    headers = ["الصنف", "SKU", "المخزن", "الكمية", "الحد الأدنى"]
    for col, h in enumerate(headers):
        sheet.write(0, col, h, header_format)

    for row, it in enumerate(items, start=1):
        sheet.write(row, 0, it["name"], row_format)
        sheet.write(row, 1, it["sku"], row_format)
        sheet.write(row, 2, it["warehouse"], row_format)
        sheet.write(row, 3, it["quantity"], row_format)
        sheet.write(row, 4, it["min_quantity"], row_format)

    workbook.close()
    return filename
