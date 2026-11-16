"""
Convierte todas las rutas de la escena que usan $HIP / $HIPNAME / $HIPFILE / $JOB
en rutas absolutas (globales), para poder copiar el .hip a otro sitio sin romper links.

Uso: pegar en Windows > Python Source Editor (o en una Shelf Tool) y ejecutar.

- Solo sustituye esas variables; $F, $F4, $OS, $SF, <UDIM>, etc. se conservan.
- Todo queda en un solo paso de Undo (Ctrl+Z lo revierte).
- Pon DRY_RUN = True para ver que cambiaria sin tocar nada.
"""
import re
import hou

DRY_RUN = False          # True = solo listar, no modificar
ONLY_FILE_PARMS = False  # True = solo parametros de tipo "File" (no toca p.ej. el
                         # "Base Name" del File Cache, que usa $HIPNAME)
VARIABLES = ["HIPNAME", "HIPFILE", "HIP", "JOB"]  # quita "JOB" si quieres conservarlo

# $HIP, ${HIP}, $HIPNAME, ... (sin confundir $HIP con $HIPNAME)
_PATTERN = re.compile(
    r"\$(?:\{(%s)\}|(%s)(?![A-Za-z0-9_]))" % ("|".join(VARIABLES), "|".join(VARIABLES))
)


def _expand(var):
    try:
        value = hou.text.expandString("$" + var)   # Houdini 18.5+
    except AttributeError:
        value = hou.expandString("$" + var)
    return value.replace("\\", "/")


def _replace(raw, values):
    return _PATTERN.sub(lambda m: values[m.group(1) or m.group(2)], raw)


def hip_to_absolute():
    values = {v: _expand(v) for v in VARIABLES}
    changed, skipped = [], []

    with hou.undos.group("HIP paths -> absolute"):
        for node in hou.node("/").allSubChildren():
            if node.isInsideLockedHDA():
                continue

            for parm in node.parms():
                tmpl = parm.parmTemplate()
                if tmpl.type() != hou.parmTemplateType.String:
                    continue
                if ONLY_FILE_PARMS and tmpl.stringType() != hou.stringParmType.FileReference:
                    continue

                # Parametros con expresion/keyframes: se revisa la expresion
                if parm.keyframes():
                    try:
                        expr = parm.expression()
                    except hou.OperationFailed:
                        continue
                    if _PATTERN.search(expr):
                        skipped.append((parm.path(), "tiene expresion: " + expr))
                    continue

                try:
                    raw = parm.unexpandedString()
                except hou.OperationFailed:
                    continue

                if not _PATTERN.search(raw):
                    continue

                new = _replace(raw, values)
                if new == raw:
                    continue

                if parm.isLocked():
                    skipped.append((parm.path(), "parametro bloqueado"))
                    continue

                if not DRY_RUN:
                    try:
                        parm.set(new)
                    except (hou.PermissionError, hou.OperationFailed) as e:
                        skipped.append((parm.path(), str(e)))
                        continue

                changed.append((parm.path(), raw, new))

    title = "SE CAMBIARIAN" if DRY_RUN else "CAMBIADOS"
    print("\n=== %s: %d parametros ===" % (title, len(changed)))
    for path, old, new in changed:
        print("%s\n    %s\n -> %s" % (path, old, new))

    if skipped:
        print("\n=== OMITIDOS (revisar a mano): %d ===" % len(skipped))
        for path, reason in skipped:
            print("%s  [%s]" % (path, reason))

    msg = "%s %d parametros." % ("Se cambiarian" if DRY_RUN else "Cambiados", len(changed))
    if skipped:
        msg += "\n%d omitidos (ver la consola de Python)." % len(skipped)
    if hou.isUIAvailable():
        hou.ui.displayMessage(msg, title="HIP -> rutas absolutas")
    return changed, skipped


hip_to_absolute()
