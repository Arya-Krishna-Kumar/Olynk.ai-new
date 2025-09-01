#!/usr/bin/env python3
"""
Test script to verify entrepreneur-friendly features:
1. Customer segmentation removed from advanced analytics
2. Correlation analysis provides business-friendly results
"""

import requests
import json
import pandas as pd
import io

def test_advanced_analytics_endpoints():
    """Test the advanced analytics endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Advanced Analytics Endpoints...")
    
    # Test 1: Check if segmentation endpoint is removed
    print("\n1. Testing if segmentation endpoint is removed...")
    try:
        response = requests.post(f"{base_url}/advanced-analysis/segmentation")
        if response.status_code == 400:
            error_data = response.json()
            if "not supported" in error_data.get('error', '').lower():
                print("✅ Customer segmentation endpoint successfully removed")
            else:
                print(f"❌ Segmentation endpoint still exists: {error_data}")
        else:
            print(f"❌ Segmentation endpoint still exists (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing segmentation endpoint: {e}")
    
    # Test 2: Check available analysis types
    print("\n2. Testing available analysis types...")
    analysis_types = ['trends', 'anomalies', 'correlations']
    
    for analysis_type in analysis_types:
        try:
            response = requests.post(f"{base_url}/advanced-analysis/{analysis_type}")
            if response.status_code == 400:
                error_data = response.json()
                if "no suitable data" in error_data.get('error', '').lower():
                    print(f"✅ {analysis_type} endpoint exists (no data uploaded)")
                else:
                    print(f"❌ {analysis_type} endpoint error: {error_data}")
            else:
                print(f"❌ {analysis_type} endpoint unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing {analysis_type} endpoint: {e}")
    
    print("\n✅ Advanced analytics endpoint tests completed!")

def test_correlation_analysis_with_sample_data():
    """Test correlation analysis with sample data"""
    base_url = "http://localhost:5000"
    
    print("\n🧪 Testing Correlation Analysis with Sample Data...")
    
    # Create sample orders data with multiple numeric columns
    sample_data = {
        'Order ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Order Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                      '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
        'Total Amount': [100, 150, 200, 120, 180, 250, 300, 90, 160, 220],
        'Quantity': [2, 3, 4, 2, 3, 5, 6, 1, 3, 4],
        'Unit Price': [50, 50, 50, 60, 60, 50, 50, 90, 53, 55],
        'Discount Amount': [10, 15, 20, 12, 18, 25, 30, 9, 16, 22]
    }
    
    # Convert to CSV
    df = pd.DataFrame(sample_data)
    csv_content = df.to_csv(index=False)
    
    print("\n1. Uploading sample orders data...")
    try:
        files = {'file': ('orders.csv', csv_content, 'text/csv')}
        response = requests.post(f"{base_url}/upload/orders", files=files)
        
        if response.status_code == 200:
            print("✅ Sample orders data uploaded successfully")
        else:
            print(f"❌ Failed to upload sample data: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Error uploading sample data: {e}")
        return
    
    # Test correlation analysis
    print("\n2. Testing correlation analysis...")
    try:
        response = requests.post(f"{base_url}/advanced-analysis/correlations")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Correlation analysis completed successfully")
            
            # Check for entrepreneur-friendly features
            print("\n3. Checking entrepreneur-friendly features...")
            
            # Check for business insights
            if 'business_insights' in data:
                print("✅ Business insights present:")
                for insight in data['business_insights']:
                    print(f"   • {insight}")
            else:
                print("❌ Business insights missing")
            
            # Check for recommendations
            if 'recommendations' in data:
                print("✅ Actionable recommendations present:")
                for rec in data['recommendations']:
                    print(f"   • {rec}")
            else:
                print("❌ Recommendations missing")
            
            # Check for business-friendly variable names
            if 'strong_correlations' in data and data['strong_correlations']:
                print("✅ Strong correlations with business-friendly names:")
                for corr in data['strong_correlations']:
                    print(f"   • {corr.get('variable1_display', corr['variable1'])} ↔ {corr.get('variable2_display', corr['variable2'])}")
                    print(f"     Interpretation: {corr.get('interpretation', 'N/A')}")
            
            # Check for variables analyzed count
            if 'variables_analyzed' in data:
                print(f"✅ Variables analyzed: {data['variables_analyzed']}")
            
            # Check for total relationships
            if 'total_relationships' in data:
                print(f"✅ Total relationships found: {data['total_relationships']}")
            
        else:
            error_data = response.json()
            print(f"❌ Correlation analysis failed: {error_data}")
            
    except Exception as e:
        print(f"❌ Error testing correlation analysis: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Entrepreneur-Friendly Features")
    print("=" * 50)
    
    # Test 1: Advanced analytics endpoints
    test_advanced_analytics_endpoints()
    
    # Test 2: Correlation analysis with sample data
    test_correlation_analysis_with_sample_data()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
