"""Ordered concrete loader controls. SOURCE ONLY until parent admission.

Finite pins below are constructed only within controls and are never passed to
the public genuine loader. No fixture, decoder or target work occurs at import.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

# -I excludes the script directory. The parent seals this exact sibling source
# and full bootstrap/runtime closure before dispatch; no ambient import lookup.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frozen_h25_inputs as loader


def require(value, message):
    if not value:
        raise RuntimeError(message)


def rejects(function, expected, fragment=None):
    try:
        function()
    except expected as error:
        require(fragment is None or fragment in str(error), "wrong rejection: " + str(error))
        return
    raise RuntimeError("expected rejection missing")


def corpus():
    result = {
        "circuit": {"h": 8, "v": 56, "additions": 1, "injections": 2, "roles": 3,
                    "roles_per_target": 0.125, "disjoint_additions": 1, "pair_star_additions": 0},
        "side_map": {"targets": 56, "nonzero_coefficients": 2, "side_map_exact": True, "coefficients": "+1/2 disjoint, -1/2 intersection two"},
        "labels": {"active_nodes": 2, "checked_inclusions": 1, "all_labels_nondegenerate": True, "all_residuals_have_odd_vectors": False},
        "role_frames": {"roles": 3, "forward_frames_nested": True, "reverse_complement_frames_nested": False}}
    witness = {"support": [0, 1 << 300, (1 << 300) + 1], "args": [None, None, [1, 1]],
               "kind": [None, "in", "d0"], "active": [2, 1],
               "pieces": [[[2, 0, 1], 2, [-1, 2]]],
               "labels": [[2, [[9, 17], [1, 3]], 2, [17, 3]], [["perp", [2, 0, 1]], [[4, 19]], 1, [19]]],
               "code": {"roles": 3, "gates": [[2, [1, 0], [1, 2]], [1, [0], [0, 1]]],
                        "sources": [[[2, 0, 1], 2], [[1, 2, 3], 0]], "outputs": [[2, 1], [0, 2]]}}
    ranks = [[[3, 1], 2], [[5], 1], [[3, 1], 2]]
    return witness, ranks, result


class Fixture:
    def __init__(self, logical=None, mutate_specs=None):
        self.root = Path(tempfile.mkdtemp(prefix="o03-loader-control-"))
        self.specs = {}
        values = corpus()
        self.logical = {}
        for relative, original in zip(loader.INPUT_SPECS, values):
            data = json.dumps(original, sort_keys=True, separators=(",", ":")).encode("ascii")
            if logical and relative in logical:
                data = logical[relative]
            self.logical[relative] = data
            packed = gzip.compress(data, mtime=0) if relative.endswith(".gz") else data
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed)
            path.chmod(0o444)
            self.specs[relative] = {"encoding": "gzip" if relative.endswith(".gz") else "plain",
                                    "transport_bytes": len(packed), "transport_sha256": hashlib.sha256(packed).hexdigest(),
                                    "logical_bytes": len(data), "logical_sha256": hashlib.sha256(data).hexdigest()}
        if mutate_specs:
            mutate_specs(self)
        for relative in reversed(loader.DIRECTORIES):
            (self.root / relative).chmod(0o555)
        self.root.chmod(0o555)
        self.custody = self.snapshot()

    def snapshot(self):
        return {"schema": "h25-input-custody-v1", "root": str(self.root), "root_identity": loader.identity(self.root.lstat()),
                "directories": {p: loader.identity((self.root / p).lstat()) for p in loader.DIRECTORIES},
                "files": {p: dict(loader.identity((self.root / p).lstat(), True), sha256=s["transport_sha256"]) for p, s in self.specs.items()}}

    def load(self):
        return loader._load(self.root, self.custody, self.specs, 3, 2)

    def close(self):
        self.root.chmod(0o700)
        for relative in loader.DIRECTORIES:
            (self.root / relative).chmod(0o700)
        shutil.rmtree(self.root)


def with_fixture(function, **kwargs):
    fixture = Fixture(**kwargs)
    try:
        function(fixture)
    finally:
        fixture.close()


WITNESS = "baseline/evidence/canonical/witness.json.gz"


def valid_fresh():
    def check(f):
        first, second = f.load(), f.load()
        expected_witness = loader.restore_witness(corpus()[0])
        require(first["witness"] == expected_witness and first["ranks"] == [((3, 1), 2), ((5,), 1), ((3, 1), 2)], "finite exact tuple/order restoration")
        require(first["result"]["labels"]["all_residuals_have_odd_vectors"] is False, "legitimate False")
        require(type(first["result"]["circuit"]["roles_per_target"]) is float, "legitimate float")
        first["witness"]["support"].append(77)
        require(second["witness"] == expected_witness and first["result"] is not second["result"], "fresh ownership")
    with_fixture(check)


def spec_failure(field, value, fragment):
    def check(f):
        f.specs[WITNESS][field] = value(f.specs[WITNESS][field])
        if field == "transport_sha256":
            f.custody["files"][WITNESS]["sha256"] = f.specs[WITNESS][field]
        rejects(f.load, loader.InputError, fragment)
    with_fixture(check)


def invalid_gzip(truncated):
    def prepare(f):
        path = f.root / WITNESS
        path.chmod(0o644)
        data = path.read_bytes()[:-5] if truncated else b"not a gzip stream"
        path.write_bytes(data)
        path.chmod(0o444)
        f.specs[WITNESS]["transport_bytes"] = len(data)
        f.specs[WITNESS]["transport_sha256"] = hashlib.sha256(data).hexdigest()
    with_fixture(lambda f: rejects(f.load, (OSError, EOFError)), mutate_specs=prepare)


def schema_mutation(mutate, message):
    witness = corpus()[0]
    mutate(witness)
    rejects(lambda: loader.restore_witness(witness), loader.InputError, message)


def order_check(path, expected):
    value = loader.restore_witness(corpus()[0])
    for key in path:
        value = value[key]
    require(value == expected, "retained order " + repr(path))


def rank_bool(row):
    value = [[[True] if row else [1], 1 if row else True]]
    rejects(lambda: loader.restore_ranks(value, 1, 1), loader.InputError, "exact int")


def result_invalid(section, key, value, fragment):
    certificate = corpus()[2]
    certificate[section][key] = value
    rejects(lambda: loader.restore_result(certificate), loader.InputError, fragment)


def decimal_error():
    limit = sys.get_int_max_str_digits()
    require(limit > 0, "decimal conversion control requires unchanged positive interpreter limit")
    rejects(lambda: loader.strict_json("1" * (limit + 1)), ValueError)
    require(sys.get_int_max_str_digits() == limit, "integer limit mutated")


def wide_integer():
    value = 1 << 3000
    require(loader.strict_json(str(value)) == value, "arbitrary-width integer changed")
    require(loader.restore_witness(corpus()[0])["support"][1] == 1 << 300, "wide tuple integer changed")


def mode_drift():
    def check(f):
        f.load()
        (f.root / WITNESS).chmod(0o644)
        rejects(f.load, loader.InputError, "identity")
    with_fixture(check)


def byte_drift():
    def check(f):
        f.load()
        path = f.root / WITNESS
        path.chmod(0o644)
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        path.chmod(0o444)
        rejects(f.load, loader.InputError, "identity")
        # Freshly accepted metadata cannot hide changed bytes under old pins.
        f.custody = f.snapshot()
        rejects(f.load, loader.InputError, "transport hash")
    with_fixture(check)


def in_call_drift(change_bytes):
    def check(f):
        original = loader.restore_result
        def changed(certificate):
            result = original(certificate)
            path = f.root / WITNESS
            path.chmod(0o644)
            if change_bytes:
                data = bytearray(path.read_bytes())
                data[-1] ^= 1
                path.write_bytes(data)
                path.chmod(0o444)
            return result
        loader.restore_result = changed
        try:
            rejects(f.load, loader.InputError, "identity")
        finally:
            loader.restore_result = original
    with_fixture(check)


def symlink_or_hardlink(symlink):
    def check(f):
        path = f.root / WITNESS
        directory = path.parent
        directory.chmod(0o755)
        saved = directory / "saved-input"
        path.rename(saved)
        if symlink:
            path.symlink_to(saved.name)
        else:
            os.link(saved, path)
        directory.chmod(0o555)
        rejects(f.load, loader.InputError)
    with_fixture(check)


def logical_json_failure(data, exception, fragment=None):
    with_fixture(lambda f: rejects(f.load, exception, fragment), logical={WITNESS: data})


CONTROL_CASES = (
    ("L01_valid_schema_types_order_fresh_ownership", valid_fresh),
    ("L02_transport_hash_before_decode", lambda: spec_failure("transport_sha256", lambda _: "0" * 64, "transport hash")),
    ("L03_transport_size_before_decode", lambda: spec_failure("transport_bytes", lambda n: n + 1, "transport size")),
    ("L04_invalid_gzip", lambda: invalid_gzip(False)),
    ("L05_truncated_gzip", lambda: invalid_gzip(True)),
    ("L06_logical_size_overrun", lambda: spec_failure("logical_bytes", lambda n: n - 1, "logical overrun")),
    ("L07_logical_final_size_before_parse", lambda: spec_failure("logical_bytes", lambda n: n + 1, "logical size")),
    ("L08_logical_digest_before_parse", lambda: spec_failure("logical_sha256", lambda _: "0" * 64, "logical hash")),
    ("L09_duplicate_json_keys", lambda: logical_json_failure(b'{"x":1,"x":2}', loader.InputError, "duplicate")),
    ("L10_nonfinite_json_nan", lambda: logical_json_failure(b'{"x":NaN}', loader.InputError, "nonfinite")),
    ("L11_nonfinite_json_infinity", lambda: logical_json_failure(b'{"x":Infinity}', loader.InputError, "nonfinite")),
    ("L12_wrong_witness_key_set", lambda: schema_mutation(lambda w: w.update(extra=[]), "exact keys")),
    ("L13_wrong_code_key_set", lambda: schema_mutation(lambda w: w["code"].update(extra=[]), "exact keys")),
    ("L14_unsupported_kind_leaf", lambda: schema_mutation(lambda w: w["kind"].__setitem__(1, []), "None or str")),
    ("L15_args_arity", lambda: schema_mutation(lambda w: w["args"].__setitem__(2, [1]), "arity")),
    ("L16_args_bool_int_rejected", lambda: schema_mutation(lambda w: w["args"].__setitem__(2, [True, 1]), "exact int")),
    ("L17_label_bad_tag", lambda: schema_mutation(lambda w: w["labels"][1][0].__setitem__(0, "other"), "perp")),
    ("L18_label_tag_arity", lambda: schema_mutation(lambda w: w["labels"][1].__setitem__(0, ["perp"]), "arity")),
    ("L19_basis_order_retained", lambda: order_check(("labels", 0, 1), [(9, 17), (1, 3)])),
    ("L20_gate_order_retained", lambda: order_check(("code", "gates"), [(2, (1, 0), (1, 2)), (1, (0,), (0, 1))])),
    ("L21_source_order_retained", lambda: order_check(("code", "sources"), [((2, 0, 1), 2), ((1, 2, 3), 0)])),
    ("L22_output_order_retained", lambda: order_check(("code", "outputs"), [(2, 1), (0, 2)])),
    ("L23_arbitrary_width_ints", wide_integer),
    ("L24_unchanged_decimal_error", decimal_error),
    ("L25_duplicate_rank_events_retained", lambda: require(loader.restore_ranks(corpus()[1], 3, 2) == [((3, 1), 2), ((5,), 1), ((3, 1), 2)], "duplicate ranks lost")),
    ("L26_rank_row_bool_rejected", lambda: rank_bool(True)),
    ("L27_rank_result_bool_rejected", lambda: rank_bool(False)),
    ("L28_result_int_bool_rejected", lambda: result_invalid("circuit", "h", True, "exact int")),
    ("L29_result_float_not_int", lambda: result_invalid("circuit", "roles_per_target", 1, "finite float")),
    ("L30_result_nonfinite_float_rejected", lambda: result_invalid("circuit", "roles_per_target", float("inf"), "finite float")),
    ("L31_wrong_rank_count", lambda: rejects(lambda: loader.restore_ranks(corpus()[1], 4, 2), loader.InputError, "full event count")),
    ("L32_wrong_distinct_count", lambda: rejects(lambda: loader.restore_ranks(corpus()[1], 3, 3), loader.InputError, "distinct row count")),
    ("L33_mode_drift_no_cached_pass", mode_drift),
    ("L34_byte_drift_no_cached_pass", byte_drift),
    ("L35_symlink_rejected", lambda: symlink_or_hardlink(True)),
    ("L36_hardlink_rejected", lambda: symlink_or_hardlink(False)),
    ("L37_before_after_mode_drift", lambda: in_call_drift(False)),
    ("L38_before_after_byte_drift", lambda: in_call_drift(True)),
    ("L39_numeric_float_overflow", lambda: logical_json_failure(b'{"x":1e9999}', loader.InputError, "nonfinite")),
)


def run_controls():
    results = []
    for name, function in CONTROL_CASES:
        function()
        results.append({"name": name, "status": "PASS"})
    return {"schema": "h25-loader-controls-v1", "status": "LOADER_CONTROLS_PASS", "optimize": sys.flags.optimize, "count": len(results), "results": results}


if __name__ == "__main__":
    print(json.dumps(run_controls(), sort_keys=True))
