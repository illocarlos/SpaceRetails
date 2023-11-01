from PyPDF2 import PdfWriter, PdfReader, Transformation
import io
from reportlab.pdfgen.canvas import Canvas


def get_color_arrow(diff):

    color = [0, 255, 0] if diff > 0 else [1, 0.3, 0.1]

    arrow = '\u2191' if diff > 0 else '\u2193'

    return color, arrow


class GenerateReport():

    def __init__(self, template_path):

        self.template_pdf = PdfReader(open(template_path, 'rb'))

        self.output = PdfWriter()
        self.op = Transformation().rotate(0).translate(tx=0, ty=0)

        self.page = None

    def add_text_to_page(self, page, text, point, font='Helvetica', fontsize=30, RGB=[0, 0, 0]):

        self.page = page

        packet = io.BytesIO()

        canvas = Canvas(packet, pagesize=(
            self.page.mediabox.width, self.page.mediabox.height))

        canvas.setFillColorRGB(*RGB)
        canvas.setFont(font, fontsize)
        canvas.drawString(point[0], point[1], text)

        canvas.save()

        packet.seek(0)

        result_pdf = PdfReader(packet)

        res_page = result_pdf.pages[0]

        res_page.add_transformation(self.op)
        self.page.merge_page(res_page)

    def merge(self):
        self.output.add_page(self.page)

    def generate(self, dest):

        outputStream = open(dest, 'wb')
        self.output.write(outputStream)
        outputStream.close()
