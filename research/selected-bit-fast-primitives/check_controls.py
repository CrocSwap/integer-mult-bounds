"""Reject changed source bindings and wrong finite route specializations."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources


def rejected(action, message):
    try:
        action()
    except ValueError as error:
        if message not in str(error):
            raise ValueError("wrong rejection boundary: " + str(error)) from error
    else:
        raise ValueError("invalid source or route accepted: " + message)


def run():
    with patch.dict(sys.modules, {"route_catalog": object()}):
        rejected(stage_sources.activate, "cold shared stage namespace")
    with patch.dict(stage_sources.ARCHIVES, {"pr2899": "0"*64}):
        rejected(stage_sources.activate, "immutable source archive")
    source, retained, _data = stage_sources.activate()
    here, root = stage_sources.HERE, stage_sources.ROOT
    manifest = json.loads((here / "SOURCES.json").read_text())
    declared = json.loads((here / "VERIFY.json").read_text())["inputs"]
    inputs = {row["path"]: row for row in manifest["files"] if row["usage"] == "input"}
    if set(inputs) != set(declared):
        raise ValueError("complete declared input inventory")
    for path, row in inputs.items():
        if sha256((root / path).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed live input: " + path)
    for row in manifest["archives"]:
        if sha256((here / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed archived input")
    from compile_routes import Registry, matrix_key
    from routes import Route
    identity = ((F(1),F(0)),(F(0),F(1)))
    swap = ((F(0),F(1)),(F(1),F(0)))
    registry = Registry(2)
    rejected(lambda: registry.register(identity, (("swap",0,1,F(1)),)), "exact factor word endpoint")
    word = (("add",0,1,F(3)),)
    rejected(lambda: registry.register(retained.replay(word,2), word), "dyadic coefficient alphabet")
    rejected(lambda: registry.compile(Route(3,2,identity,swap,swap)), "authenticated factor word")
    rejected(lambda: registry.compile(Route(3,3,identity,identity,identity)), "route dimension binding")
    rejected(lambda: registry.compile(Route(3,2,identity,swap,identity)), "complete target low class")
    # A lost carry would map this 1/2 shear to the wrong complete low class.
    word = (("add",0,1,F(1,2)),)
    chart = matrix_key(retained.replay(word,2))
    registry.register(chart, word)
    low, target = ((0,1),(2,2)), ((2,1),(0,2))
    program = registry.compile(Route(3,2,low,target,chart))
    if ("translate",0,-1) not in program or ("translate",2,2) not in program:
        raise ValueError("both signed low carries retained")
    rejected(lambda: registry.compile(Route(3,2,low,low,chart)), "complete target low class")
    return dict(rejections=8, input_paths=len(inputs), signed_carries=[-1,2],
                source_namespace=Path(source.__file__).name)


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
    print("PASS_FAST_PRIMITIVE_CONTROLS")
