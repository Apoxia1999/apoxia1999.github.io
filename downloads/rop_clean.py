"""
ROP Clean v1.0  -  Shelf tool para Houdini
------------------------------------------
Selecciona uno o varios ROPs (en /out, o ROPs de render en /stage) y pulsa
la herramienta. Se borra todo lo que esos ROPs NO necesitan para renderizar:
objetos, cámaras, luces, subnets, materiales, COPs, otros ROPs, LOPs...

Qué se conserva (se repite hasta que no aparece nada nuevo):
  * Los ROPs seleccionados y todo ROP / LOP conectado por encima de ellos.
  * Los objetos que el render ve: candidatos con display flag encendido,
    forzados, matte/phantom, menos los excluidos. Lo mismo con las luces.
    Funciona con Mantra, Redshift, Arnold y Karma (Solaris).
  * La cámara de cada ROP. El resto de cámaras se borra.
  * Todo nodo al que apunte un parámetro de algo conservado (rutas, op:,
    expresiones ch()/chs(), bundles), sus entradas y padres de transformación.
  * Los materiales del objeto, del Material SOP y del atributo
    shop_materialpath de la geometría cocinada.
  * Los geos conservados mantienen toda su red SOP y los materiales toda su
    red VOP. Subnets y matnets se quedan solo como contenedor: lo que no se
    usa dentro también se borra.

Antes de borrar pide confirmación ("Solo informe" lista lo que se borraría).
Todo es un único paso de Undo y, si la escena tiene nombre, guarda antes una
copia de seguridad numerada del .hip.

Desde Python:
    rop_clean(dry_run=True)                    # solo informa
    rop_clean([hou.node("/out/mantra1")])
"""

import hou

# --------------------------------------------------------------------------- #
# Ajustes
# --------------------------------------------------------------------------- #

# Redes de primer nivel que se limpian. Lo que está fuera no se toca.
CONTEXTS_TO_CLEAN = ("/obj", "/mat", "/shop", "/out", "/stage", "/img", "/ch", "/tasks")

# Cocina la geometría conservada para encontrar materiales asignados por
# atributo (shop_materialpath). Más lento en escenas pesadas, pero más preciso.
READ_GEOMETRY_MATERIALS = True

# Guarda una copia de seguridad numerada del .hip antes de borrar.
MAKE_BACKUP = True

# Renderer parameters that select objects / lights.
#   candidate -> matched objects are kept only if their display flag is on
#   force     -> matched objects are always kept
#   exclude   -> matched objects are removed from the candidates
OBJECT_LIST_PARMS = {
    # Mantra / legacy
    "vobject": "candidate", "forceobject": "force", "excludeobject": "exclude",
    "matte_objects": "force", "phantom_objects": "force",
    "alights": "candidate", "forcelights": "force", "excludelights": "exclude",
    "vfog": "candidate",
    # Redshift
    "RS_objects_candidate": "candidate", "RS_objects_force": "force",
    "RS_objects_exclude": "exclude",
    "RS_lights_candidate": "candidate", "RS_lights_force": "force",
    "RS_lights_exclude": "exclude",
    # Arnold (HtoA)
    "ar_objects_candidate": "candidate", "ar_objects_force": "force",
    "ar_objects_exclude": "exclude",
    "ar_lights_candidate": "candidate", "ar_lights_force": "force",
    "ar_lights_exclude": "exclude",
}

# Geometry attributes that hold material paths.
MATERIAL_ATTRIBS = ("shop_materialpath", "material_override", "shop_vm_surface")

_GLOB_CHARS = ("*", "?", "[", "^")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _is_rop(node):
    """True for /out ROPs and ROP-like nodes in other contexts (usdrender_rop...)."""
    if node.type().category() == hou.ropNodeTypeCategory():
        return True
    return node.parm("execute") is not None and node.parm("trange") is not None


def _safe_glob(base, pattern):
    try:
        return list(base.glob(pattern))
    except (hou.OperationFailed, TypeError):
        return []


