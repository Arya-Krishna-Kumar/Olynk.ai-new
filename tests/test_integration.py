#!/usr/bin/env python3
"""
Integration tests for OLynk AI MVP
Phase 3: Week 9 - Testing & Quality Assurance
"""

import unittest
import sys
import os
import tempfile
import json
import pandas as pd
import requests
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        
        # Create sample test data
        self.sample_orders = pd.DataFrame({
            'Order ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Order Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                          '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
            'Customer ID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'Customer Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson',
                            'Diana Davis', 'Edward Miller', 'Fiona Garcia', 'George Martinez', 'Helen Anderson'],
            'Product ID': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
            'Product Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E',
                           'Product F', 'Product G', 'Product H', 'Product I', 'Product J'],
            'Quantity': [2, 3, 4, 2, 3, 5, 6, 1, 3, 4],
            'Unit Price': [50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
            'Total Amount': [100, 180, 280, 160, 270, 500, 660, 120, 390, 560],
            'Payment Method': ['Credit Card', 'Cash', 'Credit Card', 'Cash', 'Credit Card',
                              'Cash', 'Credit Card', 'Cash', 'Credit Card', 'Cash'],
            'Order Status': ['Completed', 'Completed', 'Completed', 'Completed', 'Completed',
                           'Completed', 'Completed', 'Completed', 'Completed', 'Completed']
        })
        
        self.sample_customers = pd.DataFrame({
            'Customer ID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'First Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Edward', 'Fiona', 'George', 'Helen'],
            'Last Name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson', 'Davis', 'Miller', 'Garcia', 'Martinez', 'Anderson'],
            'Email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'alice@test.com', 'charlie@test.com',
                     'diana@test.com', 'edward@test.com', 'fiona@test.com', 'george@test.com', 'helen@test.com'],
            'Registration Date': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01',
                                '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01'],
            'Total Orders': [5, 7, 3, 4, 6, 8, 2, 9, 1, 10],
            'Total Spent': [500, 750, 300, 450, 600, 800, 200, 900, 100, 1000],
            'Average Order Value': [100, 107, 100, 112, 100, 100, 100, 100, 100, 100],
            'Last Order Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                               '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
            'Preferred Payment Method': ['Credit Card', 'Cash', 'Credit Card', 'Cash', 'Credit Card',
                                       'Cash', 'Credit Card', 'Cash', 'Credit Card', 'Cash'],
            'Customer Segment': ['Premium', 'Regular', 'Premium', 'Regular', 'Premium',
                               'Regular', 'Premium', 'Regular', 'Premium', 'Regular']
        })
        
        self.sample_products = pd.DataFrame({
            'Product ID': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
            'Product Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E',
                           'Product F', 'Product G', 'Product H', 'Product I', 'Product J'],
            'Category': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Electronics', 'Clothing', 'Books', 'Home', 'Sports'],
            'Brand': ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E', 'Brand F', 'Brand G', 'Brand H', 'Brand I', 'Brand J'],
            'Price': [50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
            'Cost': [30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
            'SKU': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005', 'SKU006', 'SKU007', 'SKU008', 'SKU009', 'SKU010'],
            'Stock Quantity': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
            'Weight (g)': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
            'Dimensions (cm)': ['10x10x10', '15x15x15', '20x20x20', '25x25x25', '30x30x30',
                              '35x35x35', '40x40x40', '45x45x45', '50x50x50', '55x55x55'],
            'Launch Date': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01',
                           '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01'],
            'Last Updated': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                            '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
            'Tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10'],
            'Description': ['Description A', 'Description B', 'Description C', 'Description D', 'Description E',
                           'Description F', 'Description G', 'Description H', 'Description I', 'Description J'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active']
        })
        
        self.sample_inventory = pd.DataFrame({
            'Inventory ID': [301, 302, 303, 304, 305, 306, 307, 308, 309, 310],
            'Product ID': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
            'Product Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E',
                           'Product F', 'Product G', 'Product H', 'Product I', 'Product J'],
            'SKU': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005', 'SKU006', 'SKU007', 'SKU008', 'SKU009', 'SKU010'],
            'Location': ['Warehouse A', 'Warehouse B', 'Warehouse C', 'Warehouse D', 'Warehouse E',
                        'Warehouse F', 'Warehouse G', 'Warehouse H', 'Warehouse I', 'Warehouse J'],
            'Warehouse': ['Main', 'Main', 'Main', 'Main', 'Main', 'Main', 'Main', 'Main', 'Main', 'Main'],
            'Current Stock': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
            'Minimum Stock': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            'Maximum Stock': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500],
            'Unit Cost': [30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
            'Total Value': [3000, 6000, 10000, 15000, 21000, 28000, 36000, 45000, 55000, 66000],
            'Last Restocked': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                             '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
            'Next Restock Date': ['2024-02-01', '2024-02-02', '2024-02-03', '2024-02-04', '2024-02-05',
                                '2024-02-06', '2024-02-07', '2024-02-08', '2024-02-09', '2024-02-10'],
            'Stock Status': ['In Stock', 'In Stock', 'In Stock', 'In Stock', 'In Stock',
                           'In Stock', 'In Stock', 'In Stock', 'In Stock', 'In Stock'],
            'Category': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Electronics', 'Clothing', 'Books', 'Home', 'Sports'],
            'Supplier': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E',
                        'Supplier F', 'Supplier G', 'Supplier H', 'Supplier I', 'Supplier J'],
            'Lead Time (Days)': [7, 10, 14, 21, 30, 7, 10, 14, 21, 30],
            'Reorder Point': [20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
        })
    
    def test_server_availability(self):
        """Test if server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.RequestException as e:
            self.fail(f"Server is not accessible: {e}")
    
    def test_complete_workflow(self):
        """Test complete end-to-end workflow"""
        # Step 1: Check server health
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Upload orders data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_orders.to_csv(f.name, index=False)
            f.flush()
            
            with open(f.name, 'rb') as csv_file:
                files = {'file': ('orders.csv', csv_file, 'text/csv')}
                response = requests.post(f"{self.base_url}/upload/orders", files=files)
        
        os.unlink(f.name)
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Upload customers data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_customers.to_csv(f.name, index=False)
            f.flush()
            
            with open(f.name, 'rb') as csv_file:
                files = {'file': ('customers.csv', csv_file, 'text/csv')}
                response = requests.post(f"{self.base_url}/upload/customers", files=files)
        
        os.unlink(f.name)
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Get analytics
        response = requests.get(f"{self.base_url}/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_revenue', data)
        self.assertIn('total_customers', data)
        self.assertEqual(data['total_customers'], 10)
        
        # Step 5: Get insights
        response = requests.get(f"{self.base_url}/insights")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('insights', data)
        self.assertGreater(len(data['insights']), 0)
        
        # Step 6: Test chatbot
        response = requests.post(f"{self.base_url}/chatbot",
                               json={'message': 'What is the total revenue?'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('response', data)
        
        # Step 7: Test advanced analytics
        response = requests.post(f"{self.base_url}/advanced-analysis/correlations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('variables_analyzed', data)
        
        # Step 8: Test chart generation
        response = requests.post(f"{self.base_url}/charts/revenue",
                               json={'chart_type': 'line'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('image', data)
    
    def test_performance_under_load(self):
        """Test performance under load"""
        # Upload multiple files quickly
        start_time = time.time()
        
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                # Create a smaller dataset for performance testing
                test_data = self.sample_orders.head(100)
                test_data.to_csv(f.name, index=False)
                f.flush()
                
                with open(f.name, 'rb') as csv_file:
                    files = {'file': (f'orders_{i}.csv', csv_file, 'text/csv')}
                    response = requests.post(f"{self.base_url}/upload/orders", files=files)
                
                os.unlink(f.name)
                self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for 5 uploads)
        self.assertLess(total_time, 5.0)
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test invalid file type
        response = requests.post(f"{self.base_url}/upload/invalid_type")
        self.assertEqual(response.status_code, 400)
        
        # Test upload without file
        response = requests.post(f"{self.base_url}/upload/orders")
        self.assertEqual(response.status_code, 400)
        
        # Test invalid JSON in chatbot
        response = requests.post(f"{self.base_url}/chatbot",
                               data='invalid json',
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        
        # Test non-existent endpoint
        response = requests.get(f"{self.base_url}/nonexistent")
        self.assertEqual(response.status_code, 404)
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        # Upload data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_orders.to_csv(f.name, index=False)
            f.flush()
            
            with open(f.name, 'rb') as csv_file:
                files = {'file': ('orders.csv', csv_file, 'text/csv')}
                response = requests.post(f"{self.base_url}/upload/orders", files=files)
        
        os.unlink(f.name)
        self.assertEqual(response.status_code, 200)
        
        # Check analytics
        response = requests.get(f"{self.base_url}/analytics")
        self.assertEqual(response.status_code, 200)
        analytics_data = response.json()
        
        # Check insights
        response = requests.get(f"{self.base_url}/insights")
        self.assertEqual(response.status_code, 200)
        insights_data = response.json()
        
        # Verify revenue is consistent
        revenue_in_analytics = analytics_data.get('total_revenue', 0)
        
        # Check if revenue appears in insights
        revenue_in_insights = False
        for insight in insights_data.get('insights', []):
            if 'revenue' in insight.lower() and str(revenue_in_analytics) in insight:
                revenue_in_insights = True
                break
        
        # If we have revenue data, it should be consistent
        if revenue_in_analytics > 0:
            self.assertTrue(revenue_in_insights, "Revenue should be consistent between analytics and insights")
    
    def test_template_downloads(self):
        """Test template download functionality"""
        template_types = ['products', 'orders', 'customers', 'inventory']
        
        for template_type in template_types:
            response = requests.get(f"{self.base_url}/download-template/{template_type}")
            # Should either return 200 (if template exists) or 404 (if not)
            self.assertIn(response.status_code, [200, 404])
            
            if response.status_code == 200:
                # Check if it's actually CSV content
                content_type = response.headers.get('content-type', '')
                self.assertIn('text/csv', content_type)

if __name__ == '__main__':
    unittest.main()
