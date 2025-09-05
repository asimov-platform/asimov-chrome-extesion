#!/usr/bin/env python3

import json
import sys
import subprocess
import os
import signal
import time
from typing import Dict, Any, Optional

class AsimovNativeHost:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        self.running = False
        sys.exit(0)
    
    def read_message(self) -> Optional[Dict[str, Any]]:
        try:
            raw_length = sys.stdin.buffer.read(4)
            if len(raw_length) == 0:
                return None
            
            message_length = int.from_bytes(raw_length, byteorder='little')
            message = sys.stdin.buffer.read(message_length).decode('utf-8')
            return json.loads(message)
        except Exception as e:
            self.send_error(f"Failed to read message: {str(e)}")
            return None
    
    def send_message(self, message: Dict[str, Any]):
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='little')
            sys.stdout.buffer.write(length_bytes)
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()
        except Exception:
            pass
    
    def send_error(self, error_message: str):
        self.send_message({
            "type": "error",
            "error": error_message,
            "timestamp": int(time.time() * 1000)
        })
    
    def find_asimov_path(self) -> Optional[str]:
        common_paths = [
            os.path.expanduser('~/.cargo/bin'),
            '/usr/local/bin',
            '/usr/bin',
            '/opt/homebrew/bin',
            '/usr/local/opt/asimov/bin',
        ]
        
        current_path = os.environ.get('PATH', '')
        for path in common_paths:
            if path not in current_path and os.path.exists(path):
                current_path = f"{path}:{current_path}"
        os.environ['PATH'] = current_path
        
        try:
            result = subprocess.run(['which', 'asimov'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                asimov_path = result.stdout.strip()
                if os.path.exists(asimov_path):
                    return asimov_path
        except:
            pass
        
        possible_paths = [
            os.path.expanduser('~/.cargo/bin/asimov'),
            '/usr/local/bin/asimov',
            '/usr/bin/asimov',
            '/opt/homebrew/bin/asimov',
            '/usr/local/opt/asimov/bin/asimov',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_shell_env_vars(self, env: Dict[str, str]):
        import platform
        
        system = platform.system().lower()
        
        if system == "windows":
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-Content $PROFILE 2>$null; if ($?) { & $PROFILE; Get-ChildItem Env: | ForEach-Object { "$($_.Name)=$($_.Value)" } }'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self._parse_env_output(result.stdout, env)
            except:
                pass
        else:
            shell_profiles = [
                '~/.zshrc',
                '~/.bash_profile', 
                '~/.bashrc',
                '~/.profile'
            ]
            
            for profile in shell_profiles:
                try:
                    result = subprocess.run(
                        ['bash', '-c', f'source {profile} 2>/dev/null && env'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self._parse_env_output(result.stdout, env)
                        break
                except:
                    continue
    
    def _parse_env_output(self, output: str, env: Dict[str, str]):
        for line in output.split('\n'):
            if '=' in line and not line.startswith('_'):
                try:
                    key, value = line.split('=', 1)
                    if key in ['READWISE_API_KEY', 'PATH', 'HOME', 'USER'] or key.startswith('ASIMOV_'):
                        env[key] = value
                except:
                    continue
    
    def execute_asimov_command(self, url: str) -> Dict[str, Any]:
        try:
            asimov_path = self.find_asimov_path()
            
            if not asimov_path:
                return {
                    "success": False,
                    "error": "asimov CLI not found. Please install asimov CLI first.",
                    "url": url
                }
            
            env = os.environ.copy()
            env['PATH'] = f"{os.path.dirname(asimov_path)}:{env.get('PATH', '')}"
            
            self._load_shell_env_vars(env)
            
            result = subprocess.run(
                [asimov_path, 'snapshot', url],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
                cwd=os.path.expanduser('~')
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip() or "Snapshot captured successfully",
                    "url": url,
                    "timestamp": int(time.time() * 1000)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or f"Command failed with exit code {result.returncode}",
                    "url": url,
                    "timestamp": int(time.time() * 1000)
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 60 seconds",
                "url": url,
                "timestamp": int(time.time() * 1000)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "url": url,
                "timestamp": int(time.time() * 1000)
            }
    
    def handle_message(self, message: Dict[str, Any]):
        try:
            message_type = message.get('type')
            
            if message_type == 'ping':
                self.send_message({
                    "type": "pong",
                    "timestamp": int(time.time() * 1000)
                })
                
            elif message_type == 'capture':
                url = message.get('url')
                if not url:
                    self.send_error("No URL provided for capture")
                    return
                
                result = self.execute_asimov_command(url)
                self.send_message({
                    "type": "capture_result",
                    **result
                })
                
            else:
                self.send_error(f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.send_error(f"Error handling message: {str(e)}")
    
    def run(self):
        print("ASIMOV Native Host started", file=sys.stderr)
        
        self.send_message({
            "type": "ready",
            "timestamp": int(time.time() * 1000)
        })
        
        while self.running:
            try:
                message = self.read_message()
                if message is None:
                    break
                self.handle_message(message)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.send_error(f"Unexpected error in main loop: {str(e)}")
                time.sleep(1)
        
        print("ASIMOV Native Host stopped", file=sys.stderr)

if __name__ == "__main__":
    host = AsimovNativeHost()
    host.run()