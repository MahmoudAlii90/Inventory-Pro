import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from utils.settings_manager import SettingsManager
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display


def fix_text(txt):
    if not txt:
        return ""
    return get_display(arabic_reshaper.reshape(str(txt)))


def generate_sales_invoice(item_name, qty, price, total, customer_name, username, notes, invoice_id):
    settings = SettingsManager()

    company = settings.get("company_name", "Company Name")
    phone = settings.get("company_phone", "")
    email = settings.get("company_email", "")
    logo = settings.get("logo_path", "")
    address = settings.get("company_address", "")

    filename = f"sales_invoice_{invoice_id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    # ================= HEADER =================
    if logo and os.path.exists(logo):
        c.drawImage(logo, 20*mm, height - 40*mm, width=35*mm, height=25*mm, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - 20*mm, height - 20*mm, fix_text(company))

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20*mm, height - 27*mm, fix_text(address))
    c.drawRightString(width - 20*mm, height - 32*mm, f"📞 {fix_text(phone)}")
    c.drawRightString(width - 20*mm, height - 37*mm, f"✉ {fix_text(email)}")

    # Line
    c.setLineWidth(1)
    c.line(15*mm, height - 45*mm, width - 15*mm, height - 45*mm)

    # ================= INVOICE TITLE =================
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 55*mm, fix_text("فاتورة بيع"))

    # ================= CUSTOMER INFO =================
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 20*mm, height - 70*mm, fix_text("بيانات العميل:"))

    c.setFont("Helvetica", 11)
    c.drawRightString(width - 20*mm, height - 78*mm, f"{fix_text(customer_name)}")
    c.drawRightString(width - 20*mm, height - 85*mm, f"تاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ================= INVOICE DETAILS =================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, height - 105*mm, fix_text("الصنف"))
    c.drawString(80*mm, height - 105*mm, fix_text("الكمية"))
    c.drawString(110*mm, height - 105*mm, fix_text("السعر"))
    c.drawString(150*mm, height - 105*mm, fix_text("الإجمالي"))

    # Table Lines
    c.line(20*mm, height - 108*mm, width - 20*mm, height - 108*mm)

    c.setFont("Helvetica", 12)
    c.drawString(20*mm, height - 120*mm, fix_text(item_name))
    c.drawString(85*mm, height - 120*mm, str(qty))
    c.drawString(110*mm, height - 120*mm, f"{price:.2f}")
    c.drawString(150*mm, height - 120*mm, f"{total:.2f}")

    # ================= TOTAL =================
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 25*mm, height - 150*mm, f"{total:.2f} :الإجمالي النهائي")

    # ================= NOTES =================
    if notes:
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, height - 170*mm, fix_text("ملاحظات:"))
        c.drawString(20*mm, height - 178*mm, fix_text(notes))

    # ================= SIGNATURE =================
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, height - 200*mm, fix_text(f"تم بواسطة: {username}"))

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    footer_text = "All Rights Reserved © Mahmoud Ali – 01000551634"
    c.drawCentredString(width / 2, 15*mm, footer_text)

    c.save()

    return filename
