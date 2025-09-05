# ASIMOV SNAPSHOT - Native Host Installer

This repository contains the installer for the ASIMOV SNAPSHOT Chrome extension native host.

## What is ASIMOV SNAPSHOT?

ASIMOV SNAPSHOT is a Chrome extension that allows you to capture snapshots of web pages with a single click, using your local Asimov CLI.

## Quick Start

### 1. Install Asimov CLI
```bash
cargo install asimov
```

### 2. Install the Native Host
```bash
git clone https://github.com/yourusername/asimov-chrome-extension-installer.git
cd asimov-chrome-extension-installer
python3 installer/install.py
```

### 3. Install the Chrome Extension
- Go to the [Chrome Web Store](https://chrome.google.com/webstore)
- Search for "ASIMOV SNAPSHOT" and install the extension

### 4. Start Capturing Snapshots
- Click the ASIMOV SNAPSHOT icon on any webpage
- Watch as it captures the snapshot using your local Asimov CLI

## How It Works

1. **Chrome Extension**: Installed from Chrome Web Store, handles user interactions
2. **Native Host**: This installer sets up local communication between the extension and Asimov CLI
3. **Asimov CLI**: Executes the actual snapshot capture commands

## Requirements

- Python 3.6+
- Asimov CLI installed
- Chrome or Chromium browser

## Supported Systems

- ✅ macOS
- ✅ Linux  
- ✅ Windows

## Troubleshooting

### Extension not working?
1. Make sure you installed the native host using this installer
2. Check that Asimov CLI is installed: `asimov --version`
3. Restart Chrome after installation

### Need help?
- Check the [installer documentation](installer/README.md)
- Open an issue in this repository

## Security

This installer only sets up local communication between the Chrome extension and your Asimov CLI. No data is sent to external servers.

## License

[Add your license here]