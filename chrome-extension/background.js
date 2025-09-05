console.log('🚀 ASIMOV SNAPSHOT loaded with Native Messaging');

let nativePort = null;
let isConnected = false;

initNativeMessaging();

setTimeout(() => {
  if (!isConnected) {
    console.log('🔄 First retry...');
    initNativeMessaging();
  }
}, 3000);

setTimeout(() => {
  if (!isConnected) {
    console.log('🔄 Second retry...');
    initNativeMessaging();
  }
}, 8000);

setTimeout(() => {
  if (!isConnected) {
    console.log('🔄 Third retry...');
    initNativeMessaging();
  }
}, 15000);

chrome.action.onClicked.addListener(async (tab) => {
  console.log('🎯 Icon clicked for:', tab.url);
  
  if (!isConnected) {
    console.log('🔄 Attempting to reconnect...');
    initNativeMessaging();
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    if (!isConnected) {
      await showErrorNotification(tab.id, 'Native host not connected. Please run the installation script.');
      return;
    }
  }
  
  try {
    await showStatus(tab.id, 'loading');
    
    const result = await executeAsimovSnapshotNative(tab.url);
    console.log('✅ Result:', result);
    
    if (result.success) {
      await showStatus(tab.id, 'success');
      setTimeout(() => clearStatus(tab.id), 2000);
    } else {
      await showErrorNotification(tab.id, result.error || 'Capture failed');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
    await showErrorNotification(tab.id, error.message);
  }
});

async function initNativeMessaging() {
  try {
    console.log('🔗 Attempting to connect to native host...');
    nativePort = chrome.runtime.connectNative('com.asimov.host');
    
    nativePort.onMessage.addListener((message) => {
      console.log('📨 Received from native host:', message);
      handleNativeMessage(message);
    });
    
    nativePort.onDisconnect.addListener(() => {
      console.log('❌ Disconnected from native host');
      isConnected = false;
      nativePort = null;
      
      setTimeout(initNativeMessaging, 1000);
      setTimeout(() => {
        if (!isConnected) {
          console.log('🔄 Reconnecting after disconnect...');
          initNativeMessaging();
        }
      }, 5000);
    });
    
    nativePort.postMessage({ type: 'ping' });
    
    setTimeout(() => {
      if (!isConnected) {
        console.log('⏰ Ping timeout, marking as disconnected');
        isConnected = false;
      }
    }, 5000);
    
  } catch (error) {
    console.error('❌ Failed to connect to native host:', error);
    isConnected = false;
  }
}

function handleNativeMessage(message) {
  switch (message.type) {
    case 'ready':
      console.log('✅ Native host is ready');
      isConnected = true;
      break;
      
    case 'pong':
      console.log('✅ Received pong from native host');
      isConnected = true;
      break;
      
    case 'capture_result':
      console.log('📸 Capture result:', message);
      break;
      
    case 'error':
      console.error('❌ Native host error:', message.error);
      break;
      
    default:
      console.log('📨 Unknown message type:', message.type);
  }
}

async function executeAsimovSnapshotNative(url) {
  if (!isConnected || !nativePort) {
    throw new Error('Not connected to native host');
  }
  
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Native host timeout'));
    }, 30000);
    
    const messageListener = (message) => {
      console.log('Received message in listener:', message);
      if (message.type === 'capture_result') {
        clearTimeout(timeout);
        nativePort.onMessage.removeListener(messageListener);
        
        console.log('Processing capture_result:', message);
        if (message.success) {
          resolve(message);
        } else {
          reject(new Error(message.error || 'Capture failed'));
        }
      }
    };
    
    nativePort.onMessage.addListener(messageListener);
    
    const captureMessage = {
      type: 'capture',
      url: url,
      timestamp: Date.now()
    };
    console.log('📤 Sending capture message:', captureMessage);
    nativePort.postMessage(captureMessage);
  });
}

async function showStatus(tabId, type) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: showStatusInPage,
      args: [type]
    });
  } catch (error) {
    console.warn('Could not inject status overlay:', error);
  }
}

async function clearStatus(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: removeStatusInPage
    });
  } catch (error) {
    console.warn('Could not remove status overlay:', error);
  }
}

async function showErrorNotification(tabId, errorMessage) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: showErrorInPage,
      args: [errorMessage]
    });
  } catch (error) {
    console.warn('Could not inject error notification:', error);
  }
}

