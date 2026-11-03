"""Exact-schema JSON batches and validated regular-file publication.

The unchanged writer is the fallback and independent oracle. No scientific
imports, process execution, compilation or work occurs at module import.
Only make_writer is the production entry point. _make_writer's fault parameter
exists for parent-owned finite controls, never for an admitted full caller.
"""
from __future__ import annotations

from contextlib import contextmanager
import _json
import hashlib
import json
import json.encoder
import os
from pathlib import Path
import stat
import tempfile
from types import CodeType, FunctionType


_WITNESS_KEYS = ("active", "args", "code", "kind", "labels", "pieces", "support")
_CODE_KEYS = ("gates", "outputs", "roles", "sources")
_FILES = ("result.json", "witness.json", "rank-trace.json")
_PATH_TYPE = type(Path("."))
_REJECTION = "Complete output, ordered witness, or rank trace changed from the frozen profile"
_UNSUPPORTED = object()


def _need(condition, message):
    if not condition:
        raise RuntimeError(message)


def _keys_are(mapping, keys):
    # Never hash or compare an unadmitted key (including a str subclass).
    return (type(mapping) is dict and
            all(type(key) is str for key in mapping) and
            len(mapping) == len(keys) and all(key in mapping for key in keys))


def _bound(value, limit, ancestors, depth=0):
    """Safe ASCII JSON upper bound; no user conversion/iteration/hash hooks."""
    kind = type(value)
    if kind is int:
        return int.bit_length(value) * 30103 // 100000 + 2
    if kind is str:
        return 12 * len(value) + 2
    if value is None:
        return 4
    if kind is bool:
        return 5
    if kind is float:
        return 32
    if kind not in (list, tuple, dict) or depth >= 32:
        return _UNSUPPORTED
    identity = id(value)
    if identity in ancestors:
        return _UNSUPPORTED
    ancestors.add(identity)
    try:
        size = 2
        if kind is dict:
            # Check before sorting/hashing/lookup; actual JSON sorts these keys.
            if any(type(key) is not str for key in value):
                return _UNSUPPORTED
            for key, item in dict.items(value):
                child = _bound(item, limit, ancestors, depth + 1)
                if child is _UNSUPPORTED:
                    return child
                size += 12 * len(key) + 2 + 2 + child
                if size > limit:
                    return size
        else:
            for item in value:
                child = _bound(item, limit, ancestors, depth + 1)
                if child is _UNSUPPORTED:
                    return child
                size += 1 + child
                if size > limit:
                    return size
        return size
    finally:
        ancestors.remove(identity)


def _array_admitted(value, limit):
    if type(value) not in (list, tuple):
        return False
    for item in value:
        size = _bound(item, limit, set())
        # Include batch brackets and a conservative comma allowance.
        if size is _UNSUPPORTED or size + 3 > limit:
            return False
    return True


def _admitted(result, witness, rank_calls, limit):
    result_bound = _bound(result, limit, set())
    if result_bound is _UNSUPPORTED or result_bound > limit:
        return False
    if not _keys_are(witness, _WITNESS_KEYS):
        return False
    code = witness["code"]
    if not _keys_are(code, _CODE_KEYS) or type(code["roles"]) is not int:
        return False
    if _bound(code["roles"], limit, set()) > limit:
        return False
    for key in _WITNESS_KEYS:
        if key != "code" and not _array_admitted(witness[key], limit):
            return False
    for key in _CODE_KEYS:
        if key != "roles" and not _array_admitted(code[key], limit):
            return False
    if type(rank_calls) is not list:
        return False
    for event in rank_calls:
        if (type(event) is not tuple or len(event) != 2 or
                type(event[0]) is not tuple or type(event[1]) is not int or
                any(type(row) is not int for row in event[0])):
            return False
    return _array_admitted(rank_calls, limit)


