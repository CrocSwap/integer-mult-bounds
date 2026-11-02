"""Build a source-bound conjugation adapter. Produced by Nick Petalas."""

from hashlib import sha256
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = "research/full-guard-header-census/headers.c"
DIGEST = "ab0b0c9f4b296ee4cac6d7b9d84713e16cc61ef0fb3e03eb88d3fbcc412ed4ee"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_bytes():
    raw = (HERE.parents[1] / SOURCE).read_bytes()
    authenticate(raw)
    return raw


def authenticate(raw):
    need(len(raw) <= 16384 and sha256(raw).hexdigest() == DIGEST,
         "retained engine source identity")


def adapted_source():
    source = source_bytes().decode("utf-8")
    start = source.index("static void mul(")
    stop = source.index("static int passes(", start)
    kernel = (HERE / "conjugate.h").read_text()
    need(len(kernel) <= 8192, "kernel capacity")
    source = source[:start] + kernel + "\n" + source[stop:]
    replacements = (
        ("passes(Mat g, Mat gi, Mat r, int rank)",
         "passes(Mat g, Mat gi, int r, int rank)"),
        ("Mat t, a;\n    mul(g, r, t); mul(t, gi, a);",
         "Mat a;\n    conjugated_request(g, gi, r, a);"),
        ("passes(g, gi, R[t], rk[t])", "passes(g, gi, t, rk[t])"),
    )
    for old, new in replacements:
        need(source.count(old) == 1, "unique fixed adapter site")
        source = source.replace(old, new, 1)
    return source


def build(work, compiler="cc"):
    need(work.is_dir(), "existing scratch build directory")
    baseline = work / "baseline.c"
    candidate = work / "candidate.c"
    baseline.write_bytes(source_bytes())
    candidate.write_text(adapted_source())
    binaries = []
    for name, source in (("baseline", baseline), ("candidate", candidate)):
        target = work / name
        command = [compiler, "-O2", "-std=c11", "-Wall", "-Wextra",
                   "-Werror", "-pedantic", str(source), "-o", str(target)]
        subprocess.run(command, check=True, capture_output=True, timeout=60)
        binaries.append(target)
    return binaries


def comparison_source(kernel):
    source = source_bytes().decode("utf-8")
    need(source.count("int main(int argc, char **argv)") == 1,
         "retained main declaration")
    source = source.replace("int main(int argc, char **argv)",
                            "int retained_main(int argc, char **argv)", 1)
    suffix = (HERE / "compare.c").read_text()
    need(len(kernel) <= 8192 and len(suffix) <= 8192, "comparison capacity")
    return source + "\n" + kernel + "\n" + suffix


def compile_text(work, name, source, compiler="cc"):
    path = work / (name + ".c")
    path.write_text(source)
    target = work / name
    command = [compiler, "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror",
               "-pedantic", str(path), "-o", str(target)]
    subprocess.run(command, check=True, capture_output=True, timeout=60)
    return target
