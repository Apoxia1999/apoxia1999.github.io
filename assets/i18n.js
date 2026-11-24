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
      openTool: 'Abrir Houdini Node Copypaster',
      absDescription: 'Houdini Absolute Paths v1.1. Convierte $HIP y $JOB en rutas absolutas en toda la escena.',
      absNodeAlt: 'Nodo de Houdini Absolute Paths',
      absCardDescription: 'Convierte $HIP en rutas absolutas.',
      absSummary: 'Convierte $HIP, $HIPNAME, $HIPFILE y $JOB en rutas absolutas en toda la escena, para copiar el .hip sin romper ningún link.',
      absDownload: 'Descargar script ↓',
      absCopy: 'Copiar script',
      absCopySuccess: 'Copiado. Pégalo en Windows → Python Source Editor de Houdini y pulsa Apply.',
      absCopyError: 'No se pudo copiar. Descarga el script.',
      absCopyNote: 'O copia el script y pégalo en <strong>Windows → Python Source Editor</strong>; pulsa <strong>Apply</strong> para ejecutarlo.',
      absIntegrity: 'Huella SHA-256 del script en <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      absUsage: 'Uso',
      absStep1: 'Con la escena abierta, abre <strong>Windows → Python Shell</strong> y ejecuta el script con el comando de abajo.',
      absStep2: 'Revisa en la consola la lista de parámetros cambiados (ruta anterior y nueva) y los omitidos.',
      absStep3: 'Guarda el .hip. Todo el cambio es un solo paso de <strong>Undo</strong>.',
      absCommandIntro: 'Cambia la ruta por la carpeta donde descargaste el script:',
      absCommand: "exec(open(r'RUTA/hip_to_absolute_paths.py', encoding='utf-8').read())",
      absDryRun: 'Para ver qué cambiaría sin tocar nada, pon <code>DRY_RUN = True</code> al inicio del script.',
      absKeeps: 'Se conservan $F, $F4, $OS, <UDIM> y el resto de variables. También fija el Base Name del File Cache, que usa $HIPNAME.',
      absSkips: 'No toca el interior de HDAs bloqueados, los parámetros bloqueados ni las expresiones que usan $HIP: los lista como omitidos para revisarlos a mano.',
      absRops: 'Los ROPs y nodos de render no se tocan: sus rutas de salida siguen al .hip copiado, así no se sobrescriben los renders originales. El File Cache sí se convierte. Pon <code>SKIP_ROPS = False</code> para convertirlos también.',
      absCaches: 'Los caches no se mueven: las rutas quedan apuntando a su ubicación actual.',
      fbDescription: 'Focus v1.0. Pon la distancia de enfoque de la cámara de Houdini con un clic en el viewport.',
      fbAlt: 'Cámara de Houdini enfocando un objeto',
      fbCardDescription: 'Enfoca la cámara con un clic.',
      fbSummary: 'Haz clic en el viewport y la cámara por la que miras pone su distancia de enfoque en ese punto de la geometría.',
      fbDownload: 'Descargar script ↓',
      fbCopy: 'Copiar script',
      fbCopySuccess: 'Copiado. Pégalo en la pestaña Script de una nueva herramienta del shelf.',
      fbCopyError: 'No se pudo copiar. Descarga el script.',
      fbIntegrity: 'Huella SHA-256 del script en <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      fbInstall: 'Instalación',
      fbStep1: 'En un shelf, clic derecho → <strong>New Tool…</strong> y ponle de nombre <strong>Focus</strong>.',
      fbStep2: 'En la pestaña <strong>Script</strong>, con el lenguaje en Python, pega el script y pulsa <strong>Accept</strong>.',
      fbUsage: 'Uso',
      fbUse1: 'Mira a través de la cámara en el viewport.',
      fbUse2: 'Pulsa <strong>Focus</strong> en el shelf.',
      fbUse3: 'Haz clic en la geometría que quieres enfocar. La Focus Distance de la cámara cambia a esa distancia. <strong>Esc</strong> para salir sin cambiar nada.',
      fbHow: 'Mide la profundidad del punto a lo largo del eje de la cámara, que es lo que usa el plano de foco. Si la Focus Distance está animada, crea un keyframe en el frame actual. Se deshace con un solo Undo.',
      fbLimit: 'Funciona con cámaras de OBJ, en contexto OBJ o SOP. No funciona en Solaris (LOPs).',
      cbDescription: 'Camera Bake v1.0. Hornea una cámara de Houdini con un keyframe en cada frame, en espacio mundo.',
      cbAlt: 'Cámara de Houdini con un keyframe en cada frame',
      cbCardDescription: 'Hornea la cámara frame a frame.',
      cbSummary: 'Crea una copia de la cámara con un keyframe en cada frame, en espacio mundo y sin padres ni constraints. Lista para exportar a FBX, Alembic o USD.',
      cbDownload: 'Descargar script ↓',
      cbCopy: 'Copiar script',
      cbCopySuccess: 'Copiado. Pégalo en la pestaña Script de una nueva herramienta del shelf.',
      cbCopyError: 'No se pudo copiar. Descarga el script.',
      cbIntegrity: 'Huella SHA-256 del script en <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      cbInstall: 'Instalación',
      cbStep1: 'En un shelf, clic derecho → <strong>New Tool…</strong> y ponle de nombre <strong>Camera Bake</strong>.',
      cbStep2: 'En la pestaña <strong>Script</strong>, con el lenguaje en Python, pega el script y pulsa <strong>Accept</strong>.',
      cbUsage: 'Uso',
      cbUse1: 'Selecciona una o varias cámaras, o mira a través de una en el viewport.',
      cbUse2: 'Pulsa <strong>Camera Bake</strong> en el shelf y confirma el rango de frames (por defecto, el del playbar).',
      cbUse3: 'Aparece <strong>&lt;cámara&gt;_baked</strong> en /obj. Si ya existe, te pregunta si reemplazarla. Exporta esa, no la original.',
      cbHow: 'Hornea la posición y rotación en espacio mundo, con todo lo que mueve la cámara: padres, constraints, Look At, Follow Path, CHOPs y expresiones. Copia todos los parámetros de la cámara, también los extra de render (Karma, Redshift…): los animados se hornean frame a frame y el resto queda como valor fijo, sin referencias a otros nodos. Corrige los saltos de 360° en la rotación.',
      cbKeeps: 'La cámara original no se toca. Se deshace con un solo Undo y <strong>Esc</strong> cancela el horneado.',
      cbLimit: 'Funciona con cámaras de OBJ. La escala de los padres no se copia: si la jerarquía tiene escala, el script avisa.',
      frDescription: 'AFX Frame Reader v1.0. Expresión de After Effects que muestra qué frames de la secuencia usa la capa de debajo.',
      frAlt: 'Capa de texto de After Effects mostrando el rango de frames de la secuencia de debajo',
      frCardDescription: 'Lee qué frames usa la secuencia.',
      frSummary: 'Una capa de texto que te dice qué frames de la secuencia de render se ven en la composición, y cuántos son.',
      frDownload: 'Descargar expresión ↓',
      frCopy: 'Copiar expresión',
      frCopySuccess: 'Copiado. Pégalo en la expresión de Source Text de una capa de texto.',
      frCopyError: 'No se pudo copiar. Descarga la expresión.',
      frIntegrity: 'Huella SHA-256 de la expresión en <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      frUsage: 'Uso',
      frStep1: 'Crea una capa de texto <strong>encima</strong> de la secuencia que quieres medir.',
      frStep2: 'Despliega <strong>Text</strong>, haz <strong>Alt + clic</strong> en el cronómetro de <strong>Source Text</strong> y pega la expresión.',
      frStep3: 'El texto muestra <strong>primer frame - último frame | total</strong> de la parte que se ve en la composición.',
      frHow: 'Lee la primera capa de metraje visible por debajo del texto en el frame actual, así que puedes moverte por el timeline y va cambiando de capa. Tiene en cuenta el recorte de la capa, el time stretch y el time remap.',
      frNames: 'Saca el número del primer frame del nombre: <code>render_[1001-1100].exr</code> o <code>render_1001.exr</code>. Si el nombre no tiene números, empieza a contar desde 1.',
      frLimit: 'Ignora capas de texto, formas, cámaras y luces, y las capas con opacidad 0. Si no encuentra ninguna, muestra «No visible footage layer».'
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
      openTool: 'Open Houdini Node Copypaster',
      absDescription: 'Houdini Absolute Paths v1.1. Turn $HIP and $JOB into absolute paths across the whole scene.',
      absNodeAlt: 'Houdini Absolute Paths node',
      absCardDescription: 'Turn $HIP into absolute paths.',
      absSummary: 'Turn $HIP, $HIPNAME, $HIPFILE and $JOB into absolute paths across the whole scene, so you can copy the .hip without breaking any link.',
      absDownload: 'Download script ↓',
      absCopy: 'Copy script',
      absCopySuccess: 'Copied. Paste it into Houdini’s Windows → Python Source Editor and click Apply.',
      absCopyError: 'Could not copy. Download the script instead.',
      absCopyNote: 'Or copy the script and paste it into <strong>Windows → Python Source Editor</strong>; click <strong>Apply</strong> to run it.',
      absIntegrity: 'The script’s SHA-256 hash is in <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      absUsage: 'Usage',
      absStep1: 'With the scene open, open <strong>Windows → Python Shell</strong> and run the script with the command below.',
      absStep2: 'Check the console for the list of changed parameters (old and new path) and the skipped ones.',
      absStep3: 'Save the .hip. The whole change is a single <strong>Undo</strong> step.',
      absCommandIntro: 'Replace the path with the folder where you downloaded the script:',
      absCommand: "exec(open(r'PATH/hip_to_absolute_paths.py', encoding='utf-8').read())",
      absDryRun: 'To see what would change without touching anything, set <code>DRY_RUN = True</code> at the top of the script.',
      absKeeps: '$F, $F4, $OS, <UDIM> and every other variable are kept. It also pins the File Cache Base Name, which uses $HIPNAME.',
      absSkips: 'It does not touch the inside of locked HDAs, locked parameters or expressions that use $HIP: those are listed as skipped so you can review them by hand.',
      absRops: 'ROPs and render nodes are left alone: their output paths follow the copied .hip, so the original renders are not overwritten. File Cache is still converted. Set <code>SKIP_ROPS = False</code> to convert them too.',
      absCaches: 'Caches are not moved: the paths keep pointing at their current location.',
      fbDescription: 'Focus v1.0. Set the Houdini camera focus distance with one click in the viewport.',
      fbAlt: 'Houdini camera focusing on an object',
      fbCardDescription: 'Focus the camera with one click.',
      fbSummary: 'Click in the viewport and the camera you are looking through sets its focus distance to that point on the geometry.',
      fbDownload: 'Download script ↓',
      fbCopy: 'Copy script',
      fbCopySuccess: 'Copied. Paste it into the Script tab of a new shelf tool.',
      fbCopyError: 'Could not copy. Download the script instead.',
      fbIntegrity: 'The script’s SHA-256 hash is in <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      fbInstall: 'Installation',
      fbStep1: 'Right-click a shelf → <strong>New Tool…</strong> and name it <strong>Focus</strong>.',
      fbStep2: 'In the <strong>Script</strong> tab, with the language set to Python, paste the script and click <strong>Accept</strong>.',
      fbUsage: 'Usage',
      fbUse1: 'Look through the camera in the viewport.',
      fbUse2: 'Click <strong>Focus</strong> on the shelf.',
      fbUse3: 'Click the geometry you want in focus. The camera Focus Distance changes to that distance. <strong>Esc</strong> exits without changing anything.',
      fbHow: 'It measures the point depth along the camera axis, which is what the focus plane uses. If Focus Distance is animated, it sets a keyframe on the current frame. A single Undo reverts it.',
      fbLimit: 'Works with OBJ cameras, in OBJ or SOP context. Does not work in Solaris (LOPs).',
      cbDescription: 'Camera Bake v1.0. Bake a Houdini camera to one keyframe per frame, in world space.',
      cbAlt: 'Houdini camera with a keyframe on every frame',
      cbCardDescription: 'Bake the camera frame by frame.',
      cbSummary: 'Creates a copy of the camera with a keyframe on every frame, in world space, with no parents or constraints. Ready to export to FBX, Alembic or USD.',
      cbDownload: 'Download script ↓',
      cbCopy: 'Copy script',
      cbCopySuccess: 'Copied. Paste it into the Script tab of a new shelf tool.',
      cbCopyError: 'Could not copy. Download the script instead.',
      cbIntegrity: 'The script’s SHA-256 hash is in <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      cbInstall: 'Installation',
      cbStep1: 'Right-click a shelf → <strong>New Tool…</strong> and name it <strong>Camera Bake</strong>.',
      cbStep2: 'In the <strong>Script</strong> tab, with the language set to Python, paste the script and click <strong>Accept</strong>.',
      cbUsage: 'Usage',
      cbUse1: 'Select one or more cameras, or look through one in the viewport.',
      cbUse2: 'Click <strong>Camera Bake</strong> on the shelf and confirm the frame range (the playbar range by default).',
      cbUse3: '<strong>&lt;camera&gt;_baked</strong> appears in /obj. If it already exists, it asks whether to replace it. Export that one, not the original.',
      cbHow: 'It bakes world-space position and rotation, including everything that moves the camera: parents, constraints, Look At, Follow Path, CHOPs and expressions. It copies every camera parameter, including extra render ones (Karma, Redshift…): animated ones are baked frame by frame and the rest are set as fixed values, with no references to other nodes. It fixes 360° jumps in rotation.',
      cbKeeps: 'The original camera is left untouched. A single Undo reverts it and <strong>Esc</strong> cancels the bake.',
      cbLimit: 'Works with OBJ cameras. Parent scale is not copied: if the hierarchy is scaled, the script warns you.',
      frDescription: 'AFX Frame Reader v1.0. After Effects expression that shows which sequence frames the layer below uses.',
      frAlt: 'After Effects text layer showing the frame range of the sequence below',
      frCardDescription: 'Read which frames the sequence uses.',
      frSummary: 'A text layer that tells you which frames of the render sequence show up in the comp, and how many there are.',
      frDownload: 'Download expression ↓',
      frCopy: 'Copy expression',
      frCopySuccess: 'Copied. Paste it into the Source Text expression of a text layer.',
      frCopyError: 'Could not copy. Download the expression instead.',
      frIntegrity: 'The expression’s SHA-256 hash is in <a href="../downloads/SHA256SUMS">SHA256SUMS</a>.',
      frUsage: 'Usage',
      frStep1: 'Create a text layer <strong>above</strong> the sequence you want to measure.',
      frStep2: 'Expand <strong>Text</strong>, <strong>Alt + click</strong> the <strong>Source Text</strong> stopwatch and paste the expression.',
      frStep3: 'The text shows <strong>first frame - last frame | total</strong> for the part visible in the comp.',
      frHow: 'It reads the first visible footage layer below the text on the current frame, so it switches layers as you scrub the timeline. It accounts for layer trimming, time stretch and time remap.',
      frNames: 'It takes the first frame number from the name: <code>render_[1001-1100].exr</code> or <code>render_1001.exr</code>. If the name has no numbers, it counts from 1.',
      frLimit: 'It skips text, shape, camera and light layers, and layers at 0 opacity. If it finds none, it shows “No visible footage layer”.'
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
