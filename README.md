# 🚀 OLynk AI MVP - CSV Insights Platform

Transform your CSV data into actionable business insights in minutes using AI-powered analysis.

## 📋 Project Overview

**OLynk AI MVP** is a streamlined data intelligence platform that focuses on three core capabilities:
1. **CSV Upload & Validation** - Seamless data ingestion with intelligent schema detection
2. **Automated Data Analysis** - Statistical analysis, trend detection, and anomaly identification  
3. **AI-Powered Insights** - Human-readable business recommendations and actionable next steps

## 🎯 Current Phase: Phase 2 - Enhancement

**Status**: ✅ **COMPLETED** (Weeks 5-8)
- [x] Project setup and infrastructure
- [x] CSV upload and validation
- [x] Data processing and basic analytics
- [x] MVP UI and basic insights
- [x] **Advanced Analytics Engine** (NEW!)
- [x] **ML Models Integration** (NEW!)
- [x] **Interactive Visualizations** (NEW!)
- [x] **Enhanced AI Insights** (NEW!)

**Next Phase**: Phase 3 - Launch Preparation (Weeks 9-12)

## 🏗️ Project Structure

```
New Olynk/
├── backend/                 # Flask API and ML pipeline
│   ├── app.py             # Main Flask application (Phase 2 enhanced)
│   ├── advanced_analytics.py  # ML-powered analytics engine
│   ├── insights_generator.py  # Enhanced AI insights generator
│   ├── visualization_engine.py # Chart and visualization engine
│   └── requirements.txt   # Python dependencies (Phase 2)
├── frontend/              # User interface
│   └── index.html        # Main HTML template (Phase 2 enhanced)
├── uploads/               # File storage directory
├── main.py                # Application entry point
├── test_phase2.py         # Phase 2 testing suite
├── README.md              # This file
├── OLynk_AI_MVP_PRD.md   # Product Requirements Document
└── OLynk_AI_MVP_Phase_Breakdown.md  # Implementation phases
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   # Navigate to project directory
   cd "New Olynk"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open your browser**
   - Navigate to: `http://localhost:5000`
   - Start uploading CSV files!

## 📊 Supported File Types

The MVP currently supports these CSV formats:

| Type | Description | Key Columns |
|------|-------------|-------------|
| **Products** | Shopify product catalog | Handle, Title, Price, SKU, Inventory |
| **Orders** | Sales and order data | Order Number, Date, Total, Customer |
| **Customers** | Customer information | Customer ID, Name, Email, Total Spent |
| **Inventory** | Stock and inventory data | SKU, Product Title, Quantity, Location |

## 🔧 Features Implemented

### ✅ Phase 1: Core Foundation
- **File Upload**: Drag & drop CSV files up to 50MB
- **Data Validation**: Automatic schema detection and quality scoring
- **Basic Analytics**: Descriptive statistics and aggregations
- **AI Insights**: Automated business recommendations
- **Interactive UI**: Modern, responsive dashboard

### ✅ Phase 2: Advanced Analytics & ML (NEW!)
- **Advanced Analytics Engine**: Trend detection, anomaly detection, customer segmentation
- **ML Models**: Isolation Forest, K-means clustering, correlation analysis
- **Interactive Visualizations**: Revenue trends, customer segments, inventory status
- **Enhanced AI Insights**: Cross-dataset analysis, predictive recommendations
- **Performance Optimization**: Async processing, caching, error handling

## 🚀 Phase 2 New Features

### 🔬 Advanced Analytics Engine
- **Trend Detection**: Identify revenue patterns, growth rates, seasonality
- **Anomaly Detection**: Find unusual patterns using Isolation Forest algorithm
- **Customer Segmentation**: Group customers by spending behavior using K-means
- **Correlation Analysis**: Discover relationships between business metrics
- **Forecasting**: Simple time-series predictions and trend extrapolation

### 🤖 ML-Powered Insights
- **Cross-Dataset Analysis**: Combine insights from multiple data sources
- **Predictive Recommendations**: Suggest actions based on data patterns
- **Risk Assessment**: Identify potential business risks and opportunities
- **Performance Benchmarks**: Compare metrics against industry standards

