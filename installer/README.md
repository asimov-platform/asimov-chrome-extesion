# ASIMOV SNAPSHOT - Native Host Installer

This installer sets up the native host required for the ASIMOV SNAPSHOT Chrome extension to communicate with your local Asimov CLI.

## What This Does

- Installs the native host that allows the Chrome extension to execute Asimov CLI commands
- Configures Chrome to allow communication between the extension and local CLI
- Sets up proper permissions and file locations

## Installation Steps

### 1. Install Asimov CLI
Make sure you have Asimov CLI installed on your system:
```bash
cargo install asimov
```

### 2. Install the Native Host
Run this installer to set up the native host:
```bash
python3 install.py
```

### 3. Install the Chrome Extension
- Go to the [Chrome Web Store](https://chrome.google.com/webstore)
- Search for "ASIMOV SNAPSHOT" and install the extension
- The extension will automatically connect to the native host

### 4. Start Using
- Click the ASIMOV SNAPSHOT icon on any webpage
- The extension will capture snapshots using your local Asimov CLI

## Requirements

- Python 3.6+
- Asimov CLI installed
- Chrome or Chromium browser

## Troubleshooting

### "Native host not connected"
- Make sure you ran this installer successfully
- Check that the extension is installed from Chrome Web Store
- Restart Chrome after installation

### "Asimov CLI not found"
- Install Asimov CLI: `cargo install asimov`
- Make sure it's in your PATH
- Test with: `asimov --version`

## Files Installed

This installer places files in your Chrome NativeMessagingHosts directory:
- `asimov_host.py` - Native host script
- `com.asimov.host.json` - Native host manifest

## Security

This installer only sets up local communication between the Chrome extension and your Asimov CLI. No data is sent to external servers.