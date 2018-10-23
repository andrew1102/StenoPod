import sys
import os
from fpdf import FPDF
from google_speech_wrapper import Speech_Wrapper

guest = sys.argv[1]
title = guest.replace('_', ' ')
title = 'This Week in Machine Learning & AI: '+title+' Interview'
path = os.path.join(os.environ.get('REPO'), 'pdfs')

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, '%s' % (label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, txt):
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, label, txt):
        self.add_page()
        self.chapter_title(label=label)
        self.chapter_body(txt)

pdf = PDF()
pdf.set_title(title)
wrap = Speech_Wrapper(title=guest)
script = wrap.Produce_DiarScript()
txt = ''
begin = 0
end = -1

for i in range(len(script)):
    line = script[i]
    rline = script[-i]
    if line.find('Guest') != -1: begin = i 
    if rline.find('Guest') != -1: end = -i 
    if begin > 0 and end < -1: break 

intro = ''

for line in script[:begin]:
    intro += line

body = ''

for line in script[begin:end+1]:
    body += line

outro = ''

for line in script[end+1:]:
    outro += line

pdf.print_chapter(label = 'Introduction', txt=intro)
pdf.print_chapter(label = 'Interview', txt=body)
pdf.print_chapter(label = 'Conclusion', txt=outro)
pdf.output(os.path.join(path, 'Final_'+guest+'_Transcript.pdf'), 'F')
