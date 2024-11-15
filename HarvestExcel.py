from flask import Flask, request, jsonify, render_template_string
import pandas as pd

app = Flask(__name__)

# Load Excel data
def load_excel_data():
    # Adjust the file path if your Excel file is in a different location
    df = pd.read_excel("HarvestNew.xlsx")
    return df

@app.route('/')
def home():
    # HTML and JavaScript for live scanning
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code Scanner</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.1.0/html5-qrcode.min.js"></script>
        <style>
            body { font-family: Arial; text-align: center; padding: 20px; }
            #qr-reader { width: 300px; margin: auto; }
            #status-message { margin-top: 20px; font-size: 18px; }
        </style>
    </head>
    <body>
        <h1>QR Code Scanner</h1>
        <div id="qr-reader"></div>
        <div id="status-message"></div>
        <script>
            // Initialize the QR code scanner
            const qrReader = new Html5Qrcode("qr-reader");

            function startScanning() {
                qrReader.start(
                    { facingMode: "environment" },  // Use back-facing camera
                    { fps: 10, qrbox: 250 },        // Frame per second and scanning box size
                    async (decodedText) => {
                        // Send the QR code text to the Flask backend for verification
                        try {
                            const response = await fetch('/check-qr', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ qr_text: decodedText })
                            });
                            const data = await response.json();

                            // Display the verification result
                            const statusDiv = document.getElementById('status-message');
                            statusDiv.innerHTML = `<strong>${data.status}</strong><br>${data.message}`;
                            

                            // Clear the message after 3 seconds for the next scan
                            setTimeout(() => {
                                statusDiv.innerHTML = "";
                            }, 3000);

                        } catch (err) {
                            console.error("Error verifying QR code:", err);
                        }
                    },
                    (errorMessage) => {
                        console.warn(`QR error: ${errorMessage}`);
                    }
                ).catch(err => console.error(`QR initialization error: ${err}`));
            }

            startScanning();  // Start the QR scanner
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/check-qr', methods=['POST'])
def check_qr():
    # Extract the QR text from the request
    qr_text = request.json.get('qr_text')
    if not qr_text:
        return jsonify({"status": "❌ Error", "message": "No QR code data received."}), 400

    # Load the Excel data
    df = load_excel_data()

    # Check if the QR text exists in the 'ChurchRegId' column
    is_registered = qr_text in df['ChurchRegId'].astype(str).values

    # Respond with the registration status
    if is_registered:
        return jsonify({"status": "✅ User Registered", "message": "The scanned QR code is registered."})
    else:
        return jsonify({"status": "❌ User Not Registered", "message": "The scanned QR code is not registered."})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
