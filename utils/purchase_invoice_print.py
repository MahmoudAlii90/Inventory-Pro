import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import qrcode
from utils.settings_manager import SettingsManager


class PurchaseInvoicePrinter:
    def __init__(self):
        self.settings = SettingsManager().load()

        self.company_name = self.settings.get("company_name", "Company Name")
        self.company_phone = self.settings.get("company_phone", "")
        self.company_email = self.settings.get("company_email", "")
        self.company_address = self.settings.get("company_address", "")
        self.logo_path = self.settings.get("logo_path", "")

        # Arabic font support
        ar_font = "Cairo-Regular.ttf"
        if os.path.exists(ar_font):
            pdfmetrics.registerFont(TTFont("Cairo", ar_font))
        else:
            print("⚠ Cairo font not found!")

    # =====================================================================
    def generate_pdf(self, invoice, filename, size="A4"):
        page = A4 if size == "A4" else A5
        c = canvas.Canvas(filename, pagesize=page)

        width, height = page
        y = height - 40

        # =============================== HEADER ===============================
        if self.logo_path and os.path.exists(self.logo_path):
            c.drawImage(self.logo_path, width - 120, y - 30, width=80, preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 20)
        c.drawRightString(width - 140, y, self.company_name)

        c.setFont("Helvetica", 10)
        c.drawRightString(width - 140, y - 18, self.company_phone)
        c.drawRightString(width - 140, y - 32, self.company_email)
        c.drawRightString(width - 140, y - 46, self.company_address)

        y -= 90

        # =============================== TITLE ===============================
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "PURCHASE INVOICE")
        y -= 30

        # =============================== INFO ===============================
        c.setFont("Helvetica", 12)
        c.drawString(40, y, f"Invoice No: {invoice['invoice_no']}")
        c.drawRightString(width - 40, y, f"Date: {invoice['date']}")
        y -= 25

        c.drawString(40, y, f"Supplier: {invoice['supplier']}")
        y -= 20

        # QR Code
        qr_path = f"qr_{invoice['invoice_no']}.png"
        qr = qrcode.make(invoice["invoice_no"])
        qr.save(qr_path)
        c.drawImage(qr_path, width - 120, y - 20, width=70, preserveAspectRatio=True)
        os.remove(qr_path)

        y -= 50

        # =============================== TABLE HEADER ===============================
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Item")
        c.drawString(220, y, "Qty")
        c.drawString(300, y, "Cost Price")
        c.drawRightString(width - 40, y, "Total")

        y -= 10
        c.line(40, y, width - 40, y)
        y -= 20

        # =============================== ITEMS ===============================
        c.setFont("Helvetica", 12)

        for item in invoice["items"]:
            if y < 80:
                c.showPage()
                y = height - 80

            c.drawString(40, y, item["name"])
            c.drawString(220, y, str(item["qty"]))
            c.drawString(300, y, str(item["price"]))
            c.drawRightString(width - 40, y, str(item["total"]))
            y -= 22

        y -= 15
        c.line(40, y, width - 40, y)
        y -= 30

        # =============================== TOTALS ===============================
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(width - 40, y, f"Net Total: {invoice['total']}")
        y -= 25

        # =============================== FOOTER ===============================
        c.setFont("Helvetica", 8)
        c.drawCentredString(
            width / 2,
            25,
            "All Rights Reserved © Mahmoud Ali — 01000551634"
        )

        c.save()

        return filename
