from fpdf import FPDF

title = 'Lab Results'

class PDF(FPDF):
    def header(self):
        # font
        self.set_font('helvetica', 'B', 20)
        # Calculate width of title and position
        title_w = self.get_string_width(title) + 6
        doc_w = self.w
        self.set_x((doc_w - title_w) / 2)
        self.set_fill_color(255, 255, 255) # background = yellow
        self.set_line_width(1)
        # Title
        self.cell(title_w, 10, title, ln=1, align='C', fill=1)
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        # set font
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.set_text_color(169,169,169)
        
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def createpdf(test, result, lab_technician, doctor): 

    pdf = PDF('P', 'mm', 'Letter')

    # get total page numbers
    pdf.alias_nb_pages()

    # Set auto page break
    pdf.set_auto_page_break(auto = True, margin = 15)

    #Add Page
    pdf.add_page()

    # specify font
    pdf.set_font('helvetica', 'BI', 15)
    pdf.cell(20, 7,'Test:')
    pdf.set_font('times', '', 12)
    pdf.cell(20, 7, test, ln=1)

    pdf.set_font('helvetica', 'BI', 15)
    pdf.cell(20, 7,'Result:', ln=1)
    pdf.set_font('times', '', 12)
    pdf.cell(20)
    pdf.multi_cell(150, 7, description)

    pdf.cell(1, 5, ln=1)
    pdf.set_font('helvetica', 'BI', 12)
    pdf.cell(18, 7,'Doctor:')
    pdf.set_font('times', '', 10)
    pdf.cell(20, 7, doctor, ln=1)

    pdf.set_font('helvetica', 'BI', 12)
    pdf.cell(35, 7,'Lab Technician:')
    pdf.set_font('times', '', 10)
    pdf.cell(20, 7, lab_technician, ln=1)


    pdf.output('LabResult.pdf')
