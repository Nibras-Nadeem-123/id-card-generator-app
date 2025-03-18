import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import date

def create_id_card(name, father_name, student_id, roll_no, student_class, shift, photo, border_color, text_color, logo, school_name, school_contact, issue_date="", expiry_date=""):
    width, height = 650, 400
    background = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(background)

    # Fonts Handling with Fallbacks
    try:
        title_font = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 34)
        text_font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 24)
    except:
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 34)
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            st.warning("Default font loaded.")
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

    # Logo and overlay
    if logo:
        try:
            logo_img = Image.open(logo).convert("RGBA").resize((500, 300))
            background.paste(logo_img, ((width - 500) // 2, (height - 300) // 2), logo_img)
            overlay = Image.new('RGBA', (500, 300), (255, 255, 255, 220))
            background.paste(overlay, ((width - 500) // 2, (height - 300) // 2), overlay)
        except:
            st.warning("Invalid logo image.")

    # Dynamic School Name Multi-line
    max_width = width - 100
    words = school_name.split()
    school_lines, line = [], ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=title_font) <= max_width:
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

    # Outer Border
    draw.rounded_rectangle([(10, 10), (width - 10, height - 10)], outline=border_color, width=5, radius=20)

    # Student Details
    y_pos = y_text + 10
    detail_gap = 28
    student_details = [
        f"Name: {name}",
        f"Father Name: {father_name}",
        f"Student ID: {student_id}",
        f"Roll No: {roll_no}",
        f"Class: {student_class}",
        f"Shift: {shift}"
    ]

    if issue_date:
        student_details.append(f"Issue Date: {issue_date}")
    if expiry_date:
        student_details.append(f"Expiry Date: {expiry_date}")

    for detail in student_details:
        draw.text((50, y_pos), detail, fill=text_color, font=text_font)
        y_pos += detail_gap

    # Student Photo
    if photo:
        try:
            img = Image.open(photo).resize((120, 140)).convert("RGBA")
            mask = Image.new("L", (120, 140), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 120, 140), fill=255)
            img.putalpha(mask)
            background.paste(img, (500, 100), img)
            draw.rounded_rectangle((500, 100, 620, 240), outline=border_color, width=4, radius=12)
        except:
            st.warning("Invalid student photo.")

    # Authorized Signature
    auth_text = "Authorized Signature"
    auth_width = draw.textlength(auth_text, font=text_font)
    draw.text((width - auth_width - 30, height - 70), auth_text, fill=text_color, font=text_font)

    # School Contact
    if school_contact:
        contact_text = f"Contact: {school_contact}"
        contact_width = draw.textlength(contact_text, font=text_font)
        draw.text(((width - contact_width) // 2, height - 40), contact_text, fill=text_color, font=text_font)

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
    st.markdown("<h1 style='text-align: center; color: #003366;'>🎨 Digital School ID Generator</h1>", unsafe_allow_html=True)

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