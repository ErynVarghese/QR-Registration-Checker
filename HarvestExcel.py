import os
from flask import Flask, request, render_template_string
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load Excel file (you can upload this to Render later)
def load_excel_data():
    # Read the Excel file (Excel file should be in the project directory or uploaded on Render)
    df = pd.read_excel("HarvestNew.xlsx")
    return df

@app.route('/')
def check_qr():
    qr_url = request.args.get('qr')  # Get the QR URL parameter from the query string
    if not qr_url:
        return 'QR URL is required!', 400

     # Load Excel data
    df = load_excel_data()

    # Check if the QR code value exists in the 'regid' column
    is_registered = qr_url in df['ChurchRegId'].astype(str).values  # Convert to string in case of numeric values


    # HTML response message
    response_message = '''
    <html>
        <body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h2>{{status}}</h2>
            <p>{{message}}</p>
        </body>
    </html>
    '''

    # Define the status and message based on whether the QR code is registered
    if is_registered:
        status = "✅ User Registered"
        message = "The scanned QR code is registered."
    else:
        status = "❌ User Not Registered"
        message = "The scanned QR code is not registered."

    return render_template_string(response_message, status=status, message=message)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
