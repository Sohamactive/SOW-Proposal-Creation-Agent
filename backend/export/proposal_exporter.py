from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pptx import Presentation
import os

from backend.config import settings


class ProposalExporter:

    def __init__(self):
        os.makedirs(settings.EXPORT_FOLDER, exist_ok=True)

    def export_docx(self, proposal, filename="proposal.docx"):

        os.makedirs(settings.EXPORT_FOLDER, exist_ok=True)
        path = os.path.join(settings.EXPORT_FOLDER, filename)

        doc = Document()
        doc.add_heading("Project Proposal", level=0)

        for section, content in proposal.items():

            # Section title
            doc.add_heading(section.replace("_", " ").title(), level=1)

            self._write_content(doc, content)

        doc.save(path)

        return path


    def _write_content(self, doc, content):

        if isinstance(content, str):

            doc.add_paragraph(content)

        elif isinstance(content, dict):

            for key, value in content.items():

                doc.add_heading(key.replace("_", " ").title(), level=2)

                self._write_content(doc, value)

        elif isinstance(content, list):

            for item in content:

                if isinstance(item, dict):

                    for k, v in item.items():

                        p = doc.add_paragraph(style="List Bullet")
                        p.add_run(f"{k}: ").bold = True
                        p.add_run(str(v))

                else:

                    doc.add_paragraph(str(item), style="List Bullet")

        else:

            doc.add_paragraph(str(content))

    def export_pdf(self, proposal: dict, filename="proposal.pdf"):

        path = os.path.join(settings.EXPORT_FOLDER, filename)

        c = canvas.Canvas(path, pagesize=letter)

        y = 750

        for section, content in proposal.items():

            c.drawString(50, y, section)
            y -= 20

            text = str(content)

            for line in text.split("\n"):
                c.drawString(60, y, line[:100])
                y -= 15

                if y < 50:
                    c.showPage()
                    y = 750

            y -= 10

        c.save()

        return path

    def export_pptx(self, proposal: dict, filename="proposal.pptx"):

        path = os.path.join(settings.EXPORT_FOLDER, filename)

        prs = Presentation()

        for section, content in proposal.items():

            slide = prs.slides.add_slide(prs.slide_layouts[1])

            title = slide.shapes.title
            body = slide.placeholders[1]

            title.text = section
            body.text = str(content)

        prs.save(path)

        return path