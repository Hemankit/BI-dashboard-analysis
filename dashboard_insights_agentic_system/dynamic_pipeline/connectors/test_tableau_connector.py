# test_tableau_connector.py
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import get_projects_dataframe

# Example connection config (replace with your actual details)
connection = TableauServerConnection({
    'tableau_prod': {
        'server': 'https://YOUR-TABLEAU-SERVER',
        'api_version': '3.21',  # Check your Tableau version
        'username': 'YOUR-USERNAME',
        'password': 'YOUR-PASSWORD',
        'site_name': 'YOUR-SITE-NAME',
        'site_url': 'YOUR-SITE-URL'
    }
}, env='tableau_prod')

# Login
connection.sign_in()

# Test: Fetch projects as a simple connectivity check
projects_df = get_projects_dataframe(connection)
print("✅ Tableau Connection Successful!")
print(projects_df.head())

# Logout
connection.sign_out()