import streamlit as st
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
import mimetypes
from io import StringIO

PHONE = "contact"

# Load environment variables from .env file
load_dotenv()

# Access environment variables
ULTRAMSG_TOKEN = os.getenv('ULTRAMSG_TOKEN')
ULTRAMSG_INSTANCE_ID = os.getenv('ULTRAMSG_INSTANCE_ID')
ULTRAMSG_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages" if ULTRAMSG_INSTANCE_ID else None
ULTRAMSG_MEDIA_UPLOAD_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/media/upload" if ULTRAMSG_INSTANCE_ID else None

def format_phone_number(phone):
    try:
        # Handle None or NaN
        if pd.isna(phone) or phone is None:
            return None
        # Convert to string, remove whitespace and special characters
        phone = str(phone).strip()
        # Keep only digits
        phone = ''.join(filter(str.isdigit, phone))
        # Remove leading zeros
        phone = phone.lstrip('0')
        # Remove country code if present (e.g., +91 or 91)
        if phone.startswith('91') and len(phone) >= 12:
            phone = phone[2:]
        elif phone.startswith('+91') and len(phone) >= 13:
            phone = phone[3:]
        # Validate length (10 digits for Indian numbers)
        if len(phone) == 10:
            return f"+91{phone}"
        return None
    except Exception:
        return None

def get_mime_type(filename):
    """Determine MIME type based on file extension."""
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        # Default MIME types for common extensions
        extension = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.csv': 'text/csv',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }
        mime_type = mime_types.get(extension, 'application/octet-stream')
    return mime_type

# Upload file to UltraMsg and get URL
def upload_file_to_ultramsg(file, file_type):
    try:
        filename = file.name
        mime_type = get_mime_type(filename)
        # Reset file pointer to start
        file.seek(0)
        files = {
            'file': (filename, file.read(), mime_type)
        }
        params = {
            'token': ULTRAMSG_TOKEN,
            'type': file_type,
            'filename': filename
        }
        response = requests.post(
            ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
            files=files,
            params=params
        )
        
        # Log the full response for debugging (not displayed in UI)
        response_info = {
            "status_code": response.status_code,
            "response_text": response.text,
            "response_json": response.json() if response.headers.get('content-type', '').startswith('application/json') else "Not JSON",
            "endpoint_used": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
            "request_params": params,
            "request_files": {key: value[0] for key, value in files.items()}
        }
        
        if response.status_code == 200:
            response_data = response.json()
            file_url = response_data.get('url') or response_data.get('success')
            if file_url and isinstance(file_url, str) and file_url.startswith('http'):
                return True, file_url, filename, response_info
            return False, f"No valid URL in response. Expected 'url' or 'success' key, got: {response_data}", filename, response_info
        return False, f"API error: {response.text}", filename, response_info
    except Exception as e:
        response_info = {
            "error": str(e),
            "endpoint_used": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
            "request_params": params,
            "request_files": {key: value[0] for key, value in files.items()}
        }
        return False, str(e), filename, response_info

