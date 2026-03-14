import requests
import os

BASE_URL = "http://localhost:5000"
FILENAME = "lead_predictions.csv"

def test_report(format_type):
    print(f"Testing format: {format_type}...")
    try:
        response = requests.post(
            f"{BASE_URL}/reports/download",
            json={"filename": FILENAME, "format": format_type}
        )
        if response.status_code == 200:
            print(f"  SUCCESS: {format_type} report generated. Size: {len(response.content)} bytes")
            return True
        else:
            print(f"  FAILED: {format_type} report. Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == "__main__":
    formats = ["excel", "analysis", "predictions", "insights", "pdf"]
    results = [test_report(f) for f in formats]
    
    if all(results):
        print("\nAll reports verified successfully!")
    else:
        print("\nSome report verifications failed.")
