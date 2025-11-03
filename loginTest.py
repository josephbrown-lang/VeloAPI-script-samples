import requests

# 1. Create a Session object
session = requests.Session()

session.verify = False

# 2. Perform a login request (e.g., a POST request to a login endpoint)
# The server will typically set authentication cookies in the response


login_url = "https://127.0.0.1/portal/rest/login/operatorLogin"  
login_payload = {
    "username": "super@velocloud.net",
    "password": "vcadm!n"
}
response = session.post(login_url, data=login_payload)
print(session.cookies)

