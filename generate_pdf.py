import os
import subprocess
import sys

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package} to generate PDF...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Make sure reportlab is installed
install_and_import("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_demo_pdf():
    pdf_dir = "data"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "space_exploration_guide.pdf")
    
    print(f"Creating demo PDF file at: {pdf_path}")
    
    # Create document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=54, leftMargin=54,
                            topMargin=54, bottomMargin=54)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    
    story = []
    
    # Title
    story.append(Paragraph("Ares-V Mission: The Ultimate Guide to Mars Colonization", title_style))
    story.append(Spacer(1, 10))
    
    # Section 1
    story.append(Paragraph("1. Mission Overview", heading_style))
    story.append(Paragraph(
        "The Ares-V mission is humanity's first coordinated attempt to establish a permanent human colony on Mars. "
        "The primary landing site is inside the Gale Crater due to its rich geological diversity and suspected subterranean water-ice deposits. "
        "The colonization fleet consists of three primary modules: the Habitat Core, the Agricultural Dome, and the Science Laboratory.",
        body_style
    ))
    
    # Section 2
    story.append(Paragraph("2. Habitat and Power Systems", heading_style))
    story.append(Paragraph(
        "Power generation on Mars relies on a hybrid system. The primary source is a nuclear fission surface power system "
        "providing a constant 40 kilowatts of electrical energy. This is supplemented by high-efficiency flexible solar arrays "
        "designed to operate under dusty Martian conditions. Life support systems (MOXIE-II) extract carbon dioxide from the "
        "Martian atmosphere and convert it into breathable oxygen with 98% purity.",
        body_style
    ))
    
    # Section 3
    story.append(Paragraph("3. Emergency Protocol and Safety", heading_style))
    story.append(Paragraph(
        "Martian dust storms can block up to 90% of solar radiation and last for several weeks. In the event of a Category-4 "
        "dust storm, all non-essential operations must be suspended immediately. Colonists are instructed to retreat to the "
        "subterranean radiation shelters located underneath the Habitat Core. Emergency oxygen canisters are colored yellow "
        "and have a duration of 12 hours of active breathing time.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print("✅ Successfully generated 'data/space_exploration_guide.pdf'!")

if __name__ == "__main__":
    create_demo_pdf()
