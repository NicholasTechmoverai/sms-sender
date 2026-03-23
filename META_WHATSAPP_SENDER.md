from pywa import WhatsApp
import pandas as pd

# Initialize client
wa = WhatsApp(
    phone_id="YOUR_PHONE_NUMBER_ID",
    token="YOUR_PERMANENT_ACCESS_TOKEN"
)

# Read contacts from CSV
def send_bulk_messages(csv_file: str, message: str):
    df = pd.read_csv(csv_file)
    
    for index, row in df.iterrows():
        phone = str(row['phone_number']).strip()
        name = row.get('name', 'Customer')
        
        try:
            # Send personalized message
            wa.send_message(
                to=phone,
                text=f"Hello {name}, {message}"
            )
            print(f"✓ Sent to {phone}")
        except Exception as e:
            print(f"✗ Failed to send to {phone}: {e}")

# Usage
send_bulk_messages('customers.csv', 'Your order is ready!')