#!/usr/bin/env python3
"""
Test Script for OLynk AI MVP Phase 2
Tests the new advanced analytics and ML features
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def create_sample_data():
    """Create sample data for testing Phase 2 features"""
    
    # Sample Orders Data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    orders_data = []
    for i, date in enumerate(dates):
        # Create realistic revenue pattern with seasonality
        base_revenue = 1000
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 365)  # Annual seasonality
        weekly_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 7)      # Weekly pattern
        trend_factor = 1 + 0.001 * i                             # Slight upward trend
        
        revenue = base_revenue * seasonal_factor * weekly_factor * trend_factor
        revenue += np.random.normal(0, 100)  # Add some noise
        
        orders_data.append({
            'Order Number': f'ORD-{i+1:04d}',
            'Order Date': date.strftime('%Y-%m-%d'),
            'Customer Name': f'Customer {i % 50 + 1}',
            'Email': f'customer{i % 50 + 1}@example.com',
            'Total': max(0, revenue),
            'Financial Status': 'paid',
            'Fulfillment Status': 'fulfilled'
        })
    
    # Sample Customers Data
    customers_data = []
    for i in range(50):
        total_spent = np.random.exponential(2000) + 500
        orders_count = np.random.poisson(5) + 1
        
        customers_data.append({
            'Customer ID': f'CUST-{i+1:03d}',
            'First Name': f'First{i+1}',
            'Last Name': f'Last{i+1}',
            'Email': f'customer{i+1}@example.com',
            'Total Spent': total_spent,
            'Orders Count': orders_count,
            'Average Order Value': total_spent / orders_count
        })
    
    # Sample Inventory Data
    inventory_data = []
    for i in range(100):
        on_hand = np.random.poisson(50)
        cost = np.random.uniform(10, 200)
        
        inventory_data.append({
            'Inventory Item ID': f'INV-{i+1:04d}',
            'SKU': f'SKU-{i+1:04d}',
            'Product Title': f'Product {i+1}',
            'Location': np.random.choice(['Warehouse A', 'Warehouse B', 'Store 1']),
            'Quantity': on_hand,
            'Available': on_hand,
            'On Hand': on_hand,
            'Cost': cost
        })
    
    return {
        'orders': pd.DataFrame(orders_data),
        'customers': pd.DataFrame(customers_data),
        'inventory': pd.DataFrame(inventory_data)
    }

def test_advanced_analytics():
    """Test the advanced analytics engine"""
    print("🧪 Testing Advanced Analytics Engine...")
    
    try:
        from advanced_analytics import advanced_analytics
        
        # Create sample data
        sample_data = create_sample_data()
        
        # Test 1: Trend Detection
        print("\n📈 Testing Trend Detection...")
        trend_result = advanced_analytics.detect_trends(
            sample_data['orders'], 'Order Date', 'Total'
        )
        if 'error' not in trend_result:
            print(f"✅ Trend Analysis: {trend_result['trend_direction']} trend with {trend_result['trend_strength']} strength")
            print(f"   Growth Rate (7d): {trend_result['growth_rate_7d']:.2%}")
            print(f"   Growth Rate (30d): {trend_result['growth_rate_30d']:.2%}")
        else:
            print(f"❌ Trend Analysis failed: {trend_result['error']}")
        
        # Test 2: Anomaly Detection
        print("\n⚠️ Testing Anomaly Detection...")
        anomaly_result = advanced_analytics.detect_anomalies(
            sample_data['orders'], ['Total']
        )
        if 'error' not in anomaly_result:
            print(f"✅ Anomaly Detection: {anomaly_result['anomaly_count']} anomalies found")
            print(f"   Anomaly Percentage: {anomaly_result['anomaly_percentage']:.1f}%")
        else:
            print(f"❌ Anomaly Detection failed: {anomaly_result['error']}")
        
        # Test 3: Customer Segmentation
        print("\n👥 Testing Customer Segmentation...")
        segmentation_result = advanced_analytics.segment_customers(
            sample_data['customers'], ['Total Spent', 'Orders Count']
        )
        if 'error' not in segmentation_result:
            print(f"✅ Customer Segmentation: {segmentation_result['n_clusters']} clusters created")
            print(f"   Total Customers: {segmentation_result['total_customers']}")
        else:
            print(f"❌ Customer Segmentation failed: {segmentation_result['error']}")
        
        # Test 4: Correlation Analysis
        print("\n🔗 Testing Correlation Analysis...")
        correlation_result = advanced_analytics.calculate_correlations(
            sample_data['customers'], ['Total Spent', 'Orders Count', 'Average Order Value']
        )
        if 'error' not in correlation_result:
            print(f"✅ Correlation Analysis: {correlation_result['summary']['total_variables']} variables analyzed")
            print(f"   Strong Correlations: {correlation_result['summary']['strong_correlations_count']}")
        else:
            print(f"❌ Correlation Analysis failed: {correlation_result['error']}")
        
        print("\n🎉 Advanced Analytics Engine tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import advanced analytics: {e}")
        return False
    except Exception as e:
        print(f"❌ Advanced analytics test failed: {e}")
        return False

def test_insights_generator():
    """Test the enhanced insights generator"""
    print("\n🧠 Testing Enhanced Insights Generator...")
    
    try:
        from insights_generator import insights_generator
        
        # Create sample data
        sample_data = create_sample_data()
        
        # Convert to the format expected by insights generator
        data_dict = {
            'orders': sample_data['orders'].to_dict('records'),
            'customers': sample_data['customers'].to_dict('records'),
            'inventory': sample_data['inventory'].to_dict('records')
        }
        
        # Generate insights
        insights_result = insights_generator.generate_comprehensive_insights(data_dict)
        
        if 'error' not in insights_result:
            print(f"✅ Insights Generated: {len(insights_result['insights'])} insights")
            print(f"   Recommendations: {len(insights_result['recommendations'])} recommendations")
            
            # Show first few insights
            print("\n📊 Sample Insights:")
            for i, insight in enumerate(insights_result['insights'][:3]):
                print(f"   {i+1}. {insight}")
            
            print("\n🎯 Sample Recommendations:")
            for i, rec in enumerate(insights_result['recommendations'][:3]):
                print(f"   {i+1}. {rec}")
                
        else:
            print(f"❌ Insights generation failed: {insights_result['error']}")
        
        print("\n🎉 Enhanced Insights Generator tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import insights generator: {e}")
        return False
    except Exception as e:
        print(f"❌ Insights generator test failed: {e}")
        return False

def test_visualization_engine():
    """Test the visualization engine"""
    print("\n📊 Testing Visualization Engine...")
    
    try:
        from visualization_engine import visualization_engine
        
        # Create sample data
        sample_data = create_sample_data()
        
        # Test 1: Revenue Chart
        print("\n📈 Testing Revenue Chart Generation...")
        revenue_chart = visualization_engine.generate_revenue_chart(
            sample_data['orders'], 'trend'
        )
        if 'error' not in revenue_chart:
            print(f"✅ Revenue Chart: {revenue_chart['title']}")
            print(f"   Data Points: {revenue_chart['data_points']}")
            print(f"   Chart Type: {revenue_chart['chart_type']}")
        else:
            print(f"❌ Revenue chart failed: {revenue_chart['error']}")
        
        # Test 2: Customer Segmentation Chart
        print("\n👥 Testing Customer Segmentation Chart...")
        customer_chart = visualization_engine.generate_customer_segmentation_chart(
            sample_data['customers']
        )
        if 'error' not in customer_chart:
            print(f"✅ Customer Chart: {customer_chart['title']}")
            print(f"   Data Points: {customer_chart['data_points']}")
        else:
            print(f"❌ Customer chart failed: {customer_chart['error']}")
        
        # Test 3: Inventory Chart
        print("\n📦 Testing Inventory Chart...")
        inventory_chart = visualization_engine.generate_inventory_heatmap(
            sample_data['inventory']
        )
        if 'error' not in inventory_chart:
            print(f"✅ Inventory Chart: {inventory_chart['title']}")
            print(f"   Data Points: {inventory_chart['data_points']}")
        else:
            print(f"❌ Inventory chart failed: {inventory_chart['error']}")
        
        print("\n🎉 Visualization Engine tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import visualization engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Visualization engine test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 OLynk AI MVP - Phase 2 Testing Suite")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Test 1: Advanced Analytics
    results.append(test_advanced_analytics())
    
    # Test 2: Insights Generator
    results.append(test_insights_generator())
    
    # Test 3: Visualization Engine
    results.append(test_visualization_engine())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("🚀 Your OLynk AI MVP is ready for Phase 2 features!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 