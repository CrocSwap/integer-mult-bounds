"""Compile one fixed-dimensional instance of the retained encoded consumer.

Dimension and finite label widths are compile-time constants. Runtime field
digits, coordinates and depths stay in the unchanged binary word machine.
Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/delayed-cover-chronological-fields/numerical/"


def need(condition, label):
    if not condition:
        raise ValueError(label)


@dataclass(frozen=True)
class Template:
    q: int
    rank: int
    preparation: tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class Specification:
    code: int
    template: Template
    low: tuple[tuple[int, ...], ...]
    good: bool


def changes(dimension):
    """Every specialization site is explicit and checked once against its pin."""
    n = dimension
    bits = max(16, (2*n).bit_length())
    return {
        "words": [
            ("0 <= constant <= 128", f"0 <= constant <= {2*n}"),
        ],
        "records": [
            ("FINITE_BITS = 16", f"FINITE_BITS = {bits}"),
            ("f = size//64", f"f = size//{n}"),
            ("out = [[read_word(self.tape, self.residue_arena) for _ in range(64)] for _ in range(64)]",
             f"out = [[read_word(self.tape, self.residue_arena) for _ in range({n})] for _ in range({n})]"),
            ("len(high) == 64 and all(len(row) == 64 for row in high)",
             f"len(high) == {n} and all(len(row) == {n} for row in high)"),
        ],
        "matrices": [
            ("0 < rows <= 128 and 0 < columns <= 256", f"0 < rows <= {2*n} and 0 < columns <= {4*n}"),
            ("size <= 128 and all(len(row) == size for row in matrix)",
             f"size <= {2*n} and all(len(row) == size for row in matrix)"),
            ("size <= 64", f"size <= {n}"),
        ],
        "controller": [
            ("0 < limit <= 128", f"0 < limit <= {2*n}"),
            ("for _ in range(8):", f"for _ in range({n.bit_length()+1}):"),
            ("self.index.literal(64)", f"self.index.literal({n})"),
            ("1 <= rank <= 42", f"1 <= rank < {n}"),
            ("field < 127 and reverse == (field >= 64)",
             f"field < {2*n-1} and reverse == (field >= {n})"),
            ("if row < 64:", f"if row < {n}:"),
            ("0 < target_row < 64", f"0 < target_row < {n}"),
            ("allow_fallback=False, leaf=False):",
             "allow_fallback=False, leaf=False, stack_roles=None):"),
            ("self.pending, self.values = Stack(index_arena, self.residue), Stack(index_arena, self.residue)",
             "need(stack_roles is not None and len(stack_roles) == 2, 'two borrowed continuation roles')\n"
             "        self.pending, self.values = stack_roles\n"
             "        need(all(s.index_arena is index_arena and s.residue_arena is self.residue and s.empty() "
             "for s in stack_roles), 'closed matching continuation workspace')"),
        ],
    }


def build(dimension: int):
    """Return actual encoded modules specialized before any runtime input.

    This is a source compiler, not a runtime matrix-oracle substitution.
    The arithmetic/record/stack algorithms retain their source bytes apart
    from the listed static bounds. The two listed interface edits take
    the two Stack objects from an exclusive reusable workspace.
    """
    need(type(dimension) is int and dimension >= 2, "fixed dimension >=2")
    pins = {r["path"]: r["sha256"] for r in json.loads((PACKAGE/"SOURCES.json").read_text())["files"]}
    edits = changes(dimension)
    originals = {}
    transformed = {}
    for name in ("words", "records", "matrices", "controller"):
        path = SOURCE + name + ".py"
        raw = (ROOT/path).read_bytes()
        need(sha256(raw).hexdigest() == pins[path], "source drift: " + path)
        originals[name] = raw.decode()
        text = originals[name]
        for old, new in edits.get(name, []):
            need(text.count(old) == 1, "specialization site count: " + old)
            text = text.replace(old, new, 1)
        transformed[name] = text
    # Imports in the unchanged source use these four module names. Restore the
    # process module registry after compilation so distinct N instances do not
    # alias one another or a caller's previously loaded source cohort.
    saved = {name: sys.modules.get(name) for name in transformed}
    modules = {}
    try:
        for name, text in transformed.items():
            module = ModuleType(name)
            module.__file__ = str(ROOT/(SOURCE+name+".py"))
            sys.modules[name] = module
            exec(compile(text, module.__file__, "exec"), module.__dict__)
            modules[name] = module
    finally:
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
    return SimpleNamespace(dimension=dimension,
                           finite_bits=max(16,(2*dimension).bit_length()),
                           edit_count=sum(map(len, edits.values())),
                           source_hashes={k:sha256(v.encode()).hexdigest() for k,v in originals.items()},
                           specialized_hashes={k:sha256(v.encode()).hexdigest() for k,v in transformed.items()},
                           **modules)


class Workspace:
    """One real, exclusive four-tape continuation inventory across callbacks.

    Residue/index contexts are fixed for this workspace. A callback borrows
    Program/Fields, and returns these stack roles before a later call reuses
    them. Erased historical suffixes remain in the same Tape objects.
    """
    def __init__(self, modules, ring, index_arena):
        self.modules, self.ring, self.index = modules, ring, index_arena
        self.roles = tuple(modules.records.Stack(index_arena,ring.arena) for _ in range(2))
        self.active = False
        workspace = self
        base = self.modules.controller.Callback
        class BoundCallback(base):
            def close(self):
                need(workspace.active, "live callback lease")
                super().close()
                workspace.active=False

            def abort(self):
                try:
                    super().abort()
                finally:
                    workspace.active=False
        self.callback_type = BoundCallback

    def open(self, program, fields, specifications, current_code, *, allow_fallback=False, leaf=False):
        need(not self.active, "exclusive continuation workspace")
        need(program.index_arena is self.index and fields.index_arena is self.index and
             program.residue_arena is self.ring.arena and fields.residue_arena is self.ring.arena,
             "one encoded numerical context")
        self.active = True
        try:
            return self.callback_type(self.ring,self.index,program,fields,specifications,current_code,
                                      allow_fallback=allow_fallback,leaf=leaf,stack_roles=self.roles)
        except Exception:
            # This flag has no numerical payload and never substitutes for
            # the inherited abort/rollback or input-validity contracts.
            self.active=False
            raise


def footprint(dimension, depth, residue_bits, index_bits, code_bits):
    """Conservative explicit extents; input entry history is charged separately.

    The numerical bounds are additional pending Word demand over legal entry
    residents, before a capacity guard. No successful execution is assumed.
    """
    need(type(dimension) is int and dimension >= 2, "fixed dimension")
    need(all(type(v) is int and v >= 0 for v in (depth,residue_bits,index_bits,code_bits)),
         "integer footprint inputs")
    need(residue_bits >= 2 and index_bits >= dimension.bit_length()+1 and code_bits >= 1,
         "word/label extent")
    n,h,r,i,q = dimension,depth,residue_bits,index_bits,code_bits
    f = max(16,(2*n).bit_length())
    t = max(2*i+4,r+3)
    return {"residue_pending":16*n*n+128,"index_pending":128,
            "program_extent":2*i+r+10+h*(q+5*f+2*i+12),
            "fields_extent":(h+1)*(q+n*n*(r+1)+2)+4,
            "four_stack_extents":(4*h+12)*t+16,
            "finite_label_bits":f}