function showStatusInPage(type) {
  const existingOverlay = document.getElementById('asimov-status-overlay');
  if (existingOverlay) {
    existingOverlay.remove();
  }
  
  const overlay = document.createElement('div');
  overlay.id = 'asimov-status-overlay';
  
  let icon, bgColor, borderColor;
  switch (type) {
    case 'loading':
      icon = '⏳';
      bgColor = '#1a1a2e';
      borderColor = '#16213e';
      break;
    case 'success':
      icon = '✅';
      bgColor = '#0f3460';
      borderColor = '#16213e';
      break;
    case 'error':
      icon = '❌';
      bgColor = '#dc2626';
      borderColor = '#991b1b';
      break;
  }
  
  overlay.innerHTML = `<div class="asimov-status-icon">${icon}</div>`;
  
  const styles = document.createElement('style');
  styles.id = 'asimov-status-styles';
  styles.textContent = `
    #asimov-status-overlay {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 999999;
      opacity: 0;
      transform: scale(0.8);
      transition: all 0.2s ease;
    }
    
    #asimov-status-overlay.show {
      opacity: 1;
      transform: scale(1);
    }
    
    .asimov-status-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: ${bgColor};
      border: 2px solid ${borderColor};
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: ${type === 'loading' ? 'spin 1s linear infinite' : 'none'};
    }
    
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `;
  
  document.head.appendChild(styles);
  document.body.appendChild(overlay);
  
  setTimeout(() => {
    overlay.classList.add('show');
  }, 100);
}

function removeStatusInPage() {
  const overlay = document.getElementById('asimov-status-overlay');
  const styles = document.getElementById('asimov-status-styles');
  
  if (overlay) {
    overlay.classList.remove('show');
    setTimeout(() => {
      if (overlay && overlay.parentNode) {
        overlay.remove();
      }
    }, 200);
  }
  
  if (styles) {
    styles.remove();
  }
}

function showErrorInPage(errorMessage) {
  const existingOverlay = document.getElementById('asimov-error-overlay');
  if (existingOverlay) {
    existingOverlay.remove();
  }
  
  const overlay = document.createElement('div');
  overlay.id = 'asimov-error-overlay';
  
  const isAsimovError = errorMessage.includes('asimov CLI not found') || 
                       errorMessage.includes('command not found');
  
  overlay.innerHTML = `
    <div class="asimov-error-content">
      <div class="asimov-error-icon">❌</div>
      <div class="asimov-error-title">ASIMOV SNAPSHOT Error</div>
      <div class="asimov-error-message">${errorMessage}</div>
      ${isAsimovError ? `
        <div class="asimov-error-instructions">
          <strong>To fix this:</strong>
          <ol>
            <li>Install Asimov CLI: <code>cargo install asimov</code></li>
            <li>Download this extension repository</li>
            <li>Run: <code>python3 install.py</code></li>
            <li>Update Extension ID in manifest</li>
          </ol>
        </div>
      ` : ''}
      <button class="asimov-error-close" onclick="this.parentElement.parentElement.remove()">Close</button>
    </div>
  `;
  
  const styles = document.createElement('style');
  styles.id = 'asimov-error-styles';
  styles.textContent = `
    #asimov-error-overlay {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 999999;
      opacity: 0;
      transform: scale(0.8);
      transition: all 0.2s ease;
      max-width: 350px;
    }
    
    #asimov-error-overlay.show {
      opacity: 1;
      transform: scale(1);
    }
    
    .asimov-error-content {
      background: #1a1a2e;
      border: 2px solid #dc2626;
      border-radius: 12px;
      padding: 16px;
      color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .asimov-error-icon {
      font-size: 20px;
      text-align: center;
      margin-bottom: 8px;
    }
    
    .asimov-error-title {
      font-size: 14px;
      font-weight: 600;
      text-align: center;
      margin-bottom: 8px;
      color: #dc2626;
    }
    
    .asimov-error-message {
      font-size: 12px;
      margin-bottom: 12px;
      line-height: 1.3;
      color: #e5e7eb;
    }
    
    .asimov-error-instructions {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      border-radius: 6px;
      padding: 10px;
      margin-bottom: 10px;
    }
    
    .asimov-error-instructions strong {
      color: #fbbf24;
      display: block;
      margin-bottom: 6px;
      font-size: 11px;
    }
    
    .asimov-error-instructions ol {
      margin: 0;
      padding-left: 16px;
      font-size: 10px;
      line-height: 1.3;
    }
    
    .asimov-error-instructions li {
      margin-bottom: 2px;
    }
    
    .asimov-error-instructions code {
      background: rgba(0, 0, 0, 0.3);
      padding: 1px 3px;
      border-radius: 2px;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 9px;
    }
    
    .asimov-error-close {
      width: 100%;
      padding: 6px;
      border: none;
      border-radius: 4px;
      background: #3b82f6;
      color: white;
      font-size: 11px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }
    
    .asimov-error-close:hover {
      background: #2563eb;
    }
  `;
  
  document.head.appendChild(styles);
  document.body.appendChild(overlay);
  
  setTimeout(() => {
    overlay.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    if (overlay && overlay.parentNode) {
      overlay.classList.remove('show');
      setTimeout(() => {
        if (overlay && overlay.parentNode) {
          overlay.remove();
        }
        if (styles && styles.parentNode) {
          styles.remove();
        }
      }, 200);
    }
  }, 5000);
}