import os
import json
from docling.document_converter import DocumentConverter

# Input configurations
document_name = "extracted_table.pdf"  # Use the extracted table PDF as input
source_dir = ""  # Base directory
source = os.path.join(source_dir, document_name)

# Output file
output_file = os.path.join(source_dir, "ExtractedTable.json")

# Function to normalize rows with missing values replaced by NULL
def normalize_row(headers, row):
    row = row[:len(headers)] + ["NULL"] * (len(headers) - len(row))
    return dict(zip(headers, [cell if cell.strip() else "NULL" for cell in row]))

# Function to extract table from markdown and convert to JSON
def extract_table_from_markdown(markdown_text, output_file_path):
    table_data = []
    for line in markdown_text.split("\n"):
        if "|" in line:  # Assuming tables are delimited by '|'
            row = [cell.strip() for cell in line.split("|")]
            table_data.append(row)

    if not table_data or len(table_data) < 2:
        print("No valid table found.")
        return

    # First row is the header, subsequent rows are values
    headers = table_data[0]
    rows = table_data[1:]

    # Convert rows into JSON format with normalized rows
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
        extract_table_from_markdown(markdown_output, output_file_path)
    except Exception as e:
        print(f"Error processing PDF: {e}")

# Main execution
if document_name.lower().endswith(".pdf"):
    extract_table_from_pdf_to_json(source, output_file)
else:
    print("Error: Unsupported file format. Please use an extracted table PDF as input.")