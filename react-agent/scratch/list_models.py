import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.environ.get('GOOGLE_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print("Available Models:")
        for m in models:
            print(m)
except Exception as e:
    print(f"Error fetching models: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
