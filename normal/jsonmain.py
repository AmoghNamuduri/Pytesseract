import os
import json
import cv2
import pytesseract
from pytesseract import Output
from docling.document_converter import DocumentConverter


# Input configurations
document_name = "Invoice2.pdf"  # Change to your file name (image or PDF)
source_dir = "normal"  # Base directory
source = os.path.join(source_dir, document_name)

# Output file
output_file = os.path.join(source_dir+"\output", "ExtractedTable2.json")

# Function to clean entries with empty keys
def clean_empty_keys(data):
    return {key: value for key, value in data.items() if key.strip() != ""}

# Function to normalize rows with missing values replaced by NULL
def normalize_row(headers, row):
    row = row[:len(headers)] + ["NULL"] * max(0, len(headers) - len(row))
    raw_data = dict(zip(headers, [cell if cell.strip() else "NULL" for cell in row]))
    return raw_data


# Function to extract table-like content
def extract_main_table(lines):
    start_table = False
    table_data = []

    i=True
    for line in lines:
        if "|" in line:  # Detect table rows using '|'
            if not start_table:
                start_table = True  # Start capturing table
            # Split the line into cells
            cells = line.split("|")
            print(cells)
            if len(cells) > 1 and (cells[1].strip().isdigit() or i):  # Check if the first cell (SN.) is a digit
                
                table_data.append(line.strip())
            i = False
        elif start_table:
            break  # End capturing when table ends
    print(table_data)
    return table_data

# Function to parse table into JSON
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

# Function to handle PDF input
def extract_table_from_pdf_to_json(source_path, output_file_path):
    converter = DocumentConverter()
    try:
        result = converter.convert(source_path)
        markdown_output = result.document.export_to_markdown()
        lines = [line.strip() for line in markdown_output.split("\n") if line.strip()]
        table_lines = extract_main_table(lines)
        parse_table_to_json(table_lines, output_file_path)
    except Exception as e:
        print(f"Error processing PDF: {e}")

# Main execution
if document_name.lower().endswith(".pdf"):
    extract_table_from_pdf_to_json(source, output_file)
else:
    print("Error: Unsupported file format. Please use a PDF or image file.")
