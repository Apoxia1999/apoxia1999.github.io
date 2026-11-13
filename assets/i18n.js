'use strict';

(() => {
  const messages = {
    es: {
      language: 'Idioma',
      homeDescription: 'Apoxia Toolkit. Herramientas y utilidades.',
      toolDescription: 'Houdini Node Copypaster v2.1. Copia nodos y animación entre equipos por Parsec.',
      nodeAlt: 'Nodo de Houdini Node Copypaster',
      cardDescription: 'Copia nodos y animación por Parsec.',
      empty: 'Vacío',
      toolSummary: 'Copia nodos, parámetros y animación entre equipos por Parsec.',
      download: 'Descargar ZIP ↓',
      copyInstaller: 'Copiar instalador',
      installation: 'Instalación y uso',
      step1: 'En ambos Houdini: abre <strong>Windows → Python Shell</strong>, pega el instalador y pulsa Enter.',
      step2: 'Selecciona los nodos y pulsa <strong>Copy Nodes</strong> en la pestaña <strong>Parsec Nodes v2.1</strong>.',
      step3: 'En el otro equipo, abre una red del mismo tipo y pulsa <strong>Paste Nodes</strong>.',
      clipboardNote: 'Activa el portapapeles de texto compartido de Parsec. También funciona entre redes locales.',
      manual: 'Instalación manual',
      manualIntro: 'Extrae el ZIP y ejecuta esto en la Python Shell, cambiando la ruta:',
      manualCommand: "exec(open(r'RUTA/install_parsec_nodes.py', encoding='utf-8').read())",
      missingTab: 'Si no aparece la pestaña: <strong>+ de las shelves → Shelves → Parsec Nodes v2.1</strong>.',
      downloadInstaller: 'Descargar instalador en texto',
      fullInstructions: 'ZIP e instrucciones completas',
      copySuccess: 'Copiado. Pégalo en Windows → Python Shell de Houdini y pulsa Enter.',
      copyError: 'No se pudo copiar. Usa «Instalación manual» para descargarlo.',
      openTool: 'Abrir Houdini Node Copypaster'
    },
    en: {
      language: 'Language',
      homeDescription: 'Apoxia Toolkit. Tools and utilities.',
      toolDescription: 'Houdini Node Copypaster v2.1. Copy nodes and animation between computers through Parsec.',
      nodeAlt: 'Houdini Node Copypaster node',
      cardDescription: 'Copy nodes and animation through Parsec.',
      empty: 'Empty',
      toolSummary: 'Copy nodes, parameters and animation between computers through Parsec.',
      download: 'Download ZIP ↓',
      copyInstaller: 'Copy installer',
      installation: 'Setup and usage',
      step1: 'In Houdini on both computers: open <strong>Windows → Python Shell</strong>, paste the installer and press Enter.',
      step2: 'Select your nodes and click <strong>Copy Nodes</strong> on the <strong>Parsec Nodes v2.1</strong> shelf.',
      step3: 'On the other computer, open a network of the same type and click <strong>Paste Nodes</strong>.',
      clipboardNote: 'Enable clipboard text sharing in Parsec. Copying between local networks works too.',
      manual: 'Manual installation',
      manualIntro: 'Extract the ZIP and run this in the Python Shell, replacing the path:',
      manualCommand: "exec(open(r'PATH/install_parsec_nodes.py', encoding='utf-8').read())",
      missingTab: 'If the shelf is missing: <strong>shelf + menu → Shelves → Parsec Nodes v2.1</strong>.',
      downloadInstaller: 'Download installer as text',
      fullInstructions: 'ZIP and full instructions',
      copySuccess: 'Copied. Paste it into Houdini’s Windows → Python Shell and press Enter.',
      copyError: 'Could not copy. Use “Manual installation” to download it.',
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
