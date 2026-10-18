"""Compile native recipes into a new file; never used by ordinary replay."""
from functools import lru_cache
from pathlib import Path
import argparse
import gzip
import importlib.util

spec = importlib.util.spec_from_file_location("pooled_build_check", Path(__file__).with_name("verify.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def build():
    original, correction = check.authenticate()
    oracle = check.module(check.NATIVE / "vendor/native_verify.py", "pooled_build_oracle")
    compiler = check.module(check.NATIVE / "vendor/clifford_exact.py", "pooled_compiler")
    convert, ports, labels = check.geometry(oracle)
    word = check.assemble(original, correction, convert)
    check.replay(word, ports)
    @lru_cache(maxsize=2048)
    def chart(frame):
        return compiler.canonical_frame(9, frame)
    records = []
    edges = check.native_edges(word)
    for index, ((a, b), events) in enumerate(sorted(edges.items())):
        recipe, _ = compiler.lower_child(chart(a).adjoint().then(chart(b)))
        check.need(recipe["rank"] == abs(len(a)-len(b)), "compiled rank")
        records.append({"old": list(a), "new": list(b), "events": events, "recipe": recipe})
        if index % 100 == 0:
            print("COMPILED", index + 1, len(edges), flush=True)
    endpoints = []
    for i, normal in enumerate(labels):
        for position, reg in (("entry", "X"+str(i)), ("exit", "Y"+str(i))):
            frame = tuple(word["initial_frames" if position == "entry" else "final_frames"][reg])
            if position == "entry":
                operator = compiler.cgate(9, normal).adjoint().then(chart(frame))
            else:
                operator = chart(frame).adjoint().then(compiler.cgate(9, normal, -1)).then(compiler.fourier(9))
            recipe, _ = compiler.lower_child(operator)
            check.need(recipe["rank"] == 0, "compiled monomial endpoint")
            endpoints.append({"position": position, "register": reg, "normal": normal, "frame": list(frame), "recipe": recipe})
    packet = {"schema_version": 1, "word_sha256": check.digest(check.canonical(word)), "transports": records, "endpoint_adapters": endpoints}
    check.native_check(word, packet, oracle, labels)
    return packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    check.need(not args.out.exists(), "output already exists")
    packet = build()
    with args.out.open("xb") as stream:
        stream.write(gzip.compress(check.canonical(packet), mtime=0))
    print("PASS_BUILD_P104_POOLED_NATIVE", len(packet["transports"]))


if __name__ == "__main__":
    main()
