#!/usr/bin/env python3
"""Machine check for the hosted-template post-emit field read-set claim.

Scope (agent-45, card uniform-transfer-audit, refined): the frozen PR1087 hosted
template carries 15 fields that the acceptance audit `audit_allcold.py` never
reads.  `research/t16-audit-mutant-coverage` (PR1959) asserts by text search
that no stage after `emit_allcold.py` reads any of them either, and labels that
"a text search, not a proof".  This script replaces the text search with a
pinned, machine-derived inventory:

  S1  no semantic read/test of any of the 15 field names anywhere in the
      post-emit consumer closure (constant-string subscripts, attributes,
      get/pop/setdefault/getattr arguments, membership or comparison tests).
      The only tolerated occurrences are output-receipt construction keys
      (dict()/dict-literal keys), which write other dicts, not the template;
  S2  the complete name-directed occurrence inventory of those 15 names over the
      whole pinned universe equals EXPECTED.json exactly (drift detection);
  S3  the dynamic-access and whole-object-channel inventory of the template
      variables in the post-emit closure equals EXPECTED.json exactly, and no
      entry is a top-level dynamic read of the template (no `t[k]`, no bare
      iteration/serialization/hash of the template object itself);
  S4  the detector self-test (corruption control): injected name-directed and
      dynamic probes are all detected.

Universe (pinned by SHA-256 in EXPECTED.json):
  A. every ``*.py`` member of research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz
  B. scripts/verify_frontier1094.py,
     research/community-batch1099-audit/check_frontier1094.py,
     research/complex-t16-rare-pattern-exchanges/verify.py

This is a static source audit of pinned bytes.  It does not replay the selected
chain, does not prove semantic non-interference beyond the recorded site
inventory, and does not cover the external `engines/*.py` moment modules that
`assemble.py` loads from its own package directory.
"""
import ast
import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]

ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
MAIN_FILES = [
    "scripts/verify_frontier1094.py",
    "research/community-batch1099-audit/check_frontier1094.py",
    "research/complex-t16-rare-pattern-exchanges/verify.py",
    # import closure of check_frontier1094.py: it loads these in-process and
    # passes a template object to them (the ROUND20 parent template, a pre-emit
    # artifact -- see README).
    "research/t16-owner-audit-seed67/verify.py",
    "research/pending-claims-independent-pricing/sweep.py",
]

# The 15 hosted-template fields the PR1087 audit() never reads (PR1959).
FIELDS = [
    "cover", "m", "version", "port_restriction", "provider_dispatch",
    "replica_lift", "route_semantics", "supplier_substitution",
    "expanded_scalar_interface",
    "rule", "scope", "idle_remainder_semantics", "owner_map_sha256",
    "source_plan_sha256",
]
FIELD_PATHS = {
    "cover": "cover", "m": "m", "version": "version",
    "port_restriction": "port_restriction", "provider_dispatch": "provider_dispatch",
    "replica_lift": "replica_lift", "route_semantics": "route_semantics",
    "supplier_substitution": "supplier_substitution",
    "expanded_scalar_interface": "expanded_scalar_interface",
    "rule": "hosting.rule", "scope": "hosting.scope",
    "idle_remainder_semantics": "hosting.idle_remainder_semantics",
    "owner_map_sha256": "hosting.owner_map_sha256",
    "source_plan_sha256": "async_schedule.source_plan_sha256",
}

# Stage roles from the pinned evidence/STAGES.json order
# (restore-parent, bind, emit, audit, invoice, assembly, admission-controls)
# and the PR1087 code layout.  The post-emit consumer closure is audit, invoice,
# assembly, admission-controls plus the modules the audit imports in-process.
POST_EMIT_CLOSURE = [
    "code/audit_allcold.py",
    "code/invoice_allcold.py",
    "code/assemble.py",
    "code/assembly_controls.py",
    "code/bit_supplier_controls.py",
    "code/witness.py",
    "code/generated_identity.py",
]

# Variables bound to the loaded hosted template (or a mutated copy of it) in the
# post-emit closure; declared here because pure syntax cannot bind receivers.
TEMPLATE_VARS = {
    "code/audit_allcold.py": ["ct", "t", "q"],
    "code/invoice_allcold.py": ["template"],
    "code/assemble.py": [],
    "code/assembly_controls.py": [],
    "code/bit_supplier_controls.py": [],
    "code/witness.py": [],
    "code/generated_identity.py": [],
}

HASH_CALLS = {"sha256", "sha1", "md5", "sha512", "blake2b"}
HASH_HELPERS = {"sha", "filehash", "contenthash", "digest", "programhash", "payload_identity", "json_identity"}

