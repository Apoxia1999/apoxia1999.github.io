'use strict';

const status = document.getElementById('copy-status');
const canCopy = window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText;

if (canCopy) {
  for (const button of document.querySelectorAll('[data-copy]')) {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const code = document.getElementById(button.dataset.copy);
      try {
        await navigator.clipboard.writeText(code.textContent);
        status.textContent = 'Comando copiado. Ajusta la ruta al pegarlo en la Python Shell de Houdini.';
      } catch {
        status.textContent = 'El navegador no permitió copiar. Selecciona el comando y cópialo manualmente.';
      }
    });
  }
  const installerButton = document.getElementById('copy-installer');
  if (installerButton) {
    installerButton.hidden = false;
    const installerUrl = new URL('../../downloads/INSTALAR_EN_WINDOWS.txt', window.location.href);
    let installerPromise;
    // Start fetching ahead of the click so clipboard permissions retain the user gesture.
    const loadInstaller = () => installerPromise ||= fetch(installerUrl)
      .then(response => {
        if (!response.ok) throw new Error('Installer unavailable');
        return response.text();
      }).catch(error => {
        installerPromise = undefined;
        throw error;
      });
    installerButton.addEventListener('pointerenter', () => { loadInstaller().catch(() => {}); });
    installerButton.addEventListener('focus', () => { loadInstaller().catch(() => {}); });
    installerButton.addEventListener('click', async () => {
      installerButton.disabled = true;
      try {
        const text = await loadInstaller();
        if (!text.startsWith('import base64,zlib;') || text.length > 200000) {
          throw new Error('Unexpected installer format');
        }
        await navigator.clipboard.writeText(text.trim());
        status.textContent = 'Instalador copiado. Entra en Parsec, pégalo en la Python Shell del Houdini remoto y pulsa Enter.';
      } catch {
        status.textContent = 'No se pudo copiar automáticamente. Descarga el archivo de texto del enlace inferior y copia su línea completa.';
      } finally {
        installerButton.disabled = false;
      }
    });
  }
}
