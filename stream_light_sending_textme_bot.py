# import streamlit as st
# import pandas as pd
# import requests
# import os
# import json
# from dotenv import load_dotenv
# import time
# import mimetypes
# from io import StringIO

# PHONE = "contact"

# # Load environment variables from .env file
# load_dotenv()

# # Access environment variables
# TEXTMEBOT_APIKEY = os.getenv('TEXTMEBOT_APIKEY')
# TEXTMEBOT_ENDPOINT = os.getenv('TEXTMEBOT_ENDPOINT') or "https://api.textmebot.com/send.php"
# ULTRAMSG_TOKEN = os.getenv('ULTRAMSG_TOKEN')
# ULTRAMSG_INSTANCE_ID = os.getenv('ULTRAMSG_INSTANCE_ID')
# ULTRAMSG_MEDIA_UPLOAD_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/media/upload" if ULTRAMSG_INSTANCE_ID else None
# ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/media/upload" if ULTRAMSG_INSTANCE_ID else None

# def format_phone_number(phone):
#     try:
#         # Handle None or NaN
#         if pd.isna(phone) or phone is None:
#             return None
#         # Convert to string, remove whitespace and special characters
#         phone = str(phone).strip()
#         # Keep only digits
#         phone = ''.join(filter(str.isdigit, phone))
#         # Remove leading zeros
#         phone = phone.lstrip('0')
#         # Remove country code if present (e.g., +91 or 91)
#         if phone.startswith('91') and len(phone) >= 12:
#             phone = phone[2:]
#         elif phone.startswith('+91') and len(phone) >= 13:
#             phone = phone[3:]
#         # Validate length (10 digits for Indian numbers)
#         if len(phone) == 10:
#             return phone
#         return None
#     except Exception:
#         return None

# def get_mime_type(filename):
#     """Determine MIME type based on file extension."""
#     mime_type, _ = mimetypes.guess_type(filename)
#     if not mime_type:
#         # Default MIME types for common extensions
#         extension = os.path.splitext(filename)[1].lower()
#         mime_types = {
#             '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#             '.xls': 'application/vnd.ms-excel',
#             '.csv': 'text/csv',
#             '.pdf': 'application/pdf',
#             '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
#             '.png': 'image/png',
#             '.jpg': 'image/jpeg',
#             '.jpeg': 'image/jpeg',
#             '.gif': 'image/gif',
#             '.bmp': 'image/bmp'
#         }
#         mime_type = mime_types.get(extension, 'application/octet-stream')
#     return mime_type

# # Upload image to Ultramsg and get URL
# def upload_image_to_ultramsg(image_file):
#     try:
#         filename = image_file.name
#         mime_type = get_mime_type(filename)
#         files = {
#             'file': (filename, image_file.read(), mime_type)
#         }
#         params = {
#             'token': ULTRAMSG_TOKEN,
#             'type': 'image',
#             'filename': filename
#         }
#         response = requests.post(
#             ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
#             files=files,
#             params=params
#         )
        
#         # Log the full response for debugging (not displayed in UI)
#         response_info = {
#             "status_code": response.status_code,
#             "response_text": response.text,
#             "response_json": response.json() if response.headers.get('content-type', '').startswith('application/json') else "Not JSON",
#             "endpoint_used": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
#             "request_params": params,
#             "request_files": {key: value[0] for key, value in files.items()}
#         }
        
#         if response.status_code == 200:
#             response_data = response.json()
#             image_url = response_data.get('success') or response_data.get('url')
#             if image_url and isinstance(image_url, str) and image_url.startswith('http'):
#                 return True, image_url, response_info
#             return False, f"No valid URL in response. Expected 'success' or 'url' key, got: {response_data}", response_info
#         return False, f"API error: {response.text}", response_info
#     except Exception as e:
#         response_info = {
#             "error": str(e),
#             "endpoint_used": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
#             "request_params": params,
#             "request_files": {key: value[0] for key, value in files.items()}
#         }
#         return False, str(e), response_info

