"""Rejection controls at the actual authentication and registry boundaries."""
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import bindings
import frames
from verify import check_equal


def reject(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def run():
    manifest = json.loads((bindings.HERE/"SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="frame-source-control-") as name:
        root = Path(name)
        for row in manifest["files"]:
            if row["usage"] != "input":
                continue
            path = root/row["path"]
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((bindings.ROOT/row["path"]).read_bytes())
        target = root/"research/selected-bit-fast-primitives/compile_routes.py"
        target.write_bytes(target.read_bytes()+b"\nraise RuntimeError('corrupted source executed')\n")
        reject(lambda: bindings.authenticate(root))
        proof_root = root/"proof-copy"
        (proof_root/"sources").mkdir(parents=True)
        proof = bindings.HERE/"sources/pr3301-PROOF.md"
        (proof_root/"sources/pr3301-PROOF.md").write_bytes(proof.read_bytes()+b"\nchanged tariff\n")
        reject(lambda: bindings.authenticate(package=proof_root))
    bindings.activate()
    import compile_routes
    original = (("add",0,1,F(1)),)*9
    matrix = compile_routes.retained.replay(original,2)
    registry_type = frames.scheduled_registry(compile_routes.Registry)
    registry = registry_type(2)
    bad = frames.defer(original,2)[:-1]
    with patch.object(frames,"schedule",lambda _word,_dimension:bad):
        reject(lambda: registry.register(matrix,original))
    registry = registry_type(2)
    bad = list(frames.defer(original,2))
    k,t,c,v = bad[1]
    bad[1] = k,c,t,v
    with patch.object(frames,"schedule",lambda _word,_dimension:tuple(bad)):
        reject(lambda: registry.register(matrix,original))
    registry = registry_type(2)
    registry.register(matrix,original)
    frames.need(min(frames.price(w) for m,w in registry.words.items() if m !=
                    compile_routes.matrix_key(compile_routes.retained.identity(2))) == 2,
                "valid optimized word passes the same endpoint gate")
    reject(lambda: check_equal({"native_calls":1},{"native_calls":True},"typed control"))
    reject(lambda: check_equal({"native_calls":8},{"native_calls":0},"omitted paid calls"))
    trap = (("add",0,3,F(1)),("add",0,1,F(1)),
            ("swap",0,1,F(1)),("add",0,2,F(1)))
    cheaper_calls = min((frames.defer(trap,64),frames.inverse(frames.defer(frames.inverse(trap),64))),
                        key=lambda w:(frames.price(w),len(w),repr(w)))
    frames.need((frames.price(trap),frames.price(cheaper_calls)) == (7,5) and
                (frames.paid_price(trap,64),frames.paid_price(cheaper_calls,64)) == (774958,874790),
                "fewer native calls can have a larger complete bound")
    frames.need(frames.schedule(trap,64) == trap, "reject unpriced frame setup")
    return dict(source_corruption=1, inherited_proof_corruption=1,
                actual_registry_endpoint_controls=2, paid_setup_guard=1,
                positive_registry=1, typed_and_paid_receipt_controls=2)
