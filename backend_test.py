#!/usr/bin/env python3
"""
Backend API Testing for Contact Form
Tests the POST /api/contacts endpoint with various scenarios
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("ERROR: Could not get REACT_APP_BACKEND_URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api/contacts"
print(f"Testing API endpoint: {API_URL}")

def test_valid_contact_submission():
    """Test 1: Valid contact submission"""
    print("\n=== Test 1: Valid Contact Submission ===")
    
    payload = {
        "name": "Marco Rossi",
        "email": "marco.rossi@example.com",
        "message": "Sono molto interessato al libro 'Cronache dal fronte invisibile'. Vorrei sapere quando sarà disponibile in libreria."
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == True and 'contact_id' in data:
                print("✅ PASS: Valid contact submission successful")
                return True, data.get('contact_id')
            else:
                print("❌ FAIL: Response format incorrect")
                return False, None
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ FAIL: Request failed - {e}")
        return False, None

def test_invalid_email_format():
    """Test 2: Invalid email format"""
    print("\n=== Test 2: Invalid Email Format ===")
    
    payload = {
        "name": "Giovanni Bianchi",
        "email": "invalid-email-format",
        "message": "Questo è un messaggio di test con email non valida per verificare la validazione."
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print("✅ PASS: Invalid email correctly rejected with 422")
            return True
        else:
            print(f"❌ FAIL: Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Request failed - {e}")
        return False

def test_missing_required_fields():
    """Test 3: Missing required fields"""
    print("\n=== Test 3: Missing Required Fields ===")
    
    test_cases = [
        {"email": "test@example.com", "message": "Missing name field test message"},
        {"name": "Test User", "message": "Missing email field test message"},
        {"name": "Test User", "email": "test@example.com"}
    ]
    
    all_passed = True
    
    for i, payload in enumerate(test_cases, 1):
        print(f"\nSubtest 3.{i}: Missing {list(set(['name', 'email', 'message']) - set(payload.keys()))[0]}")
        
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 422:
                print(f"✅ PASS: Missing field correctly rejected with 422")
            else:
                print(f"❌ FAIL: Expected 422, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL: Request failed - {e}")
            all_passed = False
    
    return all_passed

def test_invalid_message_length():
    """Test 4: Invalid message length"""
    print("\n=== Test 4: Invalid Message Length ===")
    
    test_cases = [
        {
            "name": "Test User",
            "email": "test@example.com", 
            "message": "Short",  # Less than 10 chars
            "description": "Message too short (< 10 chars)"
        },
        {
            "name": "Test User",
            "email": "test@example.com",
            "message": "",  # Empty message
            "description": "Empty message"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nSubtest 4.{i}: {test_case['description']}")
        payload = {k: v for k, v in test_case.items() if k != 'description'}
        
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 422:
                print(f"✅ PASS: Invalid message correctly rejected with 422")
            else:
                print(f"❌ FAIL: Expected 422, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL: Request failed - {e}")
            all_passed = False
    
    return all_passed

def test_mongodb_data_verification():
    """Test 5: Verify data is saved in MongoDB (indirect test via API)"""
    print("\n=== Test 5: MongoDB Data Verification ===")
    
    # Create a unique contact to verify storage
    unique_name = f"Test User {uuid.uuid4().hex[:8]}"
    payload = {
        "name": unique_name,
        "email": "mongodb.test@example.com",
        "message": "Questo è un messaggio di test per verificare che i dati vengano salvati correttamente nel database MongoDB."
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            contact_id = data.get('contact_id')
            
            if contact_id and data.get('success'):
                print("✅ PASS: Contact created successfully with contact_id")
                print(f"Contact ID: {contact_id}")
                
                # Verify response structure matches expected schema
                expected_fields = ['success', 'message', 'contact_id']
                if all(field in data for field in expected_fields):
                    print("✅ PASS: Response contains all expected fields")
                    return True
                else:
                    print("❌ FAIL: Response missing expected fields")
                    return False
            else:
                print("❌ FAIL: Response missing contact_id or success flag")
                return False
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Request failed - {e}")
        return False

def run_all_tests():
    """Run all backend API tests"""
    print("=" * 60)
    print("BACKEND API TESTING - Contact Form")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Valid submission
    results['valid_submission'], contact_id = test_valid_contact_submission()
    
    # Test 2: Invalid email
    results['invalid_email'] = test_invalid_email_format()
    
    # Test 3: Missing fields
    results['missing_fields'] = test_missing_required_fields()
    
    # Test 4: Invalid message length
    results['invalid_message'] = test_invalid_message_length()
    
    # Test 5: MongoDB verification
    results['mongodb_verification'] = test_mongodb_data_verification()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Contact Form API is working correctly!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Contact Form API has issues")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)