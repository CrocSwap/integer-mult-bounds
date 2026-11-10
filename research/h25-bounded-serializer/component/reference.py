"""Source-exact serializer reference extracted without importing scientific code.

EXPECTED remains the frozen complete H25 receipt. Finite consumers clone only
write_scientific into fresh globals with a separate finite EXPECTED dictionary.
No full H25 construction, native backend, compiler or scientific caller is loaded.
"""
import hashlib
import json


_RUNTIME_ERROR = RuntimeError

def require(condition, message):
    if not condition:
        raise _RUNTIME_ERROR(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

EXPECTED = {
    "result_sha256": "342e99212b12e518902ae9598613f5484113bacee8747c27a13b58a4b1d3986c",
    "exact_witness_sha256": "4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82",
    "rank_trace_sha256": "85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f",
    "rank_call_count": 59959,
    "rank_distinct_matrix_count": 252,
}

def write_scientific(output, result, witness, rank_calls):
    encoded_result = canonical(result)
    encoded_witness = canonical(witness)
    encoded_trace = canonical(rank_calls)
    receipt = {
        "result_sha256": hashlib.sha256(encoded_result).hexdigest(),
        "exact_witness_sha256": hashlib.sha256(encoded_witness).hexdigest(),
        "rank_trace_sha256": hashlib.sha256(encoded_trace).hexdigest(),
        "rank_call_count": len(rank_calls),
        "rank_distinct_matrix_count": len({rows for rows, _ in rank_calls}),
    }
    require(receipt == EXPECTED, "Complete output, ordered witness, or rank trace changed from the frozen profile")
    # Same exact bytes and serialization work in both arms; file hashes omit
    # a trailing newline exactly as the existing profile's digest did.
    (output / "result.json").write_bytes(encoded_result)
    (output / "witness.json").write_bytes(encoded_witness)
    (output / "rank-trace.json").write_bytes(encoded_trace)
    receipt["serialized_bytes"] = {"result": len(encoded_result), "witness": len(encoded_witness),
                                    "rank_trace": len(encoded_trace)}
    return receipt
