import json
import re

def validate_gstin(gstin):
    """
    Validates the GSTIN format. 
    GSTIN format is: 15 characters, where the first 2 are the state code, followed by 10 alphanumeric characters (PAN), 
    1 character for entity code, 1 digit for check code, and a final check digit.
    """
    gstin_regex = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z0-9]{1}[A-Z0-9]{1}$'
    if re.match(gstin_regex, gstin):
        return True
    return False

def calculate_gst(data):
    """
    Calculate GST, IGST, CGST, and SGST based on the provided data.
    Returns a dictionary with the total and breakdown of GST amounts.
    """
    gstin_data = data.get("gstin", [])
    amounts_data = data.get("amounts", [])
    tax_data = data.get("tax_amounts", [])
    
    # Check if GSTIN is valid
    for gst_data in gstin_data:
        gstin = gst_data.get("gstin", "")
        if not validate_gstin(gstin):
            return f"Invalid GSTIN: {gstin}"
    
    # Initialize total values
    max_amount = 0
    cgst_total = 0
    sgst_total = 0
    igst_total = 0
    
    # Calculate the maximum amount based on amounts
    for amount_data in amounts_data:
        for amount in amount_data["amounts"]:
            # Remove commas and convert to float
            amount_cleaned = amount.replace(',', '')
            max_amount = max(max_amount, float(amount_cleaned))

    # Calculate tax amounts based on CGST, SGST, IGST
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
    
    # Prepare the result with the maximum amount and GST breakdown
    result = {
        "Total_amount_with_gst": max_amount,
        "cgst": cgst_total,
        "sgst": sgst_total,
        "igst": igst_total
    }
    
    return result

def load_data_from_json(file_path):
    """
    Loads data from a JSON file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_results_to_json(validation_result, calculation_result, output_file):
    """
    Save the validation and calculation results to a JSON file.
    """
    results = {
        "GSTIN_Validation_Result": validation_result,
        "GST_Calculation_Result": calculation_result
    }
    with open(output_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)

# Load data from a JSON file
file_path = "extracted_data.json"  # Change this to the path of your JSON file
data = load_data_from_json(file_path)

# Validate GSTIN and calculate GST amounts
validation_result = [validate_gstin(gst_data["gstin"]) for gst_data in data["gstin"]]
calculation_result = calculate_gst(data)

# Save results to JSON
output_file = "gst_results.json"  # Output file name
save_results_to_json(validation_result, calculation_result, output_file)

print(f"Results saved to {output_file}")
