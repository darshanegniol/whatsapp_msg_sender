import streamlit as st
import pandas as pd
import requests
import configparser
import os
import base64

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

# Send WhatsApp text message
def send_wa_text(to, message):
    data = {
        'token': config['whatsapp']['ultramsg_token'],
        'to': to,
        'body': message
    }
    response = requests.post(
        config['whatsapp']['ultramsg_chat_endpoint'],
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return response.status_code == 200, response.text

# Send WhatsApp image
def send_wa_image(to, base64_image, filename):
    data = {
        'token': config['whatsapp']['ultramsg_token'],
        'to': to,
        'filename': filename,
        'image': base64_image
    }
    response = requests.post(
        config['whatsapp']['ultramsg_image_endpoint'],
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    return response.status_code == 200, response.text

# Send WhatsApp image with caption
def send_wa_image_with_caption(to, base64_image, filename, caption):
    data = {
        'token': config['whatsapp']['ultramsg_token'],
        'to': to,
        'filename': filename,
        'image': base64_image,
        'caption': caption
    }
    response = requests.post(
        config['whatsapp']['ultramsg_image_endpoint'],
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
                # Optionally prepend country code (e.g., +91 for India)
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
    base64_image = None
    filename = None

    # Prepare image if provided
    if image_file is not None:
        filename = image_file.name
        if filename.lower().endswith(image_extensions):
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            st.error("❌ Unsupported image format. Please use PNG, JPG, JPEG, GIF, or BMP.")
            return False, []

    # Send messages to each phone number
    for number in phone_numbers:
        try:
            if message and base64_image:  # Both text and image
                success, response_text = send_wa_image_with_caption(number, base64_image, filename, message)
            elif message:  # Only text
                success, response_text = send_wa_text(number, message)
            elif base64_image:  # Only image
                success, response_text = send_wa_image(number, base64_image, filename)
            else:
                st.error("❌ No message or image provided.")
                return False, []

            if success:
                results.append(f"✅ Sent to {number}")
            else:
                results.append(f"❌ Failed to send to {number}: {response_text}")
        except Exception as e:
            results.append(f"❌ Error sending to {number}: {e}")

    return True, results

# Streamlit UI
def main():
    st.title("WhatsApp Messaging App")
    st.write("Upload a CSV file with a 'contacts' column, enter a text message, and/or upload an image to send via WhatsApp.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV file with phone numbers", type=["csv"])

    # Text input for message
    default_message = """ clear first then type your message here..."""
    message = st.text_area("Enter your message", value=default_message, height=200)

    # File uploader for image
    image_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg", "gif", "bmp"])

    # Send button
    if st.button("Send Messages"):
        if csv_file is None:
            st.error("❌ Please upload a CSV file.")
            return

        with st.spinner("Sending messages..."):
            success, results = send_messages(csv_file, message.strip() if message.strip() else None, image_file)
            if success:
                st.success("Messages processed!")
                for result in results:
                    st.write(result)
            else:
                st.error("Failed to process messages. Check the error messages above.")

if __name__ == "__main__":
    main()