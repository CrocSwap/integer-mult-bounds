#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Show that the public V02 replay does not bind the 56 recorded assumptions.

The pinned export is commit 1998ae8ee6d46bafac647329e5b41a85941bb2e7 of
Clear1nsight/integer-mult-bounds, the head named by the #1166 handoff for
PR #7136. Those objects are not ancestors of this branch, so the seven
public files are vendored under pinned-export/ and checked by Git blob id.
No compiler is executed and the selected kappa is not changed.
"""

import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = Path(__file__).resolve().parent
REPO = PKG.parents[1]
EXPORT = PKG / "pinned-export"
DRIVER = REPO / "research/h25-c05-criterion-consumer-contract/snapshot/original/variant/variant_driver_v1.py.txt"
ROLE_PROOF = REPO / "research/h25-c05-criterion-consumer-contract/ROLE-PROOF.json"

BLOB_IDS = {
    "EVIDENCE.json": "04090aa24ad64f15c23d61d8a99299b0e81d4801",
    "FIXTURE.json": "d9f262d33dc58306172ff5dc7db43c4e9d552b3b",
    "MANIFEST.json": "844566dc566aca24ae2141c3606c9c28fcd31c28",
    "README.md": "e585da7617790ea265c66cfb135441d1d2ab18aa",
    "SOURCE_MAP.json": "ea6967d7a147dc162346ce908ea5ea5f3df7a0f4",
    "literal_walk.py": "62ae605970292a8810ed01dca0e9d040eedca5bd",
    "verify.py": "3f7c8f5bf23db36800f7e2a89f13fa8f2bafc76c",
}

DEFINED = {
    "_LP64": 1,
    "__CHAR_BIT__": 8,
    "__ELF__": 1,
    "__GNUC_MINOR__": 3,
    "__GNUC_PATCHLEVEL__": 0,
    "__GNUC__": 13,
    "__LP64__": 1,
    "__SIZEOF_LONG__": 8,
    "__SIZEOF_POINTER__": 8,
    "__STDC_HOSTED__": 1,
    "__STDC_VERSION__": 201112,
    "__STDC__": 1,
    "__amd64": 1,
    "__amd64__": 1,
    "__gnu_linux__": 1,
    "__linux": 1,
    "__linux__": 1,
    "__unix__": 1,
    "__x86_64": 1,
    "__x86_64__": 1,
}

NULLS = (
    "HAVE_IEEEFP_H", "HAVE_STAT_H", "HAVE_SYS_TERMIO_H",
    "MS_WINDOWS", "MS_WINDOWS_DESKTOP", "MS_WINDOWS_GAMES", "NT_THREADS",
    "_AIX", "_MSC_VER", "_WIN32", "_WIN64",
    "__ANDROID__", "__APPLE__", "__CYGWIN__", "__DragonFly__",
    "__FreeBSD__", "__FreeBSD_kernel__", "__GNU__", "__HAIKU__", "__ILP32__",
    "__MACH__", "__NetBSD__", "__OpenBSD__", "__VMS", "__VXWORKS__",
    "__cplusplus", "__hpux", "__hpux__", "__i386", "__i386__",
    "__rtems__", "__sgi", "__sun", "__sun__", "__vxworks", "__wasi__",
)

COMMAND_SOURCE = (
    "        command = ['/usr/bin/x86_64-linux-gnu-gcc-13', '-nostartfiles', '-shared',\n"
    "                   '-fPIC', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',\n"
    "                   '-I' + plan['include'], row['source_path'], '-o', target]"
)
INCLUDE_SOURCE = "if (not _vsame(plan['include'], '/usr/include/python3.12')):"
ROLES_SOURCE = "(not _vsame([row['role'] for row in plan['roles']], ['pyinit_failure', 'exec_failure']))"
TARGET_SOURCE = "target = directory + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so'"
DIRECTORY_SOURCE = "directory = output + '/' + row['role']"
COUNT_LINE = "    need(len(fixture['original_source_condition_assumptions']) == 56, 'assumption count differs')"
STDC_PREDEF = "/usr/include/stdc-predef.h"
PYCONFIG = (
    "/usr/include/python3.12/pyconfig.h",
    "/usr/include/x86_64-linux-gnu/python3.12/pyconfig.h",
)


def fail(message):
    raise SystemExit(message)


def git_blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_export():
    blobs = {}
    for name, expected in BLOB_IDS.items():
        data = (EXPORT / name).read_bytes()
        got = git_blob_id(data)
        if got != expected:
            fail("vendored blob id mismatch for " + name + ": " + got)
        blobs[name] = data
    fixture = json.loads(blobs["FIXTURE.json"])
    manifest = json.loads(blobs["MANIFEST.json"])
    evidence = json.loads(blobs["EVIDENCE.json"])
    source_map = json.loads(blobs["SOURCE_MAP.json"])
    return blobs, fixture, manifest, evidence, source_map


def assumption_predicate(source):
    if source.count("original_source_condition_assumptions") != 1:
        fail("public verifier does not mention the assumption object exactly once")
    if source.count(COUNT_LINE) != 1:
        fail("public assumption predicate is not the length check")
    tree = ast.parse(source)
    constants = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value == "original_source_condition_assumptions"
    ]
    if len(constants) != 1:
        fail("assumption name is not one Python string constant")
    return COUNT_LINE


def frozen_argvs(driver_text, role_proof):
    for snippet in (COMMAND_SOURCE, INCLUDE_SOURCE, ROLES_SOURCE, TARGET_SOURCE, DIRECTORY_SOURCE):
        if driver_text.count(snippet) != 1:
            fail("frozen command source snippet is not unique")
    prefix = [
        "/usr/bin/x86_64-linux-gnu-gcc-13", "-nostartfiles", "-shared",
        "-fPIC", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-I/usr/include/python3.12",
    ]
    built = []
    for role in ("pyinit_failure", "exec_failure"):
        built.append(prefix + [
            "{S}/areas/field-negative-variants-v1/" + role + "/dict_probe_fields_v1.c",
            "-o",
            "{O}/" + role + "/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so",
        ])
    recorded = [row["argv"] for row in role_proof["resolved_direct_domain"]["D_variant"]]
    if recorded != built:
        fail("ROLE-PROOF argv does not match the driver template")
    if role_proof["resolved_direct_domain"]["ordered_roles"] != ["pyinit_failure", "exec_failure"]:
        fail("role order differs")
    if role_proof["resolved_direct_domain"]["GCC_options_same_in_both_Python_modes"] is not True:
        fail("mode flag differs from the recorded contract")
    return built


def classify(assumptions, argvs):
    if set(assumptions) != set(DEFINED) | set(NULLS):
        fail("assumption key set differs from the checked partition")
    if len(assumptions) != 56 or len(DEFINED) != 20 or len(NULLS) != 36:
        fail("partition sizes differ")
    tokens = {token for argv in argvs for token in argv}
    rows = []
    for name in sorted(assumptions):
        recorded = assumptions[name]
        if name in DEFINED:
            if recorded != DEFINED[name]:
                fail("recorded value differs: " + name)
        elif recorded is not None:
            fail("null row is not null: " + name)
        agreement = None
        if name == "__GNUC__" and recorded == 13 and all(argv[0].endswith("x86_64-linux-gnu-gcc-13") for argv in argvs):
            agreement = "argv0-basename-gcc-13"
        if name == "__STDC_VERSION__" and recorded == 201112 and "-std=c11" in tokens:
            agreement = "argv-element-std-c11"
        if name in tokens:
            fail("assumption name occurs as an argv element: " + name)
        rows.append({
            "name": name,
            "recorded": recorded,
            "argv_element": False,
            "token_agreement": agreement,
            "read_by_public_replay": False,
        })
    if sum(row["token_agreement"] is not None for row in rows) != 2:
        fail("token-agreement count differs")
    return rows


def preinclude(fixture, verifier_source, assumptions):
    row = fixture["baseline_graph"][STDC_PREDEF]
    if row != {
        "bytes": 2462,
        "kind": "regular",
        "mode": 420,
        "sha256": "8db4f65e62cade8ae4d9b77960ee6aee093255acc1b637e3fb37d79179733b15",
    }:
        fail("stdc-predef graph row differs")
    if STDC_PREDEF in assumptions or "stdc-predef" in verifier_source:
        fail("public assumption check names the implicit header")
    for path in PYCONFIG:
        item = fixture["baseline_graph"][path]
        if item["kind"] != "regular" or not isinstance(item.get("sha256"), str):
            fail("pyconfig row is not a hashed regular file")
        if "content" in item or "text" in item:
            fail("pyconfig file text is present")
    namespace = {}
    exec(compile((EXPORT / "literal_walk.py").read_text(encoding="utf-8"), "<literal_walk>", "exec"), namespace)
    outcome = namespace["literal_walk"](STDC_PREDEF, fixture["baseline_graph"])
    if outcome != {"resolved": STDC_PREDEF}:
        fail("stdc-predef walk outcome differs: " + str(outcome))
    return {"path": STDC_PREDEF, "graph_row": row, "walk": outcome,
            "implicit_include_bound": False}


def run_public(directory):
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "verify.py"],
        cwd=directory, capture_output=True, text=True, timeout=60, check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def materialize(destination, blobs, fixture_override=None):
    destination.mkdir()
    for name, data in blobs.items():
        (destination / name).write_bytes(data)
    if fixture_override is None:
        return
    payload = json.dumps(fixture_override, indent=2).encode() + b"\n"
    (destination / "FIXTURE.json").write_bytes(payload)
    manifest = json.loads(blobs["MANIFEST.json"])
    for row in manifest["files"]:
        if row["path"] == "FIXTURE.json":
            row["bytes"] = len(payload)
            row["sha256"] = hashlib.sha256(payload).hexdigest()
    (destination / "MANIFEST.json").write_bytes(json.dumps(manifest, indent=2).encode() + b"\n")


def public_controls(blobs, fixture):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        original = root / "original"
        materialize(original, blobs)
        code, out, err = run_public(original)
        if code != 0 or err:
            fail("unmodified public replay failed: " + err[-400:])
        original_result = json.loads(out)
        if original_result.get("status") != "PASS" or original_result.get("original_commands_executed") != 0:
            fail("unmodified public replay is not a zero-command PASS")

        changed = json.loads(json.dumps(fixture))
        if changed["original_source_condition_assumptions"]["__GNUC_MINOR__"] != 3:
            fail("minor version seed differs")
        changed["original_source_condition_assumptions"]["__GNUC_MINOR__"] = 4
        mutated = root / "mutated-minor"
        materialize(mutated, blobs, changed)
        code, out, err = run_public(mutated)
        if code != 0 or err:
            fail("value-changed public replay failed: " + err[-400:])
        if json.loads(out) != original_result:
            fail("public PASS changed when __GNUC_MINOR__ changed")

        shrunk = json.loads(json.dumps(fixture))
        del shrunk["original_source_condition_assumptions"]["HAVE_IEEEFP_H"]
        deleted = root / "deleted-key"
        materialize(deleted, blobs, shrunk)
        code, out, err = run_public(deleted)
        if code == 0 or "assumption count differs" not in (out + err):
            fail("deleting an assumption key was accepted")
    return original_result


def main():
    blobs, fixture, manifest, evidence, source_map = load_export()
    listed = {row["path"]: row["sha256"] for row in manifest["files"]}
    for name, row_hash in listed.items():
        if hashlib.sha256(blobs[name]).hexdigest() != row_hash:
            fail("manifest hash differs: " + name)
    verifier_source = blobs["verify.py"].decode()
    assumption_predicate(verifier_source)
    if "original host file contents" not in source_map["excluded_data"]:
        fail("export does not exclude host file contents")
    if evidence["remaining_obligations"][0] != (
        "Bind inherited 56 predefined/configuration facts and the implicit hosted "
        "stdc-predef.h policy to original authenticated frontend, options and input closure."
    ):
        fail("recorded remaining obligation differs")
    assumptions = fixture["original_source_condition_assumptions"]
    argvs = frozen_argvs(DRIVER.read_text(encoding="utf-8"), json.loads(ROLE_PROOF.read_text(encoding="utf-8")))
    rows = classify(assumptions, argvs)
    header = preinclude(fixture, verifier_source, assumptions)
    readme = (PKG / "README.md").read_text(encoding="utf-8")
    missing = [row["name"] for row in rows if row["name"] not in readme]
    if missing:
        fail("README omits assumption names: " + ", ".join(missing))
    public = public_controls(blobs, fixture)
    result = {
        "status": "PASS_V02_ASSUMPTION_VALUES_UNBOUND",
        "assumption_count": 56,
        "defined_count": 20,
        "null_count": 36,
        "public_predicate": "len(original_source_condition_assumptions) == 56",
        "public_pass_unchanged_when_GNUC_MINOR_becomes_4": True,
        "deleted_key_rejected": "HAVE_IEEEFP_H",
        "token_agreements": [row for row in rows if row["token_agreement"]],
        "argv_element_matches": 0,
        "implicit_include": header,
        "installed_compiler_executed": False,
        "original_commands_executed_by_public_replay": public["original_commands_executed"],
        "kappa_changed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
