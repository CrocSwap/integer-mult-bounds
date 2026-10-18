#!/usr/bin/env python3
"""Check numerical lifetimes of the pinned BIT coefficient evaluator."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
NAMES = ("words", "records", "matrices", "controller", "forms", "numeric")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), "fixed typed receipt")


def authenticated_sources():
    manifest = json.loads((PACKAGE / "SNAPSHOT.json").read_text())
    need(manifest["head"] == HEAD, "exact scientific dependency")
    need(manifest["repository"] == "https://github.com/CrocSwap/integer-mult-bounds",
         "canonical scientific repository")
    expected = {name + ".py" for name in NAMES} | {"NOTICE.md"}
    need(len(manifest["files"]) == len(expected), "closed source inventory")
    exports = {}
    for item in manifest["files"]:
        name = Path(item["path"]).name
        need(name in expected and name not in exports, "unique source name")
        need(item["path"] == "vendor/" + name, "canonical local source path")
        original = "research/selected-bit-node/" + ("" if name == "NOTICE.md" else "vendor/") + name
        need(item["source_path"] == original, "exact original source path")
        path = PACKAGE / item["path"]
        need(not path.is_symlink(), "regular source export")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
        exports[name] = raw
    return exports


def load_sources():
    exports = authenticated_sources()
    need(not any(name in sys.modules for name in NAMES), "no preloaded scientific modules")
    try:
        for name in NAMES:
            module = ModuleType(name)
            path = PACKAGE / "vendor" / (name + ".py")
            module.__file__ = str(path)
            sys.modules[name] = module
            # Authenticate every export before execution; bypass stale .pyc files.
            exec(compile(exports[name + ".py"], str(path), "exec", dont_inherit=True), module.__dict__)
    except Exception:
        for name in NAMES:
            sys.modules.pop(name, None)
        raise
    return SimpleNamespace(**{name: sys.modules[name] for name in NAMES})


class Census:
    """Observe allocations, with independent scans of occupied numerical cells."""

    def __init__(self, modules, residues, indices, extra_residues, extra_indices):
        self.modules, self.arenas = modules, (residues, indices)
        self.entry = tuple(len(arena.live) for arena in self.arenas)
        self.limits = tuple(a + b for a, b in zip(self.entry, (extra_residues, extra_indices), strict=True))
        self.peak, self.next_scan = list(self.entry), [1, 1]
        self.scans = self.inverse_depth = 0
        self.inverse_entries = {}
        self.zero, self.inverse = modules.words.Arena.zero, modules.words.Ring.inverse

    def scan(self, arena):
        symbols = sum(cell not in (self.modules.words.LEFT, self.modules.words.BLANK)
                      for word in (*arena.words, arena.template) for cell in word.cells)
        need(symbols == (len(arena.live) + 1) * (arena.bits + 1), "literal numerical cell census")
        self.scans += 1

    def allocate(self, arena):
        word = self.zero(arena)
        if arena not in self.arenas:
            return word
        position, live = self.arenas.index(arena), len(arena.live)
        need(live <= self.limits[position], "numerical word budget exceeded")
        if live > self.peak[position]:
            self.peak[position] = live
            if live >= self.next_scan[position] or self.inverse_depth:
                self.scan(arena)
                self.next_scan[position] = max(2 * live, self.next_scan[position])
        return word

    def invert(self, ring, operand):
        caller = sys._getframe(2).f_code.co_name
        self.inverse_entries[caller] = max(self.inverse_entries.get(caller, 0), len(ring.arena.live))
        self.inverse_depth += 1
        try:
            return self.inverse(ring, operand)
        finally:
            self.inverse_depth -= 1

    def __enter__(self):
        for arena in self.arenas:
            self.scan(arena)
        self.modules.words.Arena.zero = lambda arena: self.allocate(arena)
        self.modules.words.Ring.inverse = lambda ring, operand: self.invert(ring, operand)
        return self

    def __exit__(self, *_exception):
        self.modules.words.Arena.zero, self.modules.words.Ring.inverse = self.zero, self.inverse

    def record(self):
        return {"entry": self.entry, "peak": self.peak,
                "extra": [a - b for a, b in zip(self.peak, self.entry, strict=True)],
                "cell_scans": self.scans, "inverse_entry_maxima": self.inverse_entries}


def fixture(modules, modes, modulus=3, residents=3, current=False):
    need(len(modes) <= 4 and set(modes) <= set("GPUHR"), "finite fixture domain")
    w, r = modules.words, modules.records
    root_size = 64 ** (len(modes) + 1)
    indices = w.Arena(root_size.bit_length() + 1, 128)
    residues = w.Arena(modulus.bit_length() + 1, 65536)
    mod = residues.literal(modulus)
    ring = w.Ring(mod)
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    bad, good = [list(row) for row in identity], [list(row) for row in identity]
    for i in range(64):
        bad[i][0], bad[i][1], bad[i][2] = int(i in (0, 1)), int(i == 2), int(i == 1)
    good[2][0] = 1
    specs = {code: SimpleNamespace(code=code, good=bool(code), low=low,
             template=SimpleNamespace(q=modulus, rank=2, preparation=identity))
             for code, low in enumerate((bad, good))}
    events = [(0, 1, 2, 0, 0, 0) if mode == "G" else (2, 0, 2, 0, 0, mode == "H")
              if mode in "UH" else (1, 0, 2, 64 if mode == "R" else 0, mode == "R", 0)
              for mode in modes]
    program = r.Program.fixture(indices, residues, root_size, 2, events)
    fields = r.Fields.fixture(indices, residues, [(event[1], [[0] * 64 for _ in range(64)])
                             for event in events] + ([(0, [[0] * 64 for _ in range(64)])] if current else []))
    borrowed = [residues.literal(i % modulus) for i in range(residents)]
    index_borrowed = [indices.literal(i) for i in range(residents)]
    coordinate = indices.zero()
    callback = modules.controller.Callback(ring, indices, program, fields, specs, 0,
                                           allow_fallback=True, leaf=not current)
    return SimpleNamespace(**locals())


def preserved(case, saved, source_bytes):
    actual = tuple({slot: bytes(arena.words[slot].cells) for slot in arena.live}
                   for arena in (case.residues, case.indices))
    need(actual == saved, "numerical ownership and all borrowed values restored")
    need((bytes(case.program.tape.cells), bytes(case.fields.tape.cells)) == source_bytes,
         "program and fields unchanged")
    need(case.program.tape.head == case.fields.tape.head == 1, "input tape heads restored")
    for arena in (case.residues, case.indices):
        need(all(arena.words[slot].head == 1 for slot in arena.live), "borrowed word heads restored")
        need(arena.template.head == 1, "template head restored")
    for stack in (case.callback.pending, case.callback.values):
        for tape in (stack.tape, stack.reverse):
            need(tape.head == 1 and all(symbol == 4 for symbol in tape.cells[1:]),
                 "continuation tape erased and head restored")


def cleanup(case, page=None):
    if page is not None:
        page.close()
        case.indices.free(page.columns)
    case.callback.close()
    case.program.tape.clear()
    case.fields.tape.clear()
    case.indices.rollback(set())
    case.ring.close()
    case.residues.free(case.mod)
    for word in case.borrowed:
        case.residues.free(word)
    need(not case.residues.live and not case.indices.live, "complete fixture cleanup")


def weight_case(modules, modes, modulus=3, residents=3, index_budget=10):
    case = fixture(modules, modes, modulus, residents)
    saved = tuple({slot: bytes(arena.words[slot].cells) for slot in arena.live}
                  for arena in (case.residues, case.indices))
    source_bytes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    # Fixed integer fixtures: good pivots are one; pair field zero swaps
    # rows zero/one and has diagonal -1. Reset and reversed field64 give one.
    expected = 1 if modes and modes[-1] in "UHR" else (modulus - 1 if "P" in modes else 2)
    with Census(modules, case.residues, case.indices, 20490, index_budget) as census:
        result = case.callback.weight(case.coordinate)
        need(result.inspect() == expected, "literal expected generated coefficient")
        case.residues.free(result)
        for arena in census.arenas:
            census.scan(arena)
    preserved(case, saved, source_bytes)
    record = {"modes": modes, "modulus": modulus, "residents": residents,
              "coefficient": expected, **census.record()}
    cleanup(case)
    return record


def page_fixture(modules, modes="P"):
    case = fixture(modules, modes, current=True)
    scope = case.callback.plus(case.callback.depth, case.callback.one_index)
    projector = case.callback.prepare(case.callback.depth, 0, scope)
    case.indices.free(scope)
    form = modules.forms.fallback_form(projector, case.ring)
    modules.matrices.Matrices(case.ring).free(projector)
    signature = tuple((r.kind, r.target, r.source, r.permutation) for r in form.reductions)
    plan = SimpleNamespace(good=False, dimension=64, rank=2, reductions=signature,
                           permutation=form.permutation, negative_sign=form.negative_sign)
    columns = case.indices.literal(case.callback.final_size.inspect() // 64)
    page = modules.numeric.Page(plan, form, case.ring, case.indices, columns, case.callback.weight,
                                case.callback.depth, 0, case.program)
    need(len(case.residues.live) == len(case.borrowed) + 16388, "fallback form plus four constants")
    need(len(case.indices.live) == len(case.index_borrowed) + 11, "page and callback indices")
    need(form.permutation[0] == 1 and form.diagonal[0].inspect() == 2, "fixed pair fixture")
    return case, page


def page_case(modules, reverse=False, negative=False, modes="P"):
    case, page = page_fixture(modules, modes)
    saved = tuple({slot: bytes(arena.words[slot].cells) for slot in arena.live}
                  for arena in (case.residues, case.indices))
    source_bytes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    request = SimpleNamespace(kind="child", child_kind="pair", field=0, reverse=reverse,
                              coordinate=case.coordinate, negative_inverse=negative)
    # Both parent weights equal two. The diagonal is two; -1/2 is one mod3.
    expected = 1 if negative else 2
    with Census(modules, case.residues, case.indices, 36879 + 3 - len(case.residues.live),
                23 + 4 - len(case.indices.live)) as census:
        result = page.evaluate(request)
        need(result.inspect() == expected, "literal expected page coefficient")
        case.residues.free(result)
    preserved(case, saved, source_bytes)
    record = {"modes": modes, "reverse": reverse, "negative": negative,
              "coefficient": expected, **census.record()}
    cleanup(case, page)
    return record


def inverse_case(modules, size=2, budget=None):
    w = modules.words
    residues, indices = w.Arena(4, 128), w.Arena(8, 8)
    modulus = residues.literal(5)
    ring = w.Ring(modulus)
    matrices = modules.matrices.Matrices(ring)
    source = [[residues.literal(2 if i == j else 0) for j in range(size)] for i in range(size)]
    saved = set(residues.live)
    with Census(modules, residues, indices, 2 * size * size + 10 if budget is None else budget, 0) as census:
        result = matrices.inverse(source)
        need([[x.inspect() for x in row] for row in result] ==
             [[3 if i == j else 0 for j in range(size)] for i in range(size)], "literal inverse endpoint")
        matrices.free(result)
    need(set(residues.live) == saved, "inverse returns only owned matrix")
    need(census.peak[0] - census.entry[0] == 2 * size * size + 10, "sharp matrix inverse witness")
    matrices.free(source)
    ring.close()
    residues.free(modulus)
    return {"size": size, **census.record()}


def form_case(modules, dimension, rank):
    w = modules.words
    residues = w.Arena(3, 512)
    modulus = residues.literal(3)
    ring = w.Ring(modulus)
    projector = [[residues.literal(int(i == j and i < rank)) for j in range(dimension)]
                 for i in range(dimension)]
    baseline = set(residues.live)
    good = modules.forms.good_form(projector, rank, ring)
    good_words = len(residues.live) - len(baseline)
    need(good_words == dimension ** 2 + 2 * dimension * rank - rank ** 2, "exact stored good form")
    good.close(ring)
    fallback = modules.forms.fallback_form(projector, ring)
    fallback_words = len(residues.live) - len(baseline)
    need(fallback_words == 4 * dimension ** 2, "exact stored fallback form")
    fallback.close(ring)
    need(set(residues.live) == baseline, "form close restores borrowed input")
    modules.matrices.Matrices(ring).free(projector)
    ring.close()
    residues.free(modulus)
    need(not residues.live, "form fixture cleanup")
    return {"dimension": dimension, "rank": rank, "good": good_words, "fallback": fallback_words}


def verify():
    modules = load_sources()
    cases = [weight_case(modules, modes) for modes in ("", "G", "P", "U", "H", "R", "PP", "GP", "PG", "PPPP")]
    cases.append(weight_case(modules, "P", 5, 7))
    pages = [page_case(modules, reverse, negative) for reverse in (False, True) for negative in (False, True)]
    pages.append(page_case(modules, modes="PG"))
    inverse = [inverse_case(modules, size) for size in (1, 2, 3)]
    forms = [form_case(modules, m, r) for m, r in ((2, 1), (3, 1), (3, 2), (4, 3))]
    return {"status": "PASS_SELECTED_CALLBACK_WORD_LIVENESS", "source_head": HEAD,
            "bounds": {"weight_residues": 20490, "weight_indices": 10,
                       "page_residues": 36879, "page_indices": 23},
            "weight_cases": cases, "page_cases": pages, "sharp_inverse_cases": inverse, "form_cases": forms,
            "scope": "Numerical content of weight and initialized Page.evaluate; no constructor, physical placement or total reserve admission."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="print fresh receipt without comparing the committed one")
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    if args.sources_only:
        authenticated_sources()
        print(HEAD)
        return
    result = verify()
    if not args.emit:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        check_receipt(result, expected)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
