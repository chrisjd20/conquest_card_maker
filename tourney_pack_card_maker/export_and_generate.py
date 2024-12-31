import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os


def bold_headers_and_preserve_newlines(text):
    """Bold specific headers and preserve newlines."""
    headers = [
        "Setting up the Battlefield",
        "Scenario Special Rules",
        "Victory Points",
        "Game Length",
    ]
    for header in headers:
        text = text.replace(header, f"**{header}**")  # Mark headers for bolding and underlining
    return text


def process_pdf_high_res_to_cards(pdf_path, output_pdf_path, page_range):
    # Create temporary folder for images
    image_output_folder = "temp_images"
    os.makedirs(image_output_folder, exist_ok=True)

    pdf_document = fitz.open(pdf_path)
    images_and_texts = []

    for page_num in page_range:
        page = pdf_document[page_num - 1]  # Pages are zero-indexed in PyMuPDF

        # Get the page dimensions
        rect = page.rect
        width, height = rect.width, rect.height

        # Define the custom rectangle for the snapshot (top half of the page)
        # left = 0.12 * width
        # top = 0.06 * height
        # right = 0.88 * width
        # bottom = 0.52 * height

        left = 0.14 * width
        top = 0.07 * height
        right = 0.86 * width
        bottom = 0.49 * height

        custom_rect = fitz.Rect(left, top, right, bottom)

        # Snapshot the custom rectangle with very high resolution
        zoom = 4.0  # High zoom for better quality
        mat = fitz.Matrix(zoom, zoom).prerotate(90)  # Rotate during rendering
        pix = page.get_pixmap(matrix=mat, clip=custom_rect)
        image_filename = os.path.join(image_output_folder, f"page_{page_num}_snapshot.png")
        pix.save(image_filename)

        # Extract text from the bottom 50% of the page
        bottom_rect = fitz.Rect(0, height / 2, width, height)
        text = page.get_text("text", clip=bottom_rect)
        text = bold_headers_and_preserve_newlines(text)

        # Save the image path and text to the list
        images_and_texts.append((image_filename, text))

    # Create the card PDF
    create_card_pdf(output_pdf_path, images_and_texts)

    # Clean up temporary images
    for image_path, _ in images_and_texts:
        os.remove(image_path)
    os.rmdir(image_output_folder)


def create_card_pdf(output_pdf_path, images_and_texts):
    """
    Creates a printable PDF with images and text arranged on 8.5"x11" pages.
    """
    from reportlab.lib.colors import gray

    page_width, page_height = letter
    card_width = 2.5 * inch
    card_height = 3.5 * inch
    top_margin = 0.5 * inch
    left_right_margin = 0.3 * inch
    #left_right_margin = 0.25 * inch
    horizontal_spacing = 0.1 * inch
    vertical_spacing = 0.1 * inch

    c = canvas.Canvas(output_pdf_path, pagesize=letter)

    current_x = left_right_margin
    current_y = page_height - top_margin - card_height

    for image_path, text in images_and_texts:
        # Draw the image card
        img = fitz.open(image_path)
        pix = img[0].get_pixmap()
        aspect_ratio = pix.height / pix.width
        img_width = card_width
        img_height = card_width * aspect_ratio
        if img_height > card_height:
            img_height = card_height
            img_width = card_height / aspect_ratio

        img_x = current_x + (card_width - img_width) / 2
        img_y = current_y + (card_height - img_height) / 2
        c.drawImage(image_path, img_x, img_y, img_width, img_height)

        # Draw a border around the image card
        c.setLineWidth(0.5)  # Set border width to 1 pixel
        c.setStrokeColor(gray)  # Set border color to grey
        c.rect(current_x, current_y, card_width, card_height)

        # Move to next card position for the text
        current_y -= card_height + vertical_spacing
        if current_y < top_margin:
            current_y = page_height - top_margin - card_height
            current_x += card_width + horizontal_spacing
            if current_x + card_width > page_width - left_right_margin:
                c.showPage()  # Start a new page
                current_x = left_right_margin

        # Draw the text card
        c.setLineWidth(0.5)  # Set border width to 1 pixel
        c.setStrokeColor(gray)  # Set border color to grey
        c.rect(current_x, current_y, card_width, card_height)

        # Set font and dynamically adjust font size
        font_size = 5.75
        c.setFont("Helvetica", font_size)
        text_x = current_x + 0.1 * inch
        text_y = current_y + card_height - 0.2 * inch
        max_lines = int((card_height - 0.4 * inch) // (font_size + 2))  # Adjust based on card height
        lines = text.splitlines()

        text_top_left_offset_y = -5

        # Render text with bold and underlined headers
        for line in lines:
            if line.startswith("**") and line.endswith("**"):  # Bold and underlined headers
                c.setFont("Helvetica-Bold", font_size)
                header = line[2:-2]  # Remove bold markers
                c.drawString(text_x , text_y - text_top_left_offset_y, header)
                # Underline the header
                text_width = c.stringWidth(header, "Helvetica-Bold", font_size)
                c.line(text_x, text_y - text_top_left_offset_y - 2, text_x + text_width, text_y - text_top_left_offset_y  - 2)
            else:
                c.setFont("Helvetica", font_size)
                c.drawString(text_x, text_y - text_top_left_offset_y, line.strip())

            text_y -= font_size + 2.5  # Line spacing

            # Avoid overflowing the card
            #if text_y < current_y + 0.2 * inch:
            #    break

        # Move to the next card position
        current_y -= card_height + vertical_spacing
        if current_y < top_margin:
            current_y = page_height - top_margin - card_height
            current_x += card_width + horizontal_spacing
            if current_x + card_width > page_width - left_right_margin:
                c.showPage()  # Start a new page
                current_x = left_right_margin

    c.save()
    print(f"Card PDF created at {output_pdf_path}")



# Parameters
pdf_file_path = "TLAOK_TOURNAMENT_SCENARIO_PACK_April-Update.pdf"
output_pdf_path = "playing_cards.pdf"
page_range = range(7, 19)  # Pages 7 to 18 (inclusive)

process_pdf_high_res_to_cards(pdf_file_path, output_pdf_path, page_range)
