import unittest
import requests
import os

class TestLeadAPI(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api"

    def test_health(self):
        try:
            response = requests.get("http://localhost:5000/health")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("API Server not running")

    def test_upload_missing_file(self):
        try:
            response = requests.post(f"{self.BASE_URL}/upload")
            self.assertEqual(response.status_code, 400)
        except requests.exceptions.ConnectionError:
            self.skipTest("API Server not running")

if __name__ == '__main__':
    unittest.main()
