#!/usr/bin/env python3
"""Check acceptance and rejection paths without changing saved sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    package, build = args.package.resolve(), args.build.resolve()
    require(not build.exists(), "The build path must not exist.")
    build.mkdir(parents=True)
    compiler = shutil.which("clang++") or shutil.which("g++")
    require(compiler, "A C++17 compiler is required.")
    rows = []
    for engine in ["integer", "field"]:
        source = package / "sources/four-register/independent/clean-zero" / (engine + ".cpp")
        class_name = "Solver" if engine == "integer" else "Search"
        state_name = "Rows" if engine == "integer" else "Basis"
        off_name = "offrows" if engine == "integer" else "off"
        terminal_name = "terminal" if engine == "integer" else "terminals"
        setup = "" if engine == "integer" else "setup();"
        code = f'''#define main saved_engine_main
#include {json.dumps(str(source))}
#undef main
int main() {{
    {setup}
    for (int test = 0; test < 5; ++test) {{
        {class_name} solver;
        int target = test == 1 ? 3 : 7;
        solver.terms = {{{{target, 1 | 32 | 1024}}, {{0, 32768}}}};
        if (test == 2) {{
            solver.terms.push_back({{64, 2}});
            solver.terms.push_back({{128, 2}});
            solver.{off_name}.push_back(192);
        }}
        if (test == 3) {{
            solver.terms.push_back({{0, 2}});
            solver.terms.push_back({{64, 2}});
            solver.{off_name}.push_back(64);
        }}
        if (test == 4) {{
            solver.terms.push_back({{1, 2}});
            solver.terms.push_back({{2, 2}});
            solver.{off_name}.push_back(3);
        }}
        solver.go({state_name}{{}});
        std::cout << test << " " << solver.{terminal_name} << " " << solver.robust << "\\n";
    }}
}}
'''
        harness = build / (engine + "-controls.cpp")
        harness.write_text(code)
        binary = build / (engine + "-controls")
        compiled = subprocess.run([compiler, "-std=c++17", "-O2",
                                   "-fsanitize=undefined", "-fno-sanitize-recover=all",
                                   str(harness), "-o", str(binary)],
                                  text=True, capture_output=True, check=True)
        (build / (engine + "-compile.log")).write_text(compiled.stdout + compiled.stderr)
        result = subprocess.run([str(binary)], text=True, capture_output=True, check=True)
        (build / (engine + "-run.log")).write_text(result.stdout + result.stderr)
        expected = "0 1 1\n1 1 0\n2 1 1\n3 0 0\n4 1 0\n"
        require(result.stdout == expected, engine + " polynomial control results")
        rows.append({"engine": engine, "output": result.stdout,
                     "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})

    optimized = subprocess.run([sys.executable, "-O", "-B", str(package / "verify.py"),
                                "--build", str(build / "optimized-output")],
                               text=True, capture_output=True)
    require(optimized.returncode != 0 and "without -O" in optimized.stderr,
            "Optimized Python must be rejected")
    require(not (build / "optimized-output").exists(), "Optimized run wrote output")
    environment = dict(os.environ, PYTHONOPTIMIZE="2")
    isolated = subprocess.run([sys.executable, "-E", "-B", "-c",
                               "import sys; assert __debug__; print(sys.flags.optimize)"],
                              env=environment, text=True, capture_output=True, check=True)
    require(isolated.stdout == "0\n", "Child optimization environment leaked")
    copy = build / "tampered-package"
    shutil.copytree(package, copy)
    victim = copy / "sources/four-register/CLEAN-SPAN-FOUR.txt"
    victim.write_bytes(victim.read_bytes() + b"\n")
    tampered = subprocess.run([sys.executable, "-B", str(copy / "verify.py"),
                               "--build", str(build / "tampered-output")],
                              text=True, capture_output=True)
    require(tampered.returncode != 0 and "Source hash:" in tampered.stderr,
            "Source corruption must be rejected")
    require(not (build / "tampered-output").exists(), "Tampered run wrote output")
    result = {"status": "PASS_INDEPENDENT_CONTROLS", "polynomial_engines": rows,
              "fixture_scope": "Five polynomial fixtures; these are not paid-call circuit constructions.",
              "fixtures": ["accept monomial targets of support three",
                           "reject a target of support two",
                           "accept after a required collision",
                           "reject a collision that forces a zero paid frame",
                           "reject a target reduced to a two-frame span"],
              "optimized_python_rejected": True, "source_corruption_rejected": True,
              "child_optimization_environment_ignored": True}
    (build / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
