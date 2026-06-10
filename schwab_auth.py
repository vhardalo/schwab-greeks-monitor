import json
import base64
import requests
import urllib.parse
import config

def get_authorization_url():
    """Generates the URL you need to paste into your browser to log in."""
    params = {
        "response_type": "code",
        "client_id": config.APP_KEY,
        "redirect_uri": config.REDIRECT_URI
    }
    url = f"{config.AUTH_BASE_URL}?{urllib.parse.urlencode(params)}"
    
    print("\n" + "="*60)
    print("STEP 1: LAUNCH THE LOGIN HANDSHAKE")
    print("="*60)
    print("Copy and paste this entire URL into your web browser:")
    print(f"\n{url}\n")
    print("-> Log in with your normal Schwab account credentials.")
    print("-> Grant permission to your app.")
    print("-> The browser will eventually redirect to a page that says 'Can't be reached'.")
    print("   THAT IS NORMAL. Do not close it!")

def exchange_code_for_tokens(returned_url):
    """Parses the authorization code from your redirected address bar to get your tokens."""
    parsed_url = urllib.parse.urlparse(returned_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print("\n[!] Error: Could not find the 'code' parameter in that URL. Make sure you copied the whole address bar.")
        return False
        
    # Schwab's OAuth requires 'code' to have a trailing '@' removed if it appends one
    auth_code = query_params['code'][0]
    
    # Format the authorization header using Base64 encoding per Schwab's requirements
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{config.APP_KEY}:{config.APP_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': config.REDIRECT_URI
    }
    
    print("\nExchanging authorization code for permanent app tokens...")
    response = requests.post(config.TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        # Save tokens to our local file (which is safely hidden by .gitignore)
        with open("schwab_tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)
            
        print("\n" + "="*60)
        print("SUCCESS! AUTHENTICATION COMPLETE")
        print("="*60)
        print("Your application tokens have been securely generated and saved to 'schwab_tokens.json'.")
        print("Your app can now safely pull options market data automatically.")
        return True
    else:
        print(f"\n[!] Error exchanging code: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    # 1. Run the URL generator
    get_authorization_url()
    
    # 2. Wait for you to paste the resulting web address back in
    print("-"*60)
    user_url = input("STEP 2: Paste the ENTIRE URL from your browser's address bar here:\n> ")
    if user_url.strip():
        exchange_code_for_tokens(user_url)