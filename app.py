import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import date

def create_id_card(name, father_name, student_id, roll_no, student_class, shift, photo, border_color, text_color, logo, school_name, school_contact, issue_date="", expiry_date=""):
    width, height = 650, 400
    background = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(background)

    # Load Fonts with Fallback
    try:
        title_font = ImageFont.truetype("Montserrat-Bold.ttf", 36)
        text_font = ImageFont.truetype("Roboto-Regular.ttf", 18)
    except:
        try:
        # Fallback to DejaVuSans (commonly available on Linux)
            title_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 36)
            text_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf"   , 18)
        except:
        # Final fallback to default PIL font
            st.warning("Custom and system fonts not found. Using default font.")
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()


    # Paste logo with white overlay
    if logo:
        try:
            logo_img = Image.open(logo).convert("RGBA").resize((500, 300))
            background.paste(logo_img, ((width - 500) // 2, (height - 300) // 2), logo_img)
            overlay = Image.new('RGBA', (500, 300), (255, 255, 255, 220))
            background.paste(overlay, ((width - 500) // 2, (height - 300) // 2), overlay)
        except:
            st.warning("Logo file is not a valid image.")

    # Multi-line school name
    max_school_name_width = width - 100
    school_lines = []
    words = school_name.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=title_font) <= max_school_name_width:
            line = test_line
        else:
            school_lines.append(line)
            line = word
    school_lines.append(line)

    y_text = 30
    for line in school_lines:
        line_width = draw.textlength(line, font=title_font)
        draw.text(((width - line_width) // 2, y_text), line, fill=border_color, font=title_font)
        y_text += 40
 
    # Outer border
    draw.rounded_rectangle([(10, 10), (width - 10, height - 10)], outline=border_color, width=5, radius=20)

    # Student Details
    y_pos = y_text + 10
    draw.text((50, y_pos), f"Name: {name}", fill=text_color, font=text_font)
    y_pos += 30
    draw.text((50, y_pos), f"Father Name: {father_name}", fill=text_color, font=text_font)
    y_pos += 30
    draw.text((50, y_pos), f"Student ID: {student_id}", fill=text_color, font=text_font)
    y_pos += 30
    draw.text((50, y_pos), f"Roll No: {roll_no}", fill=text_color, font=text_font)
    y_pos += 30
    draw.text((50, y_pos), f"Class: {student_class}", fill=text_color, font=text_font)
    y_pos += 30
    draw.text((50, y_pos), f"Shift: {shift}", fill=text_color, font=text_font)
    y_pos += 30

    if issue_date:
        draw.text((50, y_pos), f"Issue Date: {issue_date}", fill=text_color, font=text_font)
        y_pos += 30
    if expiry_date:
        draw.text((50, y_pos), f"Expiry Date: {expiry_date}", fill=text_color, font=text_font)

    # Photo Section with validation
    if photo:
        try:
            img = Image.open(photo).resize((140, 160)).convert("RGBA")
            mask = Image.new("L", (140, 160), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 140, 160), fill=255)
            img.putalpha(mask)
            background.paste(img, (480, 100), img)
            draw.rounded_rectangle((480, 100, 620, 260), outline=border_color, width=4, radius=12)
        except:
            st.warning("Student photo is not a valid image.")

    # Authorized signature
    authorized_signature_text = "Authorized Signature"
    signature_text_width = draw.textlength(authorized_signature_text, font=text_font)
    draw.text((width - signature_text_width - 30, height - 50), authorized_signature_text, fill=text_color, font=text_font)

    # School Contact Info below Authorized Signature
    if school_contact:
        contact_text = f"Contact: {school_contact}"
        contact_text_width = draw.textlength(contact_text, font=text_font)
        draw.text(((width - contact_text_width) // 2, height - 30), contact_text, fill=text_color, font=text_font)
    return background


def create_pdf(id_card):
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    id_card_bytes = io.BytesIO()
    id_card.save(id_card_bytes, format="PNG")
    id_card_bytes.seek(0)
    image = ImageReader(id_card_bytes)
    pdf.drawImage(image, 80, 350, width=500, height=300)
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def main():
    st.set_page_config(page_title="ID Card Generator", layout="wide")

    st.markdown("""
        <h1 style='text-align: center; color: #003366;'>🎨 Digital School ID Generator</h1>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🎨 Customize")
        border_color = st.color_picker("📝 Border Color", "#003366")
        text_color = st.color_picker("📝 Text Color", "#000000")
        logo = st.file_uploader("📷 Upload School Logo", type=["jpg", "png"])
        school_name = st.text_input("🏫 School Name")
        school_contact = st.text_input("📞 School Contact (Optional)")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("📌 Student Name")
        father_name = st.text_input("👨‍👦 Father Name")
        student_id = st.text_input("🆔 Student ID")
        roll_no = st.text_input("🔢 Roll No")
        student_class = st.text_input("📚 Class")
        shift = st.text_input("⏳ Shift")
        issue_date = st.date_input("📅 Issue Date (Optional)", value=date.today())
        expiry_date = st.date_input("📅 Expiry Date (Optional)", value=date.today())
        photo = st.file_uploader("📷 Upload Student Photo", type=["jpg", "png"])

    with col2:
        st.subheader("📞 ID Card Preview")
        st.info("ℹ️ Fill the details and click 'Generate ID Card' to preview and download.")

    generate = st.button("✅ Generate ID Card")
    reset = st.button("🔄 Reset Form")

    if generate:
        if all([name, father_name, student_id, roll_no, student_class, shift, photo, school_name]):
            id_card = create_id_card(
                name, father_name, student_id, roll_no, student_class, shift,
                photo, border_color, text_color, logo, school_name, school_contact,
                issue_date.strftime("%d-%m-%Y"), expiry_date.strftime("%d-%m-%Y")
            )
            col2.image(id_card, caption="🔍 Preview", use_container_width=True)
            pdf_file = create_pdf(id_card)
            buf_card = io.BytesIO()
            id_card.save(buf_card, format="PNG")
            col2.download_button("📥 Download ID Card (PNG)", buf_card.getvalue(), "id_card.png", "image/png")
            col2.download_button("📥 Download PDF", pdf_file.getvalue(), "id_card.pdf", "application/pdf")
        else:
            st.warning("⚠️ Please fill all required fields and upload images to generate the ID card.")

    if reset:
        st.experimental_rerun()


if __name__ == "__main__":
    main()
