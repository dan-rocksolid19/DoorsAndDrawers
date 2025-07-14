#!/usr/bin/env python3
"""
Production deployment script using Waitress WSGI server.
Run this script to start the Django application in production mode.
"""

import os
import sys
import webbrowser
import threading
import time
from waitress import serve

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DoorsAndDrawers.settings')

# Import Django WSGI application
from DoorsAndDrawers.wsgi import application

if __name__ == '__main__':
    print("Starting DoorsAndDrawers application with Waitress...")
    print("Server will be available at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")

    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8080")

    threading.Thread(target=open_browser, daemon=True).start()

    # Serve the application with Waitress
    # You can customize host, port, and other settings as needed
    serve(
        application,
        host='0.0.0.0',  # Listen on all interfaces
        port=8080,       # Port to listen on
        threads=6,       # Number of threads to handle requests
        connection_limit=1000,  # Maximum number of connections
        cleanup_interval=30,    # Cleanup interval in seconds
    )
