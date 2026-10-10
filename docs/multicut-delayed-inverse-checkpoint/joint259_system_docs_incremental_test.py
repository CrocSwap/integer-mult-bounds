#!/usr/bin/env python3
"""Read-only, in-memory mutation and equivalence tests for the visual cache."""
from __future__ import annotations
import argparse, contextlib, copy, hashlib, io, json, subprocess, time
from pathlib import Path
from xml.etree import ElementTree
import joint259_system_docs_incremental as inc


def raster(raw, dpi, page=None):
    command = ["pdftoppm", "-r", str(dpi)]
    if page:
        command += ["-f", str(page), "-l", str(page), "-singlefile"]
    return subprocess.run(command + ["-"], input=raw, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout


def pdf_structure(raw):
    reader = inc.PdfReader(io.BytesIO(raw), strict=True)
    targets = {p.indirect_reference.idnum: i for i, p in enumerate(reader.pages)}
    links = []
    for i, page in enumerate(reader.pages):
        assert (page.extract_text() or "").strip(), ("Empty page", i)
        for item in page.get("/Annots", []):
            annotation = item.get_object()
            action = annotation.get("/A", {})
            if action.get("/S") == "/URI":
                links.append((i, tuple(annotation["/Rect"]), str(action["/URI"])))
                continue
            dest = annotation.get("/Dest")
            if dest is None:
                dest = action["/D"]
            assert dest[0].idnum in targets, ("Dangling link", i, dest)
            links.append((i, tuple(annotation["/Rect"]), targets[dest[0].idnum]))
    destinations = {n: reader.get_destination_page_number(d) for n, d in reader.named_destinations.items()}
    assert all(0 <= p < len(reader.pages) for p in destinations.values())
    return {"texts": [p.extract_text() for p in reader.pages],
            "streams": [hashlib.sha256(p.get_contents().get_data()).hexdigest() for p in reader.pages],
            "links": links, "destinations": destinations, "page_count": len(reader.pages)}


@contextlib.contextmanager
def patched(cls, attribute, function):
    old = getattr(cls, attribute)
    setattr(cls, attribute, function(old))
    try:
        yield
    finally:
        setattr(cls, attribute, old)


def run(source, dpi=40, svg=True):
    r = inc.renderer
    model = json.loads(r.MODEL.read_text())
    source_count = r.integrity(source, model["source_manifest_sha256"])
    refs = r.source_index(source, model)
    report = {"status": "RUNNING", "source_files": source_count, "raster_dpi": dpi,
              "scope": "Documentation and cache tests only; no scientific replay.",
              "baseline": {}, "mutations": [], "invalidation": [], "stale_cache": []}
    if dpi:
        version = subprocess.run(["pdftoppm", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        report["raster_renderer"] = (version.stdout + version.stderr).decode("utf8").strip()
    rejected = []
    for kind in ("logical", "combined"):
        for label, call in (("renderer", lambda: r.render(kind, model, refs)),
                            ("planning", lambda: inc.plan(kind, model, refs)),
                            ("cache engine", lambda: inc.Engine(model).render(kind, model, refs))):
            try:
                call()
            except ValueError as error:
                assert "Unsupported architecture output kind" in str(error)
            else:
                raise AssertionError(("Rejected output family recreated", kind, label))
            rejected.append({"kind": kind, "entry_point": label})
    report["unsupported_output_kinds_rejected"] = rejected
    cache, baseline = {}, {}
    for kind in inc.KINDS:
        cold = inc.Engine(model, cache)
        raw, details = cold.render(kind, model, refs)
        warm = inc.Engine(model, cache)
        warm_raw, _ = warm.render(kind, model, refs)
        clean = inc.Engine(model)
        clean_raw, _ = clean.render(kind, model, refs)
        t = time.perf_counter()
        original, _ = r.render(kind, model, refs)
        original_seconds = time.perf_counter() - t
        assert raw == warm_raw == clean_raw, kind
        assert not warm.events[-1]["rendered_pages"], kind
        one, two = pdf_structure(raw), pdf_structure(original)
        assert one["texts"] == two["texts"], (kind, "text")
        assert one["streams"] == two["streams"], (kind, "drawing streams")
        assert one["links"] == two["links"], (kind, "link destinations")
        if dpi:
            pixels = raster(raw, dpi)
            assert pixels == raster(original, dpi), (kind, "full raster")
            assert pixels == raster(clean_raw, dpi), (kind, "clean raster")
        baseline[kind] = (raw, details)
        report["baseline"][kind] = {"pages": one["page_count"], "links": len(one["links"]),
                                   "cold_seconds": cold.events[-1]["elapsed_seconds"],
                                   "warm_seconds": warm.events[-1]["elapsed_seconds"],
                                   "original_seconds": original_seconds,
                                   "warm_rendered_pages": 0, "sha256": inc.digest(raw),
                                   "clean_warm_byte_identical": True,
                                   "original_decoded_streams_text_links_identical": True,
                                   "all_pages_raster_identical": bool(dpi)}
    base_raw, base_details = baseline["functional"]

    def compare(label, changed_model, expected=None, changed_refs=None):
        current_refs = changed_refs if changed_refs is not None else r.source_index(source, changed_model)
        incremental = inc.Engine(changed_model, cache)
        actual, details = incremental.render("functional", changed_model, current_refs)
        clean = inc.Engine(changed_model)
        expected_raw, _ = clean.render("functional", changed_model, current_refs)
        assert actual == expected_raw, label
        assert pdf_structure(actual) == pdf_structure(expected_raw), label
        event = incremental.events[-1]
        rebuilt = event["rendered_pages"]
        if expected is not None:
            assert set(rebuilt) == set(expected), (label, rebuilt, expected)
        if dpi and rebuilt:
            changed_page = next(v["page"] for v in details["pages"] if v["id"] == rebuilt[0])
            assert raster(actual, dpi, changed_page) == raster(expected_raw, dpi, changed_page), label
        report["mutations"].append({"case": label, "rendered_pages": rebuilt,
                                    "reused_page_count": len(event["reused_pages"]),
                                    "incremental_seconds": event["elapsed_seconds"],
                                    "clean_seconds": clean.events[-1]["elapsed_seconds"],
                                    "byte_identical_to_clean": True, "navigation_valid": True})
        return actual

    changed = copy.deepcopy(model)
    changed["blocks"][0]["what"] += " Test."
    compare("block behavior", changed, ["CATALOG"])
    changed = copy.deepcopy(model)
    changed["blocks"][0]["brief"] += " Test."
    compare("block diagram summary", changed, ["FVIEW1"])
    changed = copy.deepcopy(model)
    changed["blocks"][0]["name"] += " test"
    compare("block display rename", changed, ["FVIEW1", "CATALOG"])
    changed = copy.deepcopy(model)
    changed["requirements"][0]["text"] += " Test."
    compare("requirement wording", changed, ["REQUIREMENTS"])
    changed = copy.deepcopy(model)
    changed["edges"][0]["cache_test_note"] = "An index-only controlled edit"
    compare("index-only edge metadata", changed, [])
    engine = inc.Engine(changed, cache)
    files = inc.build(source, changed, engine)
    assert json.loads(files["connection_index.json"])["block_edges"][0]["cache_test_note"] == "An index-only controlled edit"
    altered_refs = copy.deepcopy(refs)
    next(iter(altered_refs.values()))["sha256"] = "0" * 64
    compare("source traceability hash projection", model, ["SOURCES"], altered_refs)

    def change_wire(old):
        def wrapped(self, a, b, *args, **kwargs):
            if self.pages[-1]["id"] == "FVIEW1":
                a = (a[0] + 1, *a[1:])
            return old(self, a, b, *args, **kwargs)
        return wrapped
    with patched(inc.PlanningDoc, "arrow", change_wire):
        compare("diagram wiring coordinate", model, ["FVIEW1"])

    def change_target(old):
        def wrapped(self, contents, destinationname, *args, **kwargs):
            if destinationname == "B_F01":
                destinationname = "B_F03"
            return old(self, contents, destinationname, *args, **kwargs)
        return wrapped
    with patched(inc.RecordingCanvas, "linkRect", change_target):
        redirected = compare("navigation-only internal target", model, [])
        assert redirected != base_raw

    def change_url(old):
        def wrapped(self, url, *args, **kwargs):
            return old(self, url + "#cache-test", *args, **kwargs)
        return wrapped
    base_links = pdf_structure(base_raw)["links"]
    if any(isinstance(link[2], str) for link in base_links):
        with patched(inc.RecordingCanvas, "linkURL", change_url):
            redirected = compare("navigation-only external URL", model, [])
            assert redirected != base_raw

    extended = copy.deepcopy(model)
    for identifier in ("F98", "F99"):
        block = copy.deepcopy(model["blocks"][-1])
        block["id"], block["name"] = identifier, "Test-only catalog block"
        block["inputs"], block["outputs"] = [], []
        block["requirements"] = []
        extended["blocks"].append(block)
    compare("add catalog blocks and page", extended)
    renamed = copy.deepcopy(extended)
    renamed["blocks"][-1]["id"] = "F97"
    compare("stable block ID rename", renamed, ["CATALOG22"])
    restored = compare("delete added blocks and undo all edits", model, [])
    assert restored == base_raw

    return finish_checks(report, source, model, refs, cache, base_raw, base_details, source_count, svg)


def finish_checks(report, source, model, refs, cache, base_raw, base_details, source_count, svg):
    r = inc.renderer
    # Controlled dependency digests avoid writing scientific inputs.
    for dependency in ("renderer_code", "font_bytes", "requirements_pin", "source_manifest", "configuration"):
        engine = inc.Engine(model, cache, extra_dependencies={dependency: "controlled different digest"})
        raw, details = engine.render("functional", model, refs)
        assert len(engine.events[-1]["rendered_pages"]) == len(details["pages"])
        assert raw == base_raw
        report["invalidation"].append({"dependency": dependency, "rendered_page_count": len(details["pages"])})
    pages, _ = inc.plan("functional", model, refs)
    engine = inc.Engine(model, cache)
    plan_hash = inc.digest(inc.canonical(pages[0]["paint"]))
    first_key = inc.digest(inc.canonical([engine.dependency_hash, plan_hash]))
    for field, value in (("schema", "obsolete"), ("plan_sha256", "0" * 64),
                         ("dependency_sha256", "0" * 64), ("pdf_sha256", "0" * 64),
                         ("pdf_base64", "not a PDF")):
        damaged = dict(cache)
        damaged[first_key] = dict(cache[first_key], **{field: value})
        repair = inc.Engine(model, damaged)
        raw, _ = repair.render("functional", model, refs)
        assert raw == base_raw
        assert repair.events[-1]["rendered_pages"] == ["CONTENTS"]
        report["stale_cache"].append({"damaged_field": field, "rebuilt": ["CONTENTS"], "clean_equality": True})
    wrong = copy.deepcopy(model)
    wrong["source_manifest_sha256"] = "0" * 64
    try:
        inc.build(source, wrong, inc.Engine(wrong, cache))
    except ValueError as error:
        assert "Unrecognized scientific/public source manifest" in str(error)
    else:
        raise AssertionError("A stale cache bypassed source-pin checking")
    report["wrong_scientific_pin_rejected"] = True
    persisted_cache = json.loads(json.dumps(cache))
    warm_files = inc.build(source, model, inc.Engine(model, persisted_cache))
    clean_files = inc.build(source, model, inc.Engine(model))
    assert warm_files == clean_files
    report["all_clean_warm_artifacts_identical_after_cache_json_roundtrip"] = sorted(warm_files)
    if svg:
        exporter = inc.Engine(model, cache, svg=True)
        exporter.render("functional", model, refs)
        first = dict(exporter.svg_files)
        exporter.render("functional", model, refs)
        assert first == exporter.svg_files
        all_links, external_links = 0, 0
        for name, value in first.items():
            parsed = ElementTree.fromstring(value)
            assert "<image" not in value
            for element in parsed.iter():
                if element.tag.endswith("}a"):
                    target = element.attrib["{http://www.w3.org/1999/xlink}href"]
                    if target.startswith(("https://", "http://")):
                        external_links += 1
                    else:
                        assert target in first, (name, target)
                        all_links += 1
        assert all_links == base_details["internal_links"]
        report["svg"] = {"pages": len(first), "internal_links": all_links,
                         "external_links": external_links, "warm_identical": True,
                         "embedded_raster_images": 0, "converter": exporter.svg_version}
    assert r.integrity(source, model["source_manifest_sha256"]) == source_count
    report["dependencies"] = inc.dependencies(model)
    report["status"] = "PASS"
    report["limitations"] = ["Pixel equality is at the recorded resolution; human layout review is separate.",
                              "The original renderer has a different PDF object layout; decoded drawing streams, text, link targets and pixels are compared.",
                              "Dependency invalidation uses in-memory changed-digest overrides, not edits to pinned source files."]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=inc.renderer.BASE / "pr259_interval_compatibility_20261010/hybrid_package")
    parser.add_argument("--raster-dpi", type=int, default=40, help="0 skips raster checks")
    parser.add_argument("--skip-svg", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.source.resolve(), args.raster_dpi, not args.skip_svg), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