# # Upload document to Ultramsg and get URL
# def upload_document_to_ultramsg(document_file):
#     try:
#         filename = document_file.name
#         mime_type = get_mime_type(filename)
#         files = {
#             'file': (filename, document_file.read(), mime_type)
#         }
#         params = {
#             'token': ULTRAMSG_TOKEN,
#             'type': 'document',
#             'filename': filename
#         }
#         response = requests.post(
#             ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
#             files=files,
#             params=params
#         )
        
#         # Log the full response for debugging (not displayed in UI)
#         response_info = {
#             "status_code": response.status_code,
#             "response_text": response.text,
#             "response_json": response.json() if response.headers.get('content-type', '').startswith('application/json') else "Not JSON",
#             "endpoint_used": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
#             "request_params": params,
#             "request_files": {key: value[0] for key, value in files.items()}
#         }
        
#         if response.status_code == 200:
#             response_data = response.json()
#             document_url = response_data.get('success') or response_data.get('url')
#             if document_url and isinstance(document_url, str) and document_url.startswith('http'):
#                 return True, document_url, response_info
#             return False, f"No valid URL in response. Expected 'success' or 'url' key, got: {response_data}", response_info
#         return False, f"API error: {response.text}", response_info
#     except Exception as e:
#         response_info = {
#             "error": str(e),
#             "endpoint_used": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
#             "request_params": params,
#             "request_files": {key: value[0] for key, value in files.items()}
#         }
#         return False, str(e), response_info

# # Send WhatsApp message using TextMeBot API
# def send_wa_message(to, message=None, image_url=None, document_url=None, document_filename=None):
#     data = {
#         'recipient': to,
#         'apikey': TEXTMEBOT_APIKEY,
#     }
#     if message:
#         data['text'] = message
#     if image_url:
#         data['file'] = image_url
#     if document_url:
#         data['document'] = document_url
#         if document_filename:
#             data['filename'] = document_filename
    
#     try:
#         response = requests.post(
#             TEXTMEBOT_ENDPOINT,
#             data=data,
#             headers={'Content-Type': 'application/x-www-form-urlencoded'}
#         )
#         return response.status_code == 200 and "Success" in response.text, response.text
#     except Exception as e:
#         return False, str(e)

# # Main function to send messages
# def send_messages(csv_file, message, image_file, document_file):
#     # Validate environment variables
#     required_vars = {
#         "TEXTMEBOT_APIKEY": TEXTMEBOT_APIKEY,
#         "TEXTMEBOT_ENDPOINT": TEXTMEBOT_ENDPOINT,
#         "ULTRAMSG_TOKEN": ULTRAMSG_TOKEN,
#         "ULTRAMSG_INSTANCE_ID": ULTRAMSG_INSTANCE_ID,
#         "ULTRAMSG_MEDIA_UPLOAD_ENDPOINT": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
#         "ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT
#     }
#     missing_vars = [key for key, value in required_vars.items() if not value]
#     if missing_vars:
#         st.error(f"Missing environment variables: {', '.join(missing_vars)}. Check your .env file.")
#         return False, [], [], []

#     try:
#         df = pd.read_csv(csv_file, encoding='utf-8', dtype=str, na_filter=False)
#         if PHONE not in df.columns:
#             st.error("CSV must contain a 'contact' column.")
#             return False, [], [], []
        
#         # Format phone numbers
#         phone_numbers = []
#         for phone in df[PHONE]:
#             if not phone or pd.isna(phone) or phone.strip() == "":
#                 continue
#             formatted = format_phone_number(phone)
#             if formatted:
#                 formatted = f"+91{formatted}"
#                 if formatted not in phone_numbers:
#                     phone_numbers.append(formatted)

#         if not phone_numbers:
#             st.error("No valid phone numbers found in CSV.")
#             return False, [], [], []
#     except Exception as e:
#         st.error(f"Error reading CSV: {e}")
#         return False, [], [], []

#     successful_numbers = []
#     failed_numbers = []
#     image_url = None
#     document_url = None
#     document_filename = None

