import json
import time
import base64
import requests
import config

def load_tokens():
    """Loads the tokens from our secure local JSON file."""
    try:
        with open("schwab_tokens.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[!] Error: 'schwab_tokens.json' not found. Run schwab_auth.py first.")
        return None

def refresh_access_token(tokens):
    """Schwab access tokens expire every 30 minutes. This uses the refresh token

    to get a fresh one automatically without logging in again via browser.
    """
    print("\nRefreshing access token...")
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{config.APP_KEY}:{config.APP_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token']
    }
    
    response = requests.post(config.TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        new_tokens = response.json()
        # Preserve the long-term refresh token if Schwab didn't send a new one
        if 'refresh_token' not in new_tokens:
            new_tokens['refresh_token'] = tokens['refresh_token']
            
        with open("schwab_tokens.json", "w") as f:
            json.dump(new_tokens, f, indent=4)
        print("Token refreshed successfully.")
        return new_tokens
    else:
        print(f"[!] Failed to refresh token: {response.status_code}")
        print(response.text)
        return None

def get_options_chain(symbol, first_run=False):
    """Pulls the real-time options chain and Greeks for a specific underlying symbol."""
    tokens = load_tokens()
    if not tokens:
        return None
        
    # Headers require your active access token
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    
    # Target strictly 0DTE contracts within a highly concentrated strike range
    params = {
        "symbol": symbol,
        "includeUnderlyingQuote": "true",
        "strategy": "SINGLE",
        "strikeCount": "10",        # 10 strikes above/below the current price is plenty for 0DTE
        "range": "ALL",            # Includes In-the-Money and Out-of-the-Money
        "daysToExpiration": "0",     # STRICTIONS TO 0DTE ONLY (Today's expiration)
        "indicative": "true"
    }
    
    url = f"{config.MARKET_DATA_BASE_URL}/chains"
    
    # ONLY print the connection status message if it is the script's very first execution
    if first_run:
        print(f"\n📡 Initializing connection and fetching live options chain for ${symbol.upper()}...")
        
    response = requests.get(url, headers=headers, params=params)
    
    # Handle the API response payloads safely
    if response.status_code == 200:
        chain_data = response.json()
        
        # Save a local data audit cache copy for validation checks
        with open("sample_chain.json", "w") as f:
            json.dump(chain_data, f, indent=4)
            
        return chain_data
    elif response.status_code == 401:
        # Token expired midway through operation, attempt automated recovery sequence
        new_tokens = refresh_access_token(tokens)
        if new_tokens:
            return get_options_chain(symbol, first_run=False)
    else:
        # Prevent the Rich Live container from crashing if an API error packet arrives
        return None