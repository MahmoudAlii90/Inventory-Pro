# utils/invoice_print.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import qrcode
from utils.settings_manager import SettingsManager


class InvoicePrinter:
    def __init__(self):
        self.settings = SettingsManager()

    # =========================================================================
    def print(self, invoice):
        """
        invoice = {
            "id": 10,
            "date": "...",
            "customer": "...",
            "supplier": "...",
            "items": [{item_name, qty, price, total}],
            "total": number,
            "discount": number,
            "net": number,
            "tax": number,
        }
        """

        file_path = f"invoice_{invoice.get('id', 'new')}.pdf"
        self.generate_pdf(file_path, invoice)
        os.startfile(file_path)

    # =========================================================================
    def generate_pdf(self, filename, invoice):
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # ================= COMPANY INFO ===================
        logo_path = self.settings.get("logo_path")
        company_name = self.settings.get("company_name") or "Company Name"
        company_address = self.settings.get("company_address") or ""
        company_phone = self.settings.get("company_phone") or ""
        company_email = self.settings.get("company_email") or ""

        y = height - 40

        # Logo
        if logo_path and os.path.exists(logo_path):
            c.drawImage(logo_path, 450, y - 40, width=100, height=60, preserveAspectRatio=True)

        # Company Name
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, y, company_name)

        c.setFont("Helvetica", 11)
        c.drawString(40, y - 20, company_address)
        c.drawString(40, y - 35, f"Phone: {company_phone}")
        c.drawString(40, y - 50, f"Email: {company_email}")

        # ================= Invoice Header ===================
        y -= 100

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, "INVOICE")

        c.setFont("Helvetica", 12)
        c.drawString(40, y - 20, f"Invoice No: {invoice.get('id', '-')}")
        c.drawString(40, y - 35, f"Date: {invoice.get('date', '-')}")

        if invoice.get("customer"):
            c.drawString(40, y - 55, f"Customer: {invoice['customer']}")

        if invoice.get("supplier"):
            c.drawString(40, y - 55, f"Supplier: {invoice['supplier']}")

        # ================= QR CODE ===================
        qr_data = f"Invoice: {invoice.get('id')} | Total: {invoice.get('net')}"
        qr_img = qrcode.make(qr_data)
        qr_path = "qr_temp.png"
        qr_img.save(qr_path)

        c.drawImage(qr_path, 450, y - 60, width=100, height=100)

        # ================= TABLE HEADER ===================
        y -= 120

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Item")
        c.drawString(250, y, "Qty")
        c.drawString(320, y, "Price")
        c.drawString(400, y, "Total")

        y -= 10
        c.line(40, y, 550, y)
        y -= 15

        # ================= TABLE CONTENT ===================
        c.setFont("Helvetica", 11)

        for item in invoice["items"]:
            c.drawString(40, y, str(item.get("item_name", "")))
            c.drawString(250, y, str(item.get("qty", "")))
            c.drawString(320, y, f"{item.get('price', 0):.2f}")
            c.drawString(400, y, f"{item.get('total', 0):.2f}")
            y -= 22

            if y < 100:  # new page
                c.showPage()
                y = height - 50

        # ================= TOTAL SECTION ===================
        y -= 20
        c.line(40, y, 550, y)
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, f"Subtotal: {invoice.get('total', 0):.2f}")
        y -= 20

        c.drawString(40, y, f"Discount: {invoice.get('discount', 0):.2f}")
        y -= 20

        c.drawString(40, y, f"Tax: {invoice.get('tax', 0):.2f}")
        y -= 20

        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, f"Net Total: {invoice.get('net', invoice.get('total', 0)):.2f}")

        # ================= FOOTER ===================
        c.setFont("Helvetica-Oblique", 10)
        footer_text = "All Rights Reserved to Mahmoud Ali — 01000551634"
        c.drawString(40, 40, footer_text)

        c.save()

        try:
            os.remove(qr_path)
        except:
            pass