#     # Upload image to Ultramsg if provided
#     image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
#     if image_file:
#         filename = image_file.name
#         if filename.lower().endswith(image_extensions):
#             success, result, response_info = upload_image_to_ultramsg(image_file)
#             if success:
#                 image_url = result
#             else:
#                 st.error(f"Failed to upload image: {result}")
#                 return False, [], [], []
#         else:
#             st.error("Unsupported image format. Use PNG, JPG, JPEG, GIF, or BMP.")
#             return False, [], [], []

#     # Upload document to Ultramsg if provided
#     if document_file:
#         document_filename = document_file.name
#         success, result, response_info = upload_document_to_ultramsg(document_file)
#         if success:
#             document_url = result
#         else:
#             st.error(f"Failed to upload document: {result}")
#             return False, [], [], []

#     # Validate message content
#     message_content = message.strip() if message else ""
#     if not message_content and not image_url and not document_url:
#         st.error("No valid message, image, or document provided.")
#         return False, [], [], []

#     # Send messages to each phone number with 7-second delay
#     for index, number in enumerate(phone_numbers):
#         try:
#             success, response_text = send_wa_message(number, message_content, image_url, document_url, document_filename)
#             if success:
#                 st.success(f"Message sent successfully to {number}")
#                 successful_numbers.append(number)
#             else:
#                 st.error(f"Failed to send message to {number}")
#                 failed_numbers.append(number)
#             # Add 7-second delay with message
#             if index < len(phone_numbers) - 1:  # Skip delay after last contact
#                 with st.spinner("Waiting 7 seconds before sending to the next contact..."):
#                     time.sleep(7)
#         except Exception as e:
#             st.error(f"Failed to send message to {number}")
#             failed_numbers.append(number)
#             if index < len(phone_numbers) - 1:
#                 with st.spinner("Waiting 7 seconds before sending to the next contact..."):
#                     time.sleep(7)

#     # Display summary
#     total_numbers = len(phone_numbers)
#     successful_count = len(successful_numbers)
#     failed_count = len(failed_numbers)
#     st.subheader("Message Sending Summary")
#     st.write(f"Total numbers processed: {total_numbers}")
#     st.write(f"Messages sent successfully: {successful_count}")
#     st.write(f"Messages failed to send: {failed_count}")

#     return True, successful_numbers, failed_numbers, []

# # Streamlit UI
# def main():
#     st.title("WhatsApp Messaging App")
#     st.write("Upload a CSV file with a 'contact' column of phone numbers. Send text, image, document (any file type), or any combination with a 7-second delay between each.")

#     # File uploader for CSV
#     csv_file = st.file_uploader("Upload CSV file", type=["csv"])

#     # Text input with placeholder
#     message = st.text_area("Message (optional)", placeholder="Enter your message here", height=200)

#     # File uploader for image
#     image_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"], accept_multiple_files=False)

#     # File uploader for document - Allow all files
#     document_file = st.file_uploader("Upload document (optional)", type=None, accept_multiple_files=False)

#     # Send button
#     if st.button("Send Messages"):
#         if csv_file is None:
#             st.error("Please upload a CSV file.")
#             return

#         success, successful_numbers, failed_numbers, _ = send_messages(csv_file, message, image_file, document_file)
#         if success:
#             st.success("All messages processed!")
            
#             # Provide downloadable CSV files
#             if successful_numbers:
#                 successful_df = pd.DataFrame(successful_numbers, columns=["Phone Number"])
#                 successful_csv = successful_df.to_csv(index=False)
#                 st.download_button(
#                     label="Download Successful Numbers",
#                     data=successful_csv,
#                     file_name="successful_numbers.csv",
#                     mime="text/csv"
#                 )
#             if failed_numbers:
#                 failed_df = pd.DataFrame(failed_numbers, columns=["Phone Number"])
#                 failed_csv = failed_df.to_csv(index=False)
#                 st.download_button(
#                     label="Download Failed Numbers",
#                     data=failed_csv,
#                     file_name="failed_numbers.csv",
#                     mime="text/csv"
#                 )
#         else:
#             st.error("Failed to process messages. Check errors above.")

# if __name__ == "__main__":
#     main()




import streamlit as st
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
import time
import mimetypes
from io import StringIO

PHONE = "contact"

# Load environment variables from .env file
load_dotenv()

