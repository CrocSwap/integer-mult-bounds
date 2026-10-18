"""Authenticate the credited lifting, compiler and actual native collector."""
import ast
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import tarfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE_SHA = "9c171aabb02e59e53b2e4f0ed2845409fa2987fcd90a349a8c492abca1059f4b"
PINS = {
    "research/p104-reversible-lifting/lifting.py":"9424ee08f22b717f6d58f7cc46f189c5549fa86778afcd0c0762ab2daf591160",
    "research/selected-complex-compact-adapters/monomial.py":"394f9a465ac9148af0c20844d375e4befbef17d92b2fcc840d83419480dd4740",
    "research/p104-rounded-collector/inputs/WORD.json":"cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    "research/p104-rounded-collector/inputs/NATIVE.json.gz":"ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
    "research/p104-consumer-budget-audit/README.md":"13694215d0c1a245b392f7155e8395b9c4bad9c5db3558833c784d9449616417",
}
_loaded = None


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    global _loaded
    if _loaded is not None:
        return _loaded
    raw = {}
    for name, digest in PINS.items():
        raw[name] = (ROOT/name).read_bytes()
        need(sha256(raw[name]).hexdigest() == digest, "exact dense collector input: "+name)
    archive = HERE/"inputs/pr3109.tar"
    need(sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA, "frozen PR3109 archive")
    with tarfile.open(archive, "r:") as contents:
        def member(name):
            matches = [entry for entry in contents.getmembers() if entry.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique regular predecessor member")
            return contents.extractfile(matches[0]).read()
        inherited = json.loads(member("SOURCES.json"))
        for row in inherited["files"]:
            if row["usage"] == "input":
                need(sha256((ROOT/row["path"]).read_bytes()).hexdigest() == row["sha256"],
                     "inherited exact C/lifting premise: "+row["path"])
        core = ModuleType("credited_batched_model")
        core.__file__ = str(archive)+"/model.py"
        sys.modules[core.__name__] = core
        exec(compile(member("model.py"), core.__file__, "exec", optimize=0), core.__dict__)
    old = {}
    exec(compile(raw["research/p104-reversible-lifting/lifting.py"], "credited_lifting.py", "exec", optimize=0), old)
    tree = ast.parse(raw["research/selected-complex-compact-adapters/monomial.py"])
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "binary_word"]
    need(len(definitions) == 1, "one credited binary compiler")
    compiler = dict(need=need)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "credited_binary_word.py", "exec", optimize=0), compiler)
    word = json.loads(raw["research/p104-rounded-collector/inputs/WORD.json"])
    native = json.loads(gzip.decompress(raw["research/p104-rounded-collector/inputs/NATIVE.json.gz"]))
    recipes = bind(word, native)
    _loaded = dict(core=core, old=old, binary_word=compiler["binary_word"], recipes=recipes,
                   inherited_inputs=[row["path"] for row in inherited["files"] if row["usage"] == "input"])
    return _loaded


def bind(word, native):
    """Bind the same fifteen-event cut as Tekalign's PR3025."""
    events = word["program"][2025:2040]
    frame = [256, 136, 64, 40, 16, 4, 2, 1]
    sources = ["D31", "D30", "D29", "D28", "D27"]
    expected = [["zero", "C", frame]]
    expected += [["add", "C", source, 1, frame] for source in sources]
    expected += [["transport", "C", frame, [364], 7], ["add", "Q7", "C", "1", [364]],
                 ["transport", "C", [364], frame, 7]]
    expected += [["add", "C", source, "-1", frame] for source in reversed(sources)]
    expected += [["erase", "C", frame]]
    need(events == expected, "actual first collector word")
    frames = dict(word["initial_frames"])
    for event in word["program"][:2025]:
        op, register = event[:2]
        if op == "transport":
            need(frames[register] == event[2], "actual prefix frame")
            frames[register] = event[3]
        elif op == "add":
            need(register != event[2] and frames[register] == frames[event[2]] == event[4], "actual prefix ADD chart")
        else:
            need(op == "sign" and frames[register] == event[3], "invertible actual prefix")
    need(all(frames[source] == frame for source in sources) and frames["Q7"] == [364], "actual collector entrance charts")
    recipes = []
    for index in (2031, 2033):
        records = [record for record in native["transports"] if index in record["events"]]
        need(len(records) == 1, "unique actual native occurrence")
        record = records[0]
        need(word["program"][index] == ["transport", "C", record["old"], record["new"], 7], "literal native occurrence")
        need(record["recipe"]["rank"] == 7, "actual rank-seven core")
        recipes.append(record["recipe"])
    return recipes
