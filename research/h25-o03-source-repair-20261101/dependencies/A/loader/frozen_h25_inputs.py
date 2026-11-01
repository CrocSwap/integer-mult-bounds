"""Authentic retained-value H25 loader. Importing this module performs no I/O.

No scientific code is imported. Public loading always uses the fixed pins below;
private helpers are exposed only to the separately reviewed finite controls.
Custody establishes a fresh immutable replay, not historical allocation aliases.
"""
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import stat

CHUNK_BYTES = 1048576
INPUT_SPECS = {
    "baseline/evidence/canonical/witness.json.gz": {
        "encoding": "gzip", "transport_bytes": 16995263,
        "transport_sha256": "8e1b8b03320d5e077c0414c3644396faf182bdfa1a72d8067c8fea8a33dbf5d0",
        "logical_bytes": 58143622,
        "logical_sha256": "4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82"},
    "baseline/evidence/canonical/rank-trace.json.gz": {
        "encoding": "gzip", "transport_bytes": 22029,
        "transport_sha256": "20e76cd894807cf84ca740312fdc2a73d1d70740e2f0c5ec55b3d0afdd9311fa",
        "logical_bytes": 2674272,
        "logical_sha256": "85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f"},
    "baseline/evidence/canonical/complex-network.json": {
        "encoding": "plain", "transport_bytes": 5662,
        "transport_sha256": "1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f",
        "logical_bytes": 5662,
        "logical_sha256": "1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f"},
}
DIRECTORIES = ("baseline", "baseline/evidence", "baseline/evidence/canonical")
IDENTITY_FIELDS = ("dev", "ino", "mode", "uid", "gid", "nlink", "mtime_ns", "ctime_ns")
LOCAL_PATH_TYPE = type(Path())
RESULT_KEYS = ("circuit", "side_map", "labels", "role_frames")
WITNESS_KEYS = ("support", "args", "kind", "active", "pieces", "labels", "code")


class InputError(RuntimeError):
    """Schema, authentication or custody failure; never a saved PASS."""


def need(condition, message):
    if not condition:
        raise InputError(message)


def identity(info, file=False):
    out = {name: getattr(info, "st_" + name) for name in IDENTITY_FIELDS if name != "mode"}
    out["mode"] = stat.S_IMODE(info.st_mode)
    if file:
        out["size"] = info.st_size
    return out


def _exact_keys(value, names, where):
    need(type(value) is dict and set(value) == set(names), where + ": exact keys")
    return value


def _check_identity(info, expected, is_file, where):
    need(type(expected) is dict, where + ": identity object")
    _exact_keys(expected, IDENTITY_FIELDS + (("size", "sha256") if is_file else ()), where + " identity")
    actual = identity(info, is_file)
    for key, value in actual.items():
        need(type(expected.get(key)) is int and expected[key] == value, where + ": identity " + key)
    need(stat.S_ISREG(info.st_mode) if is_file else stat.S_ISDIR(info.st_mode), where + ": regular kind")
    need(actual["mode"] == (0o444 if is_file else 0o555), where + ": immutable mode")
    if is_file:
        need(actual["nlink"] == 1, where + ": unique link")


def check_custody(root, custody, specs=None):
    """Check fresh metadata every call. Hashing happens separately on held fds."""
    if specs is None:
        specs = INPUT_SPECS
    need(type(root) is LOCAL_PATH_TYPE, "root: exact local Path")
    need(root.is_absolute() and str(root.resolve(strict=True)) == str(root), "root: canonical absolute path")
    _exact_keys(custody, ("schema", "root", "root_identity", "directories", "files"), "custody")
    need(custody["schema"] == "h25-input-custody-v1" and custody["root"] == str(root), "custody: root binding")
    _check_identity(root.lstat(), custody["root_identity"], False, "root")
    _exact_keys(custody["directories"], DIRECTORIES, "custody directories")
    for relative in DIRECTORIES:
        _check_identity((root / relative).lstat(), custody["directories"][relative], False, relative)
    _exact_keys(custody["files"], specs, "custody files")
    unique = set()
    for relative, spec in specs.items():
        expected = custody["files"][relative]
        _check_identity((root / relative).lstat(), expected, True, relative)
        need(expected.get("size") == spec["transport_bytes"], relative + ": transport size")
        need(expected.get("sha256") == spec["transport_sha256"], relative + ": fixed transport pin")
        key = (expected["dev"], expected["ino"])
        need(key not in unique, relative + ": input alias")
        unique.add(key)


