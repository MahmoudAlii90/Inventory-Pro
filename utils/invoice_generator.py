import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from utils.settings_manager import SettingsManager
import qrcode
from datetime import datetime


class InvoiceGenerator:

    def __init__(self):
        self.settings = SettingsManager().load_settings()

    # ==================================================================
    # Build QR Code
    # ==================================================================
    def generate_qr(self, data_dict):
        qr_img = qrcode.make(str(data_dict))
        path = "temp_qr.png"
        qr_img.save(path)
        return path

    # ==================================================================
    # Build the invoice file
    # ==================================================================
    def create_invoice(self, invoice_data, items, output_path, size="A4"):
        """
        invoice_data {
            "invoice_id": int,
            "customer": "...",
            "supplier": "...",
            "date": "...",
            "tax": ...,
            "discount": ...,
            "total": ...
        }
        items = list of dict rows
        """

        if size == "A4":
            page_size = A4
        elif size == "A4_L":
            page_size = landscape(A4)
        elif size == "A5":
            page_size = (148 * mm, 210 * mm)
        else:
            page_size = A4

        c = canvas.Canvas(output_path, pagesize=page_size)
        width, height = page_size

        # ==================================================================
        # Header (Logo + Company Info)
        # ==================================================================
        y = height - 40

        # Draw logo
        if self.settings.get("logo_path") and os.path.exists(self.settings["logo_path"]):
            try:
                c.drawImage(self.settings["logo_path"], 40, y - 60, width=80, preserveAspectRatio=True)
            except:
                pass

        # Company name
        c.setFont("Helvetica-Bold", 18)
        c.drawString(140, y, self.settings.get("company_name", "Company Name"))

        # Company info
        c.setFont("Helvetica", 10)
        c.drawString(140, y - 15, f"📍 {self.settings.get('company_address', '')}")
        c.drawString(140, y - 30, f"☎ {self.settings.get('company_phone', '')}")
        c.drawString(140, y - 45, f"✉ {self.settings.get('company_email', '')}")

        # ==================================================================
        # Invoice Title
        # ==================================================================
        y -= 100
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"INVOICE #{invoice_data['invoice_id']}")

        # ==================================================================
        # Invoice Details
        # ==================================================================
        c.setFont("Helvetica", 10)
        y -= 25
        c.drawString(40, y, f"Date: {invoice_data.get('date', '')}")

        if invoice_data.get("customer"):
            c.drawString(40, y - 15, f"Customer: {invoice_data['customer']}")

        if invoice_data.get("supplier"):
            c.drawString(40, y - 15, f"Supplier: {invoice_data['supplier']}")

        # ==================================================================
        # QR Code (Right Corner)
        # ==================================================================
        qr_path = self.generate_qr(invoice_data)
        try:
            c.drawImage(qr_path, width - 120, height - 180, width=80, height=80)
        except:
            pass

        # ==================================================================
        # Items Table
        # ==================================================================
        table_y = y - 60
        table_data = [["Item", "Qty", "Price", "Total"]]

        for it in items:
            table_data.append([
                it["name"],
                str(it["qty"]),
                f"{it['price']:.2f}",
                f"{it['total']:.2f}"
            ])

        tbl = Table(table_data, colWidths=[180, 60, 80, 80])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0A3D91")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))

        tbl.wrapOn(c, 40, table_y)
        tbl.drawOn(c, 40, table_y)

        # ==================================================================
        # totals
        # ==================================================================
        totals_y = table_y - (len(items) * 25) - 40

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, totals_y, f"Subtotal: {invoice_data['subtotal']:.2f}")
        c.drawString(40, totals_y - 20, f"Tax: {invoice_data['tax']:.2f}")
        c.drawString(40, totals_y - 40, f"Discount: {invoice_data['discount']:.2f}")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, totals_y - 70, f"Total: {invoice_data['total']:.2f}")

        # ==================================================================
        # Footer
        # ==================================================================
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)

        footer_text = (
            f"© {datetime.now().year} Mahmoud Ali · All Rights Reserved · 01000551634"
        )

        c.drawCentredString(width / 2, 20, footer_text)

        c.save()

        if os.path.exists(qr_path):
            os.remove(qr_path)
