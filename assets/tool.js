'use strict';

const button = document.getElementById('copy-installer');
const status = document.getElementById('copy-status');

if (button && status && window.isSecureContext && navigator.clipboard?.writeText) {
  button.hidden = false;
  const url = new URL(button.dataset.installer, window.location.href);
  // Each page can declare what the copied file must start with and which messages to show.
  const prefix = button.dataset.prefix ?? 'import base64,zlib;';
  const successKey = button.dataset.successKey ?? 'copySuccess';
  const errorKey = button.dataset.errorKey ?? 'copyError';
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
      if (!text.startsWith(prefix) || text.length > 200000) {
        throw new Error('Unexpected installer format');
      }
      await navigator.clipboard.writeText(text.trim());
      window.ApoxiaI18n.setMessage(status, successKey);
    } catch {
      window.ApoxiaI18n.setMessage(status, errorKey);
    } finally {
      button.disabled = false;
    }
  });
}
