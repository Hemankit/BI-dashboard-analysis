# test_powerbi_connector.py
import msal
import requests

# Azure AD App Registration details (replace with your own)
CLIENT_ID = "YOUR-CLIENT-ID"
CLIENT_SECRET = "YOUR-CLIENT-SECRET"
TENANT_ID = "YOUR-TENANT-ID"
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

# Acquire access token
app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY_URL,
    client_credential=CLIENT_SECRET
)

token_response = app.acquire_token_for_client(scopes=SCOPE)
access_token = token_response.get("access_token")

if not access_token:
    raise Exception("❌ Failed to get token. Check credentials.")

print("✅ Got Power BI token!")

# Example: List all workspaces
url = "https://api.powerbi.com/v1.0/myorg/groups"
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get(url, headers=headers)

if resp.status_code == 200:
    workspaces = resp.json()["value"]
    print("✅ Power BI Connection Successful!")
    for ws in workspaces:
        print(f"- {ws['name']} (ID: {ws['id']})")
else:
    print("❌ Power BI request failed:", resp.text)