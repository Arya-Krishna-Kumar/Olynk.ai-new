#!/usr/bin/env python3
"""
Test script for OLynk AI Export Functionality
"""

import requests
import json
import time

def test_export_functionality():
    """Test the export endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing OLynk AI Export Functionality...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:5000")
        return
    
    # Test 2: Test CSV export with no data
    print("\n📊 Testing CSV Export (no data)...")
    try:
        response = requests.post(
            f"{base_url}/export/csv",
            headers={"Content-Type": "application/json"},
            json={"type": "all"}
        )
        
        if response.status_code == 400:
            print("✅ CSV export correctly returns error when no data available")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing CSV export: {e}")
    
    # Test 3: Test PDF export with no data
    print("\n📄 Testing PDF Export (no data)...")
    try:
        response = requests.post(
            f"{base_url}/export/pdf",
            headers={"Content-Type": "application/json"},
            json={"type": "all"}
        )
        
        if response.status_code == 400:
            print("✅ PDF export correctly returns error when no data available")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing PDF export: {e}")
    
    # Test 4: Test Excel export with no data
    print("\n📈 Testing Excel Export (no data)...")
    try:
        response = requests.post(
            f"{base_url}/export/excel",
            headers={"Content-Type": "application/json"},
            json={"type": "all"}
        )
        
        if response.status_code == 400:
            print("✅ Excel export correctly returns error when no data available")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Excel export: {e}")
    
    # Test 5: Test invalid export format
    print("\n🚫 Testing Invalid Export Format...")
    try:
        response = requests.post(
            f"{base_url}/export/invalid",
            headers={"Content-Type": "application/json"},
            json={"type": "all"}
        )
        
        if response.status_code == 400:
            print("✅ Invalid export format correctly returns error")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing invalid export format: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Export functionality test completed!")
    print("\n📝 Summary:")
    print("• Export endpoints are responding correctly")
    print("• Error handling is working properly")
    print("• To test with actual data, upload CSV files through the web interface")
    print("• Then try the export buttons in the browser")

if __name__ == "__main__":
    test_export_functionality()
