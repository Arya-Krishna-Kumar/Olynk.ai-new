#!/usr/bin/env python3
"""
Unit tests for OLynk AI MVP Backend
Phase 3: Week 9 - Testing & Quality Assurance
"""

import unittest
import sys
import os
import tempfile
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, uploaded_data, validate_csv_data, allowed_file

class TestBackend(unittest.TestCase):
    """Test cases for backend functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear uploaded data for each test
        uploaded_data['products'] = []
        uploaded_data['orders'] = []
        uploaded_data['customers'] = []
        uploaded_data['inventory'] = []
        
        # Create sample test data
        self.sample_orders = pd.DataFrame({
            'Order ID': [1, 2, 3, 4, 5],
            'Order Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'Customer ID': [101, 102, 103, 104, 105],
            'Total Amount': [100, 150, 200, 120, 180],
            'Quantity': [2, 3, 4, 2, 3]
        })
        
        self.sample_customers = pd.DataFrame({
            'Customer ID': [101, 102, 103, 104, 105],
            'First Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Last Name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'Email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'alice@test.com', 'charlie@test.com'],
            'Total Spent': [500, 750, 300, 450, 600],
            'Total Orders': [5, 7, 3, 4, 6]
        })
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
        self.assertIn('phase', data)
        self.assertIn('features', data)
    
    def test_allowed_file(self):
        """Test file extension validation"""
        self.assertTrue(allowed_file('test.csv'))
        self.assertTrue(allowed_file('data.CSV'))
        self.assertFalse(allowed_file('test.txt'))
        self.assertFalse(allowed_file('test.xlsx'))
        self.assertFalse(allowed_file('test'))
    
    def test_validate_csv_data(self):
        """Test CSV data validation"""
        # Test valid data
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        expected_cols = ['col1', 'col2']
        quality_score, issues = validate_csv_data(df, expected_cols)
        
        self.assertEqual(quality_score, 100)
        self.assertEqual(len(issues), 0)
        
        # Test missing columns
        df = pd.DataFrame({'col1': [1, 2, 3]})
        expected_cols = ['col1', 'col2', 'col3']
        quality_score, issues = validate_csv_data(df, expected_cols)
        
        self.assertLess(quality_score, 100)
        self.assertGreater(len(issues), 0)
        
        # Test empty dataframe
        df = pd.DataFrame()
        quality_score, issues = validate_csv_data(df, expected_cols)
        
        self.assertEqual(quality_score, 0)
        self.assertIn('File is empty', issues)
    
    def test_upload_endpoint(self):
        """Test file upload endpoint"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_orders.to_csv(f.name, index=False)
            f.flush()
            
            with open(f.name, 'rb') as csv_file:
                response = self.app.post('/upload/orders',
                                       data={'file': (csv_file, 'orders.csv')},
                                       content_type='multipart/form-data')
        
        # Clean up
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertEqual(data['data']['rows'], 5)
        self.assertEqual(data['data']['columns'], 5)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        response = self.app.post('/upload/invalid_type')
        self.assertEqual(response.status_code, 400)
    
    def test_upload_no_file(self):
        """Test upload without file"""
        response = self.app.post('/upload/orders')
        self.assertEqual(response.status_code, 400)
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint"""
        # First upload some data
        uploaded_data['orders'] = self.sample_orders.to_dict('records')
        uploaded_data['customers'] = self.sample_customers.to_dict('records')
        
        response = self.app.get('/analytics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_revenue', data)
        self.assertIn('total_customers', data)
        self.assertIn('total_products', data)
        self.assertIn('low_stock_items', data)
        self.assertEqual(data['total_customers'], 5)
    
    def test_analytics_no_data(self):
        """Test analytics endpoint with no data"""
        response = self.app.get('/analytics')
        self.assertEqual(response.status_code, 400)
    
    def test_insights_endpoint(self):
        """Test insights endpoint"""
        # Upload some data
        uploaded_data['orders'] = self.sample_orders.to_dict('records')
        uploaded_data['customers'] = self.sample_customers.to_dict('records')
        
        response = self.app.get('/insights')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('insights', data)
        self.assertGreater(len(data['insights']), 0)
    
    def test_chatbot_endpoint(self):
        """Test chatbot endpoint"""
        # Upload some data
        uploaded_data['orders'] = self.sample_orders.to_dict('records')
        
        response = self.app.post('/chatbot',
                               json={'message': 'What is the total revenue?'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('response', data)
    
    def test_advanced_analysis_endpoint(self):
        """Test advanced analysis endpoint"""
        # Upload some data
        uploaded_data['orders'] = self.sample_orders.to_dict('records')
        
        # Test trends analysis
        response = self.app.post('/advanced-analysis/trends')
        self.assertIn(response.status_code, [200, 400])  # 400 if insufficient data
        
        # Test anomalies analysis
        response = self.app.post('/advanced-analysis/anomalies')
        self.assertIn(response.status_code, [200, 400])
        
        # Test correlations analysis
        response = self.app.post('/advanced-analysis/correlations')
        self.assertIn(response.status_code, [200, 400])
    
    def test_chart_generation(self):
        """Test chart generation endpoint"""
        # Upload some data
        uploaded_data['orders'] = self.sample_orders.to_dict('records')
        
        response = self.app.post('/charts/revenue',
                               json={'chart_type': 'line'})
        self.assertIn(response.status_code, [200, 400])
    
    def test_template_download(self):
        """Test template download endpoint"""
        response = self.app.get('/download-template/products')
        self.assertIn(response.status_code, [200, 404])
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid endpoint
        response = self.app.get('/invalid_endpoint')
        self.assertEqual(response.status_code, 404)
        
        # Test invalid JSON
        response = self.app.post('/chatbot',
                               data='invalid json',
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

class TestDataProcessing(unittest.TestCase):
    """Test cases for data processing functionality"""
    
    def test_numeric_conversion(self):
        """Test numeric data conversion"""
        df = pd.DataFrame({
            'amount': ['100', '150', '200', 'invalid', ''],
            'quantity': [1, 2, 3, 4, 5]
        })
        
        # Test numeric conversion
        numeric_col = pd.to_numeric(df['amount'], errors='coerce')
        self.assertEqual(numeric_col.iloc[0], 100.0)
        self.assertEqual(numeric_col.iloc[1], 150.0)
        self.assertTrue(pd.isna(numeric_col.iloc[3]))  # invalid value
        self.assertTrue(pd.isna(numeric_col.iloc[4]))  # empty value
    
    def test_date_conversion(self):
        """Test date conversion"""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', 'invalid', ''],
            'value': [100, 150, 200, 250]
        })
        
        # Test date conversion
        date_col = pd.to_datetime(df['date'], errors='coerce')
        self.assertIsInstance(date_col.iloc[0], pd.Timestamp)
        self.assertIsInstance(date_col.iloc[1], pd.Timestamp)
        self.assertTrue(pd.isna(date_col.iloc[2]))  # invalid date
        self.assertTrue(pd.isna(date_col.iloc[3]))  # empty date

if __name__ == '__main__':
    unittest.main()
