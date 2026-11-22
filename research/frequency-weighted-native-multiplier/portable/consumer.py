"""Bind the emitted fields to the compiled ordinary and Gaussian receivers."""

import ast
import sys
from pathlib import Path

BINDINGS = {
    "strong_binary": {
        "graph": "return data()[2]",
        "caller": "return data()[3]",
        "fixed_binary_charts": "return data()[4]",
    },
    "grades": {
        "numerical_source": "return data()[5]",
        "numerical_recipe": "return next(t[-1] for t in data()[0] if t[-1].rank_log == rank_log)",
    },
    "raw_binary_stage": {
        "binary_word": "return data()[1]",
        "binary_recipe": "return next(r for t in data()[0] for r in t[:-1] if r.rank_log == height)",
    },
}


def install_bindings(dest):
    for name in ("tape_directory.py", "compiler_state.py", "fixed_directory.py"):
        (dest / name).write_bytes(Path(__file__).with_name(name).read_bytes())
    for name, definitions in BINDINGS.items():
        path = dest / (name + ".py")
        source = path.read_text()
        rows = source.splitlines(keepends=True)
        bodies = {
            node.name: node
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef)
        }
        for key in sorted(definitions, key=lambda k: bodies[k].lineno, reverse=True):
            node = bodies[key]
            rows[node.lineno : node.end_lineno] = ["    " + definitions[key] + "\n"]
        path.write_text("from fixed_directory import data\n" + "".join(rows))


def run():
    install_bindings(Path("/machine"))
    sys.path.insert(0, "/machine")
    from upstream import install

    install()
    from binary_receiver import Receiver
    from fixed_directory import data
    from grades import numerical_recipe, numerical_source
    from installations import PROFILES
    from raw_binary_stage import binary_recipe, binary_word
    from retimed_supplier import Positive
    from strong_binary import caller, fixed_binary_charts, graph

    compiled = data()
    assert (
        graph() is compiled[2]
        and caller() is compiled[3]
        and fixed_binary_charts() is compiled[4]
    )
    assert binary_word() is compiled[1] and numerical_source() is compiled[5]
    assert Receiver.__init__.__globals__["binary_recipe"] is binary_recipe
    for profile, layer in zip(PROFILES.values(), compiled[0], strict=True):
        for h, recipe in zip(profile.rank_logs, layer[:-1], strict=True):
            assert binary_recipe(h) is recipe
        positive = Positive(profile.complex_log, profile.positive_stop_denominator)
        assert positive.physical is compiled[5][0] and positive.recipe is layer[-1]
        assert numerical_recipe(profile.complex_log) is layer[-1]
        assert [v.multiplicity for v in positive.recipe.types()] == [1, 90]
        assert len(positive.recipe.typed_cells()) == 88
    print(
        "seven received getters, two physical suppliers, 88 typed cells per profile",
        flush=True,
    )
