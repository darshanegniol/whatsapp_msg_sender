import streamlit as st
import pandas as pd
import requests
import configparser
import os
import json

PHONE = "contacts"

# Load configuration
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

# Get base dir and config.ini
base_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(base_dir, 'config.ini')
config = load_config(config_file)

def format_phone_number(phone):
    # Convert to string and remove non-digits
    phone = ''.join(filter(str.isdigit, str(phone)))
    # Take the rightmost 10 digits
    if len(phone) >= 10:
        return phone[-10:]
    return None  # Return None for invalid numbers

# Upload image to Ultramsg and get URL
def upload_image_to_ultramsg(image_file):
    try:
        files = {
            'file': (image_file.name, image_file.read(), image_file.type),
            'token': (None, config['ultramsg']['token'])
        }
        response = requests.post(
            config['ultramsg']['ultramsg_media_upload_endpoint'],
            files=files
        )
        
        if response.status_code == 200:
            # Parse JSON response
            response_data = response.json()
            # Print the entire JSON response for debugging
            # print("Ultramsg API response:", json.dumps(response_data, indent=2))
            # Display in Streamlit UI
            st.write("**Ultramsg API response:**")
            st.json(response_data)
            
            image_url = response_data.get('success')  # Updated to use 'success' key
            if image_url:
                return True, image_url
            else:
                return False, "No image URL in response (missing 'success' field)"
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

# Send WhatsApp message using TextMe Bot API
def send_wa_message(to, message=None, image_url=None):
    data = {
        'recipient': to,
        'apikey': config['textmebot']['apikey'],
    }
    if message:
        data['text'] = message
    if image_url:
        data['file'] = image_url
    
    response = requests.post(
        config['textmebot']['endpoint'],
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return response.status_code == 200, response.text

# Main function to send messages
def send_messages(csv_file, message, image_file):
    try:
        df = pd.read_csv(csv_file)
        if PHONE not in df.columns:
            st.error(f"❌ CSV must contain a '{PHONE}' column.")
            return False, []
        # Format phone numbers to rightmost 10 digits
        phone_numbers = []
        for phone in df[PHONE]:
            formatted = format_phone_number(phone)
            if formatted:
                formatted = f"+91{formatted}"  # Adjust country code as needed
                phone_numbers.append(formatted)
            else:
                st.warning(f"⚠️ Skipped invalid phone number: {phone}")
        if not phone_numbers:
            st.error("❌ No valid phone numbers found in CSV.")
            return False, []
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        return False, []

    results = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_url = None

    # Upload image to Ultramsg if provided
    if image_file is not None:
        filename = image_file.name
        if filename.lower().endswith(image_extensions):
            with st.spinner("Uploading image to Ultramsg..."):
                success, result = upload_image_to_ultramsg(image_file)
                if success:
                    image_url = result
                    st.success(f"✅ Image uploaded successfully: {image_url}")
                else:
                    st.error(f"❌ Failed to upload image to Ultramsg: {result}")
                    return False, []
        else:
            st.error("❌ Unsupported image format. Please use PNG, JPG, JPEG, GIF, or BMP.")
            return False, []

    # Send messages to each phone number
    for number in phone_numbers:
        try:
            if message and message.strip() != "clear first then type your message here..." and image_url:  # Both text and image
                success, response_text = send_wa_message(number, message.strip(), image_url)
                action = "text and image"
            elif message and message.strip() != "clear first then type your message here...":  # Only text
                success, response_text = send_wa_message(number, message.strip())
                action = "text"
            elif image_url:  # Only image
                success, response_text = send_wa_message(number, image_url=image_url)
                action = "image"
            else:
                st.error("❌ No valid message or image provided.")
                return False, []

            if success:
                results.append(f"✅ Sent {action} to {number}")
            else:
                results.append(f"❌ Failed to send {action} to {number}: {response_text}")
        except Exception as e:
            results.append(f"❌ Error sending to {number}: {e}")

    return True, results

# Streamlit UI
def main():
    st.title("WhatsApp Messaging App (TextMe Bot with Ultramsg Image Upload)")
    st.write("Upload a CSV file with a 'contacts' column, enter a text message, and/or upload an image to send via WhatsApp. Images are uploaded via Ultramsg and sent via TextMe Bot.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV file with phone numbers", type=["csv"])

    # Text input for message
    default_message = "clear first then type your message here..."
    message = st.text_area("Enter your message (optional)", value=default_message, height=200)

    # File uploader for image
    image_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"])

    # Send button
    if st.button("Send Messages"):
        if csv_file is None:
            st.error("❌ Please upload a CSV file.")
            return

        with st.spinner("Processing messages..."):
            success, results = send_messages(csv_file, message, image_file)
            if success:
                st.success("Messages processed!")
                for result in results:
                    st.write(result)
            else:
                st.error("Failed to process messages. Check the error messages above.")

if __name__ == "__main__":
    main()