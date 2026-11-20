"""Root cross-review using the separately published rational receiver.

Only the fixture generator and emitter are imported from the author.
The semantic checker uses independently written exact Fraction matrices.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def require(value, message):
    if not value:
        raise ValueError(message)


author = module("admission_fixture", HERE / "verify.py")
receiver_path = HERE / "inputs/rational-word.py"
require(hashlib.sha256(receiver_path.read_bytes()).hexdigest()
        == "0c40e3a83ab5ae5444098072b9577745bde85aa18b43bc52af906f4f0b0abab9",
        "receiver bytes differ from separately published implementation")
receiver = module("independent_rational_receiver", receiver_path)

raw = author.toy_source()
source_word, native = author.product.specialize(raw, {1: 1, 2: 1}, 1)
emitter = author.Emitter(4, source_word.root_width(4))
emitter.native = lambda owners, columns: native(emitter, owners, columns)
author.schedule.expand(source_word, 4, list(range(emitter.productive)), emitter)
emitted = emitter.finish()
word = receiver.Word(emitted["dimension"], emitted["productive"],
                     emitted["owned"], tuple(emitted["ops"]))
require((word.dimension, word.productive, word.owned, len(word.ops))
        == (4, 2, 28, 1654), "unexpected unchanged source fixture")
require(sum(op[0] == "paid" for op in word.ops) == emitted["paid"] == 18,
        "paid position census changed")
require(word.valid_syntax(), "actual receiver syntax rejects translation")
require(word.all_columns(), "independent receiver rejects complete endpoint")
require(receiver.parse(receiver.encode(word)) == word,
        "actual receiver finite unary serialization failed")
require(not word.funded(), "toy fixture must not be labelled funded")

# Two small exact controls use the receiver alone, not the author's oracle.
direct = tuple(("paid", owner, axis) for owner in range(2) for axis in range(2))
require(receiver.Word(2, 2, 1, direct).all_columns(), "control baseline")
require(not receiver.Word(2, 2, 1, direct + (("add", 2, 0),)).all_columns(),
        "dirty private exit escaped actual receiver")
require(not receiver.Word(2, 2, 1, direct + (("i", 0), ("unit", 0),
                                            ("neg", 0))).all_columns(),
        "columnwise phase confused with exterior i: f=1 agrees, f=2 differs")

result = {"status": "PASS_INDEPENDENT_PUBLISHED_RECEIVER",
          "dimension": 4, "productive": 2, "owned": 28,
          "instructions": 1654, "paid": 18,
          "complete_all_column_endpoint": True,
          "canonical_serialization_round_trip": True,
          "toy_fixture_is_funded": False,
          "negative_controls": ["dirty_private_exit", "scalar_column_phase"],
          "source": "CubeJerry/integer-mult-bounds@88dd72b4864665362230c56538d2bd2579c6beca",
          "scope": "Independent exact receiver check of a finite compiler fixture; no physical or selected-word execution."}
expected = HERE / "review/RECEIVER-RESULT.json"
if "--record" not in sys.argv:
    require(result == json.loads(expected.read_text()), "cross-review receipt differs")
print(json.dumps(result, indent=2, sort_keys=True))