def _resolve(value, rel_node, obj_fallback=False):
    """Turn a parameter string into the nodes it points to.

    Handles absolute/relative paths, op: prefixes, @bundles and glob patterns
    (including '^' exclusions). obj_fallback resolves relative patterns
    against /obj when they find nothing relative to the node itself.
    """
    value = (value or "").strip()
    if not value:
        return []
    found = []
    tokens = value.split()

    # A whole relative pattern list ("* ^geo2") is passed to glob in one go so
    # the '^' exclusions work.
    if all(not t.startswith(("/", "op:", "@")) for t in tokens) and \
            any(c in value for c in _GLOB_CHARS):
        found = _safe_glob(rel_node, value)
        if not found and obj_fallback:
            found = _safe_glob(hou.node("/obj"), value)
        return found

    for tok in tokens:
        tok = tok.strip("\"'")
        if tok.startswith("op:"):
            tok = tok[3:]
        if not tok or tok.startswith("^"):
            continue
        if tok.startswith("@"):
            bundle = hou.nodeBundle(tok[1:])
            if bundle:
                found.extend(bundle.nodes())
            continue
        if any(c in tok for c in _GLOB_CHARS):
            head, _, tail = tok.rpartition("/")
            parent = rel_node.node(head) if head else (hou.node("/") if tok.startswith("/") else rel_node)
            if parent is not None:
                found.extend(_safe_glob(parent, tail))
            continue
        try:
            n = rel_node.node(tok)
        except hou.OperationFailed:
            n = None
        if n is None and obj_fallback and not tok.startswith("/"):
            n = hou.node("/obj/" + tok)
        if n is not None:
            found.append(n)
    return found


def _is_displayed(obj):
    try:
        return obj.isObjectDisplayed()
    except AttributeError:
        try:
            return obj.isDisplayFlagSet()
        except AttributeError:
            return True


def _object_list_mode(parm):
    """Return candidate/force/exclude for a ROP parm that selects objects/lights.

    Known names come from OBJECT_LIST_PARMS; anything else is recognised by its
    name (e.g. RS_objects_exclude, ar_lights_force, objects_candidate...), so
    renderers whose exact parm names vary between versions still work.
    """
    name = parm.name()
    if name in OBJECT_LIST_PARMS:
        return OBJECT_LIST_PARMS[name]
    lname = name.lower()
    if not any(k in lname for k in ("object", "light", "fog", "matte", "phantom")):
        return None
    if any(k in lname for k in ("mask", "categor", "shadow", "linking")):
        return None
    try:
        if parm.parmTemplate().type() != hou.parmTemplateType.String:
            return None
    except hou.OperationFailed:
        return None
    if "exclude" in lname:
        return "exclude"
    if "force" in lname or "matte" in lname or "phantom" in lname:
        return "force"
    if "candidate" in lname:
        return "candidate"
    return None


def _is_object_subnet(node):
    """An OBJ that contains other OBJs (subnet, rig container...)."""
    try:
        return node.childTypeCategory() == hou.objNodeTypeCategory()
    except AttributeError:
        return False


def _is_camera(node):
    name = node.type().nameComponents()[2].lower()
    return name in ("cam", "stereocam", "stereocamrig", "vrcam") or "camera" in name


def _is_node_ref_parm(parm):
    tmpl = parm.parmTemplate()
    if tmpl.type() != hou.parmTemplateType.String:
        return False
    return tmpl.stringType() in (hou.stringParmType.NodeReference,
                                 hou.stringParmType.NodeReferenceList)


# --------------------------------------------------------------------------- #
# Dependency collection
# --------------------------------------------------------------------------- #