def _open_checked(root, relative, expected):
    fd = os.open(root / relative, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        _check_identity(os.fstat(fd), expected, True, relative)
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise


def _transport_hash(root, relative, spec, expected):
    digest = hashlib.sha256()
    count = 0
    with _open_checked(root, relative, expected) as source:
        while True:
            block = source.read(CHUNK_BYTES)
            if not block:
                break
            count += len(block)
            need(count <= spec["transport_bytes"], relative + ": transport size overrun")
            digest.update(block)
        _check_identity(os.fstat(source.fileno()), expected, True, relative)
    need(count == spec["transport_bytes"], relative + ": transport size mismatch")
    need(digest.hexdigest() == spec["transport_sha256"], relative + ": transport hash mismatch")


def _read_logical(root, relative, spec, expected):
    """Authenticate transport before decoding; cap logical allocation at size+1.

    gzip reads are bounded, including a one-byte overrun sentinel. The complete
    logical digest/final size are authenticated BEFORE any JSON parser is called.
    gzip errors retain their original exception, including invalid/truncated data.
    """
    _transport_hash(root, relative, spec, expected)
    logical = bytearray()
    digest = hashlib.sha256()
    with _open_checked(root, relative, expected) as source:
        reader = gzip.GzipFile(fileobj=source, mode="rb") if spec["encoding"] == "gzip" else source
        try:
            while True:
                block = reader.read(min(CHUNK_BYTES, spec["logical_bytes"] - len(logical) + 1))
                if not block:
                    break
                need(len(logical) + len(block) <= spec["logical_bytes"], relative + ": logical overrun")
                logical.extend(block)
                digest.update(block)
        finally:
            if reader is not source:
                reader.close()
        _check_identity(os.fstat(source.fileno()), expected, True, relative)
    need(len(logical) == spec["logical_bytes"], relative + ": logical size mismatch")
    need(digest.hexdigest() == spec["logical_sha256"], relative + ": logical hash mismatch")
    return logical


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "JSON: duplicate key " + key)
        out[key] = value
    return out


def _constant(value):
    raise InputError("JSON: nonfinite constant " + value)


def _float(value):
    number = float(value)
    need(math.isfinite(number), "JSON: nonfinite floating value")
    return number


def strict_json(data):
    # Default parse_int preserves Python arbitrary-width semantics AND its
    # unchanged configured decimal conversion ValueError. No limit adjustment.
    return json.loads(data, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)


def _int(value, where):
    need(type(value) is int, where + ": exact int")
    return value


def _list(value, where):
    need(type(value) is list, where + ": exact list")
    return value


def _arity(value, count, where):
    _list(value, where)
    need(len(value) == count, where + ": arity")
    return value


def _ints(value, where, count=None):
    _list(value, where)
    if count is not None:
        need(len(value) == count, where + ": arity")
    return tuple(_int(item, where) for item in value)


def restore_result(certificate):
    need(type(certificate) is dict and all(key in certificate for key in RESULT_KEYS), "certificate: projection keys")
    result = {}
    fields = {
        "circuit": (("h", "v", "additions", "injections", "roles", "disjoint_additions", "pair_star_additions"), (), (), ("roles_per_target",)),
        "side_map": (("targets", "nonzero_coefficients"), ("side_map_exact",), ("coefficients",), ()),
        "labels": (("active_nodes", "checked_inclusions"), ("all_labels_nondegenerate", "all_residuals_have_odd_vectors"), (), ()),
        "role_frames": (("roles",), ("forward_frames_nested", "reverse_complement_frames_nested"), (), ()),
    }
    for key in RESULT_KEYS:
        integers, bools, strings, floats = fields[key]
        value = _exact_keys(certificate[key], integers + bools + strings + floats, "result." + key)
        restored = {}
        for name in integers:
            restored[name] = _int(value[name], "result." + key + "." + name)
        for name in bools:
            need(type(value[name]) is bool, "result." + key + "." + name + ": bool")
            restored[name] = value[name]
        for name in strings:
            need(type(value[name]) is str, "result." + key + "." + name + ": str")
            restored[name] = value[name]
        for name in floats:
            need(type(value[name]) is float and math.isfinite(value[name]), "result." + key + "." + name + ": finite float")
            restored[name] = value[name]
        result[key] = restored
    return result


