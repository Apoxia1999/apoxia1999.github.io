'use strict';

const button = document.getElementById('copy-installer');
const status = document.getElementById('copy-status');

if (button && status && window.isSecureContext && navigator.clipboard?.writeText) {
  button.hidden = false;
  const url = new URL(button.dataset.installer, window.location.href);
  let pending;
  const load = () => pending ||= fetch(url).then(response => {
    if (!response.ok) throw new Error('Installer unavailable');
    return response.text();
  }).catch(error => {
    pending = undefined;
    throw error;
  });
  button.addEventListener('pointerenter', () => { load().catch(() => {}); });
  button.addEventListener('focus', () => { load().catch(() => {}); });
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      const text = await load();
      if (!text.startsWith('import base64,zlib;') || text.length > 200000) {
        throw new Error('Unexpected installer format');
      }
      await navigator.clipboard.writeText(text.trim());
      status.textContent = 'Copiado. Pégalo en Windows → Python Shell de Houdini y pulsa Enter.';
    } catch {
      status.textContent = 'No se pudo copiar. Usa «Instalación manual» para descargarlo.';
    } finally {
      button.disabled = false;
    }
  });
}
