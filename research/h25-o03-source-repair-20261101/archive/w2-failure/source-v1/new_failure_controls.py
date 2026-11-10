"""Proposed deterministic W2 controls. SOURCE ONLY; never run in this round.

No target import and no automatic entry point. A future separately admitted
normal/-O operation supplies authenticated candidate and reference modules.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType

TARGET_SHA256 = "fdeeb791c6cb0c03a5ab15903d51c3eb4cc5ff2a945c50d7f550acfe11376f3d"
PRIMARY_STATUS_LINE = 490
NAMES = ("result.json", "witness.json", "rank-trace.json")
LITERAL_BYTES = (
    b'{"ok":true}',
    b'{"active":[],"args":[],"code":{"gates":[],"outputs":[],"roles":0,"sources":[]},"kind":[],"labels":[],"pieces":[],"support":[]}',
    b'[]',
)
ORDER = (
    "F01-primary-close-append-bookkeeping", "F02-primary-manifest-type-bookkeeping",
    "F03-copy-complete-partial-cleanup", "F04-exit-freshness-after-cleanup",
    "F05-primary-status-bookkeeping", "F06-fallback-exit-status-bookkeeping",
    "F07-primary-stringification-bookkeeping", "F08-nested-close-bookkeeping",
    "F09-close-without-primary", "F10-preacceptance-rejection",
    "F11-partial-copy-and-manifest-failure", "F12-rmdir-failure-after-unlinks",
    "F13-close-type-bookkeeping", "F14-tiny-success",
)
PREVIOUS = b"previous final bytes"


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def fixture():
    return ({"ok": True}, {"active": [], "args": [], "code": {"gates": [],
            "outputs": [], "roles": 0, "sources": []}, "kind": [], "labels": [],
            "pieces": [], "support": []}, [])


def literal_expected():
    return {"result_sha256": hashlib.sha256(LITERAL_BYTES[0]).hexdigest(),
            "exact_witness_sha256": hashlib.sha256(LITERAL_BYTES[1]).hexdigest(),
            "rank_trace_sha256": hashlib.sha256(LITERAL_BYTES[2]).hexdigest(),
            "rank_call_count": 0, "rank_distinct_matrix_count": 0}


def bounded_read(path, cap=65536):
    with path.open("rb") as stream:
        raw = stream.read(cap + 1)
    need(len(raw) <= cap, "Control artifact exceeded cap")
    return raw


class PrimaryFault(BaseException):
    pass


class CloseFault(BaseException):
    pass


class BookkeepingFault(BaseException):
    pass


class ManifestFault(BaseException):
    pass


def throw(error, observed, key):
    try:
        raise error
    except BaseException:
        observed[key] = sys.exc_info()[2]
        raise


def contains_tail(error, tail):
    current = error.__traceback__
    while current is not None:
        if current is tail:
            return True
        current = current.tb_next
    return False


def run_controls(candidate, comparison, output_root):
    """Requires a fresh external root and a distinct future control admission.

    The F05 trace hook is control-only and source-hash/line-bound. It injects
    a small explicit exception at the status assignment, never exhaustion.
    """
    need(hashlib.sha256(bounded_read(Path(candidate.__file__))).hexdigest() ==
         TARGET_SHA256, "Wrong W2 target source")
    need(sys.gettrace() is None, "F05 requires a separately admitted unused trace hook")
    root = Path(output_root)
    need(not root.exists(), "Refusing existing W2 control evidence")
    root.mkdir(parents=True)
    reference_expected_before = dict(comparison.EXPECTED)
    original_code = comparison.write_scientific.__code__
    rows = []
    for index, name in enumerate(ORDER, 1):
        output = root / name
        output.mkdir()
        observed = {}
        expected = literal_expected()
        if index == 10:
            expected["rank_call_count"] = 1
        namespace = dict(comparison.write_scientific.__globals__)
        namespace["EXPECTED"] = expected
        original = FunctionType(original_code, namespace, comparison.write_scientific.__name__)
        primary = PrimaryFault("W2 primary")
        close = CloseFault("W2 close")
        bookkeeping = BookkeepingFault("W2 diagnostic")
        manifest = ManifestFault("W2 manifest")
        if index == 7:
            class UnstringifiablePrimary(PrimaryFault):
                def __str__(self):
                    throw(bookkeeping, observed, "bookkeeping_tb")
            primary = UnstringifiablePrimary()
        class RejectAppend(list):
            def append(self, value):
                throw(bookkeeping, observed, "bookkeeping_tb")
        class NameFailureMeta(type):
            def __getattribute__(cls, attribute):
                if attribute == "__name__":
                    throw(bookkeeping, observed, "bookkeeping_tb")
                return super().__getattribute__(attribute)
        class NameFailure(BaseException, metaclass=NameFailureMeta):
            pass
        bad_name = NameFailure("W2 secondary with inaccessible type name")
        holder = {}

        def capture_natural_primary():
            error = sys.exc_info()[1]
            need(error is not None, "No active primary at failure manifest")
            observed["natural_primary"] = error
            observed["natural_primary_tb"] = error.__traceback__

        def fault(event, information):
            path = information.get("path")
            basename = None if path is None else path.name
            if event == "stage_write" and index in (1, 2, 5, 7, 13):
                if index in (1, 13):
                    holder["writer"].last_operation["close_errors"] = RejectAppend()
                throw(primary, observed, "primary_tb")
            if event == "stage_after_close" and index in (1, 9, 13):
                throw(bad_name if index == 13 else close, observed, "close_tb")
            if event == "copy_read" and index == 8:
                holder["writer"].last_operation["close_errors"] = RejectAppend()
                throw(primary, observed, "primary_tb")
            if event in ("final_after_close", "copy_after_close") and index == 8:
                throw(close, observed, "close_tb")
            if event == "cleanup_unlink" and basename == "witness.json" and index == 3:
                throw(primary, observed, "primary_tb")
            if event == "cleanup_rmdir" and index == 4:
                path.rmdir()
                expected["rank_call_count"] = 1
                return None
            if event == "cleanup_rmdir" and index == 12:
                throw(primary, observed, "primary_tb")
            if event == "final_write" and basename == "witness.json" and index == 11:
                information["stream"].write(information["data"][:1])
                throw(primary, observed, "primary_tb")
            if event == "failure_manifest":
                if index in (4, 10):
                    capture_natural_primary()
                if index == 2:
                    throw(bad_name, observed, "manifest_tb")
                if index == 11:
                    throw(manifest, observed, "manifest_tb")
            return NotImplemented

        writer = candidate._make_writer(original, comparison.canonical, expected,
                    comparison.require, copy_bytes=17, fault=fault)
        holder["writer"] = writer
        values = fixture()
        saved_default = json.JSONEncoder.default
        if index in (10, 11):
            for filename in NAMES:
                (output / filename).write_bytes(PREVIOUS)
        if index == 6:
            class RejectStatus(dict):
                def __setitem__(self, key, value):
                    if key == "status":
                        error = sys.exc_info()[1]
                        need(error is not None, "No fallback primary")
                        observed["natural_primary"] = error
                        observed["natural_primary_tb"] = error.__traceback__
                        throw(bookkeeping, observed, "bookkeeping_tb")
                    return super().__setitem__(key, value)
            class MutatingResult(dict):
                def items(self):
                    observed["fallback_mutated"] = True
                    writer.last_operation = RejectStatus(status="LITERAL_REFERENCE_FALLBACK")
                    json.JSONEncoder.default = lambda self, item: "unused"
                    return super().items()
            values = (MutatingResult(values[0]), values[1], values[2])

        def trace(frame, event, argument):
            if (index == 5 and event == "line" and frame.f_code is writer.__code__ and
                    frame.f_lineno == PRIMARY_STATUS_LINE):
                observed["status_hook_fired"] = True
                throw(bookkeeping, observed, "bookkeeping_tb")
            return trace

        got = None
        receipt = None
        try:
            if index == 5:
                sys.settrace(trace)
            try:
                receipt = writer(output, *values)
            except BaseException as error:
                got = error
        finally:
            if index == 5:
                sys.settrace(None)
            json.JSONEncoder.default = saved_default
        info = writer.last_operation
        if index == 14:
            need(got is None and info["status"] == "BOUNDED_SERIALIZATION_PASS" and
                 info["phase"] == "complete", "Tiny success differs")
            need(receipt == dict(literal_expected(), serialized_bytes={
                 "result": len(LITERAL_BYTES[0]), "witness": len(LITERAL_BYTES[1]),
                 "rank_trace": len(LITERAL_BYTES[2])}), "Tiny receipt differs")
        else:
            need(got is not None and receipt is None, "Failure returned success")
            if index in (4, 6, 10):
                authoritative = observed.get("natural_primary")
                tail = observed.get("natural_primary_tb")
                need(type(got) is RuntimeError, "Natural primary class differs")
            elif index == 9:
                authoritative, tail = close, observed.get("close_tb")
            else:
                authoritative, tail = primary, observed.get("primary_tb")
            need(got is authoritative and tail is not None and contains_tail(got, tail),
                 "Primary object or original traceback tail replaced")
            need(got is not close or index == 9, "Unexpected close precedence")
            need(got is not bookkeeping and got is not manifest and got is not bad_name,
                 "Secondary error escaped")
            if index == 5:
                need(observed.get("status_hook_fired") is True and info["status"] == "IN_PROGRESS",
                     "Status bookkeeping injection did not fire before mutation")
            elif index == 6:
                need(observed.get("fallback_mutated") is True and
                     info["status"] == "LITERAL_REFERENCE_FALLBACK", "Fallback status hook differs")
            else:
                need(info["status"] == "FAILED_EVIDENCE_RETAINED", "Failure status differs")
            if index in (1, 8, 13):
                need(type(info["close_errors"]) is RejectAppend and not info["close_errors"],
                     "Close bookkeeping failure was not exercised")
            if index == 2:
                need("bookkeeping_tb" in observed and "failure_manifest_error_type" not in info,
                     "Manifest type-name diagnostic failure not exercised")
            if index == 5:
                need(info.get("failure_manifest_error_type") == "BookkeepingFault" and
                     "error" not in info, "Primary status failure metadata differs")
            if index == 7:
                need(info.get("failure_manifest_error_type") == "BookkeepingFault" and
                     "error" not in info, "Stringification diagnostic failure differs")
            if index == 4:
                need(str(got) == "Expected serializer receipt changed" and
                     info.get("failure_manifest_error_type") == "FileNotFoundError" and
                     info["phase"] == "exit_freshness", "Late freshness disposition differs")
            if index == 6:
                need(str(got) == "JSON encoder binding changed: default", "Fallback freshness differs")
            if index == 10:
                need(str(got) == "Complete output, ordered witness, or rank trace changed from the frozen profile",
                     "Rejection differs from frozen reference")
            if index == 11:
                need(info.get("failure_manifest_error_type") == "ManifestFault", "Manifest failure unrecorded")
        expected_finals = {}
        if index in (3, 4, 6, 12, 14):
            expected_finals = dict(zip(NAMES, LITERAL_BYTES))
        elif index == 8:
            expected_finals = {NAMES[0]: b""}
        elif index == 10:
            expected_finals = dict.fromkeys(NAMES, PREVIOUS)
        elif index == 11:
            expected_finals = {NAMES[0]: LITERAL_BYTES[0], NAMES[1]: b"{", NAMES[2]: PREVIOUS}
        actual_finals = {filename: bounded_read(output / filename) for filename in NAMES
                         if (output / filename).exists()}
        need(actual_finals == expected_finals, "Sequential final-file visibility differs")
        stage = None if index == 6 else Path(info["stage"])
        residual_names = None if stage is None or not stage.exists() else sorted(p.name for p in stage.iterdir())
        expected_residual = {
            1: ["failure.json", "result.json"], 2: ["result.json"],
            3: ["failure.json", "rank-trace.json", "witness.json"], 4: None,
            5: ["result.json"], 6: None, 7: ["result.json"],
            8: ["failure.json", "rank-trace.json", "result.json", "witness.json"],
            9: ["failure.json", "result.json"],
            10: ["failure.json", "rank-trace.json", "result.json", "witness.json"],
            11: ["rank-trace.json", "result.json", "witness.json"],
            12: ["failure.json"], 13: ["failure.json", "result.json"], 14: None,
        }[index]
        need(residual_names == expected_residual, "Residual stage-name set differs")
        if stage is not None and stage.exists():
            for artifact_index, filename in enumerate(NAMES):
                path = stage / filename
                if path.exists():
                    expected_stage = b"" if index in (1, 2, 5, 7, 13) else LITERAL_BYTES[artifact_index]
                    need(bounded_read(path) == expected_stage, "Residual staged bytes differ")
            failure_path = stage / "failure.json"
            if failure_path.exists():
                failure = json.loads(bounded_read(failure_path))
                need(failure["status"] == "FAILED_EVIDENCE_RETAINED", "Failure manifest status differs")
                need(failure["error"]["type"] == type(got).__name__, "Failure manifest primary differs")
        if index == 3:
            need(info["cleanup"] == [NAMES[0]], "Partial cleanup progress differs")
        if index == 12:
            need(info["cleanup"] == list(NAMES), "Rmdir cleanup progress differs")
        if index in (4, 14):
            need(info["cleanup"] == list(NAMES) + ["stage_directory"], "Complete cleanup progress differs")
        rows.append({"case": name, "expected_failure": index != 14,
                     "primary_identity_and_traceback_tail_checked": index != 14,
                     "final_names": sorted(actual_finals), "stage_names": residual_names})
    need(comparison.EXPECTED == reference_expected_before and
         comparison.write_scientific.__code__ is original_code, "Frozen reference changed")
    report = {"schema": "w2-new-failure-control-result-v1", "status": "W2_FINITE_CONTROLS_PASS",
              "case_count": len(ORDER), "optimization": sys.flags.optimize, "cases": rows}
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8")
    need(len(raw) <= 65536, "Control report exceeded cap")
    (root / "controls.json").write_bytes(raw)
    return report
