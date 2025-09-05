#!/usr/bin/env python3

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path

class AsimovExtensionInstaller:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.host_script = self.script_dir / "asimov_host.py"
        self.manifest_file = self.script_dir / "com.asimov.host.json"
        self.system = platform.system().lower()
        
    def print_header(self):
        print("🚀 ASIMOV SNAPSHOT Chrome Extension Installer")
        print("=" * 50)
        print(f"🖥️  Detected system: {self.system.title()}")
        print()
        
    def check_files(self):
        if not self.host_script.exists():
            print(f"❌ Error: {self.host_script} not found")
            return False
            
        if not self.manifest_file.exists():
            print(f"❌ Error: {self.manifest_file} not found")
            return False
            
        return True
        
    def check_asimov_cli(self):
        print("🔍 Checking for Asimov CLI...")
        
        try:
            result = subprocess.run(['asimov', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Found Asimov CLI in PATH")
                return True
        except:
            pass
            
        common_paths = []
        if self.system == "windows":
            common_paths = [
                Path.home() / ".cargo" / "bin" / "asimov.exe",
                Path("C:/Program Files/asimov/asimov.exe"),
                Path("C:/Program Files (x86)/asimov/asimov.exe"),
            ]
        else:
            common_paths = [
                Path.home() / ".cargo" / "bin" / "asimov",
                Path("/usr/local/bin/asimov"),
                Path("/usr/bin/asimov"),
                Path("/opt/homebrew/bin/asimov"),
            ]
            
        for path in common_paths:
            if path.exists():
                print(f"✅ Found Asimov CLI at: {path}")
                return True
                
        print("❌ Asimov CLI not found!")
        print()
        print("Please install Asimov CLI first:")
        if self.system == "windows":
            print("  • Download from: https://github.com/asimov-ai/asimov")
            print("  • Or use Cargo: cargo install asimov")
        else:
            print("  • Cargo: cargo install asimov")
            print("  • Homebrew: brew install asimov")
            print("  • Or download from: https://github.com/asimov-ai/asimov")
        print()
        
        response = input("Press Enter after installing Asimov CLI, or 'q' to quit: ")
        if response.lower() == 'q':
            return False
            
        return self.check_asimov_cli()
        
    def get_chrome_manifest_dir(self):
        if self.system == "windows":
            return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts"
        elif self.system == "darwin":
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts"
        else:
            return Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts"
            
    def install_native_host(self):
        print("📦 Installing native host...")
        
        manifest_dir = self.get_chrome_manifest_dir()
        manifest_dir.mkdir(parents=True, exist_ok=True)
        
        host_script_dest = manifest_dir / "asimov_host.py"
        shutil.copy2(self.host_script, host_script_dest)
        
        if self.system != "windows":
            os.chmod(host_script_dest, 0o755)
            
        manifest_dest = manifest_dir / "com.asimov.host.json"
        
        with open(self.manifest_file, 'r') as f:
            manifest_data = json.load(f)
            
        manifest_data["path"] = str(host_script_dest)
        
        with open(manifest_dest, 'w') as f:
            json.dump(manifest_data, f, indent=2)
            
        print(f"✅ Native host installed to: {manifest_dir}")
        return True
        
    def test_installation(self):
        print("🧪 Testing installation...")
        
        try:
            if not self.host_script.exists():
                print("❌ Native host script not found")
                return False
                
            with open(self.host_script, 'r') as f:
                content = f.read()
                if 'AsimovNativeHost' in content:
                    print("✅ Native host script is valid")
                    return True
                else:
                    print("❌ Native host script appears to be invalid")
                    return False
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
            
    def print_next_steps(self):
        print()
        print("🎉 Installation complete!")
        print()
        print("📋 Next steps:")
        print("1. Open Chrome and go to chrome://extensions/")
        print("2. Enable 'Developer mode' (toggle in top right)")
        print("3. Click 'Load unpacked' and select this folder")
        print("4. Copy your Extension ID from the extensions page")
        print("5. Update the manifest with your Extension ID:")
        print()
        
        manifest_dir = self.get_chrome_manifest_dir()
        manifest_file = manifest_dir / "com.asimov.host.json"
        
        if self.system == "windows":
            print(f"   Edit: {manifest_file}")
            print("   Replace 'YOUR_EXTENSION_ID_HERE' with your actual Extension ID")
        else:
            print(f"   sed -i.bak 's/YOUR_EXTENSION_ID_HERE/YOUR_EXTENSION_ID/g' \"{manifest_file}\"")
            
        print()
        print("🎯 Then you can use the extension by clicking its icon on any webpage!")
        
    def run(self):
        self.print_header()
        
        if not self.check_files():
            return False
            
        if not self.check_asimov_cli():
            return False
            
        if not self.install_native_host():
            return False
            
        if not self.test_installation():
            return False
            
        self.print_next_steps()
        return True

if __name__ == "__main__":
    installer = AsimovExtensionInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)