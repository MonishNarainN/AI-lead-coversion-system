import requests
import json

BASE_URL = "http://localhost:5000"
FILENAME = "lead_predictions.csv"

def debug_pdf():
    print(f"Requesting PDF for {FILENAME}...")
    try:
        response = requests.post(
            f"{BASE_URL}/reports/download",
            json={"filename": FILENAME, "format": "pdf"}
        )
        if response.status_code == 200:
            print(f"SUCCESS: PDF generated. Size: {len(response.content)} bytes")
        else:
            print(f"FAILED: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response (not JSON): {response.text[:1000]}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_pdf()
