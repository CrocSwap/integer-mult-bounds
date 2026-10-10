#!/usr/bin/env python3
"""Content-addressed vector-page cache for joint259_system_docs_build.

The normal renderer is executed against a recording canvas, without painting.
Only new drawing-operation sequences are painted. Every run reconstructs PDF
destinations, links, outlines and nonvisual indexes from the current model.
Use --clean to bypass saved pages, --svg for linked per-page vector SVGs, and
--emit-json to return text artifacts without writing to the filesystem.
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import importlib.metadata
import io
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import reportlab
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import NameObject, StreamObject

import joint259_system_docs_build as renderer

SCHEMA = "joint259-vector-page-cache/1"
BASE_DOC = renderer.Doc
BASE_RENDER = renderer.render
KINDS = {"functional": "functional_architecture", "logical": "logical_wiring", "combined": "complete_system"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


class RecordedPath:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def record(*args, **kwargs):
            self.calls.append([name, pack(args), pack(kwargs)])
        return record


def pack(value):
    if isinstance(value, RecordedPath):
        return {"__path__": value.calls}
    if isinstance(value, Color):
        return {"__color__": [value.red, value.green, value.blue, value.alpha]}
    if isinstance(value, (list, tuple)):
        return [pack(v) for v in value]
    if isinstance(value, dict):
        return {k: pack(v) for k, v in value.items()}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("Unsupported drawing argument: " + type(value).__name__)


def unpack(value, target):
    if isinstance(value, dict):
        if "__color__" in value:
            return Color(*value["__color__"])
        if "__path__" in value:
            path = target.beginPath()
            for name, args, kwargs in value["__path__"]:
                getattr(path, name)(*unpack(args, target), **unpack(kwargs, target))
            return path
        return {k: unpack(v, target) for k, v in value.items()}
    if isinstance(value, list):
        return [unpack(v, target) for v in value]
    return value


class RecordingCanvas:
    """The renderer's supported canvas protocol; unsupported values fail closed."""
    def __init__(self):
        self.pages = []
        self.current = {"paint": [], "destinations": [], "links": [], "outlines": []}

    def beginPath(self):
        return RecordedPath()

    def stringWidth(self, text, fontName, fontSize, encoding="utf8"):
        return pdfmetrics.stringWidth(text, fontName, fontSize, encoding)

    def getPageNumber(self):
        return len(self.pages) + 1

    def bookmarkPage(self, key, **kwargs):
        if kwargs:
            raise ValueError("New bookmark options require explicit cache support")
        self.current["destinations"].append(key)

    def addOutlineEntry(self, title, key, level=0, closed=None):
        self.current["outlines"].append([title, key, level, bool(closed)])

    def linkRect(self, contents, destinationname, Rect=None, addtopage=1, name=None,
                 relative=1, thickness=0, color=None, dashArray=None, **kwargs):
        if relative or not addtopage or name or kwargs or thickness or color or dashArray:
            raise ValueError("New link style requires explicit cache support")
        self.current["links"].append({"target": destinationname, "rect": list(Rect)})

    def linkURL(self, url, rect, relative=0, thickness=0, color=None, dashArray=None, kind="URI", **kwargs):
        if relative or thickness or color or dashArray or kind != "URI" or kwargs:
            raise ValueError("New external-link style requires explicit cache support")
        self.current["links"].append({"url": url, "rect": list(rect)})

    def showPage(self):
        if self.current["paint"] or self.current["destinations"]:
            self.pages.append(self.current)
        self.current = {"paint": [], "destinations": [], "links": [], "outlines": []}

    def save(self):
        self.showPage()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name in {"setTitle", "setAuthor", "setSubject", "setCreator", "setKeywords"}:
            return lambda *a, **k: None
        if not hasattr(canvas.Canvas, name):
            raise AttributeError("Unsupported Canvas method " + name)
        def record(*args, **kwargs):
            self.current["paint"].append([name, pack(args), pack(kwargs)])
        return record