def _regular_destination(output):
    """Unsupported paths retain original behavior without candidate writes."""
    if type(output) is not _PATH_TYPE:
        return False
    try:
        if not stat.S_ISDIR(output.lstat().st_mode):
            return False
        for name in _FILES:
            try:
                mode = (output / name).lstat().st_mode
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(mode):
                return False
    except OSError:
        return False
    return True


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _freshness(reference_writer, reference_canonical, require):
    """Capture closure-free references and effective JSON globals/builtins.

    The source-reviewed originals have no closure/default state. JSON function
    dependencies include nested code objects (notably iterencode.floatstr).
    Each absent global is checked for new shadowing as well as builtin drift.
    """
    references = (reference_writer, reference_canonical, require)
    _need(all(type(function) is FunctionType and function.__closure__ is None and
              function.__defaults__ is None and function.__kwdefaults__ is None
              for function in references), "Unexpected serializer reference function shape")
    encoder = json.encoder
    bindings = (
        (json, "dumps", json.dumps),
        (json, "JSONEncoder", json.JSONEncoder),
        (json, "encoder", encoder),
        (encoder, "JSONEncoder", encoder.JSONEncoder),
        (encoder, "c_make_encoder", encoder.c_make_encoder),
        (encoder, "encode_basestring_ascii", encoder.encode_basestring_ascii),
        (_json, "make_encoder", _json.make_encoder),
        (_json, "encode_basestring_ascii", _json.encode_basestring_ascii),
        (hashlib, "sha256", hashlib.sha256),
        (json.JSONEncoder, "__init__", json.JSONEncoder.__init__),
        (json.JSONEncoder, "encode", json.JSONEncoder.encode),
        (json.JSONEncoder, "iterencode", json.JSONEncoder.iterencode),
        (json.JSONEncoder, "default", json.JSONEncoder.default),
    )
    _need(encoder.c_make_encoder is not None, "C JSON encoder unavailable")
    binding_maps = tuple((vars(owner), name, entry) for owner, name, entry in bindings)
    functions = []
    slots = []
    absent = object()
    for function in references + (json.dumps, json.JSONEncoder.__init__,
                                  json.JSONEncoder.encode, json.JSONEncoder.iterencode,
                                  json.JSONEncoder.default):
        _need(type(function) is FunctionType and function.__closure__ is None,
              "Unexpected JSON function shape")
        defaults = function.__defaults__
        keywords = function.__kwdefaults__
        _need(defaults is None or (type(defaults) is tuple and
              all(type(item) in (str, int, float, bool, type(None)) for item in defaults)),
              "Unsupported JSON default state")
        _need(keywords is None or (type(keywords) is dict and
              all(type(key) is str and type(value) in (str, int, float, bool, type(None))
                  for key, value in keywords.items())), "Unsupported JSON keyword state")
        keyword_items = None if keywords is None else tuple(keywords.items())
        namespace, effective_builtins = function.__globals__, function.__builtins__
        _need(type(namespace) is dict and type(effective_builtins) is dict,
              "Unexpected effective serializer namespace")
        functions.append((function, function.__code__, defaults, keywords,
                          keyword_items, namespace, effective_builtins))
        names = set()
        pending = [function.__code__]
        while pending:
            code = pending.pop()
            names.update(code.co_names)
            pending.extend(item for item in code.co_consts if type(item) is CodeType)
        for name in names:
            slots.append((namespace, name, dict.get(namespace, name, absent),
                          effective_builtins, dict.get(effective_builtins, name, absent)))
    encoder_class_map = vars(json.JSONEncoder)
    encoder_class_items = tuple(encoder_class_map.items())

    bound_len, bound_type, bound_all = len, type, all
    bound_get, bound_dict, bound_error = dict.get, dict, RuntimeError

    def check_need(condition, message):
        if not condition:
            raise bound_error(message)

    def check():
        for namespace, name, entry in binding_maps:
            check_need(namespace.get(name, absent) is entry, "JSON encoder binding changed: " + name)
        check_need(bound_len(encoder_class_map) == bound_len(encoder_class_items) and
              bound_all(encoder_class_map.get(name, absent) is entry
                  for name, entry in encoder_class_items), "JSON encoder class changed")
        for function, code, defaults, keywords, keyword_items, namespace, builtins in functions:
            check_need(function.__code__ is code and function.__defaults__ is defaults and
                  function.__kwdefaults__ is keywords and function.__closure__ is None and
                  function.__globals__ is namespace and function.__builtins__ is builtins,
                  "Serializer reference function changed")
            if keywords is not None:
                check_need(bound_type(keywords) is bound_dict and bound_len(keywords) == bound_len(keyword_items) and
                      bound_all(bound_type(key) is str for key in keywords) and
                      bound_all(bound_get(keywords, key, absent) is value for key, value in keyword_items),
                      "JSON keyword default changed")
        for namespace, name, entry, builtins, builtin_entry in slots:
            check_need(bound_get(namespace, name, absent) is entry and
                  bound_get(builtins, name, absent) is builtin_entry,
                  "Serializer effective global/builtin changed: " + name)
    return check, bindings


