#!/usr/bin/env python3
"""
Test script for advanced analytics endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Phase: {data.get('phase')}")
        return response.ok
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_advanced_analytics():
    """Test advanced analytics endpoints"""
    analysis_types = ['trends', 'anomalies', 'segmentation', 'correlations']
    
    for analysis_type in analysis_types:
        print(f"\n--- Testing {analysis_type} analysis ---")
        try:
            response = requests.post(f"{BASE_URL}/advanced-analysis/{analysis_type}")
            print(f"Status: {response.status_code}")
            
            if response.ok:
                data = response.json()
                print(f"Success: {data}")
            else:
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Error: {response.text}")
                    
        except Exception as e:
            print(f"Request failed: {e}")

def main():
    print("Testing OLynk AI Advanced Analytics...")
    
    # Wait for app to start
    print("Waiting for app to start...")
    time.sleep(5)
    
    # Test health
    if not test_health():
        print("App is not running. Please start the Flask application first.")
        return
    
    # Test advanced analytics
    test_advanced_analytics()

if __name__ == "__main__":
    main()