class PlanningDoc(BASE_DOC):
    def __init__(self, kind, model, refs):
        self.kind, self.model, self.refs = kind, model, refs
        self.buf = io.BytesIO()
        self.c = RecordingCanvas()
        self.n = 0
        self.ids, self.links, self.used_blocks, self.pages, self.boxes = set(), [], set(), [], []

    def finish(self):
        missing = {t for _, t in self.links} - self.ids
        if missing:
            raise ValueError("Broken internal links " + str(missing))
        self.c.save()
        if len(self.c.pages) != self.n:
            raise ValueError("Page recording mismatch")
        return self.c.pages, {"pages": self.pages, "internal_links": len(self.links),
                              "blocks": sorted(self.used_blocks)}


def plan(kind, model, refs):
    """Uses the authoritative renderer; no duplicated page-dispatch logic."""
    previous = renderer.Doc
    renderer.Doc = PlanningDoc
    try:
        return BASE_RENDER(kind, model, refs)
    finally:
        renderer.Doc = previous


def dependencies(model, extra=None):
    files = {"renderer": Path(renderer.__file__), "cache_implementation": Path(__file__),
             "requirements": renderer.BASE / "joint259_system_docs_requirements.txt",
             "source_binding": renderer.BASE / "joint259_system_docs_source_binding.json"}
    # Imported drawing code is a renderer dependency as well. Model JSON is
    # deliberately projected through recorded page operations, so a single
    # block edit does not invalidate every unrelated visual page.
    for name, module in vars(renderer).items():
        module_file = getattr(module, "__file__", None)
        if module_file and Path(module_file).resolve().parent == renderer.BASE.resolve():
            files["renderer_module_" + name] = Path(module_file)
    font_root = Path(reportlab.__file__).parent / "fonts"
    files.update({"font_" + f: font_root / f for f in ("Vera.ttf", "VeraBd.ttf")})
    return {"schema": SCHEMA, "files": {k: digest(v.read_bytes()) for k, v in files.items()},
            "source_manifest_sha256": model["source_manifest_sha256"],
            "python_version": list(sys.version_info[:3]),
            "packages": {n: importlib.metadata.version(n) for n in ("reportlab", "pypdf", "Pillow", "charset-normalizer")},
            "configuration": {"width": renderer.W, "height": renderer.H, "font": renderer.FONT,
                              "pdf_compression": 0, "invariant": 1},
            "extra": extra or {}}


def ascii_pdf(writer):
    for obj in writer._objects:
        if isinstance(obj, StreamObject):
            obj._data = base64.a85encode(obj.get_data()) + b"~>"
            obj[NameObject("/Filter")] = NameObject("/ASCII85Decode")
            obj.pop(NameObject("/DecodeParms"), None)
            if hasattr(obj, "decoded_self"):
                obj.decoded_self = None
    buf = io.BytesIO()
    writer.write(buf)
    raw = buf.getvalue().replace(b"%\x93\x8c\x8b\x9e", b"%ASCI", 1).replace(b"%\xe2\xe3\xcf\xd3", b"%ASCI", 1)
    raw.decode("ascii")
    return raw


def paint_page(operations):
    buf = io.BytesIO()
    target = canvas.Canvas(buf, pagesize=(renderer.W, renderer.H), pageCompression=0, invariant=1)
    for name, args, kwargs in operations:
        getattr(target, name)(*unpack(args, target), **unpack(kwargs, target))
    target.save()
    return buf.getvalue()


def entry_pdf(entry):
    return base64.b64decode(entry["pdf_base64"], validate=True)


def valid_entry(entry, key, plan_hash, dependency_hash):
    try:
        if (entry["schema"], entry["key"], entry["plan_sha256"], entry["dependency_sha256"]) != (SCHEMA, key, plan_hash, dependency_hash):
            return False
        raw = entry_pdf(entry)
        if digest(raw) != entry["pdf_sha256"]:
            return False
        reader = PdfReader(io.BytesIO(raw), strict=True)
        return len(reader.pages) == 1 and not reader.pages[0].get("/Annots")
    except Exception:
        return False


