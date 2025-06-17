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
        # Use gemini-1.5-pro for better image processing capabilities
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
8. If you cannot read certain parts clearly, use "Not Clear" as the value
9. Always return valid JSON - no extra text or explanations

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

    def preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better OCR results"""
        try:
            # Open image with PIL
            image = Image.open(image_path)
            
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get original dimensions
            width, height = image.size
            
            # Resize if image is too large (max 4MP for Gemini)
            max_pixels = 4 * 1024 * 1024  # 4 megapixels
            if width * height > max_pixels:
                # Calculate new dimensions maintaining aspect ratio
                ratio = (max_pixels / (width * height)) ** 0.5
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            
            # Enhance image contrast if it's too low
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Slightly increase contrast
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            raise

    def extract_from_image(self, image_path: str) -> Optional[GSTInvoiceData]:
        """Extract GST invoice data from an image file"""
        try:
            # Validate file exists
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at {image_path}")
                return None
            
            # Validate file size (max 20MB)
            file_size = os.path.getsize(image_path)
            if file_size > 20 * 1024 * 1024:
                print("Error: Image file too large (max 20MB)")
                return None
            
            print(f"Processing image: {image_path} (Size: {file_size/1024/1024:.2f}MB)")
            
            # Preprocess image
            image = self.preprocess_image(image_path)
            
            # Create the prompt
            prompt = self.create_extraction_prompt()
            
            # Generate content using Gemini with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Attempting extraction (attempt {attempt + 1}/{max_retries})...")
                    response = self.model.generate_content(
                        [prompt, image],
                        generation_config={
                            "temperature": 0.1,  # Low temperature for consistent output
                            "max_output_tokens": 4096,
                        }
                    )
                    
                    if not response.text:
                        print("Warning: Empty response from Gemini API")
                        continue
                    
                    break
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    continue
            
            # Parse the JSON response
            json_text = response.text.strip()
            print(f"Raw response length: {len(json_text)} characters")
            
            # Clean the response if it contains markdown formatting
            if '```json' in json_text:
                start_idx = json_text.find('```json') + 7
                end_idx = json_text.rfind('```')
                if end_idx > start_idx:
                    json_text = json_text[start_idx:end_idx].strip()
            elif '```' in json_text:
                start_idx = json_text.find('```') + 3
                end_idx = json_text.rfind('```')
                if end_idx > start_idx:
                    json_text = json_text[start_idx:end_idx].strip()
            
            # Remove any leading/trailing non-JSON text
            json_start = json_text.find('{')
            json_end = json_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = json_text[json_start:json_end]
            
            print("Parsing extracted JSON...")
            
            # Parse JSON with better error handling
            try:
                extracted_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Problematic JSON text: {json_text[:500]}...")
                return None
            
            # Validate required fields
            if not self._validate_extracted_data(extracted_data):
                print("Warning: Extracted data validation failed")
                return None
            
            # Convert to structured dataclass
            return self._dict_to_dataclass(extracted_data)
            
        except Exception as e:
            print(f"Error extracting data from image: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_from_text(self, invoice_text: str) -> Optional[GSTInvoiceData]:
        """Extract GST invoice data from text content"""
        try:
            if not invoice_text.strip():
                print("Error: Empty invoice text provided")
                return None
            
            # Create the prompt with text
            prompt = f"{self.create_extraction_prompt()}\n\nINVOICE TEXT:\n{invoice_text}"
            
            print("Processing text input...")
            
            # Generate content using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 4096,
                }
            )
            
            if not response.text:
                print("Error: Empty response from Gemini API")
                return None
            
            # Parse the JSON response
            json_text = response.text.strip()
            
            # Clean the response if it contains markdown formatting
            if '```json' in json_text:
                start_idx = json_text.find('```json') + 7
                end_idx = json_text.rfind('```')
                if end_idx > start_idx:
                    json_text = json_text[start_idx:end_idx].strip()
            elif '```' in json_text:
                start_idx = json_text.find('```') + 3
                end_idx = json_text.rfind('```')
                if end_idx > start_idx:
                    json_text = json_text[start_idx:end_idx].strip()
            
            # Remove any leading/trailing non-JSON text
            json_start = json_text.find('{')
            json_end = json_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = json_text[json_start:json_end]
            
            # Parse JSON
            try:
                extracted_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Problematic JSON text: {json_text[:500]}...")
                return None
            
            # Validate required fields
            if not self._validate_extracted_data(extracted_data):
                print("Warning: Extracted data validation failed")
                return None
            
            # Convert to structured dataclass
            return self._dict_to_dataclass(extracted_data)
            
        except Exception as e:
            print(f"Error extracting data from text: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validate_extracted_data(self, data: Dict) -> bool:
        """Validate extracted data structure"""
        try:
            required_keys = [
                'supplier_details', 'recipient_details', 'invoice_details',
                'items', 'total_values', 'additional_notes'
            ]
            
            for key in required_keys:
                if key not in data:
                    print(f"Missing required key: {key}")
                    return False
            
            # Validate that items is a list
            if not isinstance(data['items'], list):
                print("Items field must be a list")
                return False
            
            # If items list is empty, add a default empty item
            if len(data['items']) == 0:
                data['items'] = [{
                    "description": "No items found",
                    "quantity": 0.0,
                    "rate": 0.0,
                    "taxable_value": 0.0,
                    "hsn_sac_code": "",
                    "cgst_rate": 0.0,
                    "cgst_amount": 0.0,
                    "sgst_rate": 0.0,
                    "sgst_amount": 0.0,
                    "igst_rate": 0.0,
                    "igst_amount": 0.0
                }]
            
            return True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False
    
    def _dict_to_dataclass(self, data: Dict) -> GSTInvoiceData:
        """Convert dictionary to GSTInvoiceData dataclass with error handling"""
        try:
            # Helper function to safely get values with defaults
            def safe_get(d, key, default=""):
                return d.get(key, default) if d.get(key) is not None else default
            
            def safe_get_float(d, key, default=0.0):
                try:
                    value = d.get(key, default)
                    return float(value) if value is not None else default
                except (ValueError, TypeError):
                    return default
            
            # Create supplier details with safe defaults
            supplier_data = data.get('supplier_details', {})
            supplier = SupplierDetails(
                name=safe_get(supplier_data, 'name'),
                gstin=safe_get(supplier_data, 'gstin'),
                address=safe_get(supplier_data, 'address')
            )
            
            # Create recipient details with safe defaults
            recipient_data = data.get('recipient_details', {})
            recipient = RecipientDetails(
                name=safe_get(recipient_data, 'name'),
                gstin=safe_get(recipient_data, 'gstin'),
                address=safe_get(recipient_data, 'address')
            )
            
            # Create invoice details with safe defaults
            invoice_data = data.get('invoice_details', {})
            invoice = InvoiceDetails(
                invoice_number=safe_get(invoice_data, 'invoice_number'),
                date=safe_get(invoice_data, 'date'),
                place_of_supply=safe_get(invoice_data, 'place_of_supply'),
                terms=safe_get(invoice_data, 'terms')
            )
            
            # Create items list with safe defaults
            items = []
            for item_data in data.get('items', []):
                item = ItemDetails(
                    description=safe_get(item_data, 'description'),
                    quantity=safe_get_float(item_data, 'quantity'),
                    rate=safe_get_float(item_data, 'rate'),
                    taxable_value=safe_get_float(item_data, 'taxable_value'),
                    hsn_sac_code=safe_get(item_data, 'hsn_sac_code'),
                    cgst_rate=safe_get_float(item_data, 'cgst_rate'),
                    cgst_amount=safe_get_float(item_data, 'cgst_amount'),
                    sgst_rate=safe_get_float(item_data, 'sgst_rate'),
                    sgst_amount=safe_get_float(item_data, 'sgst_amount'),
                    igst_rate=safe_get_float(item_data, 'igst_rate'),
                    igst_amount=safe_get_float(item_data, 'igst_amount')
                )
                items.append(item)
            
            # Create total values with safe defaults
            total_data = data.get('total_values', {})
            totals = TotalValues(
                subtotal=safe_get_float(total_data, 'subtotal'),
                cgst_total=safe_get_float(total_data, 'cgst_total'),
                sgst_total=safe_get_float(total_data, 'sgst_total'),
                igst_total=safe_get_float(total_data, 'igst_total'),
                total_invoice_value_numbers=safe_get_float(total_data, 'total_invoice_value_numbers'),
                total_invoice_value_words=safe_get(total_data, 'total_invoice_value_words')
            )
            
            # Create additional notes with safe defaults
            notes_data = data.get('additional_notes', {})
            notes = AdditionalNotes(
                signature=safe_get(notes_data, 'signature'),
                bank_details=safe_get(notes_data, 'bank_details'),
                other_notes=safe_get(notes_data, 'other_notes')
            )
            
            return GSTInvoiceData(
                supplier_details=supplier,
                recipient_details=recipient,
                invoice_details=invoice,
                items=items,
                total_values=totals,
                additional_notes=notes
            )
            
        except Exception as e:
            print(f"Error converting dictionary to dataclass: {str(e)}")
            raise
    
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
    try:
        extractor = GSTInvoiceExtractor()
        print("GST Invoice Data Extractor initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize extractor: {str(e)}")
        return
    
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