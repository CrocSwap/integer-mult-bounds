"""Independent literal witness for the halved-extension index phase."""
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parent
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
MODULES = ("words", "records", "matrices", "controller", "children")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def source():
    """Authenticate every consumed module before executing any module."""
    manifest = json.loads((ROOT / "INPUTS.json").read_text())
    entries = {item["path"]: item for item in manifest["files"]}
    data = {}
    for name in MODULES:
        path = "vendor/" + name + ".py"
        pin = entries[path]
        raw = (ROOT / path).read_bytes()
        require(pin["source_head"] == HEAD, "independent source head")
        require(pin["source_path"] == "research/selected-bit-node/" + path,
                "independent original source path")
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"],
                "independent source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == pin["git_blob"], "independent source Git blob")
        data[name] = raw
    require(not any(name in sys.modules for name in MODULES), "fresh source imports")
    for name in MODULES:
        module = ModuleType(name)
        module.__file__ = str(ROOT / "vendor" / (name + ".py"))
        sys.modules[name] = module
        exec(compile(data[name], module.__file__, "exec", dont_inherit=True),
             module.__dict__)
    return SimpleNamespace(**{name: sys.modules[name] for name in MODULES})


def half_extension(s, allowance):
    """The closed entry owns one coordinate; the parent owns six more indices."""
    residue = s.words.Arena(3, 32)
    index = s.words.Arena(10, 1 + allowance)
    modulus = residue.input(3)
    ring = s.words.Ring(modulus)
    coordinate = index.input(0)
    entry_indices = len(index.live)
    program = s.records.Program.fixture(index, residue, 256, 1, [])
    fields = s.records.Fields.fixture(index, residue, [(0, [[0] * 64 for _ in range(64)])])
    spec = SimpleNamespace(code=0, good=False, template=SimpleNamespace(q=3, rank=1))
    parent = s.controller.Callback(ring, index, program, fields, {0: spec}, 0,
                                   allow_fallback=True)
    request = SimpleNamespace(child_kind="unit", half=True, coordinate=coordinate,
                              field=0, reverse=False)
    require(len(index.live) == 7, "coordinate and six distinct parent indices")
    borrowed = bytes(coordinate.cells)
    original_zero, demands = s.words.Arena.zero, []

    def observed_zero(arena):
        if arena is index:
            demands.append(len(arena.live) + 1 - entry_indices)
        return original_zero(arena)

    failed, extended = False, None
    s.words.Arena.zero = observed_zero
    try:
        extended = s.children.extend(parent, request)
    except ValueError as error:
        require(str(error) == "fixed register inventory", "exact rejected guard")
        failed = True
    finally:
        s.words.Arena.zero = original_zero
    peak = max(demands)
    require(peak == 11, "halved extension demands eleven indices above closed entry")
    require(failed == (allowance == 10), "actual capacity separates ten from eleven")
    if extended is not None:
        extended.tape.clear()
        parent.close()
    else:
        parent.abort()  # extend alone has no exception-cleanup wrapper.
    require(index.live == {coordinate.slot}, "explicit witness cleanup")
    require(bytes(coordinate.cells) == borrowed and coordinate.head == 1,
            "borrowed coordinate preserved")
    index.free(coordinate)
    ring.close()
    residue.free(modulus)
    require(not index.live and not residue.live, "complete witness teardown")
    return {"allowance": allowance, "pending_demand": peak, "inventory_failure": failed}


def main():
    s = source()
    receipt = {"source_head": HEAD, "half_extension": [half_extension(s, n) for n in (10, 11)]}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
