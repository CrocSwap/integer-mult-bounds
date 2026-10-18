"""Opt-in native compilation benchmark. Every build is linked and executed afresh.

Uses ccache's existing preprocessor mode, not a new cache algorithm.
Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import HUB, ROOT, canonical, fixtures, need, normalize, read, replay, sha, source_pins


def clean_environment():
    # Never inherit a user's relaxed cache policy, remote storage or cache directory.
    env = {k: v for k, v in os.environ.items() if not k.startswith("CCACHE_")}
    env.update(LC_ALL="C", LANG="C")
    return env


def toolchain_profile(cxx, env):
    """Fresh content digests, including compiler subprocesses and their libraries."""
    def query(*args):
        return subprocess.check_output([str(cxx), *args], env=env, text=True).strip()

    tools = {"driver": cxx.resolve()}
    for name in ("cc1plus", "as", "collect2", "ld"):
        value = query("-print-prog-name=" + name)
        resolved = Path(value) if Path(value).is_absolute() else Path(shutil.which(value, path=env.get("PATH")) or value)
        need(resolved.is_file(), "GCC tool missing: " + name)
        tools[name] = resolved.resolve()
    files = set(tools.values())
    for path in tools.values():
        result = subprocess.run(["ldd", str(path)], env=env, capture_output=True, text=True, timeout=15)
        need(result.returncode == 0, "supported dynamically linked Linux GCC toolchain required")
        for item in re.findall(r"/[^\s()]+", result.stdout):
            library = Path(item)
            if library.is_file():
                files.add(library.resolve())
    return {"version": query("--version"), "target": query("-dumpmachine"),
            "specs_sha256": sha(query("-dumpspecs").encode()),
            "environment_sha256": sha(canonical(env).encode()),
            "system": platform.system(), "machine": platform.machine(),
            "tools": {key: str(value) for key, value in tools.items()},
            "content_sha256": {str(path): sha(path.read_bytes()) for path in sorted(files)}}


def cache_environment(work, env):
    config = work / "ccache.conf"
    config.write_text("compiler_check = content\ndirect_mode = false\ndepend_mode = false\n"
                      "sloppiness =\nremote_storage =\nhard_link = false\n"
                      "hash_dir = true\nstats = true\nmax_size = 200M\n")
    return dict(env, CCACHE_CONFIGPATH=str(config), CCACHE_DIR=str(work / "cache"),
                CCACHE_EXTRAFILES=str(work / "toolchain.json"))


def stats(ccache, env):
    raw = subprocess.check_output([str(ccache), "--print-stats"], env=env, text=True)
    return {row.split()[0]: int(row.split()[1]) for row in raw.splitlines()}


def delta(before, after):
    return {key: after.get(key, 0) - before.get(key, 0) for key in set(before) | set(after)
            if after.get(key, 0) != before.get(key, 0)}


def run_benchmark(args):
    work = args.work.resolve()
    need(not work.exists() and not work.is_relative_to(ROOT), "fresh external work directory required")
    need(sys.byteorder == "little", "native RAW6 fixture requires little-endian host")
    need(args.repeats >= 2, "at least two paired timing samples required")
    independent = replay()
    work.mkdir(parents=True)
    raw = fixtures()
    expected = read(HERE / "NATIVE.json")
    source = work / "source"
    source.mkdir()
    for name in ("columns_k.cpp", "json.hpp"):
        shutil.copyfile(ROOT / HUB / "code/bit/checkers" / name, source / name)
    # A two-level include gives a real transitive-header invalidation control.
    (source / "fixture_config.hpp").write_text('#include "copy_count.hpp"\n')
    (source / "copy_count.hpp").write_text("#define NCOPY 9\n")
    for label, data in raw.items():
        (work / (label + ".bin")).write_bytes(data)
    cxx, ccache = args.cxx.resolve(), args.ccache.resolve()
    need(cxx.is_file() and ccache.is_file(), "compiler and ccache executables required")
    env = clean_environment()
    cenv = cache_environment(work, env)
    version = subprocess.check_output([str(ccache), "--version"], env=env, text=True).splitlines()[0]
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(args.boost_include.resolve()), "-include", str(source / "fixture_config.hpp")]
    builds, executions, profiles = [], [], {}

    def execute(command, folder, name, *, command_env=env):
        t = time.perf_counter()
        result = subprocess.run([str(x) for x in command], cwd=source, env=command_env,
                                capture_output=True, timeout=120)
        seconds = time.perf_counter() - t
        (folder / (name + ".stdout")).write_bytes(result.stdout)
        (folder / (name + ".stderr")).write_bytes(result.stderr)
        return result, seconds

    def build(name, cached, *, pairs=4, profile_salt=None):
        t = time.perf_counter()
        # Input hashing and profile collection remain inside every measured build.
        source_pins()
        fixtures()
        profile = toolchain_profile(cxx, env)
        if profile_salt is not None:
            profile["invalidation_control"] = profile_salt
        profile_raw = (canonical(profile) + "\n").encode()
        (work / "toolchain.json").write_bytes(profile_raw)
        key = sha(profile_raw)
        profiles[key] = profile
        before = stats(ccache, cenv)
        folder = work / name
        folder.mkdir()
        object_file, binary = folder / "columns.o", folder / "columns"
        compile_cmd = ([str(ccache)] if cached else []) + [str(cxx), *flags,
            "-DKPAIRS=" + str(pairs), "-c", str(source / "columns_k.cpp"), "-o", str(object_file)]
        r, compile_seconds = execute(compile_cmd, folder, "compile", command_env=cenv if cached else env)
        need(r.returncode == 0, "compile failed: " + name)
        # The linker always executes; no executable or proof receipt is cached here.
        link_cmd = [str(cxx), str(object_file), "-o", str(binary)]
        r, link_seconds = execute(link_cmd, folder, "link")
        need(r.returncode == 0, "link failed: " + name)
        changes = delta(before, stats(ccache, cenv))
        build_seconds = time.perf_counter() - t
        record = {"name": name, "cached": cached, "pairs": pairs, "profile_sha256": key,
                  "build_seconds": build_seconds, "compile_seconds": compile_seconds,
                  "link_seconds": link_seconds, "stats_delta": changes,
                  "object_sha256": sha(object_file.read_bytes()), "binary_sha256": sha(binary.read_bytes()),
                  "source_sha256": sha((source / "columns_k.cpp").read_bytes()),
                  "commands": [compile_cmd, link_cmd]}
        builds.append(record)
        print("build", name, round(build_seconds, 4), changes, flush=True)
        return binary, record

    def hit(record):
        need(record["stats_delta"].get("preprocessed_cache_hit") == 1 and
             record["stats_delta"].get("cache_miss", 0) == 0 and
             record["stats_delta"].get("direct_cache_hit", 0) == 0, "expected preprocessor cache hit")

    def miss(record):
        need(record["stats_delta"].get("cache_miss") == 1 and
             record["stats_delta"].get("preprocessed_cache_hit", 0) == 0, "expected cache invalidation")

    def native(binary, name, label, *, error=None, pairs=4):
        folder = binary.parent
        data = work / (label + ".bin")
        receipt_path = folder / (name + ".json")
        command = [binary, data, receipt_path]
        r, seconds = execute(command, folder, name)
        record = {"build": folder.name, "name": name, "label": label, "seconds": seconds,
                  "exit_code": r.returncode, "input_sha256": sha(data.read_bytes()),
                  "stdout_sha256": sha(r.stdout), "stderr_sha256": sha(r.stderr),
                  "command": list(map(str, command))}
        if error is None:
            need(r.returncode == 0 and receipt_path.is_file(), "native execution failed: " + name)
            receipt = normalize(read(receipt_path), data, data.read_bytes())
            need(canonical(json.loads(r.stdout, object_pairs_hook=None)) == canonical(read(receipt_path)),
                 "native stdout and receipt differ")
            stages = 2 * pairs + 1
            lines = r.stderr.decode().splitlines()
            need(len(lines) == stages and all(re.fullmatch(r"stage " + str(i) + r" PASS elapsed [0-9.e+-]+s", line)
                                            for i, line in enumerate(lines)), "native stage execution log")
            if pairs == 4:
                need(canonical(receipt) == canonical(expected[label]), "complete native receipt differs")
            else:
                need(receipt["formal_columns_checked"] == 2 * pairs * 111 + 439 and
                     len(receipt["stages"]) == stages and len(receipt["negative_controls"]) == 6 * (pairs - 1),
                     "changed flag coverage")
            record["receipt_sha256"] = sha(canonical(receipt).encode())
        else:
            need(r.returncode == 2 and not receipt_path.exists() and error in r.stderr.decode(),
                 "invalid mathematical rejection control: " + name)
            record["expected_failure"] = error
        executions.append(record)
        return seconds

    def both(binary):
        return sum(native(binary, label, label) for label in ("baseline", "deferred"))

    timings = {"uncached": [], "warm": []}
    fill_start = time.perf_counter()
    binary, fill = build("fill", True)
    miss(fill)
    fill["native_seconds"] = both(binary)
    fill["total_replay_seconds"] = time.perf_counter() - fill_start
    result_files = list((work / "cache").rglob("*R"))
    need(len(result_files) == 1, "one cache result after initial fill")
    base_result = result_files[0]
    # Interleave timing modes to avoid attributing a one-way warmup trend to caching.
    for i in range(args.repeats):
        for mode in (("uncached", "warm") if i % 2 == 0 else ("warm", "uncached")):
            start = time.perf_counter()
            binary, record = build(mode + "-" + str(i), mode == "warm")
            if mode == "warm":
                hit(record)
            need(record["object_sha256"] == fill["object_sha256"], "reference/cached object differs")
            record["native_seconds"] = both(binary)
            record["total_replay_seconds"] = time.perf_counter() - start
            timings[mode].append(record["total_replay_seconds"])

    # Every invalidation uses the actual C++ compiler, cache and executable.
    header = source / "copy_count.hpp"
    old, stat = header.read_bytes(), header.stat()
    header.write_bytes(old.replace(b"NCOPY 9", b"NCOPY 8"))
    os.utime(header, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    binary, record = build("changed-transitive-header", True)
    miss(record)
    native(binary, "wrong-copy-count", "deferred", error="center boundaries")
    header.write_bytes(old)
    os.utime(header, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    cpp = source / "columns_k.cpp"
    old, stat = cpp.read_bytes(), cpp.stat()
    need(old.count(b"if(q.c&1)xo") == 1, "source mutation site")
    cpp.write_bytes(old.replace(b"if(q.c&1)xo", b"if(q.c&0)xo"))
    os.utime(cpp, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    binary, record = build("changed-source", True)
    miss(record)
    native(binary, "wrong-parity", "deferred", error="local defining-decoder full formal column")
    cpp.write_bytes(old)
    os.utime(cpp, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    binary, record = build("changed-flags", True, pairs=5)
    miss(record)
    native(binary, "eleven-stages", "deferred", pairs=5)
    binary, record = build("changed-profile", True, profile_salt="simulated-toolchain-content-change")
    miss(record)
    both(binary)
    binary, record = build("restored-inputs", True)
    hit(record)
    both(binary)
    native(binary, "missing-undo", "missing-undo", error="local defining-decoder full formal column")
    # Corrupt only this experiment's private cached compiler result.
    broken = bytearray(base_result.read_bytes())
    broken[len(broken) // 2] ^= 1
    base_result.write_bytes(broken)
    binary, record = build("damaged-cache", True)
    miss(record)
    both(binary)
    medians = {key: statistics.median(value) for key, value in timings.items()}
    result = {"status": "PASS_NATIVE_CCACHE_COLUMNS", "native_executed": True,
              "ccache_version": version, "ccache_sha256": sha(ccache.read_bytes()),
              "python": sys.version, "profiles": profiles,
              "input_replay": independent, "builds": builds, "executions": executions,
              "timings_seconds": timings, "median_seconds": medians,
              "warm_speedup": medians["uncached"] / medians["warm"],
              "fill_seconds": fill["total_replay_seconds"],
              "controls": ["same-size same-mtime transitive header", "same-size same-mtime source",
                           "changed compile flag", "changed toolchain profile", "restored-input cache hit",
                           "invalid word after cache hit", "corrupt private cache result"],
              "scope": "One native column checker and two pinned words; fresh link and execution every time. No full selected replay or new mathematical result."}
    (work / "BENCHMARK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], "warm_speedup=" + str(result["warm_speedup"]), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--cxx", type=Path, required=True)
    parser.add_argument("--ccache", type=Path, required=True)
    parser.add_argument("--boost-include", type=Path, default=Path("/usr/include"))
    parser.add_argument("--repeats", type=int, default=3)
    run_benchmark(parser.parse_args())


if __name__ == "__main__":
    main()
