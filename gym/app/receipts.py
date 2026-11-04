"""
Place at: app/receipts.py
Requires: pip install reportlab

A receipt is generated from one Subscription row, since a Subscription
is the record of a membership payment (amount_paid, payment_method, transaction_id).
"""
from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def is_paid(subscription):
    """A subscription only exists once the membership was paid for
    (cash recorded by admin, or eSewa payment verified)."""
    return True


def receipt_data(subscription):
    user = subscription.user
    return {
        'id': subscription.pk,
        'number': f"FT-{subscription.pk:06d}",
        'date': subscription.created_at,
        'member_name': user.get_full_name() or user.username,
        'member_email': user.email,
        'package': subscription.package.name,
        'period_start': subscription.start_date,
        'period_end': subscription.end_date,
        'amount': subscription.amount_paid,
        'method': subscription.get_payment_method_display(),
        'reference': subscription.transaction_id or '-',
        'status': 'PAID',
    }


def _fmt_date(value):
    if value is None:
        return '-'
    if hasattr(value, 'astimezone') and timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime('%d %b %Y')


def _fmt_money(value):
    try:
        return f"Rs. {float(value):,.2f}"
    except (TypeError, ValueError):
        return f"Rs. {value}"


def build_receipt_pdf(subscription):
    """Returns the receipt as PDF bytes."""
    d = receipt_data(subscription)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left, right = 20 * mm, width - 20 * mm

    # ---- Header band ----
    c.setFillColor(colors.HexColor('#0f172a'))
    c.rect(0, height - 42 * mm, width, 42 * mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#34d399'))
    c.setFont('Helvetica-Bold', 26)
    c.drawString(left, height - 23 * mm, 'FitTrack')
    c.setFillColor(colors.white)
    c.setFont('Helvetica', 10)
    c.drawString(left, height - 31 * mm, 'Gym Management System')
    c.setFont('Helvetica-Bold', 14)
    c.drawRightString(right, height - 23 * mm, 'PAYMENT RECEIPT')
    c.setFont('Helvetica', 10)
    c.drawRightString(right, height - 31 * mm, d['number'])

    # ---- Detail rows ----
    period = f"{_fmt_date(d['period_start'])}  to  {_fmt_date(d['period_end'])}"
    rows = [
        ('Receipt No.', d['number']),
        ('Date', _fmt_date(d['date'])),
        ('Member', d['member_name']),
        ('Email', d['member_email'] or '-'),
        ('Package', d['package']),
        ('Membership period', period),
        ('Payment method', d['method']),
        ('Transaction ref.', d['reference']),
        ('Status', d['status']),
    ]

    y = height - 62 * mm
    for label, value in rows:
        c.setFillColor(colors.HexColor('#64748b'))
        c.setFont('Helvetica', 8.5)
        c.drawString(left, y, label.upper())
        c.setFillColor(colors.HexColor('#0f172a'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(left + 55 * mm, y, str(value)[:60])
        c.setStrokeColor(colors.HexColor('#e2e8f0'))
        c.line(left, y - 4 * mm, right, y - 4 * mm)
        y -= 11 * mm

    # ---- Total box ----
    y -= 4 * mm
    c.setFillColor(colors.HexColor('#ecfdf5'))
    c.setStrokeColor(colors.HexColor('#34d399'))
    c.roundRect(left, y - 16 * mm, right - left, 20 * mm, 3 * mm, stroke=1, fill=1)
    c.setFillColor(colors.HexColor('#065f46'))
    c.setFont('Helvetica-Bold', 11)
    c.drawString(left + 6 * mm, y - 6 * mm, 'AMOUNT PAID')
    c.setFont('Helvetica-Bold', 18)
    c.drawRightString(right - 6 * mm, y - 8 * mm, _fmt_money(d['amount']))

    # ---- Footer ----
    c.setFillColor(colors.HexColor('#64748b'))
    c.setFont('Helvetica', 8.5)
    c.drawCentredString(width / 2, 25 * mm,
                        'This is a computer-generated receipt and does not require a signature.')
    c.drawCentredString(width / 2, 20 * mm,
                        f"Generated on {timezone.localtime().strftime('%d %b %Y, %H:%M')}")

    c.showPage()
    c.save()
    return buffer.getvalue()
