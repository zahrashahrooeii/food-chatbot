import requests
import json
import random
import string

BASE_URL = 'http://127.0.0.1:8000/api'
AUTH_TOKEN = None

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f'{BASE_URL}/health-check/')
    print('Health Check Response:', response.json())
    return response.status_code == 200

def test_register():
    """Test user registration"""
    global AUTH_TOKEN
    username = f'testuser_{random_string()}'
    password = 'TestPass123!'
    
    data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(f'{BASE_URL}/auth/register/', json=data)
    print('\nRegister Response:', response.json())
    
    if response.status_code == 201:
        AUTH_TOKEN = response.json()['token']
        return True
    return False

def test_login():
    """Test user login"""
    global AUTH_TOKEN
    data = {
        'username': 'testuser',  # Use a known user
        'password': 'testpass123'
    }
    
    response = requests.post(f'{BASE_URL}/auth/login/', json=data)
    print('\nLogin Response:', response.json())
    
    if response.status_code == 200:
        AUTH_TOKEN = response.json()['token']
        return True
    return False

def test_chat_start():
    """Test starting a chat conversation"""
    headers = {'Authorization': f'Token {AUTH_TOKEN}'} if AUTH_TOKEN else {}
    response = requests.post(f'{BASE_URL}/chat/start/', headers=headers)
    print('\nChat Start Response:', response.json())
    return response.status_code in [200, 201]

def test_simulate_conversations():
    """Test simulating conversations"""
    headers = {'Authorization': f'Token {AUTH_TOKEN}'} if AUTH_TOKEN else {}
    data = {'count': 5}  # Test with just 5 conversations
    response = requests.post(f'{BASE_URL}/chat/simulate/', json=data, headers=headers)
    print('\nSimulation Response:', response.json())
    return response.status_code == 200

def test_vegetarian_list():
    """Test getting vegetarian list"""
    headers = {'Authorization': f'Token {AUTH_TOKEN}'} if AUTH_TOKEN else {}
    response = requests.get(f'{BASE_URL}/vegetarian-list/', headers=headers)
    print('\nVegetarian List Response:', response.json())
    return response.status_code == 200

if __name__ == '__main__':
    print('Running API Tests...\n')
    
    print('1. Testing Health Check...')
    health_ok = test_health_check()
    print(f'Health Check {"✓" if health_ok else "✗"}')
    
    print('\n2. Testing User Registration...')
    register_ok = test_register()
    print(f'Registration {"✓" if register_ok else "✗"}')
    
    if not AUTH_TOKEN:
        print('\n3. Testing User Login...')
        login_ok = test_login()
        print(f'Login {"✓" if login_ok else "✗"}')
    
    if AUTH_TOKEN:
        print('\n4. Testing Chat Start...')
        chat_ok = test_chat_start()
        print(f'Chat Start {"✓" if chat_ok else "✗"}')
        
        print('\n5. Testing Conversation Simulation...')
        sim_ok = test_simulate_conversations()
        print(f'Simulation {"✓" if sim_ok else "✗"}')
        
        print('\n6. Testing Vegetarian List...')
        veg_ok = test_vegetarian_list()
        print(f'Vegetarian List {"✓" if veg_ok else "✗"}') 