def assemble(pages, page_pdfs, model):
    writer = PdfWriter()
    for raw in page_pdfs:
        writer.add_page(PdfReader(io.BytesIO(raw)).pages[0])
    targets = {}
    for number, page in enumerate(pages):
        for name in page["destinations"]:
            if name in targets:
                raise ValueError("Duplicate destination " + name)
            targets[name] = number
    for name in sorted(targets):
        writer.add_named_destination(name, targets[name])
    parents = {}
    for number, page in enumerate(pages):
        for title, key, level, closed in page["outlines"]:
            if level and level - 1 not in parents:
                raise ValueError("Outline skips a level")
            parents[level] = writer.add_outline_item(title, targets[key], parent=parents.get(level - 1), is_open=not closed)
            for obsolete in [i for i in parents if i > level]:
                del parents[obsolete]
        for link in page["links"]:
            if "url" in link:
                annotation = Link(rect=tuple(link["rect"]), url=link["url"])
            else:
                annotation = Link(rect=tuple(link["rect"]), target_page_index=targets[link["target"]])
            inserted = writer.add_annotation(number, annotation)
            if "url" not in link:
                # pypdf 6.10 leaves target_page_index as an integer here;
                # an explicit same-document destination requires a page ref.
                inserted["/Dest"][0] = writer.pages[targets[link["target"]]].indirect_reference
    writer.add_metadata({"/Title": model["title"], "/Author": "Henry Grant; prepared with OpenAI assistance",
                         "/Creator": "joint259_system_docs_incremental", "/Producer": "pypdf"})
    # Each isolated page carries self-contained fonts. Coalesce identical
    # resources before final serialization, keeping the assembled PDF compact.
    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    return ascii_pdf(writer)


