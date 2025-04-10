import requests

# Your authentication token
TOKEN = '56c0c4519794149120216c6f9bc873abe9ff4919'
BASE_URL = 'http://127.0.0.1:8000/api'

# Headers for authenticated requests
headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

def test_chat_simulation():
    print('\nTesting Chat Simulation...')
    url = f'{BASE_URL}/chat/simulate/'
    data = {'count': 5}  # Start with just 5 simulations
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print('Status:', response.status_code)
        print('Response:', response.json())
    except Exception as e:
        print('Error:', str(e))

def test_vegetarian_list():
    print('\nTesting Vegetarian List...')
    url = f'{BASE_URL}/vegetarian-list/'
    
    try:
        response = requests.get(url, headers=headers)
        print('Status:', response.status_code)
        print('Response:', response.json())
    except Exception as e:
        print('Error:', str(e))

if __name__ == '__main__':
    print('Testing API endpoints with authentication...')
    test_chat_simulation()
    test_vegetarian_list() 