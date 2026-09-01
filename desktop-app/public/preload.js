const { contextBridge, ipcMain } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  encryptImage: (imagePath) => ipcMain.invoke('encrypt-image', imagePath),
  verifyImage: (imagePath) => ipcMain.invoke('verify-image', imagePath),
  getVersion: () => '1.0.0'
});
