import requests

url = "http://127.0.0.1:5000/upload_resume"
with open("real_test_resume.pdf", "rb") as f:
    files = {"resume": f}
    response = requests.post(url, files=files)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
