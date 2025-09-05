# ASIMOV SNAPSHOT - Chrome Extension

This folder contains the Chrome extension files for capturing snapshots using the Asimov CLI.

## Included Files:

- `manifest.json` - Chrome extension manifest
- `background.js` - Service worker that manages communication with the native host
- `logo.png` - Extension icon

## How to Use:

1. First install the local installer (from `../installer/` folder)
2. Run `python3 install.py` in the installer folder
3. Load this folder as an unpacked extension in Chrome
4. Update the Extension ID in the native host manifest file

## Features:

- One-click snapshot capture from web pages
- Native communication with local Asimov CLI
- Visual status interface (loading, success, error)
- Error handling with installation instructions