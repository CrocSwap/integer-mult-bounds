#!/usr/bin/env python3
"""Static audit of inert source snapshots. Never import/execute archived code.
Clear1nsight/ChrisR; substantial OpenAI Pro/Codex/Sol Max assistance.
New checker Apache-2.0; third-party source notices remain intact.
"""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parent
KERNEL = "88cb661f6b53f472167d39a72241b5396e34ab2a"
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 512

def need(condition, message):
    if not condition:
        raise ValueError(message)

def canonical(path):
    need(type(path) is str and bool(path), "invalid path type")
    p = PurePosixPath(path)
    need(not p.is_absolute() and ".." not in p.parts and "." not in p.parts
         and str(p) == path, "noncanonical package path")
    return path

def raw(path):
    p = ROOT / canonical(path)
    cur = ROOT
    for part in PurePosixPath(path).parts:
        cur = cur / part
        need(not cur.is_symlink(), "symlink input")
    need(p.is_file() and p.stat().st_size <= MAX_FILE, "input type or size")
    return p.read_bytes()

def data(path):
    return json.loads(raw(path))

def pin_matches(blob, row):
    return len(blob) == row["bytes"] and hashlib.sha256(blob).hexdigest() == row["sha256"]

def get_ref(name, named, inventory):
    need(name in named, "dangling source reference")
    p = named[name]
    need(p in inventory, "undeclared source reference")
    return p

def hook_pairs(source):
    # Exact selected source structure, not a general C parser/preprocessor.
    pattern = (r"static struct security_hook_list apparmor_hooks\[\]"
               r" __ro_after_init\s*=\s*\{(.*?)\n\};")
    blocks = re.findall(pattern, source, re.S)
    need(len(blocks) == 1, "hook initializer count")
    need(re.search(r"security_add_hooks\(\s*apparmor_hooks\s*,\s*"
                   r"ARRAY_SIZE\(apparmor_hooks\)\s*,\s*&apparmor_lsmid\s*\)", source),
         "registered initializer not used")
    return [list(x) for x in re.findall(
        r"LSM_HOOK_INIT\(\s*(\w+)\s*,\s*(\w+)\s*\)", blocks[0])]