# Access environment variables
TEXTMEBOT_APIKEY = os.getenv('TEXTMEBOT_APIKEY')
TEXTMEBOT_ENDPOINT = os.getenv('TEXTMEBOT_ENDPOINT') or "https://api.textmebot.com/send.php"
ULTRAMSG_TOKEN = os.getenv('ULTRAMSG_TOKEN')
ULTRAMSG_INSTANCE_ID = os.getenv('ULTRAMSG_INSTANCE_ID')
ULTRAMSG_MEDIA_UPLOAD_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/media/upload" if ULTRAMSG_INSTANCE_ID else None
ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/media/upload" if ULTRAMSG_INSTANCE_ID else None

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
            return phone
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

# Upload image to Ultramsg and get URL
def upload_image_to_ultramsg(image_file):
    try:
        filename = image_file.name
        mime_type = get_mime_type(filename)
        files = {
            'file': (filename, image_file.read(), mime_type)
        }
        params = {
            'token': ULTRAMSG_TOKEN,
            'type': 'image',
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
            image_url = response_data.get('success') or response_data.get('url')
            if image_url and isinstance(image_url, str) and image_url.startswith('http'):
                return True, image_url, response_info
            return False, f"No valid URL in response. Expected 'success' or 'url' key, got: {response_data}", response_info
        return False, f"API error: {response.text}", response_info
    except Exception as e:
        response_info = {
            "error": str(e),
            "endpoint_used": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
            "request_params": params,
            "request_files": {key: value[0] for key, value in files.items()}
        }
        return False, str(e), response_info

# Upload document to Ultramsg and get URL
def upload_document_to_ultramsg(document_file):
    try:
        filename = document_file.name
        mime_type = get_mime_type(filename)
        files = {
            'file': (filename, document_file.read(), mime_type)
        }
        params = {
            'token': ULTRAMSG_TOKEN,
            'type': 'document',
            'filename': filename
        }
        response = requests.post(
            ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
            files=files,
            params=params
        )
        
        # Log the full response for debugging (not displayed in UI)
        response_info = {
            "status_code": response.status_code,
            "response_text": response.text,
            "response_json": response.json() if response.headers.get('content-type', '').startswith('application/json') else "Not JSON",
            "endpoint_used": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
            "request_params": params,
            "request_files": {key: value[0] for key, value in files.items()}
        }
        
        if response.status_code == 200:
            response_data = response.json()
            document_url = response_data.get('success') or response_data.get('url')
            if document_url and isinstance(document_url, str) and document_url.startswith('http'):
                return True, document_url, response_info
            return False, f"No valid URL in response. Expected 'success' or 'url' key, got: {response_data}", response_info
        return False, f"API error: {response.text}", response_info
    except Exception as e:
        response_info = {
            "error": str(e),
            "endpoint_used": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT,
            "request_params": params,
            "request_files": {key: value[0] for key, value in files.items()}
        }
        return False, str(e), response_info

# Send WhatsApp message using TextMeBot API
def send_wa_message(to, message=None, image_url=None, document_url=None, document_filename=None):
    # Validate inputs
    if not to:
        return False, "Missing required parameter: recipient phone number", None
    if not TEXTMEBOT_APIKEY:
        return False, "Missing required parameter: API key", None
    if not message and not image_url and not document_url:
        return False, "Missing required content: message, image, or document", None

    data = {
        'recipient': to,
        'apikey': TEXTMEBOT_APIKEY,
    }
    if message:
        data['text'] = message
    if image_url:
        data['file'] = image_url
    if document_url:
        data['document'] = document_url
        if document_filename:
            data['filename'] = document_filename
    
    try:
        response = requests.post(
            TEXTMEBOT_ENDPOINT,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response_text = response.text
        # Parse response to provide specific error messages
        if response.status_code == 200 and "Success" in response_text:
            return True, "Message sent successfully", response_text
        else:
            # Try to parse JSON response for specific errors
            try:
                response_data = response.json()
                error_message = response_data.get('error', response_data.get('message', response_text))
                if "invalid phone number" in error_message.lower() or "recipient" in error_message.lower():
                    return False, "Invalid phone number", response_text
                elif "api key" in error_message.lower():
                    return False, "Invalid or missing API key", response_text
                elif "rate limit" in error_message.lower():
                    return False, "API rate limit exceeded", response_text
                elif "parameter" in error_message.lower():
                    return False, f"Missing or invalid parameter: {error_message}", response_text
                else:
                    return False, f"API error: {error_message}", response_text
            except ValueError:
                # Non-JSON response
                if "invalid phone number" in response_text.lower():
                    return False, "Invalid phone number", response_text
                elif "api key" in response_text.lower():
                    return False, "Invalid or missing API key", response_text
                elif "rate limit" in response_text.lower():
                    return False, "API rate limit exceeded", response_text
                else:
                    return False, f"API error: {response_text}", response_text
    except Exception as e:
        return False, f"Network or API connection error: {str(e)}", str(e)

# Main function to send messages
def send_messages(csv_file, message, image_file, document_file):
    # Validate environment variables
    required_vars = {
        "TEXTMEBOT_APIKEY": TEXTMEBOT_APIKEY,
        "TEXTMEBOT_ENDPOINT": TEXTMEBOT_ENDPOINT,
        "ULTRAMSG_TOKEN": ULTRAMSG_TOKEN,
        "ULTRAMSG_INSTANCE_ID": ULTRAMSG_INSTANCE_ID,
        "ULTRAMSG_MEDIA_UPLOAD_ENDPOINT": ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
        "ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT": ULTRAMSG_DOCUMENT_UPLOAD_ENDPOINT
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
                formatted = f"+91{formatted}"
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

    # Upload image to Ultramsg if provided (only once)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    if image_file:
        filename = image_file.name
        if filename.lower().endswith(image_extensions):
            # Reset file pointer to start if it's a BytesIO object
            image_file.seek(0)
            success, result, response_info = upload_image_to_ultramsg(image_file)
            if success:
                image_url = result
            else:
                st.error(f"Failed to upload image: {result}")
                return False, [], [], []
        else:
            st.error("Unsupported image format. Use PNG, JPG, JPEG, GIF, or BMP.")
            return False, [], [], []

    # Upload document to Ultramsg if provided (only once)
    if document_file:
        document_filename = document_file.name
        # Reset file pointer to start if it's a BytesIO object
        document_file.seek(0)
        success, result, response_info = upload_document_to_ultramsg(document_file)
        if success:
            document_url = result
        else:
            st.error(f"Failed to upload document: {result}")
            return False, [], [], []

    # Validate message content
    message_content = message.strip() if message else ""
    if not message_content and not image_url and not document_url:
        st.error("No valid message, image, or document provided.")
        return False, [], [], []

    # Send messages to each phone number with 7-second delay
    for index, number in enumerate(phone_numbers):
        try:
            success, error_message, response_text = send_wa_message(number, message_content, image_url, document_url, document_filename)
            if success:
                st.success(f"Message sent successfully to {number}")
                successful_numbers.append(number)
            else:
                st.error(f"Failed to send message to {number}. Reason: {error_message}")
                failed_numbers.append(number)
            # Add 7-second delay with message
            if index < len(phone_numbers) - 1:  # Skip delay after last contact
                with st.spinner("Waiting 7 seconds before sending to the next contact..."):
                    time.sleep(7)
        except Exception as e:
            st.error(f"Failed to send message to {number}. Reason: Unexpected error: {str(e)}")
            failed_numbers.append(number)
            if index < len(phone_numbers) - 1:
                with st.spinner("Waiting 7 seconds before sending to the next contact..."):
                    time.sleep(7)

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
    st.write("Upload a CSV file with a 'contact' column of phone numbers. Send text, image, document (any file type), or any combination with a 7-second delay between each.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV file", type=["csv"])

    # Text input with placeholder
    message = st.text_area("Message (optional)", placeholder="Enter your message here", height=200)

    # File uploader for image
    image_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"], accept_multiple_files=False)

    # File uploader for document - Allow all files
    document_file = st.file_uploader("Upload document (optional)", type=None, accept_multiple_files=False)

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