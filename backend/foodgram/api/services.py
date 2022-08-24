import io
from typing import TextIO

from django.conf import settings
from reportlab.lib.colors import navy, olive
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_pdf(data: list, title: str) -> TextIO:
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('Open Sans Bold',
               f'{settings.BASE_DIR}{settings.STATIC_URL}open-sans-bold.ttf')
    )
    pdfmetrics.registerFont(
        TTFont('Open Sans',
               f'{settings.BASE_DIR}{settings.STATIC_URL}open-sans.ttf')
    )
    page.setFont('Open Sans Bold', 20)
    axis_y = 810
    page.setFillColor(olive)
    page.drawString(55, axis_y, f'{title}')
    axis_y -= 30
    page.setFont('Open Sans', 14)
    page.setFillColor(navy)
    string_number = 1
    for count in data:
        page.drawString(
            15, axis_y,
            f'{string_number}. {count[0].capitalize()} '
            f'({count[1]}) - {count[2]}'
        )
        axis_y -= 20
        string_number += 1
    page.showPage()
    page.save()
    buffer.seek(0)
    return buffer