# Send WhatsApp message using UltraMsg API
def send_wa_message(to, message=None, image_url=None, document_url=None, document_filename=None):
    # Validate inputs
    if not to:
        return False, "Missing required parameter: recipient phone number", None
    if not ULTRAMSG_TOKEN or not ULTRAMSG_INSTANCE_ID:
        return False, "Missing required parameters: UltraMsg token or instance ID", None
    if not message and not image_url and not document_url:
        return False, "Missing required content: message, image, or document", None

    # Determine message type and endpoint
    if image_url:
        endpoint = f"{ULTRAMSG_ENDPOINT}/image"
        data = {
            'token': ULTRAMSG_TOKEN,
            'to': to,
            'image': image_url
        }
        if message:
            data['caption'] = message
    elif document_url:
        endpoint = f"{ULTRAMSG_ENDPOINT}/document"
        data = {
            'token': ULTRAMSG_TOKEN,
            'to': to,
            'document': document_url,
            'filename': document_filename
        }
        if message:
            data['caption'] = message
    else:
        endpoint = f"{ULTRAMSG_ENDPOINT}/chat"
        data = {
            'token': ULTRAMSG_TOKEN,
            'to': to,
            'body': message
        }

    try:
        response = requests.post(
            endpoint,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response_text = response.text
        # Parse response for specific error messages
        if response.status_code == 200:
            try:
                response_data = response.json()
                if response_data.get('sent') == 'true':
                    return True, "Message sent successfully", response_text
                else:
                    error_message = response_data.get('error', response_text)
                    return False, f"API error: {error_message}", response_text
            except ValueError:
                # Non-JSON response
                if "sent" in response_text.lower():
                    return True, "Message sent successfully", response_text
                return False, f"API error: {response_text}", response_text
        else:
            try:
                response_data = response.json()
                error_message = response_data.get('error', response_data.get('message', response_text))
                if "invalid phone number" in error_message.lower() or "recipient" in error_message.lower():
                    return False, "Invalid phone number", response_text
                elif "token" in error_message.lower() or "instance" in error_message.lower():
                    return False, "Invalid or missing token/instance ID", response_text
                elif "rate limit" in error_message.lower():
                    return False, "API rate limit exceeded", response_text
                else:
                    return False, f"API error: {error_message}", response_text
            except ValueError:
                return False, f"API error: {response_text}", response_text
    except Exception as e:
        return False, f"Network or API connection error: {str(e)}", str(e)

# Main function to send messages
def send_messages(csv_file, message, image_file, document_file):
    # Validate environment variables
    required_vars = {
        "ULTRAMSG_TOKEN": ULTRAMSG_TOKEN,
        "ULTRAMSG_INSTANCE_ID": ULTRAMSG_INSTANCE_ID,
        "ULTRAMSG_ENDPOINT": ULTRAMSG_ENDPOINT,
        "ULTRAMSG_MEDIA_UPLOAD_ENDPOINT": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT
    }
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}. Check your .env file.")
        return False, [], [], []

    try:
        df = pd.read_csv(csv_file, encoding='utf-8', dtype=str, na_filter=False)
        if PHONE not in df.columns:
            st.error("CSV must contain a 'contact' column.")
            return False, [], [], []
        
        # Format phone numbers
        phone_numbers = []
        invalid_numbers = []
        for phone in df[PHONE]:
            if not phone or pd.isna(phone) or phone.strip() == "":
                continue
            formatted = format_phone_number(phone)
            if formatted:
                if formatted not in phone_numbers:
                    phone_numbers.append(formatted)
            else:
                invalid_numbers.append(phone)

        if invalid_numbers:
            st.error(f"Invalid phone numbers found: {', '.join(invalid_numbers)}")
        
        if not phone_numbers:
            st.error("No valid phone numbers found in CSV.")
            return False, [], [], []
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return False, [], [], []

    successful_numbers = []
    failed_numbers = []
    image_url = None
    document_url = None
    document_filename = None

    # Upload image to UltraMsg if provided (only once)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    if image_file:
        filename = image_file.name
        if filename.lower().endswith(image_extensions):
            # Reset file pointer to start
            image_file.seek(0)
            success, result, _, response_info = upload_file_to_ultramsg(image_file, 'image')
            if success:
                image_url = result
            else:
                st.error(f"Failed to upload image: {result}")
                return False, [], [], []
        else:
            st.error("Unsupported image format. Use PNG, JPG, JPEG, GIF, or BMP.")
            return False, [], [], []

    # Upload document to UltraMsg if provided (only once)
    if document_file:
        document_filename = document_file.name
        success, result, filename, response_info = upload_file_to_ultramsg(document_file, 'document')
        if success:
            document_url = result
            document_filename = filename  # Ensure original filename is used
        else:
            st.error(f"Failed to upload document: {result}")
            return False, [], [], []

    # Validate message content
    message_content = message.strip() if message else ""
    if not message_content and not image_url and not document_url:
        st.error("No valid message, image, or document provided.")
        return False, [], [], []

    # Send messages to each phone number
    for number in phone_numbers:
        try:
            success, error_message, response_text = send_wa_message(number, message_content, image_url, document_url, document_filename)
            if success:
                st.success(f"Message sent successfully to {number}")
                successful_numbers.append(number)
            else:
                st.error(f"Failed to send message to {number}. Reason: {error_message}")
                failed_numbers.append(number)
        except Exception as e:
            st.error(f"Failed to send message to {number}. Reason: Unexpected error: {str(e)}")
            failed_numbers.append(number)

    # Display summary
    total_numbers = len(phone_numbers)
    successful_count = len(successful_numbers)
    failed_count = len(failed_numbers)
    st.subheader("Message Sending Summary")
    st.write(f"Total numbers processed: {total_numbers}")
    st.write(f"Messages sent successfully: {successful_count}")
    st.write(f"Messages failed to send: {failed_count}")

    return True, successful_numbers, failed_numbers, []

# Streamlit UI
def main():
    st.title("WhatsApp Messaging App")
    st.write("Upload a CSV file with a 'contact' column of phone numbers. Send text, image, document (in its original format, e.g., CSV, PDF), or any combination.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV file", type=["csv"])

    # Text input with placeholder
    message = st.text_area("Message (optional)", placeholder="Enter your message here", height=200)

    # File uploader for image
    image_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"], accept_multiple_files=False)

    # File uploader for document - Allow all files
    document_file = st.file_uploader("Upload document (optional, sent in original format)", type=None, accept_multiple_files=False)

    # Send button
    if st.button("Send Messages"):
        if csv_file is None:
            st.error("Please upload a CSV file.")
            return

        success, successful_numbers, failed_numbers, _ = send_messages(csv_file, message, image_file, document_file)
        if success:
            st.success("All messages processed!")
            
            # Provide downloadable CSV files
            if successful_numbers:
                successful_df = pd.DataFrame(successful_numbers, columns=["Phone Number"])
                successful_csv = successful_df.to_csv(index=False)
                st.download_button(
                    label="Download Successful Numbers",
                    data=successful_csv,
                    file_name="successful_numbers.csv",
                    mime="text/csv"
                )
            if failed_numbers:
                failed_df = pd.DataFrame(failed_numbers, columns=["Phone Number"])
                failed_csv = failed_df.to_csv(index=False)
                st.download_button(
                    label="Download Failed Numbers",
                    data=failed_csv,
                    file_name="failed_numbers.csv",
                    mime="text/csv"
                )
        else:
            st.error("Failed to process messages. Check errors above.")

if __name__ == "__main__":
    main()