def restore_witness(value):
    _exact_keys(value, WITNESS_KEYS, "witness")
    support = list(_ints(value["support"], "support"))
    args = [None if item is None else _ints(item, "args", 2) for item in _list(value["args"], "args")]
    kinds = []
    for item in _list(value["kind"], "kind"):
        need(item is None or type(item) is str, "kind: None or str")
        kinds.append(item)
    need(len(support) == len(args) == len(kinds), "witness: aligned node lists")
    active = list(_ints(value["active"], "active"))
    pieces = []
    for item in _list(value["pieces"], "pieces"):
        target, node, coefficient = _arity(item, 3, "piece")
        pieces.append((_ints(target, "piece target", 3), _int(node, "piece node"), _ints(coefficient, "coefficient", 2)))
    labels = []
    for item in _list(value["labels"], "labels"):
        key, basis, dim, label_key = _arity(item, 4, "label")
        if type(key) is not int:
            tag, triple = _arity(key, 2, "label tagged key")
            need(type(tag) is str and tag == "perp", "label: literal perp tag")
            key = (tag, _ints(triple, "label target", 3))
        labels.append((key, [_ints(pair, "basis pair", 2) for pair in _list(basis, "basis")], _int(dim, "label dim"), _ints(label_key, "label key")))
    code = _exact_keys(value["code"], ("roles", "gates", "sources", "outputs"), "code")
    gates = []
    for item in _list(code["gates"], "gates"):
        node, inputs, outputs = _arity(item, 3, "gate")
        gates.append((_int(node, "gate node"), _ints(inputs, "gate inputs"), _ints(outputs, "gate outputs")))
    sources = []
    for item in _list(code["sources"], "sources"):
        triple, slot = _arity(item, 2, "source")
        sources.append((_ints(triple, "source triple", 3), _int(slot, "source slot")))
    outputs = [_ints(item, "output", 2) for item in _list(code["outputs"], "outputs")]
    return {"support": support, "args": args, "kind": kinds, "active": active,
            "pieces": pieces, "labels": labels,
            "code": {"roles": _int(code["roles"], "code.roles"), "gates": gates, "sources": sources, "outputs": outputs}}


def restore_ranks(value, expected_count=59959, expected_distinct=252):
    ranks = []
    for event in _list(value, "ranks"):
        rows, rank = _arity(event, 2, "rank event")
        ranks.append((_ints(rows, "rank rows"), _int(rank, "rank result")))
    need(len(ranks) == expected_count, "rank: full event count")
    need(len({rows for rows, _ in ranks}) == expected_distinct, "rank: distinct row count")
    return ranks


def _load(root, custody, specs, expected_count, expected_distinct):
    check_custody(root, custody, specs)
    values = []
    receipt = {}
    # Fixed order witness,rank,certificate. Logical buffers die after each parse;
    # decoded and restored containers overlap during each restoration, billed.
    for relative, spec in specs.items():
        data = _read_logical(root, relative, spec, custody["files"][relative])
        parsed = strict_json(data)
        del data
        if relative.endswith("witness.json.gz"):
            restored = restore_witness(parsed)
        elif relative.endswith("rank-trace.json.gz"):
            restored = restore_ranks(parsed, expected_count, expected_distinct)
        else:
            restored = restore_result(parsed)
        values.append(restored)
        del parsed, restored
        receipt[relative] = dict(spec)
    # Rehash all original transports; metadata alone never supplies cached PASS.
    check_custody(root, custody, specs)
    for relative, spec in specs.items():
        _transport_hash(root, relative, spec, custody["files"][relative])
    check_custody(root, custody, specs)
    witness, ranks, result = values
    return {"result": result, "witness": witness, "ranks": ranks,
            "input_receipt": {"schema": "h25-fresh-input-receipt-v1", "scope": "authentic retained values; historical aliases not recovered", "files": receipt,
                              "rank_call_count": len(ranks), "rank_distinct_matrix_count": len({rows for rows, _ in ranks}),
                              "custody_before_after": "MATCH", "cached_pass": False}}


def load_frozen_inputs(input_root, custody):
    """Load complete authentic data; caller cannot replace fixed pins or counts."""
    return _load(input_root, custody, INPUT_SPECS, 59959, 252)


def authenticate_inputs(input_root, custody):
    """Fresh complete transport-only readback, including both metadata edges.

    This never supplies schema/logical PASS or skips work on a later load. It
    supports the consumer's after-writer custody edge without reloading values.
    """
    check_custody(input_root, custody)
    for relative, spec in INPUT_SPECS.items():
        _transport_hash(input_root, relative, spec, custody["files"][relative])
    check_custody(input_root, custody)
    return {"schema": "h25-input-authentication-v1", "files": {p: dict(s) for p, s in INPUT_SPECS.items()},
            "custody_before_after": "MATCH", "cached_pass": False, "logical_validation": "NOT_PERFORMED_IN_TRANSPORT_READBACK"}
