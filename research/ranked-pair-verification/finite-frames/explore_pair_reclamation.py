#!/usr/bin/env python3
"""Reproduce the original or ranked PR62 words from immutable upstream source.

Graph: Avi Eisenberg, with Claude assistance. Joint compiler: eumemic, with
OpenAI Codex assistance. Descending-rank retired-slot priority: Chafik Boukhalfa,
with OpenAI Codex assistance. The only ranked compiler edit is the exact
manifest-pinned sort-key replacement; upstream files are never rewritten.

The result certifies finite algebra and bounded-minor CRT profiles, not the
all-size residual compiler, fixed-tape implementation or multiplication theorem.
"""
import argparse
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
from pinned_upstream import PACKAGE, PIN, generated_directory, require, validate_upstream


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--h", type=int, choices=(23, 25), required=True)
    parser.add_argument("--priority", choices=("original", "ranked"), default="ranked")
    args = parser.parse_args()
    root, manifest, source_hashes, ranked_source = validate_upstream(args.upstream)
    out = generated_directory(args.generated, root)
    experiments = root / "scripts/experiments"
    sys.path.insert(0, str(experiments))
    sys.path.insert(0, str(PACKAGE / "audit"))
    from scatter_binding_audit import verify_scatter

    compiler_path = experiments / "binary_frame_compiler.py"
    source = compiler_path.read_text() if args.priority == "original" else ranked_source
    namespace = {"__file__": str(compiler_path), "__name__": "pinned_ranked_pair_compiler"}
    exec(compile(source, str(compiler_path), "exec"), namespace)
    wrapper_path = root / "research/pair-assembly/frame/frame_compile.py"
    spec = importlib.util.spec_from_file_location("pinned_pair_frame_compile", wrapper_path)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    namespace["graph"] = wrapper.load_graph()
    compiled, word = namespace["compile_"](args.h, matching=True, reclaim=True, dirty=True)
    raw = (json.dumps(word, separators=(",", ":")) + "\n").encode()
    strict = verify_scatter(json.loads(raw))
    if args.priority == "original":
        expected = gzip.decompress((wrapper_path.parent / f"frame-word-{args.h}.json.gz").read_bytes())
        require(raw == expected, "Regenerated original word differs from PR62")
    else:
        require(sha256(raw).hexdigest() == manifest["words"][str(args.h)]["word_sha256"],
                "Regenerated ranked word differs from selected witness")
        bundled = PACKAGE / f"finite-frames/pair-ranked-word-{args.h}.json.gz"
        require(raw == gzip.decompress(bundled.read_bytes()), "Regenerated word differs from bundled bytes")

    # Empty gzip filename and zero mtime make even compressed output independent
    # of the generated-directory name. Decompressed bytes are the witness ID.
    word_path = out / f"{args.priority}-{args.h}.json.gz"
    with word_path.open("wb") as stream:
        with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as archive:
            archive.write(raw)
    from binary_frame_replay import replay
    from binary_frame_profile_prepare import prepare
    from binary_frame_math import exactness, js
    replayed = replay(word_path)
    binary_path = out / f"{args.priority}-{args.h}.bin"
    transitions = prepare(word_path, binary_path)
    profiler = out / f"profiler-{args.priority}-{args.h}"
    subprocess.run(["c++", "-O3", "-std=c++17", "-I",
                    str(root / "references/frame-compiler/pr48/scripts/partial_swap"),
                    str(experiments / "binary_frame_profiles.cpp"), "-o", str(profiler)], check=True)
    subprocess.run([str(profiler), str(binary_path)], check=True)
    profile = json.loads(Path(str(binary_path) + ".profiles.json").read_text())
    if args.priority == "ranked":
        selected = json.loads((PACKAGE / f"finite-frames/pair-ranked-{args.h}-receipt.json").read_text())
        require(profile == selected["profile"], "Regenerated profile differs from selected witness")
    result = dict(pin=PIN, priority=args.priority, h=args.h,
                  sort_key="sorted(retired)" if args.priority == "original" else manifest["compiler_transform"]["new"],
                  compiler_source_sha256=sha256(compiler_path.read_bytes()).hexdigest(),
                  experimental_compiler_sha256=sha256(source.encode()).hexdigest(),
                  source_files_sha256=source_hashes, graph_source_sha256=wrapper.GRAPH_SHA256,
                  word_sha256=sha256(raw).hexdigest(), compiled=compiled, replay=replayed,
                  transitions=transitions, profile=profile, exactness=exactness(args.h),
                  literal_scatter=strict,
                  scope="Finite word, dirty-state replay and bounded-minor CRT profiles only; all-size transfer is not formalized")
    (out / f"{args.priority}-{args.h}-receipt.json").write_text(json.dumps(js(result), indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(status="PASS", h=args.h, priority=args.priority,
                          roles=compiled["roles"], word_sha256=result["word_sha256"])))


if __name__ == "__main__":
    main()