### 📊 Interactive Visualizations
- **Revenue Trend Charts**: Line charts with moving averages and trend lines
- **Customer Segmentation**: Distribution charts and cluster analysis
- **Inventory Status**: Pie charts showing stock levels and alerts
- **Weekly Performance**: Bar charts for period-over-period analysis

### ⚡ Performance Enhancements
- **Async Processing**: Handle large files without blocking
- **Smart Caching**: Cache analysis results for faster subsequent access
- **Error Recovery**: Graceful fallbacks when advanced features fail
- **Progress Tracking**: Real-time updates during analysis

## 🎨 User Interface

The Phase 2 MVP features an enhanced interface with:

- **Phase Badge**: Clear indication of current implementation phase
- **Advanced Analytics Panel**: One-click access to ML-powered analysis
- **Visualization Controls**: Interactive chart generation buttons
- **Enhanced Dashboard**: More metrics and real-time updates
- **Responsive Design**: Works seamlessly on all devices

## 📈 Data Quality Features

### Quality Scoring System
- **90-100%**: Excellent - Data is clean and complete
- **75-89%**: Good - Minor issues, mostly usable
- **60-74%**: Fair - Some issues, may need attention
- **0-59%**: Poor - Significant issues, review required

### Validation Checks
- Column presence and completeness
- Data type validation (dates, numbers, text)
- Missing value detection
- File size and format validation

## 🔮 Upcoming Features (Phase 3)

### Week 9-10: Testing & Quality Assurance
- Comprehensive testing suite
- Performance testing and optimization
- Security audit and vulnerability assessment

### Week 11-12: Launch Preparation
- Production deployment
- Monitoring and logging systems
- User documentation and help system

## 🧪 Testing the MVP

### Test Phase 2 Features
```bash
# Run the Phase 2 testing suite
python test_phase2.py
```

### Sample Data
You can test the platform with:
1. **Sample CSV files** from your business data
2. **Template files** available in the UI
3. **Any CSV** with the supported column structures

### Test Scenarios
1. **Upload a small CSV** (< 1MB) to test basic functionality
2. **Upload a larger file** to test performance
3. **Try different file types** to test validation
4. **Use the chatbot** to ask questions about your data
5. **Generate charts** to test visualization engine
6. **Run advanced analysis** to test ML models

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Ensure you're in the project directory
cd "New Olynk"
# Install dependencies (Phase 2 includes ML libraries)
pip install -r backend/requirements.txt
```

**Port already in use**
```bash
# Change port in main.py or kill existing process
# Windows: netstat -ano | findstr :5000
# Then: taskkill /PID <PID> /F
```

**File upload errors**
- Check file size (max 50MB)
- Ensure file is valid CSV format
- Verify column headers match expected format

**Phase 2 features not working**
- Check if all dependencies are installed
- Verify the application shows "Phase 2" badge
- Check browser console for JavaScript errors

## 📚 API Endpoints

### Phase 1 Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/health` | GET | Health check endpoint |
| `/upload/<type>` | POST | Upload CSV file |
| `/analyze/<type>` | POST | Analyze uploaded data |
| `/analytics` | GET | Get overall analytics |
| `/insights` | GET | Get AI-generated insights |
| `/chatbot` | POST | Chat with AI about data |

### Phase 2 New Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/visualizations` | GET | Get dashboard visualizations |
| `/charts/<type>` | POST | Generate specific chart types |
| `/advanced-analysis/<type>` | POST | Run ML-powered analysis |

## 🤝 Contributing

This is an MVP implementation following the phase breakdown in `OLynk_AI_MVP_Phase_Breakdown.md`.

**Current Status**: Phase 2 complete with advanced analytics and ML features.

**Next Focus**: Phase 3 implementation for production readiness.

## 📄 License

This project is part of the OLynk AI platform development.

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the PRD and phase breakdown documents
3. Ensure all dependencies are installed correctly
4. Run the test suite to verify functionality

---

## 🎉 Phase 2 Achievement Unlocked!

**Your OLynk AI MVP now includes:**
- ✅ **Advanced Analytics Engine** with ML models
- ✅ **Interactive Visualizations** and charts
- ✅ **Enhanced AI Insights** with cross-dataset analysis
- ✅ **Performance Optimizations** for better user experience

**🚀 Ready to transform your data with AI & ML? Start the application and explore the new Phase 2 features!** 