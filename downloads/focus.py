"""
Focus  -  Shelf tool para Houdini
---------------------------------
1. Mira a través de una cámara en el viewport.
2. Pulsa la herramienta Focus en el shelf.
3. Haz clic en cualquier punto de la geometría.

La cámara pone su Focus Distance a la distancia de ese punto (profundidad
medida a lo largo del eje de la cámara, que es lo que usa el plano de foco).
Si el parámetro está animado, crea un keyframe en el frame actual.
Esc para salir sin cambiar nada.
"""

import hou

STATE_NAME_OBJ = "apoxia_focus_obj"
STATE_NAME_SOP = "apoxia_focus_sop"
FOCUS_PARMS = ("focus", "focusdistance", "focusDistance")


# ----------------------------------------------------------------------------
# Cámara
# ----------------------------------------------------------------------------
def _viewer_camera(scene_viewer):
    """Cámara OBJ por la que mira el viewport, o None."""
    viewport = scene_viewer.curViewport()
    cam = viewport.camera()
    if cam is None or not isinstance(cam, hou.ObjNode):
        return None
    return cam


def _focus_parm(cam):
    for name in FOCUS_PARMS:
        parm = cam.parm(name)
        if parm is not None:
            return parm
    return None


# ----------------------------------------------------------------------------
# Raycast contra toda la geometría visible
# ----------------------------------------------------------------------------
def _visible_geometry():
    for node in hou.node("/obj").allSubChildren():
        if not isinstance(node, hou.ObjNode):
            continue
        if node.childTypeCategory() != hou.sopNodeTypeCategory():
            continue
        try:
            if not node.isObjectDisplayed():
                continue
            sop = node.displayNode()
            if sop is None:
                continue
            geo = sop.geometry()
            if geo is None or not geo.prims():
                continue
        except hou.Error:
            continue
        yield node, geo


def _raycast(origin, direction):
    """Posición en mundo del impacto más cercano, o None."""
    best_pos = None
    best_dist = 1e30
    for obj, geo in _visible_geometry():
        xform = obj.worldTransform()
        inv = xform.inverted()
        l_orig = origin * inv
        l_dir = (origin + direction) * inv - l_orig

        pos = hou.Vector3()
        nml = hou.Vector3()
        uvw = hou.Vector3()
        if geo.intersect(l_orig, l_dir, pos, nml, uvw) < 0:
            continue
        world = pos * xform
        dist = (world - origin).length()
        if dist < best_dist:
            best_dist = dist
            best_pos = world
    return best_pos


def _focus_depth(cam, world_pos):
    """Profundidad del punto a lo largo del eje de visión de la cámara."""
    xform = cam.worldTransform()
    cam_pos = hou.Vector3(0, 0, 0) * xform
    forward = (hou.Vector3(0, 0, -1) * xform - cam_pos).normalized()
    return (world_pos - cam_pos).dot(forward)


def _set_value(parm, value):
    if parm.keyframes():
        key = hou.Keyframe(value, hou.frameToTime(hou.frame()))
        parm.setKeyframe(key)
    else:
        parm.set(value)


# ----------------------------------------------------------------------------
# Viewer state
# ----------------------------------------------------------------------------
class FocusState(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

    def onEnter(self, kwargs):
        self.scene_viewer.setPromptMessage(
            "Focus: clic en la geometría para enfocar ahí. Esc para salir.")

    def onExit(self, kwargs):
        self.scene_viewer.clearPromptMessage()

    def _warn(self, text):
        self.scene_viewer.setPromptMessage(text, hou.promptMessageType.Warning)

    def onMouseEvent(self, kwargs):
        ui_event = kwargs["ui_event"]
        if ui_event.reason() != hou.uiEventReason.Picked:
            return False

        cam = _viewer_camera(self.scene_viewer)
        if cam is None:
            self._warn("Focus: mira a través de una cámara primero.")
            return True
        parm = _focus_parm(cam)
        if parm is None:
            self._warn("Focus: %s no tiene parámetro de Focus Distance." % cam.name())
            return True

        origin, direction = ui_event.ray()
        hit = _raycast(origin, direction)
        if hit is None:
            self._warn("Focus: no hay geometría bajo el ratón.")
            return True

        depth = _focus_depth(cam, hit)
        if depth <= 0:
            self._warn("Focus: el punto está detrás de la cámara.")
            return True

        with hou.undos.group("Focus"):
            _set_value(parm, depth)

        hou.ui.setStatusMessage("Focus: %s → %.3f" % (cam.name(), depth))
        # Un clic y listo: vuelve a la herramienta de selección
        self.scene_viewer.setCurrentState("select")
        return True


def _register(name, category):
    if hou.ui.isRegisteredViewerState(name):
        hou.ui.unregisterViewerState(name)
    template = hou.ViewerStateTemplate(name, "Focus", category)
    template.bindFactory(FocusState)
    hou.ui.registerViewerState(template)


def run():
    viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if viewer is None:
        hou.ui.displayMessage("Focus: no se encontró un Scene Viewer.")
        return
    if _viewer_camera(viewer) is None:
        hou.ui.displayMessage("Focus: mira a través de una cámara en el viewport primero.")
        return

    category = viewer.pwd().childTypeCategory()
    if category == hou.sopNodeTypeCategory():
        name = STATE_NAME_SOP
    elif category == hou.objNodeTypeCategory():
        name = STATE_NAME_OBJ
    else:
        hou.ui.displayMessage("Focus: úsalo en contexto OBJ o SOP.")
        return

    _register(name, category)
    viewer.setCurrentState(name)


run()
