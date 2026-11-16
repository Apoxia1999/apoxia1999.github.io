'use strict';

(() => {
  const messages = {
    es: {
      language: 'Idioma',
      homeDescription: 'Apoxia Toolkit. Herramientas y utilidades.',
      toolDescription: 'Houdini Node Copypaster v2.2. Copia nodos y animación entre equipos por Parsec.',
      nodeAlt: 'Nodo de Houdini Node Copypaster',
      cardDescription: 'Copia nodos y animación por Parsec.',
      empty: 'Vacío',
      toolSummary: 'Copia nodos, parámetros y animación entre equipos por Parsec.',
      integrity: 'SHA-256 del ZIP: <code>ff19e80314185e1099a6ff6a719f4606c36d5b45b613b4ea747113ca7d4f89ae</code>. Compruébalo antes de instalar; huellas de las tres descargas en <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      security: 'La v2.2 es una versión de seguridad: actualiza los dos equipos. Las versiones anteriores podían ejecutar código al pegar un portapapeles manipulado.',
      altIntro: 'Solo si no puedes copiar archivos al otro equipo. Es el mismo instalador comprimido en una línea: no se puede leer a simple vista, así que úsalo solo desde esta página.',
      download: 'Descargar ZIP ↓',
      copyInstaller: 'Copiar instalador',
      installation: 'Instalación y uso',
      step1: 'En ambos Houdini: extrae el ZIP, abre <strong>Windows → Python Shell</strong> y ejecuta el instalador con el comando de abajo.',
      step2: 'Selecciona los nodos y pulsa <strong>Copy Nodes</strong> en la pestaña <strong>Parsec Nodes v2.2</strong>.',
      step3: 'En el otro equipo, abre una red del mismo tipo y pulsa <strong>Paste Nodes</strong>.',
      clipboardNote: 'Activa el portapapeles de texto compartido de Parsec. También funciona entre redes locales.',
      manual: 'Alternativa: instalar por el portapapeles',
      manualIntro: 'Cambia la ruta por la carpeta donde extrajiste el ZIP:',
      manualCommand: "exec(open(r'RUTA/install_parsec_nodes.py', encoding='utf-8').read())",
      missingTab: 'Si no aparece la pestaña: <strong>+ de las shelves → Shelves → Parsec Nodes v2.2</strong>.',
      downloadInstaller: 'Descargar instalador en texto',
      fullInstructions: 'ZIP e instrucciones completas',
      copySuccess: 'Copiado. Pégalo en Windows → Python Shell de Houdini y pulsa Enter.',
      copyError: 'No se pudo copiar. Descarga el ZIP y usa el instalador incluido.',
      openTool: 'Abrir Houdini Node Copypaster'
    },
    en: {
      language: 'Language',
      homeDescription: 'Apoxia Toolkit. Tools and utilities.',
      toolDescription: 'Houdini Node Copypaster v2.2. Copy nodes and animation between computers through Parsec.',
      nodeAlt: 'Houdini Node Copypaster node',
      cardDescription: 'Copy nodes and animation through Parsec.',
      empty: 'Empty',
      toolSummary: 'Copy nodes, parameters and animation between computers through Parsec.',
      integrity: 'ZIP SHA-256: <code>ff19e80314185e1099a6ff6a719f4606c36d5b45b613b4ea747113ca7d4f89ae</code>. Check it before installing; hashes for the three downloads are in <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      security: 'v2.2 is a security release: update both computers. Earlier versions could run code when pasting a tampered clipboard.',
      altIntro: 'Only if you cannot copy files to the other computer. It is the same installer compressed into one line: it cannot be read at a glance, so only use it from this page.',
      download: 'Download ZIP ↓',
      copyInstaller: 'Copy installer',
      installation: 'Setup and usage',
      step1: 'In Houdini on both computers: extract the ZIP, open <strong>Windows → Python Shell</strong> and run the installer with the command below.',
      step2: 'Select your nodes and click <strong>Copy Nodes</strong> on the <strong>Parsec Nodes v2.2</strong> shelf.',
      step3: 'On the other computer, open a network of the same type and click <strong>Paste Nodes</strong>.',
      clipboardNote: 'Enable clipboard text sharing in Parsec. Copying between local networks works too.',
      manual: 'Fallback: install through the clipboard',
      manualIntro: 'Replace the path with the folder where you extracted the ZIP:',
      manualCommand: "exec(open(r'PATH/install_parsec_nodes.py', encoding='utf-8').read())",
      missingTab: 'If the shelf is missing: <strong>shelf + menu → Shelves → Parsec Nodes v2.2</strong>.',
      downloadInstaller: 'Download installer as text',
      fullInstructions: 'ZIP and full instructions',
      copySuccess: 'Copied. Paste it into Houdini’s Windows → Python Shell and press Enter.',
      copyError: 'Could not copy. Download the ZIP and use the bundled installer.',
      openTool: 'Open Houdini Node Copypaster'
    }
  };
  const supported = value => Object.hasOwn(messages, value);
  let language = 'es';
  try {
    const saved = window.localStorage.getItem('apoxia-language');
    language = supported(saved) ? saved : 'es';
  } catch {
    // The selector still works when browser storage is disabled.
  }
  const t = key => messages[language][key] ?? messages.es[key] ?? key;
  const apply = () => {
    document.documentElement.lang = language;
    document.querySelectorAll('[data-i18n]').forEach(element => {
      element.textContent = t(element.dataset.i18n);
    });
    // HTML translations are fixed strings defined above, never remote/user content.
    document.querySelectorAll('[data-i18n-html]').forEach(element => {
      element.innerHTML = t(element.dataset.i18nHtml);
    });
    for (const [attribute, dataKey] of [['alt', 'i18nAlt'], ['content', 'i18nContent'], ['aria-label', 'i18nAriaLabel']]) {
      document.querySelectorAll(`[data-${dataKey.replace(/[A-Z]/g, letter => '-' + letter.toLowerCase())}]`).forEach(element => {
        element.setAttribute(attribute, t(element.dataset[dataKey]));
      });
    }
    document.querySelectorAll('[data-language]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.language === language));
    });
  };
  window.ApoxiaI18n = {
    t,
    setMessage(element, key) {
      element.dataset.i18n = key;
      element.textContent = t(key);
    }
  };
  document.querySelectorAll('[data-language]').forEach(button => {
    button.addEventListener('click', () => {
      const next = button.dataset.language;
      if (!supported(next)) return;
      language = next;
      try { window.localStorage.setItem('apoxia-language', language); } catch {}
      apply();
    });
  });
  apply();
  document.querySelectorAll('.language-switch').forEach(selector => { selector.hidden = false; });
})();