class _Collector(object):
    def __init__(self):
        self.full = {}       # path -> node : node AND all its contents are kept
        self.folder = {}     # path -> node : node kept only as a container
        self._queue = []
        self._scanned = set()

    # -- marking ------------------------------------------------------------ #
    def keep(self, node):
        if node is None:
            return
        path = node.path()
        if path in self.full or path == "/":
            return
        # Already inside something kept in full -> nothing to do.
        for anc in self._ancestors(node):
            if anc.path() in self.full:
                self._enqueue(node)
                return
        self.full[path] = node
        self.folder.pop(path, None)
        self._enqueue(node)
        for anc in self._ancestors(node):
            if anc.path() not in self.full and anc.path() not in self.folder:
                self.folder[anc.path()] = anc
                self._enqueue(anc, contents=False)

    @staticmethod
    def _ancestors(node):
        p = node.parent()
        while p is not None and p.path() != "/":
            yield p
            p = p.parent()

    def _enqueue(self, node, contents=True):
        self._queue.append((node, contents))

    # -- scanning ----------------------------------------------------------- #
    def run(self):
        while self._queue:
            node, contents = self._queue.pop()
            nodes = [node]
            if contents:
                try:
                    nodes.extend(node.allSubChildren())
                except hou.OperationFailed:
                    pass
            for n in nodes:
                key = (n.path(), contents or n is not node)
                if key in self._scanned:
                    continue
                self._scanned.add(key)
                self._scan_node(n)

    def _scan_node(self, node):
        # Wired inputs (also transform parents for objects, ROP dependencies).
        for inp in node.inputs():
            if inp is not None:
                self.keep(inp)
        # Channel references and expression dependencies.
        cat = node.type().category()
        is_rop = _is_rop(node)
        try:
            for ref in node.references(include_children=False):
                # A renderer's object/light lists show up as references to
                # every object they *could* render; those are resolved below
                # with display flags and exclusions instead.
                if is_rop and ref.type().category() == hou.objNodeTypeCategory():
                    continue
                self.keep(ref)
        except (hou.OperationFailed, TypeError, AttributeError):
            pass
        # String parameters pointing to nodes.
        obj_fallback = cat in (hou.ropNodeTypeCategory(), hou.lopNodeTypeCategory())
        for parm in node.parms():
            if is_rop and _object_list_mode(parm):
                continue  # handled with renderer logic
            lname = parm.name().lower()
            if "mask" in lname or "categor" in lname:
                continue  # light/reflection masks filter, they don't add nodes
            try:
                if parm.parmTemplate().type() != hou.parmTemplateType.String:
                    continue
                value = parm.evalAsString()
            except (hou.OperationFailed, hou.Error):
                continue
            if not value:
                continue
            if _is_node_ref_parm(parm):
                targets = _resolve(value, node, obj_fallback)
                if any(c in value for c in _GLOB_CHARS):
                    # Patterns only pull in objects that are actually visible.
                    targets = [t for t in targets
                               if t.type().category() != hou.objNodeTypeCategory()
                               or _is_displayed(t)]
            elif "/" in value or value.startswith(("op:", "@")):
                # Only explicit paths in free-text parms, to avoid false matches.
                targets = _resolve(" ".join(t for t in value.split()
                                            if t.startswith(("/", "op:", "../", "@"))),
                                   node)
            else:
                targets = []
            for t in targets:
                self.keep(t)

        if is_rop:
            self._scan_renderer_objects(node)
        if READ_GEOMETRY_MATERIALS and cat == hou.objNodeTypeCategory():
            self._scan_geometry_materials(node)

    def _scan_renderer_objects(self, rop):
        groups = {"candidate": [], "force": [], "exclude": []}
        found_any = False
        for parm in rop.parms():
            mode = _object_list_mode(parm)
            if mode is None:
                continue
            found_any = True
            groups[mode].extend(_resolve(parm.evalAsString(), hou.node("/obj"), True))
        if not found_any:
            # Unknown renderer with a camera: keep every displayed object to be safe.
            if rop.parm("camera") is None and rop.parm("RS_renderCamera") is None:
                return
            groups["candidate"] = list(hou.node("/obj").allSubChildren())
        excluded = set(n.path() for n in groups["exclude"])
        pending = list(groups["candidate"])
        while pending:
            n = pending.pop()
            if n.type().category() != hou.objNodeTypeCategory() or n.path() in excluded:
                continue
            if _is_object_subnet(n):
                # Look inside subnets instead of keeping all their contents.
                pending.extend(n.children())
                continue
            if _is_camera(n):
                continue  # cameras come only from the ROP's camera parm
            if _is_displayed(n):
                self.keep(n)
        for n in groups["force"]:
            self.keep(n)

    def _scan_geometry_materials(self, obj):
        try:
            sop = obj.renderNode() or obj.displayNode()
        except AttributeError:
            return
        if sop is None:
            return
        try:
            geo = sop.geometry()
        except hou.OperationFailed:
            return
        if geo is None:
            return
        for name in MATERIAL_ATTRIBS:
            for finder in (geo.findPrimAttrib, geo.findPointAttrib, geo.findGlobalAttrib):
                try:
                    attrib = finder(name)
                except hou.OperationFailed:
                    attrib = None
                if attrib is None or attrib.dataType() != hou.attribData.String:
                    continue
                try:
                    values = attrib.strings()
                except hou.OperationFailed:
                    values = [geo.attribValue(name)] if finder == geo.findGlobalAttrib else []
                for v in values:
                    for t in _resolve(v, sop):
                        self.keep(t)


