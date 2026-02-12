#!/usr/bin/env python
"""
Scalable AI System - Combined Startup Script
Starts all modules: Backend, Vision, and Audio
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
import signal
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SystemStartup")

# Project paths
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
VISION_DIR = PROJECT_ROOT / "ai-modules" / "vision"
AUDIO_DIR = PROJECT_ROOT / "ai-modules" / "audio"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Python interpreter
PYTHON = sys.executable

# Store processes for cleanup
processes = []


def run_process(cmd, name, cwd=None):
    """Run a process and track it"""
    logger.info(f"Starting {name}...")
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            stdout=None,  # Inherit stdout
            stderr=None,  # Inherit stderr
            text=True,
            bufsize=1
        )
        processes.append(process)
        logger.info(f"{name} started (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        return None


def check_dependencies():
    """Verify all required packages are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", "requests",
        "opencv-python", "ultralytics", "numpy", "mediapipe",
        "sounddevice", "librosa", "react"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
        logger.info("Run: pip install -r requirements.txt")
    else:
        logger.info("All dependencies available")


def start_backend():
    """Start FastAPI backend server"""
    logger.info("=" * 60)
    logger.info("Starting Backend Server (FastAPI)")
    logger.info("=" * 60)
    
    cmd = [PYTHON, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    process = run_process(cmd, "Backend", PROJECT_ROOT)
    return process


def start_vision():
    """Start vision module"""
    logger.info("=" * 60)
    logger.info("Starting Vision Module")
    logger.info("=" * 60)
    
    cmd = [PYTHON, "main.py"]
    process = run_process(cmd, "Vision", VISION_DIR)
    return process


def start_audio():
    """Start audio module"""
    logger.info("=" * 60)
    logger.info("Starting Audio Module")
    logger.info("=" * 60)
    
    cmd = [PYTHON, "main.py"]
    process = run_process(cmd, "Audio", AUDIO_DIR)
    return process


def start_frontend():
    """Start frontend development server"""
    logger.info("=" * 60)
    logger.info("Starting Frontend (Vite Dev Server)")
    logger.info("=" * 60)
    
    # Use npm.cmd on Windows
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    cmd = [npm_cmd, "run", "dev"]
    process = run_process(cmd, "Frontend", FRONTEND_DIR)
    return process


def cleanup(signum=None, frame=None):
    """Cleanup and terminate all processes"""
    logger.info("\n" + "=" * 60)
    logger.info("Shutting down all services...")
    logger.info("=" * 60)
    
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"Terminated process {process.pid}")
        except subprocess.TimeoutExpired:
            process.kill()
            logger.warning(f"Killed process {process.pid}")
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
    
    logger.info("All services stopped")
    sys.exit(0)


def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("Scalable AI Exam Monitoring System")
    logger.info("Starting all modules...")
    logger.info("=" * 60)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Check dependencies
    check_dependencies()
    time.sleep(1)
    
    # Start services in order
    backend = start_backend()
    time.sleep(3)  # Wait for backend to start
    
    vision = start_vision()
    time.sleep(2)
    
    audio = start_audio()
    time.sleep(2)
    
    frontend = start_frontend()
    time.sleep(2)
    
    logger.info("=" * 60)
    logger.info("SYSTEM READY")
    logger.info("=" * 60)
    logger.info("Backend:  http://localhost:8000 (API)")
    logger.info("Backend:  http://localhost:8000/docs (API Docs)")
    logger.info("Frontend: http://localhost:3000 (Dashboard)")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 60)
    
    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for process in processes:
                if process and process.poll() is not None:
                    logger.warning(f"Process {process.pid} has terminated")
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
