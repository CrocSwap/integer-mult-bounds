"""Independent execution of the narrow source reservation adapter.

The candidate source_binding.py is loaded against a tiny port shim and the
independent literal interpreter from check_graph.py. No candidate hardware.py,
verify.py, numerical provider, or #7596 arithmetic graph is imported.
"""
from __future__ import annotations

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_graph as independent

CANDIDATE = independent.CANDIDATE


class Port:
    def __init__(self, word):
        self.word = word

    @property
    def cells(self):
        return self.word.cells

    @property
    def head(self):
        return self.word.head

    @head.setter
    def head(self, value):
        self.word.head = value


class Tape:
    def __init__(self, cells, head=0):
        self.cells = cells
        self.head = head


shim = types.ModuleType("hardware")
shim.WordPort = Port
sys.modules["hardware"] = shim
spec = spec_from_file_location("candidate_source_binding", CANDIDATE / "source_binding.py")
binding = module_from_spec(spec)
spec.loader.exec_module(binding)


class Machine:
    def __init__(self, code, metadata):
        self.code, self.metadata = code, metadata
        self.steps = self.calls = 0

    def run(self, ports, entry):
        cells = [p.cells for p in ports]
        heads = [p.head for p in ports]
        pc = self.metadata["entries"][entry] if isinstance(entry, str) else entry
        result = independent.execute(self.code, cells, heads, pc)
        for p, head in zip(ports, heads):
            p.head = head
        self.steps += result["instructions"]
        self.calls += 1
        return result


class Arena:
    pass


class Word:
    pass


class ParentBinding:
    def reserve(self, *args):
        raise ValueError("unreplaced parent two-output reservation called")

    def reserve_simple(self, *args):
        raise ValueError("unreplaced parent simple reservation called")


def create(code, metadata, p=7):
    cells, heads = independent.new_fixture(p, list(range(63, 7, -1)), pattern=5)
    arena = Arena()
    arena.capacity = 64
    arena.available = list(range(63, 7, -1))
    arena.live = set(range(8))
    arena.words = []
    arena.meter = types.SimpleNamespace(allocations=0, peak_live=8)
    for slot in range(65):
        word = Word()
        word.slot = slot if slot < 64 else -1
        word.arena = arena
        word.cells = cells[slot]
        word.head = heads[slot]
        if slot < 64:
            arena.words.append(word)
        else:
            arena.template = word
    machine = Machine(code, metadata)
    owner = binding.Owner(arena, machine, *(Tape(cells[t]) for t in (65, 66, 67)))
    return arena, owner, machine


def complete(word, p=7):
    """Explicit external-producer simulation, excluded from lifecycle invoice."""
    independent.require(set(word.cells[1:]) <= {"_"}, "reserved body blank")
    word.cells[1:p + 2] = ["1"] * p + ["R"]


def expected_cost(m, outputs):
    return (122 * m + 242, 158 * m + 397, 194 * m + 516)[outputs]


def run():
    code, metadata = independent.candidate.compile_program()
    domains = []
    total_calls = total_steps = 0
    for m in (0, 1, 2, 17, 55, 56):
        for count in range(3):
            if count > m:
                continue
            arena, owner, machine = create(code, metadata)
            for _ in range(56 - m):
                word = owner.allocate()
                complete(word)
            beginning = machine.steps
            before = [deepcopy(w.cells) for w in arena.words]
            # Equal simple operands are legal. Two-output division stays distinct.
            left = arena.words[0]
            right = arena.words[1 if count == 2 else 0]
            selected = binding.arithmetic_binding(ParentBinding, owner)()
            if count == 2:
                result = selected.reserve(arena, left, right)
            else:
                one = selected.reserve_simple(arena, left, right, bool(count))
                result = (one,) if count else ()
            used = machine.steps - beginning
            independent.require(used == expected_cost(m, count), "reservation invoice")
            expected_slots = list(range(64 - m, 64 - m + count))
            independent.require([w.slot for w in result] == expected_slots,
                                "exact successive LIFO owners")
            independent.require(len({id(w.cells) for w in result}) == count,
                                "new outputs physically distinct")
            independent.require(all(w is not left and w is not right for w in result),
                                "outputs cannot alias equal-valued or aliased inputs")
            independent.require(before == [w.cells for w in arena.words],
                                "reservation does not write numerical bodies")
            independent.require(all(w.head == 1 for w in arena.words), "reservation input heads")
            domains.append({"initial_free": m, "outputs": count,
                            "returned_slots": expected_slots, "instructions": used})
            total_steps += used
            total_calls += machine.calls
    arena, owner, machine = create(code, metadata)
    selected = binding.arithmetic_binding(ParentBinding, owner)()
    old = deepcopy(owner.ports[65].cells)
    try:
        selected.reserve(arena, arena.words[0], arena.words[0])
    except ValueError as exc:
        independent.require(str(exc) == "division requires distinct inputs", "division alias rejection")
    else:
        raise ValueError("aliased division inputs accepted")
    independent.require(owner.ports[65].cells == old, "alias rejection leaves ordered stack")
    word = arena.zero()
    arena.free(word)
    old = deepcopy(owner.ports[65].cells)
    try:
        selected.reserve_simple(arena, word, arena.words[0], True)
    except ValueError as exc:
        independent.require(str(exc) == "bound live arithmetic input", "inactive input rejection")
    else:
        raise ValueError("inactive arithmetic input accepted")
    independent.require(owner.ports[65].cells == old, "inactive rejection leaves ordered stack")
    try:
        _ = arena.available
    except ValueError as exc:
        independent.require("host free-stack access" in str(exc), "host available inaccessible")
    else:
        raise ValueError("host free-stack remained available")
    for t in owner.ports[66:]:
        independent.require(t.head == 0 and set(t.cells) <= {"_"}, "queries retire selectors")
    return {
        "status": "PASS_INDEPENDENT_CRT_RESERVATION_ADAPTER",
        "domains": domains,
        "reservation_instructions": total_steps,
        "all_initialization_and_preparation_calls": total_calls,
        "controls": ["aliased_simple_inputs_accepted", "aliased_division_inputs_rejected",
                     "inactive_source_rejected", "host_available_inaccessible",
                     "old_parent_reservation_forbidden"],
        "scope": "Typed source adapter and lifecycle graph only. Full arithmetic union not executed."
    }


if __name__ == "__main__":
    result = run()
    independent.require(json.loads(json.dumps(result)) == json.loads((Path(__file__).with_name("RESERVATION-RESULT.json")).read_text()), "independent reservation receipt mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))

