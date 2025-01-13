import re
import cv2
import pytesseract
import json
from nltk.tokenize import word_tokenize
import nltk

# Download necessary NLTK resources
nltk.download('punkt')

def check_and_replace_gstin_keywords(gstin_numbers, extracted_outputs, gst_keywords):
    """
    Check if GSTIN-related words are in other extracted outputs, 
    and replace the GSTIN numbers with the matched output if found.
    """
    updated_gstin_output = []
    for gstin in gstin_numbers:
        matched = False
        for keyword, line, amounts in extracted_outputs:
            # Check if any GST-related keyword exists in the line
            if any(gst_keyword in line.lower() for gst_keyword in gst_keywords):
                updated_gstin_output.append((gstin, line))  # Replace GSTIN output with the matched line
                matched = True
                break
        if not matched:
            updated_gstin_output.append((gstin, "Original GSTIN Matched"))  # Keep the original GSTIN if no match
    return updated_gstin_output

# Read the image
image = cv2.imread('data/invoice.jpg', 0)

# Convert it into text using OCR
text = pytesseract.image_to_string(image)

# Define keywords related to amounts and taxes
amount_keywords = ["total", "amount", "balance", "subtotal", "tax", "due", "payment"]
tax_keywords = ["cgst", "sgst", "igst", "tax"]

# GST-related keywords for the function
gst_keywords = ["gstin", "gst", "uin", "tax id", "tax identification number"]

# Extract amounts using regex (e.g., numbers with or without decimal points, currency symbols)
amounts_with_keywords = []
tax_amounts_with_keywords = []

# Define the GSTIN regex pattern
gst_regex = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b'

# Extract GSTIN/UINs using NLTK
tokens = word_tokenize(text)  # Tokenize the text
tokenized_text = " ".join(tokens)  # Combine tokens for regex matching
gstin_numbers = re.findall(gst_regex, tokenized_text)  # Find GSTIN numbers

# Split text into lines for better context
lines = text.split('\n')
for line in lines:
    # Extract general amounts
    for keyword in amount_keywords:
        if keyword.lower() in line.lower():  # Case-insensitive matching
            amounts = re.findall(r'\b[\$\u20AC\u00A3]?\d+(?:,\d{3})*(?:\.\d{1,2})?\b', line)
            if amounts:
                amounts_with_keywords.append((keyword, line.strip(), amounts))
    
    # Extract tax-specific amounts
    for tax_keyword in tax_keywords:
        if tax_keyword.lower() in line.lower():  # Case-insensitive matching
            tax_amounts = re.findall(r'\b[\$\u20AC\u00A3]?\d+(?:,\d{3})*(?:\.\d{1,2})?\b', line)
            if tax_amounts:
                tax_amounts_with_keywords.append((tax_keyword, line.strip(), tax_amounts))

# Check and replace GSTIN-related keywords
updated_gstin_output = check_and_replace_gstin_keywords(
    gstin_numbers, amounts_with_keywords + tax_amounts_with_keywords, gst_keywords
)

# Prepare the JSON structure
extracted_data = {
    "gstin": [
        {"gstin": gstin, "context": context} for gstin, context in updated_gstin_output
    ],
    "amounts": [
        {"keyword": keyword, "line": line, "amounts": amounts} for keyword, line, amounts in amounts_with_keywords
    ],
    "tax_amounts": [
        {"tax_keyword": tax_keyword, "line": line, "amounts": tax_amounts} for tax_keyword, line, tax_amounts in tax_amounts_with_keywords
    ]
}

# Save the extracted data to a JSON file
output_file = 'extracted_data.json'
with open(output_file, 'w') as json_file:
    json.dump(extracted_data, json_file, indent=4)

print(f"Data successfully saved to {output_file}")