def svg_version():
    result = subprocess.run(["pdftocairo", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return {"version": (result.stdout + result.stderr).decode("utf8").strip(),
            "executable_sha256": digest(Path(shutil.which("pdftocairo")).read_bytes())}


def paint_svg(raw):
    result = subprocess.run(["pdftocairo", "-svg", "-", "-"], input=raw,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    value = result.stdout.decode("utf8")
    if "<svg" not in value or "<image" in value:
        raise ValueError("Expected self-contained vector SVG")
    return value


def svg_name(kind, page_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", page_id):
        raise ValueError("Unsafe page ID for SVG filename")
    return KINDS[kind] + "__" + page_id + ".svg"


def linked_svgs(kind, pages, report, entries, version):
    targets = {name: svg_name(kind, info["id"]) for page, info in zip(pages, report["pages"]) for name in page["destinations"]}
    files = {}
    for page, info, entry in zip(pages, report["pages"], entries):
        svg_key = digest(canonical([entry["pdf_sha256"], version]))
        saved = entry.get("svg", {})
        if saved.get("key") != svg_key or digest(saved.get("text", "").encode("utf8")) != saved.get("sha256"):
            value = paint_svg(entry_pdf(entry))
            saved = {"key": svg_key, "text": value, "sha256": digest(value.encode("utf8"))}
            entry["svg"] = saved
        overlays = []
        for link in page["links"]:
            x1, y1, x2, y2 = link["rect"]
            overlays.append('<a xlink:href=%s><rect x="%s" y="%s" width="%s" height="%s" fill="transparent" pointer-events="all"/></a>' %
                            (quoteattr(link["url"] if "url" in link else targets[link["target"]]), x1, renderer.H-y2, x2-x1, y2-y1))
        files[svg_name(kind, info["id"])] = saved["text"].replace("</svg>", "\n" + "\n".join(overlays) + "\n</svg>")
    return files


class Engine:
    def __init__(self, model, cache=None, extra_dependencies=None, svg=False):
        self.cache = cache if cache is not None else {}
        self.dependencies = dependencies(model, extra_dependencies)
        self.dependency_hash = digest(canonical(self.dependencies))
        self.events = []
        self.svg_files = {}
        self.svg_version = svg_version() if svg else None

    def render(self, kind, model, refs):
        start = time.perf_counter()
        pages, report = plan(kind, model, refs)
        planning_seconds = time.perf_counter() - start
        page_pdfs, entries, rebuilt, reused = [], [], [], []
        for page, info in zip(pages, report["pages"]):
            plan_hash = digest(canonical(page["paint"]))
            key = digest(canonical([self.dependency_hash, plan_hash]))
            entry = self.cache.get(key)
            if not valid_entry(entry, key, plan_hash, self.dependency_hash):
                raw = paint_page(page["paint"])
                entry = {"schema": SCHEMA, "key": key, "plan_sha256": plan_hash,
                         "dependency_sha256": self.dependency_hash, "pdf_sha256": digest(raw), "pdf_base64": base64.b64encode(raw).decode("ascii")}
                self.cache[key] = entry
                rebuilt.append(info["id"])
            else:
                reused.append(info["id"])
            entries.append(entry)
            page_pdfs.append(entry_pdf(entry))
        raw = assemble(pages, page_pdfs, model)
        if self.svg_version is not None:
            self.svg_files.update(linked_svgs(kind, pages, report, entries, self.svg_version))
        report["sha256"] = digest(raw)
        self.events.append({"kind": kind, "rendered_pages": rebuilt, "reused_pages": reused,
                            "planning_seconds": planning_seconds, "elapsed_seconds": time.perf_counter() - start})
        return raw, report


def build(source, model, engine):
    """Run authoritative integrity/index/QA code with this engine's rendering."""
    source = renderer.source_views.open_source(source)
    previous_render, previous_model, previous_argv = renderer.render, renderer.MODEL, sys.argv
    class ModelInput:
        def read_text(self):
            return json.dumps(model)
    renderer.render, renderer.MODEL = engine.render, ModelInput()
    sys.argv = [str(Path(renderer.__file__)), "--source", str(source), "--emit-json"]
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            renderer.main(source_override=source)
    finally:
        renderer.render, renderer.MODEL, sys.argv = previous_render, previous_model, previous_argv
    files = json.loads(output.getvalue())
    files.update(engine.svg_files)
    receipt = {"schema": SCHEMA, "dependencies": engine.dependencies,
               "dependency_sha256": engine.dependency_hash, "model_sha256": digest(canonical(model)),
               "auxiliary_models": {p.name: digest(p.read_bytes()) for p in renderer.BASE.glob("joint259_system_docs_hierarchy*.json")},
               "pdfs": {n: digest(v.encode("ascii")) for n, v in files.items() if n.endswith(".pdf")},
               "source_binding": json.loads(files['source_binding.json']),
               "svg_converter": engine.svg_version,
               "scope": "Vector-page rendering cache only; science replay is separate.",
               "page_cache_validation": "Schema, dependency and drawing-plan keys, PDF hash and single-page structure checked before reuse."}
    files["incremental_receipt.json"] = renderer.stable(receipt)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=renderer.MODEL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cache", type=Path, help="Persistent cache JSON; default OUTPUT/../joint259-page-cache.json")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--svg", action="store_true", help="Also export linked vector SVGs; requires pdftocairo")
    parser.add_argument("--emit-json", action="store_true", help="No filesystem writes; emit artifacts and cache in one JSON object")
    args = parser.parse_args()
    if not args.emit_json and args.output is None:
        parser.error("--output or --emit-json is required")
    cache_path = args.cache or (args.output.parent / "joint259-page-cache.json" if args.output else None)
    cache = {}
    if not args.clean and cache_path and cache_path.exists():
        try:
            saved = json.loads(cache_path.read_text())
            if saved.get("schema") == SCHEMA and isinstance(saved.get("pages"), dict):
                cache = saved["pages"]
        except (OSError, ValueError):
            pass  # An absent or damaged cache is a clean rebuild, never success by receipt.
    model = json.loads(args.model.read_text())
    engine = Engine(model, cache, svg=args.svg)
    files = build(args.source.resolve(), model, engine)
    saved = {"schema": SCHEMA, "pages": engine.cache}
    result = {"files": files, "cache": saved, "measurements": engine.events}
    if args.emit_json:
        print(renderer.stable(result), end="")
        return
    # Fail before touching prior output; deliberately never writes scientific inputs.
    source = args.source.resolve()
    for candidate in (args.output.resolve(), cache_path.resolve()):
        if candidate == source or source in candidate.parents:
            parser.error("Output and cache must be outside the scientific source package")
    args.output.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        (args.output / name).write_text(content, encoding="utf8")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cache_path.with_name(cache_path.name + ".tmp")
    temporary.write_text(renderer.stable(saved), encoding="utf8")
    temporary.replace(cache_path)
    print(renderer.stable({"output": str(args.output), "cache": str(cache_path), "measurements": engine.events}), end="")


if __name__ == "__main__":
    main()