def make_writer(reference_write_scientific, reference_canonical, expected, require,
                *, batch_bytes=1048576, batch_rows=1024, copy_bytes=1048576):
    return _make_writer(reference_write_scientific, reference_canonical, expected, require,
                        batch_bytes=batch_bytes, batch_rows=batch_rows,
                        copy_bytes=copy_bytes)


def _make_writer(reference_write_scientific, reference_canonical, expected, require,
                 *, batch_bytes=1048576, batch_rows=1024, copy_bytes=1048576,
                 fault=None):
    """fault(event, info) -> NotImplemented or injected operation return.

    Private test seam: only parent finite controls pass fault. It can raise or
    replace an IO result. Production make_writer cannot receive this argument.
    """
    _need(type(batch_bytes) is int and 64 <= batch_bytes <= 1048576 and
          type(batch_rows) is int and 1 <= batch_rows <= 1024 and
          type(copy_bytes) is int and 1 <= copy_bytes <= 1048576,
          "Invalid bounded serializer limits")
    _need(type(expected) is dict and
          all(type(key) is str and type(value) in (str, int)
              for key, value in expected.items()), "Unexpected expected receipt")
    expected_copy = dict(expected)
    freshness, bindings = _freshness(reference_write_scientific, reference_canonical, require)
    canonical = reference_canonical

    def expected_unchanged():
        _need(type(expected) is dict and
              all(type(key) is str and type(value) in (str, int)
                  for key, value in expected.items()) and expected == expected_copy,
              "Expected serializer receipt changed")

    def operation(event, action, **information):
        if fault is not None:
            injected = fault(event, information)
            if injected is not NotImplemented:
                return injected
        return action()

    def full_write(stream, raw, phase, path):
        view = memoryview(raw)
        written = operation(phase + "_write", lambda: stream.write(view),
                            stream=stream, data=view, path=path)
        if type(written) is not int or written != len(view):
            raise OSError("Short " + phase + " write; no retry")

    def arrays(values, emit, info):
        emit(b"[")
        position = 0
        first = True
        while position < len(values):
            stop = position
            bound = 2
            while stop < len(values) and stop - position < batch_rows:
                item_bound = _bound(values[stop], batch_bytes, set())
                _need(item_bound is not _UNSUPPORTED and item_bound + 3 <= batch_bytes,
                      "Admitted serializer input changed")
                if stop > position and bound + item_bound + 1 > batch_bytes:
                    break
                bound += item_bound + 1
                stop += 1
            batch = values[position:stop]
            raw = canonical(batch)
            _need(len(raw) <= batch_bytes and raw[:1] == b"[" and raw[-1:] == b"]",
                  "Canonical batch violated bound or framing")
            info["batch_count"] += 1
            info["largest_batch_bytes"] = max(info["largest_batch_bytes"], len(raw))
            if not first:
                emit(b",")
            emit(memoryview(raw)[1:-1])
            first = False
            position = stop
        emit(b"]")

    def witness_bytes(witness, emit, info):
        emit(b"{")
        for index, key in enumerate(_WITNESS_KEYS):
            if index:
                emit(b",")
            emit(canonical(key))
            emit(b":")
            if key != "code":
                arrays(witness[key], emit, info)
                continue
            emit(b"{")
            for code_index, code_key in enumerate(_CODE_KEYS):
                if code_index:
                    emit(b",")
                emit(canonical(code_key))
                emit(b":")
                if code_key == "roles":
                    emit(canonical(witness["code"][code_key]))
                else:
                    arrays(witness["code"][code_key], emit, info)
            emit(b"}")
        emit(b"}")

    def writer(output, result, witness, rank_calls):
        freshness()
        expected_unchanged()
        if not _admitted(result, witness, rank_calls, batch_bytes) or not _regular_destination(output):
            writer.last_operation = {"status": "LITERAL_REFERENCE_FALLBACK"}
            answer = reference_write_scientific(output, result, witness, rank_calls)
            try:
                freshness()
                expected_unchanged()
            except BaseException:
                try:
                    writer.last_operation["status"] = "FALLBACK_EXIT_FRESHNESS_FAILED"
                except BaseException:
                    pass
                raise
            return answer
        info = {"status": "IN_PROGRESS", "phase": "stage_create", "stage": None,
                "batch_count": 0, "largest_batch_bytes": 0,
                "batch_bytes_limit": batch_bytes, "batch_rows_limit": batch_rows,
                "copy_bytes_limit": copy_bytes, "files": {}, "cleanup": []}
        writer.last_operation = info
        stage = None
        accepted = {}

        @contextmanager
        def managed(stream, phase, path):
            primary = None
            try:
                yield stream
            except BaseException as error:
                primary = error
                raise
            finally:
                try:
                    stream.close()
                    operation(phase + "_after_close", lambda: None, path=path)
                except BaseException as close_error:
                    if primary is None:
                        raise
                    try:
                        info.setdefault("close_errors", []).append({
                            "phase": phase, "type": type(close_error).__name__})
                    except BaseException:
                        pass
        try:
            stage = Path(operation("stage_create", lambda: tempfile.mkdtemp(
                prefix=".serialization-", dir=output), output=output))
            info["stage"] = str(stage)
            for name, value in zip(_FILES, (result, witness, rank_calls)):
                path = stage / name
                info["phase"] = "stage:" + name
                row = {"hashed_bytes": 0, "accepted_write_bytes": 0,
                       "copy_read_bytes": 0, "copy_write_bytes": 0}
                info["files"][name] = row
                hasher = hashlib.sha256()
                stream = operation("stage_open", lambda: path.open("xb"), path=path)
                with managed(stream, "stage", path):
                    def emit(raw):
                        operation("stage_hash", lambda: hasher.update(raw), path=path, data=raw)
                        row["hashed_bytes"] += len(raw)
                        full_write(stream, raw, "stage", path)
                        row["accepted_write_bytes"] += len(raw)
                    if name == "result.json":
                        emit(canonical(value))
                    elif name == "witness.json":
                        witness_bytes(value, emit, info)
                    else:
                        arrays(value, emit, info)
                    operation("stage_flush", stream.flush, path=path, stream=stream)
                    facts = os.fstat(stream.fileno())
                    _need(stat.S_ISREG(facts.st_mode) and
                          facts.st_size == row["accepted_write_bytes"],
                          "Staged artifact is not the complete regular file")
                    operation("stage_before_close", lambda: None, path=path, stream=stream)
                _need(_identity(path.lstat()) == _identity(facts), "Staged artifact identity changed")
                accepted[name] = (_identity(facts), hasher.hexdigest(), row["accepted_write_bytes"])
                row["sha256"] = accepted[name][1]
            receipt = {
                "result_sha256": accepted["result.json"][1],
                "exact_witness_sha256": accepted["witness.json"][1],
                "rank_trace_sha256": accepted["rank-trace.json"][1],
                "rank_call_count": len(rank_calls),
                "rank_distinct_matrix_count": len({rows for rows, _ in rank_calls}),
            }
            info["phase"] = "expected_receipt"
            require(receipt == expected_copy, _REJECTION)
            operation("after_acceptance", lambda: None, stage=stage, output=output)
            for name in _FILES:
                source, target = stage / name, output / name
                identity, expected_digest, expected_size = accepted[name]
                row = info["files"][name]
                info["phase"] = "copy:" + name
                _need(_identity(source.lstat()) == identity, "Staged artifact changed before copy")
                copied_hash = hashlib.sha256()
                incoming = operation("copy_open", lambda: source.open("rb"), path=source)
                with managed(incoming, "copy", source):
                    _need(_identity(os.fstat(incoming.fileno())) == identity and
                          _identity(source.lstat()) == identity, "Staged read identity changed")
                    outgoing = operation("final_open", lambda: target.open("wb"), path=target)
                    with managed(outgoing, "final", target):
                        _need(stat.S_ISREG(os.fstat(outgoing.fileno()).st_mode),
                              "Final serializer sink is not a regular file")
                        while True:
                            raw = operation("copy_read", lambda: incoming.read(copy_bytes),
                                            path=source, stream=incoming)
                            _need(type(raw) is bytes and len(raw) <= copy_bytes,
                                  "Invalid bounded staged read")
                            if not raw:
                                break
                            row["copy_read_bytes"] += len(raw)
                            _need(row["copy_read_bytes"] <= expected_size, "Staged artifact grew during copy")
                            operation("copy_hash", lambda: copied_hash.update(raw), path=source, data=raw)
                            full_write(outgoing, raw, "final", target)
                            row["copy_write_bytes"] += len(raw)
                        operation("final_flush", outgoing.flush, path=target, stream=outgoing)
                        _need(os.fstat(outgoing.fileno()).st_size == expected_size,
                              "Final artifact byte count changed")
                        operation("final_before_close", lambda: None, path=target, stream=outgoing)
                    _need(_identity(os.fstat(incoming.fileno())) == identity,
                          "Staged artifact changed during copy")
                _need(_identity(source.lstat()) == identity,
                      "Staged artifact path changed during copy")
                _need(row["copy_read_bytes"] == expected_size and
                      row["copy_write_bytes"] == expected_size and
                      copied_hash.hexdigest() == expected_digest,
                      "Staged copy digest or byte count changed")
                row["copy_sha256"] = copied_hash.hexdigest()
            info["phase"] = "precleanup_freshness"
            freshness()
            expected_unchanged()
            info["phase"] = "cleanup"
            for name in _FILES:
                path = stage / name
                operation("cleanup_unlink", path.unlink, path=path)
                info["cleanup"].append(name)
            operation("cleanup_rmdir", stage.rmdir, path=stage)
            info["cleanup"].append("stage_directory")
            receipt["serialized_bytes"] = {
                "result": accepted["result.json"][2],
                "witness": accepted["witness.json"][2],
                "rank_trace": accepted["rank-trace.json"][2],
            }
            info["phase"] = "exit_freshness"
            freshness()
            expected_unchanged()
            info["phase"] = "complete"
            info["status"] = "BOUNDED_SERIALIZATION_PASS"
            return receipt
        except BaseException as error:
            # Logging failures must never replace the primary exception.
            try:
                info["status"] = "FAILED_EVIDENCE_RETAINED"
                info["error"] = {"type": type(error).__name__, "message": str(error)[:2048]}
                if stage is not None:
                    for name, row in info["files"].items():
                        try:
                            row["retained_stage_stat_bytes"] = (stage / name).lstat().st_size
                        except OSError:
                            row["retained_stage_stat_bytes"] = None
                    raw = canonical(info)
                    _need(len(raw) <= 65536, "Serialization failure manifest exceeded bound")
                    operation("failure_manifest", lambda: (stage / "failure.json").write_bytes(raw), path=stage)
            except BaseException as secondary:
                try:
                    info["failure_manifest_error_type"] = type(secondary).__name__
                except BaseException:
                    pass
            raise

    writer.last_operation = None
    writer._h25_serialization_bindings = bindings
    writer._h25_serialization_faults_enabled = fault is not None
    return writer