def functions(tree):
    return {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

def literal_assignment(tree, name):
    found = [n.value for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    need(len(found) == 1, "literal assignment count: " + name)
    return ast.literal_eval(found[0])

def names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

def attributes(node):
    return {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}

def reject(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("adverse control accepted: " + message)

def predicate(kind, text, tokens):
    need(kind == "literal_tokens", "unknown predicate kind")
    need(all(t in text for t in tokens), "source anchor differs")

def main():
    manifest = data("MANIFEST.json")
    need(manifest["schema"] == "h25-canonical-byte-manifest/v1", "manifest schema")
    rows = manifest["files"]
    need(0 < len(rows) <= MAX_FILES, "manifest count")
    inventory = {canonical(r["path"]): r for r in rows}
    need(len(inventory) == len(rows) and "MANIFEST.json" not in inventory,
         "manifest duplicates/self reference")
    actual = set()
    for p in ROOT.rglob("*"):
        need(not p.is_symlink(), "package symlink")
        if p.is_file():
            actual.add(p.relative_to(ROOT).as_posix())
    need(actual == set(inventory) | {"MANIFEST.json"}, "package inventory differs")
    for path, row in inventory.items():
        need(pin_matches(raw(path), row), "byte pin differs: " + path)
    origin = data("SOURCE-ORIGINS.json")
    need(origin["kernel_commit"] == KERNEL, "kernel source pin differs")
    named = origin["named_sources"]
    origins = origin["files"]
    need(len({x["path"] for x in origins}) == len(origins), "duplicate source origin")
    for row in origins:
        need(row["executed"] is False and pin_matches(raw(row["path"]), row),
             "source-origin pin differs")
    kernel_rows = [r for r in origins if r["kind"] == "exact-kernel-source"]
    aa_rows = [r for r in origins if r["kind"] == "selected-unapplied-apparmor-source"]
    need(len(kernel_rows) == 25 and len(aa_rows) == 54
         and sum(r["bytes"] for r in aa_rows) == 843856, "selected source set differs")
    lgpl = raw("snapshot/apparmor-unapplied/libraries/libapparmor/COPYING.LGPL")
    need(len(lgpl) == 26432 and hashlib.sha256(lgpl).hexdigest() ==
         "6095e9ffa777dd22839f7801aa845b31c9ed07f3d6bf8a26dc5d2dec8ccc0ef3",
         "required LGPL-2.1 license text differs")
    obs = data("OBSERVATIONS.json")
    review = data("audit/unit11/compatibility/ORIGINAL-CONTRACT-CHANNEL-REVIEW-v1.json")
    for name, row in review["sources"].items():
        need(pin_matches(raw(get_ref(name, named, inventory)), row),
             "review source pin differs: " + name)
    # Authenticate original acquisition receipt-to-body associations.
    origin_map = {r["origin"]: r for r in origins}
    authenticated_kernel = set()
    for receipt, key in [("EXACT-SOURCE-ACQUISITION-v1.json","bounded_sources"),
                         ("ADDITIONAL-EXACT-SOURCE-ACQUISITION-v1.json","sources")]:
        for row in data("audit/unit11/kernel/" + receipt)[key]:
            if row.get("outcome") != "retained":
                continue
            need(row["path"] in origin_map, "missing retained kernel receipt source")
            retained = origin_map[row["path"]]
            need(len(raw(retained["path"])) == row["size_bytes"]
                 and retained["sha256"] == row["sha256"]
                 and row["commit"] == KERNEL, "kernel acquisition pin differs")
            authenticated_kernel.add(retained["path"])
    need(authenticated_kernel == {r["path"] for r in kernel_rows},
         "kernel receipt coverage differs")
    aa_count = 0
    for archive in data("audit/unit11/kernel/APPARMOR-SELECTED-SOURCE-v2.json")["archives"]:
        for row in archive["retained_regular_files"]:
            need(row["path"] in origin_map, "missing retained AppArmor member")
            retained = origin_map[row["path"]]
            need(retained["sha256"] == row["sha256"]
                 and retained["bytes"] == row["size_bytes"], "AppArmor member pin differs")
            aa_count += 1
    need(aa_count == 54, "AppArmor member receipt count differs")
    def text(name):
        return raw(get_ref(name, named, inventory)).decode("utf-8")
    lsm = text("aa_lsm")
    hooks = hook_pairs(lsm)
    need(hooks == obs["apparmor_registered_hook_pairs"], "hook pairs differ")
    hooknames = {h[0] for h in hooks}
    need({"inode_getattr", "file_receive", "file_open", "file_permission"} <= hooknames,
         "expected registered hooks absent")
    need(not set(obs["absent_from_apparmor_registered_array"]) & hooknames,
         "claimed array-absent hook present")
    predicate("literal_tokens", lsm, ["aa_inherit_files(bprm->cred, current->files)",
              "current->pdeath_signal = 0", "__aa_transition_rlimits(label, new_label)"])
    predicate("literal_tokens", text("aa_file"), [
        "return unconfined(obj_label)", "__file_is_delegated(flabel)",
        "iterate_fd(files, 0, match_file, &cl)", "replace_fd(n - 1, devnull, 0)"])
    predicate("literal_tokens", text("aa_domain"), ["LSM_UNSAFE_SHARE", "FIXME"])
    predicate("literal_tokens", text("bpf_lsm"), [
        "bpf_lsm_disabled_hooks", "bpf_lsm_verify_prog", "attach_btf_id"])
    predicate("literal_tokens", text("aa_compat"), ["map_old_perms", "AA_MAY_GETATTR"])
    predicate("literal_tokens", raw("snapshot/kernel/security/apparmor/include/file.h").decode(),
              ["aa_map_file_to_perms", "flags & O_APPEND", "MAY_APPEND", "FMODE_WRITE"])
    predicate("literal_tokens", raw("snapshot/kernel/security/bpf/hooks.c").decode(),
              ["security_add_hooks", "bpf_lsm_hooks", "bpf_lsm_init", "DEFINE_LSM(bpf)"])
    # Parse archived Python only as DATA. No compile/eval/exec/import of snapshots.
    provider = ast.parse(text("provider"), filename="inert-provider.py.txt")
    pf = functions(provider)
    runtime = literal_assignment(provider, "_RUNTIME_FILES")
    need(type(runtime) is tuple and len(runtime) == 216, "runtime literal row count")
    need(all(type(r) is tuple and len(r) == 3 and type(r[0]) is str
             and re.fullmatch("[0-9a-f]{64}", r[1]) and type(r[2]) is int
             and r[2] > 0 for r in runtime), "runtime literal shape")
    headers = [r for r in runtime if r[0] != "/proc/self/exe"]
    need(len(headers) == 215 and sum(r[2] for r in headers) == 1256818
         and sum(r[0].startswith("/usr/include/python3.12/") for r in headers) == 214
         and sum(r[0] == "/proc/self/exe" for r in runtime) == 1, "header partition")
    returns = [n.value for n in ast.walk(pf["_profile_files"]) if isinstance(n, ast.Return)]
    need(len(returns) == 1 and isinstance(returns[0], ast.BinOp)
         and isinstance(returns[0].op, ast.Add)
         and isinstance(returns[0].left, ast.Name)
         and returns[0].left.id == "_RUNTIME_FILES"
         and isinstance(returns[0].right, ast.Tuple) and len(returns[0].right.elts) == 1,
         "profile addition differs")
    need({"_profile_files", "_audit_files"} <= names(pf["preflight_runtime"]),
         "separate preflight call chain differs")
    need("_hash_regular" in names(pf["_audit_files"]), "audit source differs")
    need(literal_assignment(provider, "_PROFILE_BASENAME") == "RUNTIME-PROFILE.json",
         "profile basename")
    if "runtime_profile" in named:
        need(hashlib.sha256(raw(get_ref("runtime_profile", named, inventory))).hexdigest()
             == literal_assignment(provider, "_PROFILE_SHA256"), "profile bytes differ")
    variant = ast.parse(text("variant"), filename="inert-variant.py.txt")
    vmain = functions(variant)["_variant_main"]
    need("_vcheck_literal_sources" in names(vmain), "variant literal guard not called")
    role_lists = [n for n in ast.walk(vmain) if isinstance(n, ast.List)
                  and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in n.elts)]
    need(["pyinit_failure", "exec_failure"] in [[x.value for x in n.elts] for n in role_lists],
         "main role-list guard differs")
    vf = functions(variant)["_vcheck_literal_sources"]
    roles = literal_assignment(variant, "_VARIANT_SOURCE_PINS")
    need(set(roles) == {"pyinit_failure", "exec_failure"}, "role literal set")
    expected = [n.value for n in ast.walk(vf) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "expected" for t in n.targets)]
    need(len(expected) == 1 and isinstance(expected[0], ast.Dict), "role dict")
    keys = [ast.literal_eval(k) for k in expected[0].keys]
    need(keys == ["dict_probe_fields_v1.c", "field_service_v1.h",
                  "field_loader_snapshot_v1.h"] and len(keys) * len(roles) == 6,
         "six role occurrences differ")
    need("_VARIANT_SOURCE_PINS" in names(vf) and "_RUNTIME_FILES" not in names(vf),
         "variant/provider membership conflated")
    need("/usr/include/python3.12" in {n.value for n in ast.walk(vf)
         if isinstance(n, ast.Constant) and isinstance(n.value,str)}, "fixed include")
    helper = ast.parse(text("cold_helper"), filename="inert-cold-helper.py.txt")
    popens = [n for n in ast.walk(helper) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Attribute) and n.func.attr == "Popen"]
    need(len(popens) == 1, "Popen source call count")
    kw = {x.arg:x.value for x in popens[0].keywords}
    need("cwd" not in kw and "env" not in kw
         and ast.literal_eval(kw["close_fds"]) is True
         and ast.literal_eval(kw["start_new_session"]) is False
         and "DEVNULL" in attributes(kw["stdin"]), "original Popen context")
    flags = [n.value for n in ast.walk(helper) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "flags" for t in n.targets)]
    need(len(flags) == 1 and attributes(flags[0]) ==
         {"O_WRONLY", "O_CREAT", "O_EXCL", "O_CLOEXEC", "O_NOFOLLOW"},
         "original nonappend open flags")
    gate = data("audit/unit11/SOURCE-GATE-CLOSE-v1.json")
    need(gate["complete_accepted_count"] == 0 and gate["fixed_denominator"] == 4
         and gate["status"] == "CLOSED_AT_FAILED_INPUT_GATE_STOP_BEFORE_INSTALLER"
         and gate["parser_supplement_is_late_append_only_bookkeeping_not_checkpoint_credit"]
         and not gate["full_C05"] and not gate["full_V03"], "closed gate differs")
    need(len(obs["channels"]) == 21 and all(
        r["whole_claim_status"] == "OPEN_NO_COMPLETE_CHANNEL_CREDIT" for r in obs["channels"]),
        "channel closure status differs")
    need(obs["full_C05"] is False and obs["full_V03"] is False
         and obs["actual_GCC_use_of_gaps_shown"] is False
         and obs["rawlog_clobber_demonstrated"] is False
         and obs["universal_impossibility_proved"] is False
         and obs["outside_costs"] == "OPEN_NOT_ZERO"
         and obs["parser_composition"] == "UNQUALIFIED", "assurance scope differs")
    # New pure literal adverse controls; no archived code/test execution.
    reject(lambda: predicate("invented", "", []), "unknown predicate")
    reject(lambda: get_ref("MISSING", named, inventory), "dangling source")
    need(not pin_matches(b"changed", {"bytes":7,"sha256":"0"*64}), "changed pin control")
    fake = ("static struct security_hook_list apparmor_hooks[] __ro_after_init = {\n"
            "LSM_HOOK_INIT(file_open, open_impl),\n};\n"
            "security_add_hooks(apparmor_hooks, ARRAY_SIZE(apparmor_hooks), &apparmor_lsmid);\n"
            "LSM_HOOK_INIT(inode_readlink, outside_array);\n")
    need(hook_pairs(fake) == [["file_open","open_impl"]], "outside-array control")
    need(hook_pairs(fake.replace("file_open","inode_readlink")) != hook_pairs(fake),
         "changed registered-hook control")
    print(json.dumps({"status":"PASS_STATIC_SOURCE_AUDIT_ONLY",
        "optimized":bool(sys.flags.optimize), "manifest_files":len(rows),
        "retained_source_files":len(origins),"kernel_bodies":25,"apparmor_files":54,
        "apparmor_bytes":843856,"runtime_literal_rows":216,"header_rows":215,
        "separate_profile_preflight_files":217,"variant_role_occurrences":6,
        "channel_obligations_open":21,"pure_literal_controls":5,
        "complete_accepted_checkpoints":"0/4","full_C05":False,"full_V03":False,
        "outside_costs":"OPEN_NOT_ZERO","archived_code_executed":False},sort_keys=True))

if __name__ == "__main__":
    main()
