import streamlit as st
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
import time

PHONE = "contact"

# Load environment variables from .env file
load_dotenv()

# Access environment variables
TEXTMEBOT_APIKEY = os.getenv('TEXTMEBOT_APIKEY')
TEXTMEBOT_ENDPOINT = os.getenv('TEXTMEBOT_ENDPOINT')
ULTRAMSG_TOKEN = os.getenv('ULTRAMSG_TOKEN')
ULTRAMSG_MEDIA_UPLOAD_ENDPOINT = os.getenv('ULTRAMSG_MEDIA_UPLOAD_ENDPOINT')

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

# Upload image to Ultramsg and get URL
def upload_image_to_ultramsg(image_file):
    try:
        files = {
            'file': (image_file.name, image_file.read(), image_file.type),
            'token': (None, ULTRAMSG_TOKEN)
        }
        response = requests.post(
            ULTRAMSG_MEDIA_UPLOAD_ENDPOINT,
            files=files
        )
        
        if response.status_code == 200:
            response_data = response.json()
            image_url = response_data.get('success')
            if image_url:
                return True, image_url
            return False, "No image URL in response"
        return False, response.text
    except Exception as e:
        return False, str(e)

# Send WhatsApp message using TextMe Bot API
def send_wa_message(to, message=None, image_url=None):
    data = {
        'recipient': to,
        'apikey': TEXTMEBOT_APIKEY,
    }
    if message:
        data['text'] = message
    if image_url:
        data['file'] = image_url
    
    try:
        response = requests.post(
            TEXTMEBOT_ENDPOINT,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        return response.status_code == 200 and "Success" in response.text, response.text
    except Exception as e:
        return False, str(e)

# Main function to send messages
def send_messages(csv_file, message, image_file):
    # Validate environment variables
    if not all([TEXTMEBOT_APIKEY, TEXTMEBOT_ENDPOINT, ULTRAMSG_TOKEN, ULTRAMSG_MEDIA_UPLOAD_ENDPOINT]):
        st.error("Missing environment variables. Check your .env file.")
        return False, []

    try:
        df = pd.read_csv(csv_file, encoding='utf-8', dtype=str, na_filter=False)
        if PHONE not in df.columns:
            st.error("CSV must contain a 'contact' column.")
            return False, []
        
        # Format phone numbers
        phone_numbers = []
        for phone in df[PHONE]:
            if not phone or pd.isna(phone) or phone.strip() == "":
                continue
            formatted = format_phone_number(phone)
            if formatted:
                formatted = f"+91{formatted}"
                if formatted not in phone_numbers:
                    phone_numbers.append(formatted)

        if not phone_numbers:
            st.error("No valid phone numbers found in CSV.")
            return False, []
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return False, []

    results = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_url = None

    # Upload image to Ultramsg if provided
    if image_file:
        filename = image_file.name
        if filename.lower().endswith(image_extensions):
            success, result = upload_image_to_ultramsg(image_file)
            if success:
                image_url = result
            else:
                st.error(f"Failed to upload image to Ultramsg: {result}")
                return False, []
        else:
            st.error("Unsupported image format. Use PNG, JPG, JPEG, GIF, or BMP.")
            return False, []

    # Validate message content
    message_content = message.strip() if message else ""
    if not message_content and not image_url:
        st.error("No valid message or image provided.")
        return False, []

    # Send messages to each phone number with 7-second delay
    for number in phone_numbers:
        try:
            success, response_text = send_wa_message(number, message_content, image_url)
            if success:
                results.append(f"Message sent successfully to {number}")
                st.success(f"Message sent to {number}")
            else:
                results.append(f"Failed to send to {number}: {response_text}")
                st.error(f"Failed to send message to {number}")
            # Add 7-second of delay
            if number != phone_numbers[-1]:  # Skip delay after last contact
                time.sleep(7)
        except Exception as e:
            results.append(f"Error sending to {number}: {e}")
            st.error(f"Error sending to {number}")
            if number != phone_numbers[-1]:
                time.sleep(7)

    return True, results

# Streamlit UI
def main():
    st.title("WhatsApp Messaging App")
    st.write("Upload a CSV file with a 'contact' column of phone numbers. Messages (text, image, or both) will be sent to all valid contacts with a 7-second delay between each.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV file", type=["csv"])

    # Text input with placeholder
    message = st.text_area("Message (optional)", placeholder="Enter your message here", height=200)

    # File uploader for image
    image_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"])

    # Send button
    if st.button("Send Messages"):
        if csv_file is None:
            st.error("Please upload a CSV file.")
            return

        success, results = send_messages(csv_file, message, image_file)
        if success:
            st.success("All messages processed!")
        else:
            st.error("Failed to process messages. Check errors above.")

if __name__ == "__main__":
    main()