# Pinned whole-object file-binding channels: the exact statements through which a
# change to any hosted-template field (read or unread) still reaches post-emit
# acceptance.  Asserted present verbatim so the README's channel map stays
# checkable at a glance; the files themselves are SHA-256 pinned above.
CHANNEL_PINS = [
    ("archive:code/audit_allcold.py",
     "assert hashlib.sha256(raw).hexdigest()==summary['template_sha256']"),
    ("archive:code/invoice_allcold.py",
     "assert template_hash==control['complex_template_sha256']==owners['template_sha256']==summary['template_sha256']"),
    ("archive:code/invoice_allcold.py",
     "template_hash=contenthash(template_path)"),
]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_universe():
    """Return {label: (text, sha256)} for every pinned source file."""
    out = {}
    ap = ROOT / ARCHIVE
    with tarfile.open(ap, "r:gz") as tf:
        for m in sorted(tf.getmembers(), key=lambda x: x.name):
            if not m.name.endswith(".py"):
                continue
            raw = tf.extractfile(m).read()
            out["archive:" + m.name] = (raw.decode("utf-8", "replace"), sha256_bytes(raw))
    for rel in MAIN_FILES:
        raw = (ROOT / rel).read_bytes()
        out["main:" + rel] = (raw.decode("utf-8", "replace"), sha256_bytes(raw))
    return out


def const_context(parent_stack, node):
    """Classify how a constant string is used: (context, access).

    access is "read" (the field name is looked up), "write" (subscript store),
    "construct" (dict literal key / dict() keyword: building some dict), "test"
    (membership or comparison), or "opaque" (string passed to an unclassified call).
    """
    if not parent_stack:
        return "string-expr", "opaque"
    par = parent_stack[-1]
    if isinstance(par, ast.Subscript):
        target = par.slice
        if isinstance(target, ast.Constant) and target.value == node.value:
            if isinstance(par.ctx, ast.Load):
                return "subscript-key", "read"
            return "subscript-key", "write"
        return "string-expr", "opaque"
    if isinstance(par, ast.Dict):
        for k in par.keys:
            if k is node:
                return "dict-literal-key", "construct"
        return "dict-literal-value", "opaque"
    if isinstance(par, ast.keyword):
        return "keyword-value", "opaque"
    if isinstance(par, ast.Call):
        fn = ""
        if isinstance(par.func, ast.Attribute):
            fn = par.func.attr
        elif isinstance(par.func, ast.Name):
            fn = par.func.id
        access = "opaque"
        if fn in ("get", "pop", "setdefault", "getattr", "hasattr"):
            access = "read"
        elif fn in ("__setitem__", "setattr", "setdefault"):
            access = "write"
        return "call-arg:" + fn, access
    if isinstance(par, ast.Compare):
        return "membership-or-compare", "test"
    if isinstance(par, (ast.JoinedStr, ast.FormattedValue)):
        return "fstring-part", "opaque"
    return "type:" + type(par).__name__, "opaque"


def walk_with_parents(tree):
    """Yield (node, parent_stack) for every node."""
    stack = []

    def visit(node):
        stack.append(node)
        yield node, list(stack[:-1])
        for child in ast.iter_child_nodes(node):
            yield from visit(child)
        stack.pop()

    yield from visit(tree)


def static_path(expr, roots):
    """Resolve a chain of constant subscripts/attributes on a root variable.

    Returns ("top", root) for a bare root, ("path", root, "a.b") for a named
    subfield, or None when the expression is unrelated to any root.
    """
    parts = []
    cur = expr
    while True:
        if isinstance(cur, ast.Subscript) and isinstance(cur.slice, ast.Constant) and isinstance(cur.slice.value, str):
            parts.append(cur.slice.value)
            cur = cur.value
            continue
        if isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
            continue
        break
    if isinstance(cur, ast.Name) and cur.id in roots:
        if not parts:
            return ("top", cur.id)
        return ("path", cur.id, ".".join(reversed(parts)))
    return None


def name_sites(text):
    """All name-directed occurrences of the 15 field names (S1/S2)."""
    tree = ast.parse(text)
    sites = []
    for node, parents in walk_with_parents(tree):
        name = None
        ctx = None
        access = None
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in FIELDS:
            name = node.value
            ctx, access = const_context(parents, node)
        elif isinstance(node, ast.Attribute) and node.attr in FIELDS:
            name = node.attr
            ctx = "attribute"
            access = "read" if isinstance(node.ctx, ast.Load) else "write"
        elif isinstance(node, ast.keyword) and node.arg in FIELDS:
            name, ctx, access = node.arg, "dict-or-call-keyword", "construct"
        if name is not None:
            line = text.splitlines()[node.lineno - 1].strip()
            sites.append({
                "line": node.lineno, "name": name, "field": FIELD_PATHS[name],
                "context": ctx, "access": access, "code": line[:160],
            })
    sites.sort(key=lambda s: (s["line"], s["name"], s["context"]))
    return sites


