# libraries
import logging as log
from PyPDF2 import PdfWriter, PdfReader, Transformation
import io
from reportlab.pdfgen.canvas import Canvas


def get_color_arrow(diff):

    diff = change_diff_inv(diff)

    color = [0, 255, 0] if diff > 0 else [1, 0.3, 0.1]    # green/red

    arrow = '\u2191' if diff > 0 else '\u2193'  # up/down

    return color, arrow


def change_number(x):
    
    x = str(x)
    
    return f'{x[:-3]}.{x[-3:]}' if len(x)<=6 else f'{x[:-6]}.{x[-6:-3]}.{x[-3:]}'


def change_diff(x):
    
    x = str(x)
    
    return x.replace('.', ',')


def change_diff_inv(x):

    x = str(x)
    
    x = x.replace(',', '.')
    
    x = float(x)
    
    return x



# logging for feedback
class Logger:
    def __init__(self, name: str):
        """
        Create logger for feedback.
        :param name: String. Name of the logger.
        """
        self.logger = log.getLogger(name)
        self.logger.setLevel(log.DEBUG)

        # create console handler and set level to debug
        ch = log.StreamHandler()
        ch.setLevel(log.DEBUG)

        # create formatter
        formatter = log.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)


# class for generate pdf report
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
