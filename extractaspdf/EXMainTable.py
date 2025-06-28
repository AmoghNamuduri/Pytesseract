import fitz  # PyMuPDF
import cv2
import pytesseract
from fpdf import FPDF
import os

def extract_table_from_pdf(input_pdf, output_pdf):
    try:
        # Open the original PDF
        pdf_document = fitz.open(input_pdf)
        page = pdf_document[0]  # Assuming the table is on the first page

        # Extract all text blocks from the page
        blocks = page.get_text("blocks")
        table_blocks = []

        # Identify blocks containing the main table
        for block in blocks:
            text = block[4]  # Text content of the block
            if "SN" in text or "Sr" in text:  # Start of the table
                table_blocks.append(block)
            elif "Amount" in text and table_blocks:  # End of the table
                table_blocks.append(block)
                break

        if not table_blocks:
            print("No table detected in the PDF.")
            return

        # Calculate the bounding box for the main table
        x0, y0, x1, y1 = 9999, 9999, 0, 0
        for block in table_blocks:
            x0 = min(x0, block[0])
            y0 = min(y0, block[1])
            x1 = max(x1, block[2])
            y1 = max(y1, block[3])

        # Define the table boundary rectangle
        table_rect = fitz.Rect(x0, y0, x1, y1)

        # Extract table as an image
        table_image = page.get_pixmap(clip=table_rect)
        table_image.save("temp_table.png")

        # Convert the table image to a PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.image("temp_table.png", x=10, y=10, w=190)  # Fit image to page
        pdf.output(output_pdf)
        print(f"Extracted table saved to {output_pdf}")
    except Exception as e:
        print(f"Error extracting table from PDF: {e}")

def extract_table_from_image(input_image, output_pdf):
    try:
        # Read the image
        image = cv2.imread(input_image)
        if image is None:
            print("Error: Image not found or unsupported format.")
            return

        # Perform OCR to extract text
        d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Detect rows that start with "SN"/"Sr" and end with "Amount"
        n_boxes = len(d['level'])
        x_min, y_min, x_max, y_max = 9999, 9999, 0, 0
        table_started = False

        for i in range(n_boxes):
            text = d['text'][i].strip()
            x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]

            if "SN" in text or "Sr" in text:  # Start of the table
                table_started = True

            if table_started:
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x + w), max(y_max, y + h)

            if "Amount" in text and table_started:  # End of the table
                break

        # Crop and save the table region
        if x_min < x_max and y_min < y_max:
            table_image = image[y_min:y_max, x_min:x_max]
            cv2.imwrite("temp_table.png", table_image)

            # Convert the table image to a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.image("temp_table.png", x=10, y=10, w=190)  # Fit image to page
            pdf.output(output_pdf)
            print(f"Extracted table saved to {output_pdf}")
        else:
            print("No valid table region detected.")
    except Exception as e:
        print(f"Error extracting table from image: {e}")

# Main execution for extraction
input_file = "Invoice2.pdf"  # Change to your file name (image or PDF)
output_file = "extracted_table.pdf"

if input_file.lower().endswith(".pdf"):
    extract_table_from_pdf(input_file, output_file)
elif input_file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
    extract_table_from_image(input_file, output_file)
else:
    print("Error: Unsupported file format. Please use a PDF or image file.")
