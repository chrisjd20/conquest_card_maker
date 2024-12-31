import fitz  # PyMuPDF
import os

def process_pdf_high_res(pdf_path, image_output_folder, text_output_folder, page_range):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Ensure output directories exist
    os.makedirs(image_output_folder, exist_ok=True)
    os.makedirs(text_output_folder, exist_ok=True)

    for page_num in page_range:
        page = pdf_document[page_num - 1]  # Pages are zero-indexed in PyMuPDF

        # Get the page dimensions
        rect = page.rect
        width, height = rect.width, rect.height

        # Define the custom rectangle for the snapshot (5% to 55%)
        left = 0.12 * width
        top = 0.06 * height
        right = 0.88 * width
        bottom = 0.52 * height
        custom_rect = fitz.Rect(left, top, right, bottom)

        # Snapshot the custom rectangle with high resolution
        zoom = 2.0  # Increase zoom for higher resolution
        mat = fitz.Matrix(zoom, zoom)  # Scale the rendering
        pix = page.get_pixmap(matrix=mat, clip=custom_rect)
        image_filename = os.path.join(image_output_folder, f"page_{page_num}_snapshot.png")
        pix.save(image_filename)

        # Extract text from the bottom 50% of the page
        bottom_rect = fitz.Rect(0, height / 2, width, height)
        text = page.get_text("text", clip=bottom_rect)
        text_filename = os.path.join(text_output_folder, f"page_{page_num}_bottom.txt")
        with open(text_filename, "w", encoding="utf-8") as text_file:
            text_file.write(text)

    print(f"Processing complete. Images saved to {image_output_folder}, text saved to {text_output_folder}.")

# Parameters
pdf_file_path = "TLAOK_TOURNAMENT_SCENARIO_PACK_April-Update.pdf"
image_output_dir = "snapshot_images_high_res"
text_output_dir = "extracted_text"
page_range = range(7, 19)  # Pages 7 to 18 (inclusive)

process_pdf_high_res(pdf_file_path, image_output_dir, text_output_dir, page_range)
