import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import base64
import io

# Load environment variables
load_dotenv()

@dataclass
class SupplierDetails:
    name: str
    gstin: str
    address: str

@dataclass
class RecipientDetails:
    name: str
    gstin: str
    address: str

@dataclass
class InvoiceDetails:
    invoice_number: str
    date: str
    place_of_supply: str
    terms: str

@dataclass
class ItemDetails:
    description: str
    quantity: float
    rate: float
    taxable_value: float
    hsn_sac_code: str
    cgst_rate: float
    cgst_amount: float
    sgst_rate: float
    sgst_amount: float
    igst_rate: float
    igst_amount: float

@dataclass
class TotalValues:
    subtotal: float
    cgst_total: float
    sgst_total: float
    igst_total: float
    total_invoice_value_numbers: float
    total_invoice_value_words: str

@dataclass
class AdditionalNotes:
    signature: str
    bank_details: str
    other_notes: str

@dataclass
class GSTInvoiceData:
    supplier_details: SupplierDetails
    recipient_details: RecipientDetails
    invoice_details: InvoiceDetails
    items: List[ItemDetails]
    total_values: TotalValues
    additional_notes: AdditionalNotes

class GSTInvoiceExtractor:
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def create_extraction_prompt(self) -> str:
        """Create a detailed prompt for GST invoice data extraction"""
        return """
You are an expert in extracting data from Indian GST invoices. Analyze the provided invoice image/document and extract all the mandatory GST invoice fields in a structured JSON format.

Extract the following information with high accuracy:

**SUPPLIER DETAILS:**
- Name (Business/Company name)
- GSTIN (15-digit GST identification number)
- Address (Complete address including state and PIN code)

**RECIPIENT DETAILS:**
- Name (Buyer's name/company)
- GSTIN (15-digit GST identification number)
- Address (Complete billing/shipping address)

**INVOICE DETAILS:**
- Invoice Number
- Invoice Date (format: DD/MM/YYYY or DD-MM-YYYY)
- Place of Supply (State name or state code)
- Payment Terms (if mentioned)

**ITEMIZED LIST:** (For each item/service)
- Description (Product/Service name)
- Quantity (with unit if specified)
- Rate (per unit price)
- Taxable Value (before tax amount)
- HSN/SAC Code (Harmonized System/Service Accounting Code)
- CGST Rate (%) and Amount
- SGST Rate (%) and Amount  
- IGST Rate (%) and Amount (if applicable)

**TOTAL VALUES:**
- Subtotal (sum of all taxable values)
- Total CGST Amount
- Total SGST Amount
- Total IGST Amount (if applicable)
- Total Invoice Value (final amount in numbers)
- Total Invoice Value in Words (spelled out amount)

**ADDITIONAL INFORMATION:**
- Signature details (if present)
- Bank Details (Account number, IFSC, etc.)
- Other notes or terms and conditions

**IMPORTANT INSTRUCTIONS:**
1. Return ONLY a valid JSON object with the extracted data
2. Use null for missing/unavailable fields
3. Ensure all numeric values are properly formatted (use 0 for zero amounts)
4. For tax rates, include both percentage and calculated amounts
5. Maintain precision for all monetary values
6. Extract HSN/SAC codes exactly as shown
7. For items list, include all line items separately

**JSON Structure:**
```json
{
  "supplier_details": {
    "name": "string",
    "gstin": "string", 
    "address": "string"
  },
  "recipient_details": {
    "name": "string",
    "gstin": "string",
    "address": "string"
  },
  "invoice_details": {
    "invoice_number": "string",
    "date": "string",
    "place_of_supply": "string",
    "terms": "string"
  },
  "items": [
    {
      "description": "string",
      "quantity": 0.0,
      "rate": 0.0,
      "taxable_value": 0.0,
      "hsn_sac_code": "string",
      "cgst_rate": 0.0,
      "cgst_amount": 0.0,
      "sgst_rate": 0.0,
      "sgst_amount": 0.0,
      "igst_rate": 0.0,
      "igst_amount": 0.0
    }
  ],
  "total_values": {
    "subtotal": 0.0,
    "cgst_total": 0.0,
    "sgst_total": 0.0,
    "igst_total": 0.0,
    "total_invoice_value_numbers": 0.0,
    "total_invoice_value_words": "string"
  },
  "additional_notes": {
    "signature": "string",
    "bank_details": "string",
    "other_notes": "string"
  }
}
```

Now analyze the invoice and provide the extracted data in the exact JSON format specified above.
"""

    def extract_from_image(self, image_path: str) -> Optional[GSTInvoiceData]:
        """Extract GST invoice data from an image file"""
        try:
            # Load and process image
            image = Image.open(image_path)
            
            # Create the prompt
            prompt = self.create_extraction_prompt()
            
            # Generate content using Gemini
            response = self.model.generate_content([prompt, image])
            
            # Parse the JSON response
            json_text = response.text.strip()
            
            # Clean the response if it contains markdown formatting
            if json_text.startswith('```json'):
                json_text = json_text[7:-3].strip()
            elif json_text.startswith('```'):
                json_text = json_text[3:-3].strip()
            
            # Parse JSON
            extracted_data = json.loads(json_text)
            
            # Convert to structured dataclass
            return self._dict_to_dataclass(extracted_data)
            
        except Exception as e:
            print(f"Error extracting data from image: {str(e)}")
            return None
    
    def extract_from_text(self, invoice_text: str) -> Optional[GSTInvoiceData]:
        """Extract GST invoice data from text content"""
        try:
            # Create the prompt with text
            prompt = f"{self.create_extraction_prompt()}\n\nINVOICE TEXT:\n{invoice_text}"
            
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            json_text = response.text.strip()
            
            # Clean the response if it contains markdown formatting
            if json_text.startswith('```json'):
                json_text = json_text[7:-3].strip()
            elif json_text.startswith('```'):
                json_text = json_text[3:-3].strip()
            
            # Parse JSON
            extracted_data = json.loads(json_text)
            
            # Convert to structured dataclass
            return self._dict_to_dataclass(extracted_data)
            
        except Exception as e:
            print(f"Error extracting data from text: {str(e)}")
            return None
    
    def _dict_to_dataclass(self, data: Dict) -> GSTInvoiceData:
        """Convert dictionary to GSTInvoiceData dataclass"""
        supplier = SupplierDetails(**data['supplier_details'])
        recipient = RecipientDetails(**data['recipient_details'])
        invoice = InvoiceDetails(**data['invoice_details'])
        
        items = [ItemDetails(**item) for item in data['items']]
        
        totals = TotalValues(**data['total_values'])
        notes = AdditionalNotes(**data['additional_notes'])
        
        return GSTInvoiceData(
            supplier_details=supplier,
            recipient_details=recipient,
            invoice_details=invoice,
            items=items,
            total_values=totals,
            additional_notes=notes
        )
    
    def save_to_json(self, invoice_data: GSTInvoiceData, output_path: str):
        """Save extracted data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(invoice_data), f, indent=2, ensure_ascii=False)
            print(f"Data saved to {output_path}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")
    
    def print_extracted_data(self, invoice_data: GSTInvoiceData):
        """Print extracted data in a formatted way"""
        print("\n" + "="*50)
        print("GST INVOICE DATA EXTRACTION RESULTS")
        print("="*50)
        
        print(f"\n📄 SUPPLIER DETAILS:")
        print(f"  Name: {invoice_data.supplier_details.name}")
        print(f"  GSTIN: {invoice_data.supplier_details.gstin}")
        print(f"  Address: {invoice_data.supplier_details.address}")
        
        print(f"\n👤 RECIPIENT DETAILS:")
        print(f"  Name: {invoice_data.recipient_details.name}")
        print(f"  GSTIN: {invoice_data.recipient_details.gstin}")
        print(f"  Address: {invoice_data.recipient_details.address}")
        
        print(f"\n📋 INVOICE DETAILS:")
        print(f"  Invoice Number: {invoice_data.invoice_details.invoice_number}")
        print(f"  Date: {invoice_data.invoice_details.date}")
        print(f"  Place of Supply: {invoice_data.invoice_details.place_of_supply}")
        print(f"  Terms: {invoice_data.invoice_details.terms}")
        
        print(f"\n📦 ITEMS ({len(invoice_data.items)} items):")
        for i, item in enumerate(invoice_data.items, 1):
            print(f"  Item {i}:")
            print(f"    Description: {item.description}")
            print(f"    Quantity: {item.quantity}")
            print(f"    Rate: ₹{item.rate}")
            print(f"    Taxable Value: ₹{item.taxable_value}")
            print(f"    HSN/SAC: {item.hsn_sac_code}")
            print(f"    CGST: {item.cgst_rate}% (₹{item.cgst_amount})")
            print(f"    SGST: {item.sgst_rate}% (₹{item.sgst_amount})")
            if item.igst_rate > 0:
                print(f"    IGST: {item.igst_rate}% (₹{item.igst_amount})")
        
        print(f"\n💰 TOTAL VALUES:")
        print(f"  Subtotal: ₹{invoice_data.total_values.subtotal}")
        print(f"  CGST Total: ₹{invoice_data.total_values.cgst_total}")
        print(f"  SGST Total: ₹{invoice_data.total_values.sgst_total}")
        if invoice_data.total_values.igst_total > 0:
            print(f"  IGST Total: ₹{invoice_data.total_values.igst_total}")
        print(f"  Total Invoice Value: ₹{invoice_data.total_values.total_invoice_value_numbers}")
        print(f"  Amount in Words: {invoice_data.total_values.total_invoice_value_words}")
        
        print(f"\n📝 ADDITIONAL NOTES:")
        print(f"  Signature: {invoice_data.additional_notes.signature}")
        print(f"  Bank Details: {invoice_data.additional_notes.bank_details}")
        print(f"  Other Notes: {invoice_data.additional_notes.other_notes}")

def main():
    """Main function to demonstrate usage"""
    extractor = GSTInvoiceExtractor()
    
    print("GST Invoice Data Extractor")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Extract from image file")
        print("2. Extract from text input")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            image_path = input("Enter the path to the invoice image: ").strip()
            if os.path.exists(image_path):
                print("Processing image...")
                invoice_data = extractor.extract_from_image(image_path)
                
                if invoice_data:
                    extractor.print_extracted_data(invoice_data)
                    
                    # Ask if user wants to save
                    save_choice = input("\nSave data to JSON file? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        output_path = input("Enter output file path (default: extracted_invoice_data.json): ").strip()
                        if not output_path:
                            output_path = "extracted_invoice_data.json"
                        extractor.save_to_json(invoice_data, output_path)
                else:
                    print("Failed to extract data from the image.")
            else:
                print("File not found!")
        
        elif choice == '2':
            print("Enter the invoice text (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "" and len(lines) > 0 and lines[-1] == "":
                    break
                lines.append(line)
            
            invoice_text = "\n".join(lines[:-1])  # Remove the last empty line
            
            if invoice_text.strip():
                print("Processing text...")
                invoice_data = extractor.extract_from_text(invoice_text)
                
                if invoice_data:
                    extractor.print_extracted_data(invoice_data)
                    
                    # Ask if user wants to save
                    save_choice = input("\nSave data to JSON file? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        output_path = input("Enter output file path (default: extracted_invoice_data.json): ").strip()
                        if not output_path:
                            output_path = "extracted_invoice_data.json"
                        extractor.save_to_json(invoice_data, output_path)
                else:
                    print("Failed to extract data from the text.")
            else:
                print("No text provided!")
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()