#!/usr/bin/env python3
"""
Unified launcher for Task Manager application
Starts both backend API and frontend UI
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
import signal
import argparse

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║     📋 TASK MANAGER SYSTEM v1.0         ║
    ║     Full Stack Application              ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

def run_backend():
    """Run FastAPI backend server"""
    print("🚀 Starting Backend Server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_frontend():
    """Run Streamlit frontend"""
    print("🎨 Starting Frontend UI...")
    time.sleep(2)  # Give backend time to start
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

def open_browser():
    """Open browser automatically"""
    time.sleep(4)
    webbrowser.open("http://localhost:8501")
    print("\n✅ Application ready!")
    print("📱 Frontend: http://localhost:8501")
    print("📡 API Docs: http://localhost:8000/docs")
    print("🔍 API Redoc: http://localhost:8000/redoc")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down Task Manager...")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Task Manager Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Run only backend")
    parser.add_argument("--frontend-only", action="store_true", help="Run only frontend")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()
    
    print_banner()
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if args.backend_only:
        print("Running in backend-only mode")
        run_backend()
    elif args.frontend_only:
        print("Running in frontend-only mode")
        run_frontend()
    else:
        print("Starting full application...")
        
        # Start backend in a thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend in a thread
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        
        # Open browser if not disabled
        if not args.no_browser:
            threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            sys.exit(0)

if __name__ == "__main__":
    main()