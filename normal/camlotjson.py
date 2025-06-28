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

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return cv2.GaussianBlur(binary_image, (5, 5), 0)

def extract_table_cells(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    # Sort by Y (row) and then by X (column)
    sorted_boxes = sorted(bounding_boxes, key=lambda b: (b[1], b[0]))
    return sorted_boxes

# Function to clean entries with empty keys
def clean_empty_keys(data):
    return {key: value for key, value in data.items() if key.strip() != ""}

# Function to normalize rows with missing values replaced by NULL
def normalize_row(headers, row):
    row = row[:len(headers)] + ["NULL"] * (len(headers) - len(row))
    raw_data = dict(zip(headers, [cell if cell.strip() else "NULL" for cell in row]))
    return clean_empty_keys(raw_data)

def extract_table_cells(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    bounding_boxes = sorted(bounding_boxes, key=lambda b: (b[1], b[0]))  # Sort by Y, then X
    return bounding_boxes

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
            if cells[1].strip().isdigit() or i :  # Check if the first cell (SN.) is a digit
                
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

def extract_table_from_pdf_to_json(source_path, output_file_path):
    import camelot  # Import Camelot for table extraction

    try:
        # Use Camelot to read tables from the PDF
        tables = camelot.read_pdf(source_path, pages="all", flavor="stream")  # Use 'stream' for robust detection

        if not tables or len(tables) == 0:
            print("No tables found in the PDF.")
            return

        for i, table in enumerate(tables):
            print(f"Processing table {i + 1}...")

            # Convert to a Pandas DataFrame directly from Camelot
            df = table.df

            # Ensure the table has at least two rows (header + data)
            if df.shape[0] < 2 or df.shape[1] < 2:
                print(f"Skipping invalid or empty table {i + 1}")
                continue

            # Camelot handles headers directly (first row as headers)
            headers = df.iloc[0].tolist()  # First row as headers
            rows = df.iloc[1:].values.tolist()  # Remaining rows as data

            # Map rows to JSON format using headers as keys
            json_data = []
            for row in rows:
                # Pair headers with row values
                row_dict = {headers[idx].strip(): value.strip() if value.strip() else "NULL" for idx, value in enumerate(row)}
                json_data.append(row_dict)

            # Save JSON to a file
            table_output_file = output_file_path.replace(".json", f"_table_{i + 1}.json")
            with open(table_output_file, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4)

            print(f"Table {i + 1} extracted and saved as JSON to {table_output_file}")
    except Exception as e:
        print(f"Error processing PDF with Camelot: {e}")




# Main execution
if document_name.lower().endswith(".pdf"):
    extract_table_from_pdf_to_json(source, output_file)
else:
    print("Error: Unsupported file format. Please use a PDF or image file.")