def const_key_bindings(tree):
    """Map variable names bound to constant string collections (for-loops and
    assignments), so bounded dynamic subscripts can be resolved to finite key sets."""
    binds = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            vals = const_str_set(node.iter)
            if vals is not None:
                binds.setdefault(node.target.id, set()).update(vals)
        if isinstance(node, ast.Assign):
            vals = const_str_set(node.value)
            if vals is not None:
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        binds.setdefault(tgt.id, set()).update(vals)
    return binds


def const_str_set(expr):
    if isinstance(expr, (ast.Tuple, ast.List, ast.Set)):
        vals = []
        for el in expr.elts:
            if isinstance(el, ast.Constant) and isinstance(el.value, str):
                vals.append(el.value)
            else:
                return None
        return vals
    return None


def dynamic_sites(text, roots):
    """Dynamic accesses and whole-object channels on template variables (S3)."""
    if not roots:
        return []
    tree = ast.parse(text)
    keybinds = const_key_bindings(tree)

    def resolve_keys(expr):
        """Finite key set for a dynamic subscript slice, or None."""
        if isinstance(expr, ast.Name) and expr.id in keybinds:
            return sorted(keybinds[expr.id])
        return None

    out = []
    lines = text.splitlines()
    for node, parents in walk_with_parents(tree):
        kind = None
        detail = ""
        keys = None
        if isinstance(node, ast.Subscript):
            sp = static_path(node.value, set(roots))
            if sp is not None and not (isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)):
                top = sp[0] == "top"
                keys = resolve_keys(node.slice)
                if keys is not None:
                    kind = "subscript-bounded-top" if top else "subscript-bounded-path"
                    detail = sp[1] + ("" if top else "." + sp[2]) + " keys=" + ",".join(keys)
                else:
                    kind = "subscript-dynamic-top" if top else "subscript-dynamic-path"
                    detail = sp[1] + ("" if top else "." + sp[2])
        elif isinstance(node, (ast.For, ast.comprehension)):
            sp = static_path(node.iter, set(roots))
            if sp is not None:
                top = sp[0] == "top"
                kind = "iter-top" if top else "iter-path"
                detail = sp[1] + ("" if top else "." + sp[2])
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if k is None:
                    sp = static_path(v, set(roots))
                    if sp is not None:
                        kind = "dict-unpack"
                        detail = sp[1]
        elif isinstance(node, ast.Call):
            fn = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else "")
            for arg in list(node.args) + [k.value for k in node.keywords]:
                sp = static_path(arg, set(roots))
                if sp is None:
                    continue
                if fn in HASH_CALLS or fn in HASH_HELPERS:
                    kind = "hash-of-arg"
                elif fn in ("dumps", "dump", "loads", "load"):
                    kind = "json-of-arg"
                elif fn in ("deepcopy", "copy"):
                    kind = "deepcopy-of-arg"
                elif fn == "sorted":
                    kind = "sorted-of-arg"
                elif fn in ("str", "repr", "len", "list", "tuple", "set", "dict"):
                    kind = "convert-of-arg"
                if kind:
                    detail = sp[1] + ("" if sp[0] == "top" else "." + sp[2])
        elif isinstance(node, ast.Compare):
            for operand in [node.left] + list(node.comparators):
                sp = static_path(operand, set(roots))
                if sp is not None:
                    kind = "compare-operand"
                    detail = sp[1] + ("" if sp[0] == "top" else "." + sp[2])
        if kind:
            lineno = getattr(node, "lineno", None)
            if lineno is None and hasattr(node, "iter"):
                lineno = node.iter.lineno
            out.append({
                "line": lineno, "kind": kind, "on": detail,
                "keys": sorted(keys) if kind.startswith("subscript-bounded") else None,
                "code": lines[lineno - 1].strip()[:160],
            })
    out.sort(key=lambda s: (s["line"], s["kind"], s["on"]))
    return out


def build_inventory():
    universe = load_universe()
    inv = {
        "universe_sha256": {label: digest for label, (_, digest) in sorted(universe.items())},
        "archive_sha256": sha256_bytes((ROOT / ARCHIVE).read_bytes()),
        "channel_pins": [list(p) for p in CHANNEL_PINS],
        "post_emit_closure": {rel: universe["archive:" + rel][1] for rel in POST_EMIT_CLOSURE},
        "template_vars": TEMPLATE_VARS,
        "post_emit_name_sites": {},
        "universe_name_sites": {},
        "post_emit_dynamic_sites": {},
    }
    for label, needle in CHANNEL_PINS:
        if needle not in universe[label][0]:
            raise AssertionError("channel pin missing from " + label + ": " + needle)
    for label, (text, _) in sorted(universe.items()):
        sites = name_sites(text)
        if sites:
            inv["universe_name_sites"][label] = sites
    for rel in POST_EMIT_CLOSURE:
        text = universe["archive:" + rel][0]
        inv["post_emit_name_sites"][rel] = name_sites(text)
        inv["post_emit_dynamic_sites"][rel] = dynamic_sites(text, TEMPLATE_VARS[rel])
    return inv


