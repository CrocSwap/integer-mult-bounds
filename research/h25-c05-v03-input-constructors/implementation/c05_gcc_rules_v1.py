"""Bounded, passive source derivation for one original GCC command shape.

This module neither imports archived code nor executes GCC, make, patch, shell
recipes, native targets or diagnostics. It derives a *conditional source model*.
An effective configuration is deliberately unavailable until its named frontier
is closed. Source identity is not a reproducible-build or installed-semantics
proof. All public results retain full_C05=False and execution_ready=False.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import shlex
from pathlib import Path
from typing import Mapping, Sequence


PINSET_SHA256 = "5564d0d2b47a5803c96b3767d838676e8f2427089e3b02cda1b1e62430a3c24d"
PINSET_NAME = "c05_gcc_rules_sourcepins_v1.json"
COMPILER = "/usr/bin/x86_64-linux-gnu-gcc-13"
COMPILER_SHA256 = "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26"
FIXED_OPTIONS = ("-nostartfiles", "-shared", "-fPIC", "-O3", "-std=c11",
                 "-Wall", "-Wextra", "-Werror", "-I/usr/include/python3.12")
NATIVE_ENVIRONMENT = {
    "PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0", "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8", "TZ": "UTC", "PYTHONDONTWRITEBYTECODE": "1",
}
BASE = "gcc-base-selected/"
PACKAGING = "gcc-13_13.3.0-6ubuntu2~24.04.1-selected/debian/"
PATCH_BASE = "gcc-debian-patch-inputs/debian/"
MAX_SOURCE_FILE = 4 * 1024 * 1024
MAX_SOURCE_TOTAL = 16 * 1024 * 1024
ORIGINAL_CAPS = {"rows": 512, "file_bytes": 64 * 1024 * 1024,
                 "capture_bytes": 256 * 1024 * 1024,
                 "depth": 24, "nodes": 65536, "string": 8192,
                 "aggregate_text": 524288, "sequence_or_mapping": 1024,
                 "raw_record_bytes": 1048576}


class UnsupportedConfiguration(ValueError):
    """The supplied configuration is outside the single supported source scope."""


class IncompleteConfiguration(UnsupportedConfiguration):
    def __init__(self, model: dict):
        self.model = model
        super().__init__("effective configuration unproved: " + ", ".join(
            item["id"] for item in model["frontier"]))


class UnknownMakeValue(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_manifest() -> dict:
    raw = Path(__file__).with_name(PINSET_NAME).read_bytes()
    if sha256(raw) != PINSET_SHA256:
        raise UnsupportedConfiguration("source pinset identity mismatch")
    data = json.loads(raw)
    if data["schema"] != "c05-gcc-rule-sourcepins-v1":
        raise UnsupportedConfiguration("unsupported source pinset schema")
    return data


def verify_source_bytes(corpus: Mapping[str, bytes]) -> None:
    expected = {item["path"]: item for item in pinned_manifest()["files"]}
    if set(corpus) != set(expected):
        raise UnsupportedConfiguration("source corpus must match exact pinned key set")
    total = 0
    for name, value in corpus.items():
        if type(value) is not bytes or len(value) > MAX_SOURCE_FILE:
            raise UnsupportedConfiguration("source type/size: " + name)
        total += len(value)
        if (total > MAX_SOURCE_TOTAL or len(value) != expected[name]["bytes"]
                or sha256(value) != expected[name]["sha256"]):
            raise UnsupportedConfiguration("source content identity/size: " + name)


def load_pinned_sources(source_artifacts: str | Path) -> dict[str, bytes]:
    """Read only the 162 explicitly pinned data files; no discovery or import."""
    root = Path(source_artifacts)
    corpus = {}
    for item in pinned_manifest()["files"]:
        path = root / item["path"]
        with path.open("rb") as stream:
            corpus[item["path"]] = stream.read(item["bytes"] + 1)
    verify_source_bytes(corpus)
    return corpus


def _text(corpus: Mapping[str, bytes], name: str) -> str:
    return corpus[name].decode("utf-8", "strict")


def source_ref(corpus: Mapping[str, bytes], name: str, needle: str) -> dict:
    text = _text(corpus, name)
    if needle not in text:
        raise UnsupportedConfiguration("missing source anchor: " + name + ": " + needle)
    index = text.index(needle)
    return {"path": name, "sha256": sha256(corpus[name]),
            "line": text[:index].count("\n") + 1, "anchor": needle}


def _split_arguments(text: str) -> list[str]:
    """Split commas outside nested $(...), without interpreting any recipe."""
    result, start, depth = [], 0, 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise UnsupportedConfiguration("unbalanced make expression")
        elif char == "," and depth == 0:
            result.append(text[start:index])
            start = index + 1
    if depth:
        raise UnsupportedConfiguration("unbalanced make expression")
    result.append(text[start:])
    return result


def expand_make_data(text: str, values: Mapping[str, str], depth: int = 0) -> str:
    """Tiny rejecting data evaluator: variables, filter, findstring, if only.

    Unknown variables stay unknown; $(shell ...) is never executed or treated as
    empty. This is not GNU make and does not claim to evaluate package recipes.
    """
    if depth > 24 or len(text) > 8192:
        raise UnsupportedConfiguration("make expression bound")
    output, index = [], 0
    while index < len(text):
        if text[index] != "$":
            output.append(text[index]); index += 1; continue
        if not text.startswith("$(", index):
            raise UnknownMakeValue("unsupported dollar expression: " + text[index:])
        end, level = index + 2, 1
        while end < len(text) and level:
            if text[end] == "(": level += 1
            elif text[end] == ")": level -= 1
            end += 1
        if level:
            raise UnsupportedConfiguration("unbalanced make expression")
        inner = text[index + 2:end - 1]
        head = re.match(r"([A-Za-z_][\w-]*)(?:\s+)(.*)\Z", inner, re.S)
        if not head:
            if inner not in values:
                raise UnknownMakeValue(inner)
            value = values[inner]
        else:
            function, arguments = head.groups()
            parts = _split_arguments(arguments)
            if function == "if":
                if len(parts) not in (2, 3):
                    raise UnsupportedConfiguration("make if arity")
                condition = expand_make_data(parts[0], values, depth + 1).strip()
                selected = parts[1] if condition else (parts[2] if len(parts) == 3 else "")
                value = expand_make_data(selected, values, depth + 1)
            elif function in ("findstring", "filter") and len(parts) == 2:
                left, right = (expand_make_data(p, values, depth + 1) for p in parts)
                if function == "findstring":
                    value = left if left in right else ""
                else:
                    patterns = left.split()
                    def matches(word: str, pattern: str) -> bool:
                        # GNU make filter permits one percent wildcard.
                        if pattern.count("%") > 1:
                            raise UnknownMakeValue("multiple filter percent wildcards")
                        return bool(re.fullmatch(re.escape(pattern).replace("%", ".*"), word))
                    value = " ".join(w for w in right.split()
                                     if any(matches(w, p) for p in patterns))
            else:
                raise UnknownMakeValue("unsupported make function: " + function)
        output.append(value); index = end
    return "".join(output)


def _condition(text: str, values: Mapping[str, str]) -> bool | None:
    match = re.fullmatch(r"(ifeq|ifneq)\s*\((.*)\)", text)
    if not match:
        raise UnsupportedConfiguration("unsupported conditional: " + text)
    arguments = _split_arguments(match[2])
    if len(arguments) != 2:
        raise UnsupportedConfiguration("conditional arity")
    try:
        # Make strips whitespace around parenthesized conditional operands.
        left, right = (expand_make_data(a.strip(), values) for a in arguments)
    except UnknownMakeValue:
        return None
    equal = left == right
    return equal if match[1] == "ifeq" else not equal


def _and(a: bool | None, b: bool | None) -> bool | None:
    return False if a is False or b is False else (True if a is True and b is True else None)


def _or(a: bool | None, b: bool | None) -> bool | None:
    return True if a is True or b is True else (False if a is False and b is False else None)


def _not(value: bool | None) -> bool | None:
    return None if value is None else not value


def _logical_lines(text: str):
    pending, start = "", 0
    for number, line in enumerate(text.splitlines(), 1):
        if not pending: start = number
        if line.rstrip().endswith("\\"):
            pending += line.rstrip()[:-1] + " "
        else:
            yield start, pending + line
            pending = ""
    if pending:
        raise UnsupportedConfiguration("unterminated make continuation")


def _annotated_lines(text: str, values: Mapping[str, str]):
    """Yield recipe/data lines with three-valued conditional provenance."""
    stack, active = [], True
    for number, raw in _logical_lines(text):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("ifeq", "ifneq")):
            result = _condition(line, values) if active is not False else False
            stack.append({"parent": active, "taken": result,
                          "expression": line, "result": result})
            active = _and(active, result)
        elif line == "else" or line.startswith("else if") or line.startswith("else #"):
            if not stack:
                raise UnsupportedConfiguration("unmatched else")
            frame = stack[-1]
            tail = line[4:].strip()
            test = _condition(tail, values) if tail.startswith("if") else True
            active = _and(frame["parent"], _and(_not(frame["taken"]), test))
            frame["taken"] = _or(frame["taken"], test)
            frame["expression"] = line
            frame["result"] = active
        elif line.startswith("endif"):
            if not stack:
                raise UnsupportedConfiguration("unmatched endif")
            active = stack.pop()["parent"]
        else:
            conditions = [{"expression": f["expression"], "value": f["result"]}
                          for f in stack]
            yield number, raw, active, conditions
    if stack:
        raise UnsupportedConfiguration("unterminated condition")


def select_patch_data(text: str, values: Mapping[str, str]) -> dict:
    """Read the declarative patch-selection prefix, stopping before recipes."""
    prefix = text.split("series_stamp =", 1)[0]
    definite = {"debian_patches": [], "hardening_patches": []}
    conditional, records = [], []
    for number, raw, active, conditions in _annotated_lines(prefix, values):
        match = re.fullmatch(r"\s*(debian_patches|hardening_patches)\s*(\+?=)\s*(.*)", raw)
        if not match or active is False:
            continue
        variable, operator, expression = match.groups()
        try:
            names = expand_make_data(expression.strip(), values).split()
        except UnknownMakeValue as error:
            conditional.append({"expression": expression, "reason": str(error),
                                "line": number, "conditions": conditions})
            continue
        if operator == "=" and active is not True:
            raise UnsupportedConfiguration("unresolved patch-list reset")
        if operator == "=": definite[variable] = []
        for name in names:
            if not re.fullmatch(r"[\w+.\-]+", name):
                raise UnsupportedConfiguration("unsupported patch name")
            record = {"patch": name + ".diff", "line": number,
                      "selected": active, "list": variable, "conditions": conditions}
            records.append(record)
            if active is True: definite[variable].append(name + ".diff")
            else: conditional.append(record)
    # rules.patch appends hardening only for non-trunk builds.
    if values.get("trunk_build") == "yes":
        hardening = []
    elif "trunk_build" in values:
        hardening = definite["hardening_patches"]
    else:
        raise UnsupportedConfiguration("unknown trunk build")
    return {"definitely_selected": definite["debian_patches"] + hardening,
            "conditional": conditional, "records": records,
            "executed_make": False}


def _patch_target(path: str) -> str:
    path = path.split("\t", 1)[0].split(" ", 1)[0]
    for prefix in ("a/", "b/"):
        if path.startswith(prefix): path = path[len(prefix):]
    if path.startswith("src/"): path = path[4:]
    return path


def patch_targets(patch: bytes) -> list[str]:
    return list(dict.fromkeys(_patch_target(line[4:])
                for line in patch.decode().splitlines() if line.startswith("+++ ")))


def project_patch(base: bytes, patch: bytes, target: str) -> tuple[bytes, list[dict]]:
    """Apply only exact textual hunks to an in-memory selected file.

    Unique exact context relocation is permitted and recorded. No fuzz,
    whitespace repair, patch process, source mutation or generated code runs.
    """
    lines = base.splitlines(keepends=True)
    patch_lines = patch.splitlines(keepends=True)
    index, current, displacement, receipt = 0, None, 0, []
    while index < len(patch_lines):
        raw = patch_lines[index]
        if current == target and raw.startswith(b"\\ No newline at end of file"):
            raise UnsupportedConfiguration("non-LF patch hunk unsupported")
        if raw.startswith(b"+++ "):
            current = _patch_target(raw[4:].decode().rstrip("\r\n"))
        match = re.match(rb"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", raw)
        if match is None or current != target:
            index += 1; continue
        old_start, old_count, new_start, new_count = (
            int(match[1]), int(match[2] or b"1"), int(match[3]), int(match[4] or b"1"))
        before, after = [], []
        index += 1
        while index < len(patch_lines) and (len(before) < old_count or len(after) < new_count):
            line = patch_lines[index]
            if line.startswith(b" "): before.append(line[1:]); after.append(line[1:])
            elif line.startswith(b"-"): before.append(line[1:])
            elif line.startswith(b"+"): after.append(line[1:])
            elif line.startswith(b"\\ No newline at end of file"):
                raise UnsupportedConfiguration("non-LF patch hunk unsupported")
            else: raise UnsupportedConfiguration("malformed hunk body")
            index += 1
        if len(before) != old_count or len(after) != new_count or not before:
            raise UnsupportedConfiguration("hunk count or insertion-only frontier")
        expected = old_start - 1 + displacement
        if lines[expected:expected + len(before)] == before:
            location = expected
        else:
            matches = [i for i in range(len(lines) - len(before) + 1)
                       if lines[i:i + len(before)] == before]
            if len(matches) != 1:
                raise UnsupportedConfiguration("nonunique/missing exact patch context: " + target)
            location = matches[0]
        lines[location:location + len(before)] = after
        receipt.append({"old_line": old_start, "new_line": new_start,
                        "actual_old_line": location + 1, "old_count": old_count,
                        "new_count": new_count, "exact_context": True})
        displacement = location - (old_start - 1) + new_count - old_count
    return b"".join(lines), receipt


def _fixed_build_values(corpus: Mapping[str, bytes]) -> dict[str, str]:
    build = json.loads(corpus["gcc-13-x86-64-linux-gnu-BUILD-v1.json"])
    embedded = json.loads(corpus["../evidence/EMBEDDED-CONFIGURATION-v1.json"])
    if (build.get("source_package_name") != "gcc-13"
            or build.get("source_package_version") != "13.3.0-6ubuntu2~24.04.1"
            or build.get("arch_tag") != "amd64"
            or not build.get("distro_series_link", "").endswith("/noble")
            or embedded.get("path") != COMPILER or embedded.get("sha256") != COMPILER_SHA256
            or len(embedded.get("matches", [])) != 1):
        raise UnsupportedConfiguration("fixed build/configuration metadata mismatch")
    tokens = shlex.split(embedded["matches"][0])
    required = ("--prefix=/usr", "--libdir=/usr/lib", "--libexecdir=/usr/libexec",
                "--program-prefix=x86_64-linux-gnu-", "--program-suffix=-13",
                "--enable-multiarch", "--enable-multilib", "--enable-default-pie",
                "--with-abi=m64", "--with-gcc-major-version-only",
                "--with-multilib-list=m32,m64,mx32", "--build=x86_64-linux-gnu",
                "--host=x86_64-linux-gnu", "--target=x86_64-linux-gnu")
    if any(tokens.count(token) != 1 for token in required):
        raise UnsupportedConfiguration("unsupported configure metadata")
    # Values below follow metadata + native build premise + named rules.defs
    # branches. Unproved optional language/build overrides stay UNKNOWN.
    return {"PKGSOURCE": "gcc-13", "distrelease": "noble", "derivative": "Ubuntu",
            "DEB_TARGET_ARCH": "amd64", "DEB_TARGET_ARCH_OS": "linux",
            "build_type": "build-native", "DEB_CROSS": "", "single_package": "",
            "trunk_build": "", "GFDL_INVARIANT_FREE": "no",
            "with_multiarch_cxxheaders": "yes", "with_ada": "yes",
            "multilib": "yes", "biarch64": "no", "biarchhfarchs": "",
            "biarchsfarchs": "", "with_async_unwind": "yes",
            "with_stack_clash": "yes", "with_cf_protection": "yes",
            "with_timet64": "", "no_timet64_distreleases":
            "jessy stretch buster bullseye bookworm precise trusty xenial bionic focal jammy kinetic lunar mantic"}


def derive_distro_defines(rules_patch: str, values: Mapping[str, str]) -> dict:
    """Extract literal echo data from the named generator; do not execute it."""
    lines = rules_patch.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if ': # generate the distro-defaults.h header' in line)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == 'mv pxxx $@')
    definite, conditional = {}, []
    for number, raw, active, conditions in _annotated_lines("\n".join(lines[start:end]), values):
        for match in re.finditer(r"echo '?(#define\s+([A-Z0-9_]+)\s+[^';]+)'", raw):
            # A recipe continuation can contain several echo statements. Locate
            # each exact directive in the physical source rather than assigning
            # every one the continuation's first line number.
            physical_line = rules_patch[:rules_patch.index(match[1])].count("\n") + 1
            record = {"directive": match[1], "line": physical_line, "conditions": conditions}
            if active is True: definite[match[2]] = record
            elif active is None: conditional.append(record)
    return {"definite_under_build_values": definite, "conditional": conditional,
            "generated_header_observed": False, "executed_recipe": False}


def _validate_command(command: Sequence[str], environment: Mapping, cwd: str) -> None:
    if (not isinstance(command, (list, tuple)) or len(command) != 13
            or any(type(v) is not str or "\0" in v for v in command)
            or command[0] != COMPILER or tuple(command[1:10]) != FIXED_OPTIONS
            or command[11] != "-o"):
        raise UnsupportedConfiguration("unsupported original command shape/options")
    if type(cwd) is not str or not cwd.startswith("/") or "\0" in cwd:
        raise UnsupportedConfiguration("cwd must be an explicit absolute stage path")
    if posixpath.normpath(cwd) != cwd or cwd == "/":
        raise UnsupportedConfiguration("cwd must be a normalized non-root stage path")
    for index in (10, 12):
        path = command[index]
        if not path.startswith(cwd + "/") or posixpath.normpath(path) != path:
            raise UnsupportedConfiguration("source/output must be stage-bound absolute occurrences")
    if not command[10].endswith(".c") or command[10] == command[12]:
        raise UnsupportedConfiguration("unsupported source/output occurrence")
    normalized = {}
    for key, value in environment.items():
        if type(key) not in (str, bytes) or type(value) not in (str, bytes):
            raise UnsupportedConfiguration("native environment type")
        key = key.decode("ascii") if type(key) is bytes else key
        value = value.decode("ascii") if type(value) is bytes else value
        if key in normalized: raise UnsupportedConfiguration("duplicate normalized environment key")
        normalized[key] = value
    if normalized != NATIVE_ENVIRONMENT:
        raise UnsupportedConfiguration("native environment must match the exact six-entry launch context")


def construct_fixed_rule_model(corpus: Mapping[str, bytes], command: Sequence[str],
                               native_environment: Mapping, cwd: str) -> dict:
    """Construct source-derived candidates, never an admitted effective chain.

    The source/output occurrences are recorded, not authenticated as the six
    originals. That binding remains the owning C05 constructor's obligation.
    """
    verify_source_bytes(corpus)
    _validate_command(command, native_environment, cwd)
    values = _fixed_build_values(corpus)
    selection = select_patch_data(_text(corpus, PATCH_BASE + "rules.patch"), values)
    selection["scope"] = "Under the stated metadata-aligned fixed build values; unrecorded build overrides and conditional selections are not resolved."
    projection, projection_frontier = [], []
    for name in sorted(k for k in corpus if k.startswith(BASE)):
        target, data = name[len(BASE):], corpus[name]
        applied = []
        for patch in selection["definitely_selected"]:
            key = PATCH_BASE + "patches/" + patch
            if key not in corpus:
                projection_frontier.append({"patch": patch, "reason": "selected patch bytes missing"})
                continue
            if target not in patch_targets(corpus[key]): continue
            try:
                result, receipt = project_patch(data, corpus[key], target)
            except UnsupportedConfiguration as error:
                projection_frontier.append({"target": target, "patch": patch, "reason": str(error)})
                # Later hunks no longer have a known predecessor; do not repair.
                break
            data = result
            applied.append({"patch": patch, "patch_sha256": sha256(corpus[key]), "hunks": receipt})
        projection.append({"target": target, "base_sha256": sha256(corpus[name]),
                           "definite_patch_projection_sha256": sha256(data), "patches": applied,
                           "installed_applied_equivalence_proven": False})
    refs = {
        "defaults": source_ref(corpus, BASE + "gcc/cppdefault.cc", "const struct default_include cpp_include_defaults[]"),
        "preprocessor_defines": source_ref(corpus, BASE + "gcc/Makefile.in", "PREPROCESSOR_DEFINES ="),
        "directory_identity": source_ref(corpus, BASE + "gcc/incpath.cc", "remove_duplicates (cpp_reader"),
        "chain_merge": source_ref(corpus, BASE + "gcc/incpath.cc", "merge_include_chains (const char *sysroot"),
        "automatic_specs": source_ref(corpus, BASE + "gcc/gcc.cc", 'find_a_file (&startfile_prefixes, "specs", R_OK, true)'),
        "override_specs": source_ref(corpus, BASE + "gcc/gcc.cc", "strcat (specs_file, spec_machine_suffix);"),
        "environment_rebuild": source_ref(corpus, BASE + "gcc/gcc.cc", 'putenv_from_prefixes (&exec_prefixes, "COMPILER_PATH", false)'),
        "relocation": source_ref(corpus, BASE + "gcc/gcc.cc", "gcc_exec_prefix = get_relative_prefix"),
        "pch": source_ref(corpus, BASE + "libcpp/files.cc", 'static const char extension[] = ".gch";'),
        "pch_order": source_ref(corpus, BASE + "libcpp/files.cc", "if (pch_open_file (pfile, file, invalid_pch))"),
        "preinclude": source_ref(corpus, BASE + "gcc/config/glibc-c.cc", 'return "stdc-predef.h";'),
        "preinclude_condition": source_ref(corpus, BASE + "gcc/c-family/c-opts.cc", "if (flag_hosted && std_inc && !cpp_opts->preprocessed)"),
        "prefixed_as_ld": source_ref(corpus, PATCH_BASE + "patches/gcc-search-prefixed-as-ld.diff", "/* search for the <triplet>-as / -ld first.  */"),
        "canonical_paths": source_ref(corpus, PATCH_BASE + "patches/canonical-cpppath.diff", "char *rp = lrealpath (str);"),
        "multiarch": source_ref(corpus, PATCH_BASE + "patches/gcc-multiarch.diff", "MULTIARCH_DIRNAME = $(call if_multiarch,x86_64-linux-gnu)"),
        "multilib": source_ref(corpus, PATCH_BASE + "patches/gcc-multilib-multiarch.diff", "MULTILIB_OSDIRNAMES = m64=../lib$(call if_multiarch,:x86_64-linux-gnu)"),
        "distro_generator": source_ref(corpus, PATCH_BASE + "rules.patch", ": # generate the distro-defaults.h header"),
        "link_emulation": source_ref(corpus, BASE + "gcc/config/i386/linux64.h", '#define GNU_USER_LINK_EMULATION64 "elf_x86_64"'),
        "startfiles_condition": source_ref(corpus, BASE + "gcc/gcc.cc", "%{!nostdlib:%{!r:%{!nostartfiles:%S}}}"),
        "libc_selection": source_ref(corpus, BASE + "gcc/config/gnu-user.h", "#define LIB_SPEC GNU_USER_TARGET_LIB_SPEC"),
        "build_native": source_ref(corpus, PACKAGING + "rules.defs", "build_type = build-native"),
        "multiarch_cxx_branch": source_ref(corpus, PACKAGING + "rules.defs", "with_multiarch_cxxheaders := yes"),
        "ubuntu_gfdl": source_ref(corpus, PACKAGING + "rules.defs", "GFDL_INVARIANT_FREE := no"),
        "installed_layout": source_ref(corpus, PACKAGING + "rules2", "gcc_lexec_dir\t= $(libexecdir)/$(gcc_subdir_name)/$(TARGET_ALIAS)/$(versiondir)"),
    }
    target, version = "x86_64-linux-gnu", "13"
    libsubdir = "/usr/lib/gcc/" + target + "/" + version
    libexecsubdir = "/usr/libexec/gcc/" + target + "/" + version
    include_templates = [
        ("bracket", "/usr/include/python3.12", "explicit -I", False),
        ("system", libsubdir + "/include", "GCC_INCLUDE_DIR", False),
        ("system", "/usr/local/include/" + target, "LOCAL_INCLUDE_DIR + multiarch", True),
        ("system", "/usr/local/include", "LOCAL_INCLUDE_DIR", True),
        ("system", libsubdir + "/include-fixed/" + target, "FIXED_INCLUDE_DIR + multiarch", False),
        ("system", libsubdir + "/include-fixed", "FIXED_INCLUDE_DIR", False),
        ("system", "/usr/" + target + "/include", "TOOL_INCLUDE_DIR", False),
        ("system", "/usr/include/" + target, "NATIVE_SYSTEM_HEADER_DIR + multiarch", True),
        ("system", "/usr/include", "NATIVE_SYSTEM_HEADER_DIR", True),
    ]
    candidates = [{"chain": chain, "path": path, "rule": rule, "add_sysroot": sysroot,
                   "effective": False} for chain, path, rule, sysroot in include_templates]
    frontier = [
        {"id": "GCC_GENERATED_CONFIGURATION_AND_BUILD_CORRESPONDENCE",
         "needed": "Exact applied config.h/auto-host.h/tm.h/options.h/specs.h/multilib.h, generated distro-defaults.h and configured Makefile substitutions or an equivalent complete source derivation tied to the pinned installed driver/cc1/collect2 bytes."},
        {"id": "GCC_COMPLETE_TARGET_AND_RELOCATION_RULES",
         "needed": "All selected tm_file headers and hooks, gcc/prefix.cc update_path, libiberty make_relative_prefix/lrealpath, target/default options; literal argv prefix alone does not decide runtime relocation/aliases."},
        {"id": "GCC_AUTOMATIC_AND_TRANSITIVE_SPECS_LOOKUPS",
         "needed": "Actual ordered startfile-prefix specs lookups, independent standard_exec_prefix/target/specs lookup, selected contents and every reached specs include/function edge, with genuine errors."},
        {"id": "GCC_INCLUDE_DIRECTORY_IDENTITIES_AND_LOOKUPS",
         "needed": "Actual stat errors, canonical paths, device/inode aliases, GCC directory deduplication and target include hooks before calling any template an effective chain."},
        {"id": "GCC_PCH_CONTENT_VALIDATION_AND_ORDER",
         "needed": "Actual eligible .gch existence/type, readdir order and members, exact gcc/c-family/c-pch.cc validity rules and full selected PCH content dependencies."},
        {"id": "GCC_INITIAL_MACROS_AND_HEADER_CLOSURE",
         "needed": "Applied option/target builtins, automatic stdc-predef.h and recursive file-producing preprocessing rules; generator defaults may be affected by external specs."},
        {"id": "GCC_SUBPROGRAM_COLLECT2_AND_LINK_INPUT_SELECTION",
         "needed": "Exact exec/startfile prefix construction/expansion and access results, collect2 configured alternatives, subordinate environment and actual binutils/loader closure."},
        {"id": "C05_ORIGINAL_BINDING_NAMESPACE_INTERVAL_AND_CAPS",
         "needed": "Authenticated six original path occurrences, actual content/negative lookup custody, namespace stability interval, owning process integration and fit under every unchanged original cap."},
    ]
    if projection_frontier:
        frontier.insert(0, {"id": "EXACT_TEXTUAL_PATCH_PROJECTION", "needed": projection_frontier})
    if selection["conditional"]:
        frontier.insert(0, {"id": "GCC_CONDITIONAL_PATCH_SELECTION_AND_BUILD_OVERRIDES",
                           "needed": selection["conditional"]})
    return {
        "schema": "c05-fixed-gcc-rule-model-v1", "full_C05": False, "full_V03": False,
        "execution_ready": False, "effective_include_chain_proven": False,
        "installed_applied_equivalence_proven": False,
        "source_pinset_sha256": PINSET_SHA256, "compiler": COMPILER,
        "compiler_sha256": COMPILER_SHA256, "command": list(command), "cwd": cwd,
        "native_launch_environment": dict(NATIVE_ENVIRONMENT),
        "original_occurrence_binding_proven": False,
        "fixed_build_values": values, "build_values_override_absence_proven": False,
        "patch_selection": selection, "definite_patch_projection": projection,
        "conditional_distro_defines": derive_distro_defines(_text(corpus, PATCH_BASE + "rules.patch"), values),
        "configuration_recipe": {"prefix": "/usr", "libdir": "/usr/lib",
            "libexecdir": "/usr/libexec", "libsubdir": libsubdir,
            "libexecsubdir": libexecsubdir, "target": target, "version": version,
            "default_abi": "m64", "default_multiarch": target,
            "default_os_multilib": "../lib", "default_pie": True,
            "authoritative_generated_configuration": False},
        "include_templates_before_relocation_hooks_canonicalization_and_dedup": candidates,
        "quote_source_directory_rule": "Search including file's directory first unless the exact include mechanism disables it; source and alias identity still required.",
        "automatic_preinclude": {"name": "stdc-predef.h", "condition": "hosted && std_inc && !preprocessed with selected glibc targetcm", "effective": False},
        "automatic_specs_rules": [
            {"rule": "find_a_file(startfile_prefixes, specs, R_OK, do_multi=true)", "ordered_candidates_proven": False},
            {"rule": "independent access(STANDARD_EXEC_PREFIX + target/ + specs, R_OK)",
             "configured_candidate": "/usr/lib/gcc/x86_64-linux-gnu/specs", "observed": False}],
        "pch_rule": {"candidate": "consequential-header-path + .gch", "before_normal_header": True,
                     "eligibility": "first non-implicit-preinclude include and enabled valid_pch callback",
                     "directory_members": "readdir order, excluding . and .., until first valid candidate", "observed": False},
        "subprogram_root_templates": [libexecsubdir, libsubdir, "/usr/" + target + "/bin", "/usr/bin", "/bin"],
        "subprogram_templates_are_complete_or_ordered": False,
        "prefixed_as_ld_rule": "At each GCC file_at_path prefix, try x86_64-linux-gnu-as/ld before unprefixed as/ld; collect2 has its own configured search.",
        "builtin_shared_link_recipe": {"emulation_candidate": "elf_x86_64",
            "nostartfiles_suppresses": "startfile/endfile specs, not all standard libraries",
            "dynamic_interpreter_for_shared_output": "GNU_USER_TARGET_LINK_SPEC guards the dynamic-linker option with !shared; toolchain ELF loading is a separate closure.",
            "applied_effective_recipe_proven": False},
        "subordinate_environment_rule": "GCC may create GCC_EXEC_PREFIX and rebuilds COMPILER_PATH and LIBRARY_PATH from filtered configured prefix lists; launch-time absence is not subprocess absence.",
        "source_evidence": refs, "frontier": frontier, "original_caps": dict(ORIGINAL_CAPS),
        "original_target_executed": False, "new_scientific_activity_credit": 0,
        "recorded_policy_debit_seconds": "94.550533479/2400", "physical_costs": "OPEN_NOT_ZERO",
    }


def construct_effective_configuration(corpus: Mapping[str, bytes], command: Sequence[str],
                                      native_environment: Mapping, cwd: str) -> dict:
    """Fail closed: no caller-supplied chain or completeness boolean is trusted."""
    model = construct_fixed_rule_model(corpus, command, native_environment, cwd)
    raise IncompleteConfiguration(model)
