#!/usr/bin/env python3
"""
Deployment Script for OLynk AI MVP
Phase 3: Week 11 - Production Deployment
"""

import os
import sys
import subprocess
import argparse
import time
import requests
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    prerequisites = {
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version',
        'python': 'python --version',
        'pip': 'pip --version'
    }
    
    all_installed = True
    for tool, command in prerequisites.items():
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"✅ {tool} is installed")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not installed")
            all_installed = False
    
    return all_installed

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    return run_command("python run_tests.py", "Running tests")

def build_docker_image():
    """Build Docker image"""
    print("\n🐳 Building Docker image...")
    return run_command("docker build -t olynk-ai-mvp .", "Building Docker image")

def deploy_with_docker_compose(environment):
    """Deploy using Docker Compose"""
    print(f"\n🚀 Deploying to {environment} environment...")
    
    # Set environment variables
    env_file = f".env.{environment}"
    if not os.path.exists(env_file):
        print(f"⚠️  Environment file {env_file} not found, using defaults")
    
    # Start services
    if environment == 'production':
        command = "docker-compose -f docker-compose.yml up -d"
    else:
        command = "docker-compose -f docker-compose.yml up -d olynk-app"
    
    return run_command(command, f"Starting {environment} services")

def wait_for_service(url, timeout=60):
    """Wait for service to be ready"""
    print(f"⏳ Waiting for service at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Service is ready at {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    print(f"❌ Service failed to start within {timeout} seconds")
    return False

def run_health_checks():
    """Run health checks"""
    print("\n🏥 Running health checks...")
    
    health_endpoints = [
        "http://localhost:5000/health",
        "http://localhost:5000/analytics"
    ]
    
    all_healthy = True
    for endpoint in health_endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} is healthy")
            else:
                print(f"❌ {endpoint} returned status {response.status_code}")
                all_healthy = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} is not accessible: {e}")
            all_healthy = False
    
    return all_healthy

def rollback():
    """Rollback deployment"""
    print("\n🔄 Rolling back deployment...")
    run_command("docker-compose down", "Stopping services")
    run_command("docker-compose up -d olynk-app", "Starting previous version")

def cleanup():
    """Clean up resources"""
    print("\n🧹 Cleaning up...")
    run_command("docker system prune -f", "Cleaning up Docker resources")

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy OLynk AI MVP')
    parser.add_argument('environment', choices=['development', 'staging', 'production'],
                       help='Deployment environment')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests')
    parser.add_argument('--skip-build', action='store_true',
                       help='Skip building Docker image')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback to previous version')
    
    args = parser.parse_args()
    
    print("🚀 OLynk AI MVP - Deployment Script")
    print("=" * 50)
    print(f"Environment: {args.environment}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install required tools.")
        sys.exit(1)
    
    # Rollback if requested
    if args.rollback:
        rollback()
        return
    
    # Run tests (unless skipped)
    if not args.skip_tests:
        if not run_tests():
            print("❌ Tests failed. Deployment aborted.")
            sys.exit(1)
    
    # Build Docker image (unless skipped)
    if not args.skip_build:
        if not build_docker_image():
            print("❌ Docker build failed. Deployment aborted.")
            sys.exit(1)
    
    # Deploy
    if not deploy_with_docker_compose(args.environment):
        print("❌ Deployment failed.")
        rollback()
        sys.exit(1)
    
    # Wait for service to be ready
    if not wait_for_service("http://localhost:5000/health"):
        print("❌ Service failed to start.")
        rollback()
        sys.exit(1)
    
    # Run health checks
    if not run_health_checks():
        print("❌ Health checks failed.")
        rollback()
        sys.exit(1)
    
    # Cleanup
    cleanup()
    
    print("\n🎉 Deployment completed successfully!")
    print(f"🌐 Application is available at: http://localhost:5000")
    
    if args.environment == 'production':
        print("📊 Monitoring is available at:")
        print("   - Prometheus: http://localhost:9090")
        print("   - Grafana: http://localhost:3000")

if __name__ == '__main__':
    main()