def detector_self_test():
    """S4: every probe form must be detected (corruption control)."""
    probes = {
        "probe_subscript": ("def f(ct):\n    return ct['cover']\n", "name", "subscript-key", "read"),
        "probe_attribute": ("def f(t):\n    return t.owner_map_sha256\n", "name", "attribute", "read"),
        "probe_keyword": ("def f():\n    return dict(rule='x')\n", "name", "dict-or-call-keyword", "construct"),
        "probe_dict_key": ("def f():\n    return {'version': 1}\n", "name", "dict-literal-key", "construct"),
        "probe_get": ("def f(t):\n    return t.get('replica_lift')\n", "name", "call-arg:get", "read"),
        "probe_write": ("def f(t):\n    t['cover'] = 1\n", "name", "subscript-key", "write"),
        "probe_compare": ("def f(t):\n    return 'port_restriction' in t\n", "name", "membership-or-compare", "test"),
        "probe_dyn_top": ("def f(t, k):\n    return t[k]\n", "dyn", "subscript-dynamic-top", None),
        "probe_bounded_top": ("def f(t):\n    for k in ('a', 'b'):\n        assert t[k] == 1\n", "dyn", "subscript-bounded-top", None),
        "probe_iter_top": ("def f(t):\n    return [x for x in t]\n", "dyn", "iter-top", None),
        "probe_hash_top": ("def f(t):\n    return sha256(t)\n", "dyn", "hash-of-arg", None),
    }
    bad = []
    for label, (src, mode, want, want_access) in probes.items():
        if mode == "name":
            sites = name_sites(src)
            got = [(s["context"], s["access"]) for s in sites]
            if (want, want_access) not in got:
                bad.append((label, (want, want_access), got))
        else:
            got = [s["kind"] for s in dynamic_sites(src, ["t", "ct"])]
            if want not in got:
                bad.append((label, want, got))
    return bad


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    bad = detector_self_test()
    if bad:
        for label, want, got in bad:
            print("SELF-TEST MISS", label, "want", want, "got", got)
        print("FAIL_POSTEMIT_FIELD_READSET_SELFTEST")
        raise SystemExit(1)
    inv = build_inventory()
    expected_path = PKG / "EXPECTED.json"
    if "--write" in sys.argv:
        expected_path.write_text(json.dumps(inv, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("WROTE", expected_path)
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    if inv != expected:
        for section in sorted(set(inv) | set(expected)):
            if inv.get(section) != expected.get(section):
                print("MISMATCH section:", section)
        print("FAIL_POSTEMIT_FIELD_READSET_MISMATCH")
        raise SystemExit(1)
    # S1: no semantic read/test of any of the 15 names in the post-emit closure.
    # The only tolerated occurrences are output-receipt construction keys
    # (access == "construct"); every other access class fails the claim.
    for rel, sites in inv["post_emit_name_sites"].items():
        for s in sites:
            if s["access"] != "construct":
                print("POST-EMIT NAME SITE", rel, s["line"], s["name"], s["context"], s["access"], s["code"])
                print("FAIL_POSTEMIT_FIELD_READSET_NAMES")
                raise SystemExit(1)
    # S3: no unbounded top-level dynamic read/iteration/hash of the template
    # object itself, and no bounded dynamic key set touching the 15 fields.
    for rel, sites in inv["post_emit_dynamic_sites"].items():
        for s in sites:
            if s["kind"] in ("subscript-dynamic-top", "iter-top", "hash-of-arg") and "." not in s["on"]:
                print("TOP-LEVEL DYNAMIC CHANNEL", rel, s["line"], s["kind"], s["on"], s["code"])
                print("FAIL_POSTEMIT_FIELD_READSET_DYNAMIC")
                raise SystemExit(1)
            if s["keys"] and set(s["keys"]) & set(FIELDS):
                print("BOUNDED KEYS HIT FIELD", rel, s["line"], s["keys"], s["code"])
                print("FAIL_POSTEMIT_FIELD_READSET_DYNAMIC")
                raise SystemExit(1)
    n_universe = sum(len(v) for v in inv["universe_name_sites"].values())
    n_dyn = sum(len(v) for v in inv["post_emit_dynamic_sites"].values())
    print("universe files:", len(inv["universe_sha256"]))
    print("universe name-directed sites (all classified and pinned):", n_universe)
    print("post-emit name-directed sites:", sum(len(v) for v in inv["post_emit_name_sites"].values()))
    print("post-emit dynamic/whole-object sites (pinned):", n_dyn)
    print("PASS_POSTEMIT_FIELD_READSET")


if __name__ == "__main__":
    main()
