"""Generate complemented P104 native recipes into a new file only."""
from functools import lru_cache
from pathlib import Path
import argparse
import gzip
import json

import verify as check


def compile_edges(word, compiler):
    @lru_cache(maxsize=2048)
    def chart(frame):
        return compiler.canonical_frame(9, frame)
    result = []
    edges = check.native_edges(word)
    for index, ((old, new), events) in enumerate(sorted(edges.items())):
        operator = chart(old).adjoint().then(chart(new))
        recipe, _ = compiler.lower_child(operator)
        check.need(recipe["rank"] == abs(len(old) - len(new)), "compiled positive rank")
        result.append({"old": list(old), "new": list(new), "events": events, "recipe": recipe})
        if index % 50 == 0:
            print("COMPILED", index + 1, len(edges), flush=True)
    return result


def compile_endpoints(word, labels, compiler):
    result = []
    for index, normal in enumerate(labels):
        reg = "Y" + str(index)
        frame = tuple(word["initial_frames"][reg])
        operator = compiler.cgate(9, normal).adjoint().then(compiler.canonical_frame(9, frame))
        recipe, _ = compiler.lower_child(operator)
        check.need(recipe["rank"] == 0, "entry is monomial")
        result.append({"position": "entry", "register": reg, "frame": list(frame),
                       "normal": normal, "recipe": recipe})
        reg = "X" + str(index)
        frame = tuple(word["final_frames"][reg])
        operator = compiler.canonical_frame(9, frame).adjoint().then(
            compiler.cgate(9, normal, -1)).then(compiler.fourier(9))
        recipe, _ = compiler.lower_child(operator)
        check.need(recipe["rank"] == 0, "exit is monomial")
        result.append({"position": "exit", "register": reg, "frame": list(frame),
                       "normal": normal, "recipe": recipe})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    check.need(not args.out.exists(), "output already exists")
    source = check.authenticate()
    interpreter = check.load_module(check.NATIVE / "vendor/native_verify.py", "build_native_oracle")
    compiler = check.load_module(check.NATIVE / "vendor/clifford_exact.py", "complement_clifford_compiler")
    convert, ports, labels = check.geometry(interpreter)
    word = check.lift(source, convert)
    check.replay(word, ports)
    packet = {"schema_version": 1, "word_sha256": check.digest(check.canonical_json(word)),
              "transports": compile_edges(word, compiler),
              "endpoint_adapters": compile_endpoints(word, labels, compiler)}
    check.native_check(word, packet, interpreter, labels)
    payload = gzip.compress(check.canonical_json(packet), mtime=0)
    with args.out.open("xb") as stream:
        check.need(stream.write(payload) == len(payload), "complete native payload write")
    print("PASS_BUILD_P104_COMPLEMENTARY_DUAL", len(packet["transports"]), flush=True)


if __name__ == "__main__":
    main()