# --------------------------------------------------------------------------- #
# Deletion
# --------------------------------------------------------------------------- #

def _collect_deletions(collector):
    to_delete = []

    def walk(parent):
        try:
            if parent.isLockedHDA() or parent.isInsideLockedHDA():
                return
        except AttributeError:
            pass
        for child in parent.children():
            path = child.path()
            if path in collector.full:
                continue
            if path in collector.folder:
                walk(child)
            else:
                to_delete.append(child)

    for ctx_path in CONTEXTS_TO_CLEAN:
        ctx = hou.node(ctx_path)
        if ctx is not None:
            walk(ctx)
    return to_delete


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def rop_clean(rops=None, dry_run=False, confirm=True):
    """Delete everything not needed by `rops` (defaults to the selected ROPs).

    Returns the list of deleted (or, with dry_run, deletable) node paths.
    """
    ui = hou.isUIAvailable()
    if rops is None:
        rops = [n for n in hou.selectedNodes() if _is_rop(n)]
    if not rops:
        msg = "ROP Clean: selecciona antes al menos un ROP (render output)."
        if ui:
            hou.ui.displayMessage(msg, severity=hou.severityType.Warning)
        else:
            print(msg)
        return []

    collector = _Collector()
    with hou.InterruptableOperation("ROP Clean: analizando dependencias",
                                    open_interrupt_dialog=True):
        for rop in rops:
            collector.keep(rop)
        collector.run()
    to_delete = _collect_deletions(collector)
    paths = [n.path() for n in to_delete]

    rop_names = ", ".join(r.path() for r in rops)
    if not paths:
        msg = "ROP Clean: no hay nada que borrar, todo lo usa %s." % rop_names
        if ui and confirm:
            hou.ui.displayMessage(msg)
        print(msg)
        return []

    preview = "\n".join(paths[:40]) + ("\n... y %d más" % (len(paths) - 40) if len(paths) > 40 else "")
    print("ROP Clean - se conserva lo que usa %s; nodos a borrar (%d):\n  %s"
          % (rop_names, len(paths), "\n  ".join(paths)))

    if ui and confirm and not dry_run:
        choice = hou.ui.displayMessage(
            "Conservar solo lo que renderizan estos ROPs:\n%s\n\nSe borrarán %d nodos."
            % (rop_names, len(paths)),
            buttons=("Limpiar", "Solo informe", "Cancelar"),
            default_choice=0, close_choice=2,
            details=preview, details_label="Nodos a borrar",
            title="ROP Clean")
        if choice == 2:
            return []
        dry_run = choice == 1

    if dry_run:
        if ui and confirm:
            hou.ui.displayMessage("Se borrarían %d nodos (lista completa en la consola de Python)."
                                  % len(paths), details=preview, title="ROP Clean")
        return paths

    if MAKE_BACKUP and hou.hipFile.name() != "untitled.hip":
        try:
            backup = hou.hipFile.saveAsBackup()
            print("ROP Clean: copia de seguridad en %s" % backup)
        except hou.OperationFailed as e:
            print("ROP Clean: no se pudo guardar la copia de seguridad (%s)" % e)

    deleted = []
    with hou.undos.group("ROP Clean"):
        for node in to_delete:
            try:
                path = node.path()
                node.destroy()
                deleted.append(path)
            except (hou.ObjectWasDeleted, hou.OperationFailed, hou.PermissionError):
                pass

    msg = "ROP Clean: %d nodos borrados. Ctrl+Z para deshacer." % len(deleted)
    print(msg)
    if ui and confirm:
        hou.ui.setStatusMessage(msg)
    return deleted


# Shelf tool: when this file is pasted into a shelf tool's Script tab,
# it runs on the current selection.
if __name__ in ("__main__", "__builtin__", "builtins") or "kwargs" in globals():
    rop_clean()
