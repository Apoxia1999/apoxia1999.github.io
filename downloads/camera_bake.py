"""
Camera Bake  -  Shelf tool para Houdini
---------------------------------------
1. Selecciona una o varias cámaras (o mira a través de una en el viewport).
2. Pulsa la herramienta Camera Bake en el shelf.
3. Confirma el rango de frames.

Crea una cámara nueva "<nombre>_baked" en /obj, sin padres ni constraints,
con un keyframe en CADA frame: posición y rotación en espacio mundo. Copia
también todos los parámetros de la cámara (lente, resolución y los extra de
render, como Karma o Redshift): los animados se hornean frame a frame y el
resto se copia como valor fijo, sin referencias a otros nodos.
Lista para exportar a FBX, Alembic o USD. La cámara original no se toca.
Todo se deshace con un solo Undo. Esc cancela el horneado.
"""

import hou

SUFFIX = "_baked"

# Transformación y constraints: no se copian, se reconstruyen desde la matriz
# en espacio mundo para que la cámara horneada no dependa de nada.
SKIP_TUPLES = {
    "t", "r", "s", "p", "pr", "scale", "xOrd", "rOrd", "pre_xform", "keeppos",
    "childcomp", "constraints_on", "constraints_path", "lookatpath",
    "lookupobjpath", "lookup", "pathobjpath", "roll", "pos", "uparmtype",
    "pathorient", "up", "bank",
}
SKIP_TYPES = {
    hou.parmTemplateType.Button,
    hou.parmTemplateType.FolderSet,
    hou.parmTemplateType.Folder,
    hou.parmTemplateType.Separator,
    hou.parmTemplateType.Label,
    hou.parmTemplateType.Data,
}
XFORM_PARMS = ("tx", "ty", "tz", "rx", "ry", "rz")


# ----------------------------------------------------------------------------
# Cámaras a hornear
# ----------------------------------------------------------------------------
def _is_camera(node):
    return (isinstance(node, hou.ObjNode)
            and node.parm("focal") is not None
            and node.parm("aperture") is not None)


def _pick_cameras():
    cams = [n for n in hou.selectedNodes() if _is_camera(n)]
    if cams:
        return cams

    viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if viewer is not None:
        cam = viewer.curViewport().camera()
        if cam is not None and _is_camera(cam):
            return [cam]

    path = hou.ui.selectNode(
        title="Camera Bake: elige la cámara",
        node_type_filter=hou.nodeTypeFilter.ObjCamera)
    if not path:
        return []
    node = hou.node(path)
    return [node] if node is not None and _is_camera(node) else []


def _ask_range():
    start, end = hou.playbar.playbackRange()
    button, values = hou.ui.readMultiInput(
        "Rango de frames a hornear (un keyframe por frame):",
        ("Inicio", "Fin"),
        buttons=("Hornear", "Cancelar"),
        default_choice=0, close_choice=1,
        initial_contents=("%d" % start, "%d" % end),
        title="Camera Bake")
    if button != 0:
        return None
    try:
        start, end = int(float(values[0])), int(float(values[1]))
    except ValueError:
        hou.ui.displayMessage("Camera Bake: el rango tiene que ser numérico.")
        return None
    if end < start:
        start, end = end, start
    return start, end


# ----------------------------------------------------------------------------
# Horneado
# ----------------------------------------------------------------------------
def _unique_name(parent, base):
    name, i = base, 1
    while parent.node(name) is not None:
        name = "%s%d" % (base, i)
        i += 1
    return name


def _create_target(src):
    """Crea <nombre>_baked. Si ya existe, pregunta si reemplazarla."""
    obj = hou.node("/obj")
    name = src.name() + SUFFIX
    pos = src.position() + hou.Vector2(0, -1.2)
    existing = obj.node(name)
    if existing is not None:
        choice = hou.ui.displayMessage(
            "Camera Bake: ya existe %s." % existing.path(),
            buttons=("Reemplazar", "Crear otra", "Saltar"),
            default_choice=0, close_choice=2, title="Camera Bake")
        if choice == 2:
            return None
        if choice == 0:
            pos = existing.position()
            existing.destroy()
        else:
            name = _unique_name(obj, name)
    dst = obj.createNode(src.type().name(), name)
    dst.setPosition(pos)
    dst.setColor(hou.Color(0.95, 0.68, 0.26))
    return dst


def _unwrap(prev, value):
    """Quita los saltos de 360° respecto al frame anterior (filtro Euler)."""
    if prev is None:
        return value
    return value - 360.0 * round((value - prev) / 360.0)


