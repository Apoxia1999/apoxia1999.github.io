"""
Focus Ball  -  Shelf tool para Houdini
--------------------------------------
1. Pulsa la herramienta en el shelf.
2. Haz clic sobre cualquier geometría visible en el viewport.
3. Se lanza un rayo desde el ratón, se toma el punto más cercano al impacto
   y se crea un objeto "focus_ball" con una esfera verde fosforito pegada a
   ese punto. Sigue al punto aunque el objeto se mueva o la geometría se
   deforme (va por Object Merge + Blast del punto, no es una copia estática).

Puedes hacer varios clics seguidos (una bola por clic).
Esc o cambiar de herramienta para salir.
"""

import hou

STATE_LABEL = "Focus Ball"
BALL_COLOR = (0.2, 1.0, 0.0)      # verde fosforito
BALL_SIZE_RATIO = 0.015           # radio = 1.5% de la diagonal del bbox


# ----------------------------------------------------------------------------
# Raycast
# ----------------------------------------------------------------------------
def _candidate_objects():
    """Objetos geo visibles en el viewport con geometría (excluye focus balls)."""
    out = []
    for node in hou.node("/obj").allSubChildren():
        if not isinstance(node, hou.ObjNode):
            continue
        if node.type().name() != "geo":
            continue
        if node.name().startswith("focus_ball"):
            continue
        try:
            if not node.isObjectDisplayed():
                continue
            sop = node.displayNode()
            if sop is None or sop.geometry() is None:
                continue
        except hou.Error:
            continue
        out.append(node)
    return out


def _raycast(origin, direction):
    """Devuelve (obj, sop, point_number, world_pos) del punto más cercano al
    impacto del rayo, o None si no toca nada."""
    best = None
    best_dist = 1e30

    for obj in _candidate_objects():
        sop = obj.displayNode()
        geo = sop.geometry()
        xform = obj.worldTransform()
        inv = xform.inverted()

        # Rayo a espacio local del objeto
        l_orig = origin * inv
        l_dir = (origin + direction) * inv - l_orig

        hit_pos = hou.Vector3()
        hit_nml = hou.Vector3()
        hit_uvw = hou.Vector3()
        prim_num = geo.intersect(l_orig, l_dir, hit_pos, hit_nml, hit_uvw)
        if prim_num < 0:
            continue

        world_hit = hit_pos * xform
        dist = (world_hit - origin).length()
        if dist >= best_dist:
            continue

        # Punto (vértice) más cercano al impacto dentro de la primitiva tocada
        prim = geo.prim(prim_num)
        nearest_pt = None
        nearest_d = 1e30
        for vtx in prim.vertices():
            pt = vtx.point()
            d = (pt.position() - hit_pos).length()
            if d < nearest_d:
                nearest_d = d
                nearest_pt = pt
        if nearest_pt is None:
            continue

        best_dist = dist
        best = (obj, sop, nearest_pt.number(), nearest_pt.position() * xform)

    return best


# ----------------------------------------------------------------------------
# Construcción de la red
# ----------------------------------------------------------------------------
def build_focus_ball(obj, sop, ptnum):
    geo = sop.geometry()
    parent = obj.parent()

    # Tamaño pequeño relativo a la geometría
    bbox = geo.boundingBox()
    diag = (bbox.maxvec() - bbox.minvec()).length() or 1.0
    radius = diag * BALL_SIZE_RATIO

    # Si hay atributo id, lo usamos (más robusto si cambia la topología)
    id_attrib = geo.findPointAttrib("id")
    if id_attrib is not None and id_attrib.dataType() == hou.attribData.Int:
        group_expr = "@id==%d" % geo.point(ptnum).attribValue("id")
    else:
        group_expr = str(ptnum)

    with hou.undos.group("Create Focus Ball"):
        fb = parent.createNode("geo", "focus_ball", run_init_scripts=False)
        fb.setPosition(obj.position() + hou.Vector2(0, -1.5))
        fb.setColor(hou.Color(BALL_COLOR))

        merge = fb.createNode("object_merge", "follow_geo")
        merge.parm("objpath1").set(fb.relativePathTo(sop))
        merge.parm("xformtype").set(1)          # Into This Object

        blast = fb.createNode("blast", "isolate_point")
        blast.setInput(0, merge)
        blast.parm("group").set(group_expr)
        blast.parm("grouptype").set("points")
        blast.parm("negate").set(1)             # Delete Non Selected
        blast.parm("removegrp").set(1)

        clean = fb.createNode("attribdelete", "clean_attribs")
        clean.setInput(0, blast)
        clean.parm("ptdel").set("* ^P")
        clean.parm("vtxdel").set("*")
        clean.parm("primdel").set("*")
        clean.parm("dtldel").set("*")

        sphere = fb.createNode("sphere", "ball")
        sphere.parm("type").set("polymesh")
        sphere.parmTuple("rad").set((radius, radius, radius))
        sphere.parm("rows").set(16)
        sphere.parm("cols").set(24)

        copy = fb.createNode("copytopoints::2.0", "stick_to_point")
        copy.setInput(0, sphere)
        copy.setInput(1, clean)

        color = fb.createNode("color", "fluo_green")
        color.setInput(0, copy)
        color.parmTuple("color").set(BALL_COLOR)

        out = fb.createNode("null", "OUT_FOCUS_BALL")
        out.setInput(0, color)
        out.setDisplayFlag(True)
        out.setRenderFlag(True)

        fb.layoutChildren()

    return fb


# ----------------------------------------------------------------------------
# Viewer state
# ----------------------------------------------------------------------------
class FocusBallState(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

    def onEnter(self, kwargs):
        self.scene_viewer.setPromptMessage(
            "Focus Ball: clic sobre la geometría para pegar una bola al punto "
            "más cercano. Esc para salir.")

    def onExit(self, kwargs):
        self.scene_viewer.clearPromptMessage()

    def onMouseEvent(self, kwargs):
        ui_event = kwargs["ui_event"]
        if ui_event.reason() != hou.uiEventReason.Picked:
            return False

        origin, direction = ui_event.ray()
        hit = _raycast(origin, direction)
        if hit is None:
            self.scene_viewer.setPromptMessage(
                "Focus Ball: no hay geometría bajo el ratón.",
                hou.promptMessageType.Warning)
            return True

        obj, sop, ptnum, _ = hit
        fb = build_focus_ball(obj, sop, ptnum)
        self.scene_viewer.setPromptMessage(
            "Focus Ball: %s pegada al punto %d de %s. Clic para otra, Esc para salir."
            % (fb.name(), ptnum, obj.name()))
        return True


def _register(name, category):
    if hou.ui.isRegisteredViewerState(name):
        hou.ui.unregisterViewerState(name)
    template = hou.ViewerStateTemplate(name, STATE_LABEL, category)
    template.bindFactory(FocusBallState)
    template.bindIcon("MISC_python")
    hou.ui.registerViewerState(template)


def run():
    viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if viewer is None:
        hou.ui.displayMessage("Focus Ball: no se encontró un Scene Viewer.")
        return

    # El state tiene que coincidir con el contexto actual del viewer (OBJ o SOP)
    if viewer.pwd().childTypeCategory() == hou.sopNodeTypeCategory():
        name, cat = "focus_ball_sop", hou.sopNodeTypeCategory()
    else:
        name, cat = "focus_ball_obj", hou.objNodeTypeCategory()

    _register(name, cat)
    viewer.setCurrentState(name)


run()
