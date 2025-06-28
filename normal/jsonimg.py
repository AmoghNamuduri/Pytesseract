import os
import json
import cv2
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path


# Example usage
pdf_path = "Docling\normal\Invoice2.pdf"  # Replace with your PDF file
output_file_path = "ExtractedTable.json"  # Output JSON file
temp_image_dir = "temp_images"  # Directory to save temporary images

# Preprocess the image (grayscale, binarization, and Gaussian blur)
def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return cv2.GaussianBlur(binary_image, (5, 5), 0)

# Extract table-like cells from the image
def extract_table_cells(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    sorted_boxes = sorted(bounding_boxes, key=lambda b: (b[1], b[0]))  # Sort by Y, then X
    return sorted_boxes

# Extract text from a PDF using OCR
def extract_text_from_pdf(pdf_path, output_dir):
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ocr_results = []

    for i, page in enumerate(pages):
        # Save the page as an image
        page_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
        page.save(page_path, "JPEG")

        # Preprocess the image
        preprocessed_image = preprocess_image(page_path)

        # Perform OCR
        custom_config = "--psm 6"  # Set the OCR mode to assume a single uniform block of text
        ocr_output = pytesseract.image_to_string(preprocessed_image, config=custom_config)
        ocr_results.append(ocr_output)

    return ocr_results

# Normalize rows with missing values replaced by NULL
def normalize_row(headers, row):
    row = row[:len(headers)] + ["NULL"] * (len(headers) - len(row))
    return dict(zip(headers, [cell if cell.strip() else "NULL" for cell in row]))

# Extract table rows from OCR text
def extract_main_table(lines):
    start_table = False
    table_data = []

    for line in lines:
        if "|" in line:  # Detect table rows using '|'
            if not start_table:
                start_table = True  # Start capturing table
            table_data.append(line.strip())
        elif start_table:
            break  # End capturing when table ends

    return table_data

# Parse table into JSON
def parse_table_to_json(lines, output_file_path):
    table_data = []
    for line in lines:
        row = [cell.strip() for cell in line.split("|")]
        table_data.append(row)

    if not table_data or len(table_data) < 2:
        print("No valid table found.")
        return

    # First row is the header, subsequent rows are values
    headers = table_data[0]
    rows = table_data[1:]

    # Normalize rows and convert to JSON
    json_data = [normalize_row(headers, row) for row in rows]

    # Save JSON to file
    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)
    print(f"Table extracted and saved as JSON to {output_file_path}")

# Main function to handle PDF input and process tables
def process_pdf_to_table(pdf_path, output_file_path, temp_image_dir):
    # Extract OCR text from the PDF
    ocr_results = extract_text_from_pdf(pdf_path, temp_image_dir)

    # Process each page of OCR results
    for page_num, ocr_text in enumerate(ocr_results, start=1):
        print(f"Processing page {page_num}...")

        # Split text into lines and extract tables
        lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]
        table_lines = extract_main_table(lines)

        if table_lines:
            # Save the table to JSON
            page_output_file = output_file_path.replace(".json", f"_page_{page_num}.json")
            parse_table_to_json(table_lines, page_output_file)

if pdf_path.lower().endswith(".pdf"):
    process_pdf_to_table(pdf_path, output_file_path, temp_image_dir)
else:
    print("Error: Unsupported file format. Please use a PDF file.")
