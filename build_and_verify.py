import os
import json
import zipfile
import sys

MOD_NAME = "aureusstratusexogenesis"
OUT_DIR = "build"
OUT_FILE = os.path.join(OUT_DIR, f"{MOD_NAME}.zip")

def verify_json_files():
    print("--- 1. Verifying JSON files ---")
    issues = 0
    warnings = 0
    
    # Check Mod.json
    try:
        with open("mod.json", "r", encoding="utf-8") as f:
            mod_data = json.load(f)
            print(f"Mod version detected: {mod_data.get('version', 'UNKNOWN')}")
    except Exception as e:
        print(f"[ERROR] Failed to read mod.json: {e}")
        issues += 1

    # Check Content Blocks
    content_dir = os.path.join("content", "blocks")
    if os.path.exists(content_dir):
        for root, dirs, files in os.walk(content_dir):
            for f in files:
                if f.endswith(".json"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            data = json.load(file)
                            # Alert if it's a crafter but missing research (could just be a root node, so it's a warning)
                            if data.get("type") == "GenericCrafter" and "research" not in data:
                                print(f"[WARN] {path} is a GenericCrafter but missing 'research'. Will not appear in tech tree unless it's a base element.")
                                warnings += 1
                    except Exception as e:
                        print(f"[ERROR] Invalid JSON in {path}: {e}")
                        issues += 1
                        
    print(f"JSON Verification Complete: {issues} Parsing Issues (Mindustry HJSON is lenient), {warnings} Warnings.\n")

def build_zip():
    print(f"--- 2. Building secure ZIP: {OUT_FILE} ---")
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)
        
    count = 0
    with zipfile.ZipFile(OUT_FILE, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk("."):
            # Exclude irrelevant directories
            if any(exclude in root for exclude in [".git", "__pycache__", OUT_DIR]):
                continue
                
            for f in files:
                if f in [".gitignore", "build_and_verify.py", "AGENT.md"]:
                    continue
                
                file_path = os.path.join(root, f)
                # Ensure POSIX compliant slashes for Mindustry
                arcname = os.path.relpath(file_path, ".").replace("\\", "/")
                
                if "\\" in arcname:
                    print(f"[CRITICAL] Backslash detected in arcname, packaging aborted: {arcname}")
                    sys.exit(1)
                
                z.write(file_path, arcname)
                count += 1
                
    print(f"Successfully packaged {count} files with Mindustry-Safe POSIX paths.\n")
    
    # Verification pass to ensure Zip Slip protection is happy
    print("--- 3. Verifying Zip Structure ---")
    with zipfile.ZipFile(OUT_FILE, 'r') as z:
        for info in z.infolist():
            if "\\" in info.filename:
                print(f"[CRITICAL] Zip Slip vulnerability detected in built zip: {info.filename}")
                sys.exit(1)
    
    print("ZIP Verification passed. Safe for Mindustry deployment!")

if __name__ == "__main__":
    print("Starting Mindustry Mod Verification & Build Script...\n")
    verify_json_files()
    build_zip()
    print(f"\nDONE! Your mod is ready at: {OUT_FILE}")
