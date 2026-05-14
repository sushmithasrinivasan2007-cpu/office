#!/usr/bin/env python3
"""
SmartOS Quick Start - Runs both backend and frontend
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def cleanup_ports(ports):
    print(f"[0] Cleaning up ports {ports}...")
    for port in ports:
        try:
            # Find processes using the port
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            lines = result.stdout.split('\n')
            pids = set()
            for line in lines:
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids.add(pid)
            
            # Kill the processes
            for pid in pids:
                subprocess.run(
                    ["taskkill", "/F", "/PID", pid], 
                    capture_output=True
                )
                print(f"    Killed process {pid} using port {port}")
        except Exception as e:
            print(f"    Warning: Could not cleanup port {port}: {e}")

cleanup_ports([5000, 5173])

print("""
************************************************
*     SmartOS Development Server Starting...   *
************************************************
""")

# Check prerequisites
print("[1] Checking prerequisites...")
try:
    subprocess.run(["python", "--version"], capture_output=True, check=True)
    subprocess.run(["node", "--version"], capture_output=True, check=True)
    print("    [OK] Python & Node.js found")
except Exception as e:
    print(f"    [FAIL] Missing dependency: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Check backend .env
backend_env = Path("backend/.env")
if not backend_env.exists():
    print("\n[!] backend/.env not found!")
    print("    Creating from template...")
    import shutil
    shutil.copy("backend/.env.example", "backend/.env")
    print("\n    [!] Please edit backend/.env and add your Supabase keys:")
    print("       - SUPABASE_URL")
    print("       - SUPABASE_KEY")
    print("       - JWT_SECRET")
    input("\n    Press Enter after editing .env file...")

# Start backend
print("\n[2] Starting Backend (Flask API)...")
backend_proc = subprocess.Popen(
    [sys.executable, "app_socketio.py"],
    cwd="backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for backend
time.sleep(3)
if backend_proc.poll() is not None:
    print("    [FAIL] Backend failed to start. Check backend logs:")
    print(backend_proc.stdout.read())
    input("Press Enter to exit...")
    sys.exit(1)

print("    [OK] Backend running on http://localhost:5000")

# Start frontend
print("\n[3] Starting Frontend (React)...")
frontend_proc = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd="frontend",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(5)
if frontend_proc.poll() is not None:
    print("    [FAIL] Frontend failed to start")
    input("Press Enter to exit...")
    sys.exit(1)

print("    [OK] Frontend running on http://localhost:5173")

# Open browser
print("\n[4] Opening browser...")
time.sleep(1)
webbrowser.open("http://localhost:5173")

print("""
************************************************
*   SmartOS is running!                        *
*                                              *
*   Frontend: http://localhost:5173            *
*   Backend API: http://localhost:5000         *
*                                              *
*   Press Ctrl+C to stop both servers          *
************************************************
""")

try:
    # Keep running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nShutting down...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done!")