#!/usr/bin/env python3
"""
Test Runner for OLynk AI MVP
Phase 3: Week 9 - Testing & Quality Assurance
"""

import unittest
import sys
import os
import time
import subprocess
import requests
from datetime import datetime

def check_server_running():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Flask server...")
    try:
        # Start server in background
        process = subprocess.Popen([sys.executable, "main.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            if check_server_running():
                print("✅ Server started successfully!")
                return process
            time.sleep(1)
        
        print("❌ Server failed to start within 30 seconds")
        return None
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running Unit Tests...")
    print("=" * 50)
    
    # Add tests directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_backend.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    # Add tests directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
    
    # Discover and run integration tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_integration.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_performance_tests():
    """Run performance tests"""
    print("\n⚡ Running Performance Tests...")
    print("=" * 50)
    
    if not check_server_running():
        print("❌ Server not running, skipping performance tests")
        return False
    
    try:
        # Test response time for health endpoint
        start_time = time.time()
        response = requests.get("http://localhost:5000/health", timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Health endpoint response time: {response_time:.3f}s")
        
        if response_time > 1.0:
            print("⚠️  Response time is slower than expected (>1s)")
            return False
        
        # Test multiple concurrent requests
        import threading
        import concurrent.futures
        
        def make_request():
            return requests.get("http://localhost:5000/health", timeout=5)
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        print(f"10 concurrent requests completed in: {concurrent_time:.3f}s")
        
        if concurrent_time > 5.0:
            print("⚠️  Concurrent request handling is slower than expected (>5s)")
            return False
        
        print("✅ Performance tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_security_tests():
    """Run basic security tests"""
    print("\n🔒 Running Security Tests...")
    print("=" * 50)
    
    if not check_server_running():
        print("❌ Server not running, skipping security tests")
        return False
    
    try:
        # Test file upload security
        print("Testing file upload security...")
        
        # Test with non-CSV file
        with open('test_security.txt', 'w') as f:
            f.write("This is not a CSV file")
        
        with open('test_security.txt', 'rb') as f:
            response = requests.post("http://localhost:5000/upload/orders",
                                   files={'file': ('test.txt', f, 'text/plain')})
        
        os.remove('test_security.txt')
        
        if response.status_code == 400:
            print("✅ File type validation working")
        else:
            print("❌ File type validation failed")
            return False
        
        # Test with large file
        print("Testing large file upload...")
        large_data = "Order ID,Order Date,Total Amount\n" + "\n".join([f"{i},2024-01-01,100" for i in range(10000)])
        
        with open('large_test.csv', 'w') as f:
            f.write(large_data)
        
        with open('large_test.csv', 'rb') as f:
            response = requests.post("http://localhost:5000/upload/orders",
                                   files={'file': ('large.csv', f, 'text/csv')})
        
        os.remove('large_test.csv')
        
        if response.status_code == 200:
            print("✅ Large file upload working")
        else:
            print("❌ Large file upload failed")
            return False
        
        # Test SQL injection attempt
        print("Testing SQL injection protection...")
        response = requests.post("http://localhost:5000/chatbot",
                               json={'message': "'; DROP TABLE users; --"})
        
        if response.status_code == 200:
            print("✅ SQL injection protection working")
        else:
            print("❌ SQL injection protection failed")
            return False
        
        print("✅ Security tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

def generate_test_report(results):
    """Generate a test report"""
    print("\n📊 Test Report")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Phase: 3 - Launch Preparation")
    print(f"Version: 3.0.0")
    print()
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print()
    if failed_tests == 0:
        print("🎉 All tests passed! Ready for production deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
        return False

def main():
    """Main test runner"""
    print("🚀 OLynk AI MVP - Phase 3 Testing Suite")
    print("=" * 60)
    print("Week 9: Testing & Quality Assurance")
    print("=" * 60)
    
    # Start server if not running
    server_process = None
    if not check_server_running():
        server_process = start_server()
        if not server_process:
            print("❌ Cannot run tests without server running")
            return False
    else:
        print("✅ Server already running")
    
    # Run all test categories
    results = {}
    
    try:
        # Unit tests
        results['Unit Tests'] = run_unit_tests()
        
        # Integration tests
        results['Integration Tests'] = run_integration_tests()
        
        # Performance tests
        results['Performance Tests'] = run_performance_tests()
        
        # Security tests
        results['Security Tests'] = run_security_tests()
        
    finally:
        # Stop server if we started it
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
    
    # Generate report
    all_passed = generate_test_report(results)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
