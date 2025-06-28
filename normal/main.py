import os
import cv2
import pytesseract

from docling.document_converter import DocumentConverter

document_name = "NewInvoice.png"

# Construct the full path
source_dir = "Incomplete projects\Docling"  # Base directory
source = os.path.join(source_dir, document_name)

converter = DocumentConverter()
result = converter.convert(source)

markdown_output = result.document.export_to_markdown()
output_file = os.path.join(source_dir, "ConvertedDocumentnew.txt")
with open(output_file, "w", encoding="utf-8") as file:
    file.write(markdown_output)

print(f"Conversion complete. Output saved to {output_file}")