import requests

def register_and_get_token():
    # Registration
    register_url = 'http://127.0.0.1:8000/api/auth/register/'
    register_data = {
        'username': 'testuser',
        'password': 'TestPass123!'
    }
    
    print('1. Registering new user...')
    try:
        response = requests.post(register_url, json=register_data)
        print('\nRegistration Status:', response.status_code)
        print('Registration Response:', response.json())
        
        if response.status_code == 201:  # Created
            token = response.json().get('token')
            if token:
                print('\nYour authentication token is:', token)
                print('\nTo use this token in API calls, add this header:')
                print(f'Authorization: Token {token}')
                return token
    except Exception as e:
        print('Registration Error:', str(e))
    
    return None

if __name__ == '__main__':
    print('Getting authentication token...\n')
    token = register_and_get_token()
    
    if token:
        print('\nExample API call:')
        print(f'curl -H "Authorization: Token {token}" http://127.0.0.1:8000/api/vegetarian-list/') 