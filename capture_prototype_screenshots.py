"""
Automated Screenshot Capture for MutationHunter Prototype
Uses Chrome headless mode to capture all four interactive prototype views.
"""

import os
import time
import subprocess
import urllib.request

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = "screenshots"

def wait_for_server(url="http://127.0.0.1:5000/", timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    print("Server is up and responding!")
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def capture_url(url, output_file, width=1440, height=900):
    abs_output = os.path.abspath(output_file)
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={abs_output}",
        url
    ]
    print(f"Capturing: {url} -> {abs_output}")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if os.path.exists(abs_output) and os.path.getsize(abs_output) > 1000:
        print(f"  Successfully captured: {abs_output} ({os.path.getsize(abs_output) // 1024} KB)")
        return True
    else:
        print(f"  Failed or empty screenshot for {abs_output}. Stderr: {res.stderr}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Start Flask app
    print("Launching prototype server on http://127.0.0.1:5000 ...")
    server_proc = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        if not wait_for_server("http://127.0.0.1:5000/", timeout=15):
            print("ERROR: Server failed to start within timeout.")
            return
            
        time.sleep(1.0)
        
        # 2. Capture Views
        views = [
            ("http://127.0.0.1:5000/?tab=overview", os.path.join(OUTPUT_DIR, "01_dashboard_overview.png"), 1440, 960),
            ("http://127.0.0.1:5000/?tab=nic", os.path.join(OUTPUT_DIR, "02_nic_algorithms_ga_pso.png"), 1440, 1100),
            ("http://127.0.0.1:5000/?tab=comparison", os.path.join(OUTPUT_DIR, "03_model_comparison_metrics.png"), 1440, 1150),
            ("http://127.0.0.1:5000/?tab=predictor&preset=conflict", os.path.join(OUTPUT_DIR, "04_clinical_predictor_live.png"), 1440, 960)
        ]
        
        for url, out_path, w, h in views:
            capture_url(url, out_path, width=w, height=h)
            time.sleep(1.0)
            
    finally:
        print("Stopping prototype server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except Exception:
            server_proc.kill()
            
    print("\nAll screenshot tasks finished.")

if __name__ == "__main__":
    main()
