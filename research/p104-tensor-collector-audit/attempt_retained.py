"""Optional extended PR3131 comparison; neither attempted plan finished in 600s.

Only the finite Executor n<=10 guard becomes n<=18. No arithmetic, control
plan, macro implementation or scalar oracle is changed. The archived fast
algorithm's *direct semantic* oracle remains a direct semantic oracle.
"""
import argparse
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v


def load_model(raw):
    prefix = "research/dense-paired-collector/"
    sources = types.ModuleType("sources")
    sources.__file__ = str(v.ROOT / (prefix + "sources.py"))
    exec(compile(raw[prefix + "sources.py"], sources.__file__, "exec", optimize=0), sources.__dict__)
    original = raw[prefix + "model.py"].decode()
    before, after = "1 <= n <= 10 and width >= 8", "1 <= n <= 18 and width >= 8"
    v.need(original.count(before) == 1 and after not in original, "one exact finite guard adapter")
    adapted = original.replace(before, after)
    v.need(adapted.replace(after, before) == original, "only the finite extent guard changes")
    module = types.ModuleType("retained_dense_model")
    module.__file__ = str(v.ROOT / (prefix + "model.py"))
    previous = sys.modules.get("sources")
    sys.modules["sources"] = sources
    try:
        exec(compile(adapted, module.__file__, "exec", optimize=0), module.__dict__)
    finally:
        if previous is None:
            del sys.modules["sources"]
        else:
            sys.modules["sources"] = previous
    return module


def run(plan):
    raw, word, native = v.source_inputs()
    recipe = v.bind(word, native)[0]
    model = load_model(raw)
    sources, query, f, beta = v.fixture(2, "promoted")
    original_sources, original_query = [v.digest(x) for x in sources], v.digest(query)
    # One finite plan derived from the inherited p=160 exponents, with exact
    # integer inequalities. The asymptotic outer height exceeds the rank 14.
    width = 160
    d = next(k for k in range(width, 0, -1) if k**1000 <= width**997)
    spacing = 1
    v.need(spacing**500 <= d < (spacing+1)**500, "exact spacing floor")
    suffix = (width+d-1)//d
    v.need(14**10 < width**9, "outer cap fits p^(5991997/6000000)")
    parameters = dict(width=width, d=d, spacing=spacing, suffix=suffix, outer=14)
    if plan == "defaults":
        parameters = dict(width=160, d=2, spacing=2, suffix=1, outer=3)
    engine = model.Executor(18, **parameters)
    result = model.collector(engine, sources, query, f, beta, recipe, multiplicity=2)
    # Compare full arrays against the separately written column/parity evaluator.
    F, total, fine, sent, updated = v.oracle.collector_query(sources, query, f, beta, recipe, 2)
    for name, expected in (("entrance", total), ("sent", sent), ("query", updated), ("returned", fine)):
        v.need(result[name] == expected, "retained nested evaluator: " + name)
    v.need(result["grid"] == F == 5, "retained promoted grid")
    v.need(all(z == (0, 0) for z in result["private"]), "retained private zero")
    v.need([v.digest(x) for x in sources] == original_sources and v.digest(query) == original_query,
           "retained source/query entrances unchanged")
    v.need(engine.counts["address_gates"] == 52 and engine.counts["address_oracles"] == 104,
           "actual four-wrapper gate invoice")
    return dict(schema_version=1, multiplicity=2, components=1 << 18, rank=14,
                fixture="promoted", input_grid=f, beta=beta, output_grid=F,
                finite_guard_adapter=dict(original_max_n=10, adapted_max_n=18,
                                          arithmetic_and_control_plan_unchanged=True),
                executor_parameters=parameters,
                source_sha256=original_sources, entrance_query_sha256=original_query,
                sent_sha256=v.digest(sent), query_sha256=v.digest(updated),
                returned_sha256=v.digest(result["returned"]), private_zero=True,
                counts=engine.counts,
                scope="retained nested evaluator with frozen direct semantic backend; no fast physical trace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", choices=("derived", "defaults"), default="derived")
    args = parser.parse_args()
    result = run(args.plan)
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_P104_RETAINED_TENSOR_COLLECTOR n=18 components=262144 no_new_kappa", file=sys.stderr)


if __name__ == "__main__":
    main()
