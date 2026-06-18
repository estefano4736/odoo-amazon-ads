#!/usr/bin/env python3
import os
import sys
import subprocess
import venv

# Target folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, ".venv")
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
CSS_DIR = os.path.join(STATIC_DIR, "css")
JS_DIR = os.path.join(STATIC_DIR, "js")
UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "data", "outputs")

def setup_directories():
    print("Creating local directories...")
    for directory in [DATA_DIR, CSS_DIR, JS_DIR, UPLOADS_DIR, OUTPUTS_DIR]:
        os.makedirs(directory, exist_ok=True)
    print("[OK] Directories ready.")

def create_virtual_env():
    if not os.path.exists(VENV_DIR):
        print(f"Creating Python virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        print("[OK] Virtual environment created.")
    else:
        print("[OK] Virtual environment already exists.")

def get_venv_bin(name):
    if os.name == 'nt':
        return os.path.join(VENV_DIR, 'Scripts', f'{name}.exe')
    return os.path.join(VENV_DIR, 'bin', name)

def install_dependencies():
    pip_bin = get_venv_bin('pip')
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    print("Checking and installing dependencies...")
    try:
        subprocess.check_call([pip_bin, "install", "--upgrade", "pip"])
        subprocess.check_call([pip_bin, "install", "-r", req_file])
        print("[OK] Dependencies installed successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        sys.exit(1)

def run_server():
    python_bin = get_venv_bin('python')
    main_file = os.path.join(BASE_DIR, "app", "main.py")
    
    # Check dotenv to load PORT and HOST
    port = 8000
    host = "127.0.0.1"
    
    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, *value = line.strip().split('=')
                    val = '='.join(value)
                    if key.strip() == 'PORT':
                        try:
                            port = int(val.strip())
                        except ValueError:
                            pass
                    elif key.strip() == 'HOST':
                        host = val.strip()

    print(f"Starting Amazon Ads Optimization Engine (AAOE) server on http://{host}:{port}...")
    
    try:
        # We run uvicorn programmatically or through subprocess. uvicorn is in .venv/bin/uvicorn
        uvicorn_bin = get_venv_bin('uvicorn')
        # Run subprocess to start backend
        subprocess.run([uvicorn_bin, "app.main:app", f"--host={host}", f"--port={port}", "--reload"], cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\nStopping AAOE server...")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_directories()
    # create_virtual_env()
    # install_dependencies()
    run_server()