def _key(frame, value):
    key = hou.Keyframe(value, hou.frameToTime(frame))
    key.setExpression("linear()", hou.exprLanguage.Hscript)
    return key


def _is_animated(parm):
    try:
        return parm.isTimeDependent()
    except hou.Error:
        return bool(parm.keyframes())


def _copy_parms(src, dst):
    """Copia los parámetros que no son de transformación. Devuelve los
    animados como pares (origen, destino) para hornearlos frame a frame."""
    # Copia la interfaz entera: incluye los parámetros extra de render.
    try:
        dst.setParmTemplateGroup(src.parmTemplateGroup())
    except hou.Error:
        pass

    animated = []
    for sp in src.parms():
        template = sp.parmTemplate()
        if (template.type() in SKIP_TYPES
                or sp.tuple().name() in SKIP_TUPLES):
            continue
        dp = dst.parm(sp.name())
        if dp is None or dp.isLocked():
            continue
        try:
            if template.type() == hou.parmTemplateType.String:
                dp.set(sp.eval() if sp.keyframes() else sp.unexpandedString())
            elif _is_animated(sp):
                animated.append((sp, dp))
            else:
                dp.set(sp.eval())
        except hou.Error:
            pass
    return animated


def _bake(src, start, end, op, done, total):
    dst = _create_target(src)
    if dst is None:
        return None, False
    animated = _copy_parms(src, dst)
    dst.parm("xOrd").set("srt")
    dst.parm("rOrd").set("xyz")

    keys = {name: [] for name in XFORM_PARMS}
    anim_keys = [[] for _ in animated]
    prev_rot = [None, None, None]
    scaled = False

    for frame in range(start, end + 1):
        hou.setFrame(frame)
        parts = src.worldTransform().explode(
            transform_order="srt", rotate_order="xyz")
        t, r, s = parts["translate"], parts["rotate"], parts["scale"]
        for i in range(3):
            prev_rot[i] = _unwrap(prev_rot[i], r[i])
            keys[XFORM_PARMS[i]].append(_key(frame, t[i]))
            keys[XFORM_PARMS[i + 3]].append(_key(frame, prev_rot[i]))
        if any(abs(v - 1.0) > 1e-4 for v in s):
            scaled = True
        for i, (sp, _) in enumerate(animated):
            anim_keys[i].append(_key(frame, sp.eval()))
        done += 1
        op.updateProgress(done / float(total))

    for name, frame_keys in keys.items():
        dst.parm(name).setKeyframes(frame_keys)
    for (_, dp), frame_keys in zip(animated, anim_keys):
        try:
            dp.setKeyframes(frame_keys)
        except hou.Error:
            pass

    dst.setComment("Bake de %s, frames %d-%d" % (src.path(), start, end))
    dst.setGenericFlag(hou.nodeFlag.DisplayComment, True)
    return dst, scaled


def run():
    cams = _pick_cameras()
    if not cams:
        hou.ui.displayMessage(
            "Camera Bake: selecciona una cámara o mira a través de una.")
        return
    frame_range = _ask_range()
    if frame_range is None:
        return
    start, end = frame_range
    total = len(cams) * (end - start + 1)

    current = hou.frame()
    baked, warnings = [], []
    try:
        with hou.undos.group("Camera Bake"), hou.InterruptableOperation(
                "Horneando cámara", "Camera Bake",
                open_interrupt_dialog=True) as op:
            for n, cam in enumerate(cams):
                dst, scaled = _bake(cam, start, end, op,
                                    n * (end - start + 1), total)
                if dst is None:
                    continue
                baked.append(dst)
                if scaled:
                    warnings.append(cam.name())
    except hou.OperationInterrupted:
        hou.ui.displayMessage(
            "Camera Bake: cancelado. Ctrl+Z quita lo que se llegó a crear.")
        return
    finally:
        hou.setFrame(current)

    if not baked:
        return
    for node in baked:
        node.setSelected(True, clear_all_selected=(node is baked[0]))

    msg = "Camera Bake: %s  (frames %d-%d, %d keys por canal)" % (
        ", ".join(n.path() for n in baked), start, end, end - start + 1)
    if warnings:
        msg += ("\n\nOjo: %s tiene escala en su jerarquía. La cámara "
                "horneada no la lleva (las cámaras no deberían escalarse)."
                % ", ".join(warnings))
    print(msg)
    hou.ui.displayMessage(msg, title="Camera Bake")


run()
