#!/usr/bin/env python3
"""
OLynk AI MVP - Main Application Entry Point
Phase 3: Week 11 - Production Deployment
"""

import os
import sys
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def setup_environment():
    """Setup environment for Phase 3"""
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_APP', 'main.py')

def setup_logging():
    """Setup logging configuration"""
    # Configure logging for Phase 3
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/olynk.log'),
            logging.StreamHandler()
        ]
    )

def print_startup_banner():
    """Print startup banner"""
    print("🚀 Starting OLynk AI MVP...")
    print("📁 Project Structure:")
    print("   ├── backend/     - Flask API and ML pipeline")
    print("   ├── frontend/    - HTML/CSS/JS interface")
    print("   ├── uploads/     - File storage")
    print("   ├── tests/       - Test suite")
    print("   ├── deployment/  - Production config")
    print("   └── main.py      - Application entry point")

def main():
    """Main application entry point"""
    print_startup_banner()
    setup_environment()
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    # Import app after setup
    try:
        from app import app
        logger.info("Phase 3 modules loaded successfully!")
    except ImportError as e:
        logger.error(f"Failed to import app: {e}")
        sys.exit(1)
    
    # Get configuration
    environment = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"📊 Upload CSV files to get AI-powered insights!")
    print(f"🔧 Environment: {environment}")
    print(f"📈 Phase: 3 - Launch Preparation")
    
    # Start the application
    if environment == 'production':
        # Use gunicorn for production
        import gunicorn.app.base
        
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': f'{host}:{port}',
            'workers': int(os.environ.get('WORKERS', 4)),
            'timeout': int(os.environ.get('TIMEOUT', 30)),
            'access_logfile': 'logs/access.log',
            'error_logfile': 'logs/error.log',
            'loglevel': 'info'
        }
        
        StandaloneApplication(app, options).run()
    else:
        # Use Flask development server
        app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    main() 