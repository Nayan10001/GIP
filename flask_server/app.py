from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import re
import pytesseract
import cv2

app = Flask(__name__)

# Configure the upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'imageUpload' not in request.files:
        return redirect(request.url)
    
    file = request.files['imageUpload']
    
    if file:
        # Save the uploaded image to the uploads folder
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Process the image from the uploads folder
        image = cv2.imread(filename, 0)
        text = pytesseract.image_to_string(image)

        # Extract data from text (GSTIN, amounts, taxes)
        extracted_data = extract_data_from_text(text)

        # Save the extracted data to a JSON file
        extracted_data_file = 'extracted_data.json'
        with open(extracted_data_file, 'w') as json_file:
            json.dump(extracted_data, json_file, indent=4)

        # Calculate GST results and save to results.json
        calculation_result = calculate_gst(extracted_data)
        validation_result = [validate_gstin(gst_data["gstin"]) for gst_data in extracted_data["gstin"]]

        results = {
            "GSTIN_Validation_Result": validation_result,
            "GST_Calculation_Result": calculation_result
        }

        results_file = 'gst_results.json'
        with open(results_file, 'w') as json_file:
            json.dump(results, json_file, indent=4)

        return redirect(url_for('result'))

@app.route('/result')
def result():
    # Load the results from results.json
    results_file = 'gst_results.json'

    if os.path.exists(results_file):
        with open(results_file, 'r') as json_file:
            results = json.load(json_file)
    else:
        results = {}

    return render_template('result.html', results=results)

def extract_data_from_text(text):
    """
    Extracts necessary data (GSTIN, amounts, and taxes) from the text.
    This function should include the text processing logic you already have.
    """
    gst_keywords = ["gstin", "gst", "uin", "tax id", "tax identification number"]
    amount_keywords = ["total", "amount", "balance", "subtotal", "tax", "due", "payment"]
    tax_keywords = ["cgst", "sgst", "igst", "tax"]

    # Extract GSTINs using regex
    gstin_regex = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b'
    gstin_numbers = re.findall(gstin_regex, text)

    amounts_with_keywords = []
    tax_amounts_with_keywords = []

    # Split text into lines for better context
    lines = text.split('\n')
    for line in lines:
        # Extract amounts
        for keyword in amount_keywords:
            if keyword.lower() in line.lower():
                amounts = re.findall(r'\b[\$\u20AC\u00A3]?\d+(?:,\d{3})*(?:\.\d{1,2})?\b', line)
                if amounts:
                    amounts_with_keywords.append((keyword, line.strip(), amounts))

        # Extract tax-specific amounts
        for tax_keyword in tax_keywords:
            if tax_keyword.lower() in line.lower():
                tax_amounts = re.findall(r'\b[\$\u20AC\u00A3]?\d+(?:,\d{3})*(?:\.\d{1,2})?\b', line)
                if tax_amounts:
                    tax_amounts_with_keywords.append((tax_keyword, line.strip(), tax_amounts))

    # Prepare the extracted data
    extracted_data = {
        "gstin": [{"gstin": gstin, "context": "GSTIN found in the document"} for gstin in gstin_numbers],
        "amounts": [{"keyword": keyword, "line": line, "amounts": amounts} for keyword, line, amounts in amounts_with_keywords],
        "tax_amounts": [{"tax_keyword": tax_keyword, "line": line, "amounts": tax_amounts} for tax_keyword, line, tax_amounts in tax_amounts_with_keywords]
    }

    return extracted_data

def validate_gstin(gstin):
    """
    Validates the GSTIN format.
    """
    gstin_regex = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z0-9]{1}[A-Z0-9]{1}$'
    if re.match(gstin_regex, gstin):
        return True
    return False

def calculate_gst(data):
    """
    Calculates the GST amounts based on the provided data.
    """
    gstin_data = data.get("gstin", [])
    amounts_data = data.get("amounts", [])
    tax_data = data.get("tax_amounts", [])
    
    max_amount = 0
    cgst_total = 0
    sgst_total = 0
    igst_total = 0
    
    for amount_data in amounts_data:
        for amount in amount_data["amounts"]:
            amount_cleaned = amount.replace(',', '')
            max_amount = max(max_amount, float(amount_cleaned))

    for tax in tax_data:
        tax_type = tax.get("tax_keyword", "").lower()
        for amount in tax["amounts"]:
            amount_cleaned = amount.replace(',', '')
            if tax_type == "cgst":
                cgst_total += float(amount_cleaned)
            elif tax_type == "sgst":
                sgst_total += float(amount_cleaned)
            elif tax_type == "igst":
                igst_total += float(amount_cleaned)
    
    result = {
        "Total_amount_with_gst": max_amount,
        "cgst": cgst_total,
        "sgst": sgst_total,
        "igst": igst_total
    }
    
    return result

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)
