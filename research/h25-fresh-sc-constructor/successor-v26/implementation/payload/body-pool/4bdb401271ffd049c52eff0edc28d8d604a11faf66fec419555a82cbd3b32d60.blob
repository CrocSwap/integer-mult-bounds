"""Candidate-only trace factory; does not mutate the frozen backend.

The parent owns source custody, native compilation and the live native-owner /
entry check before arithmetic. Install the final trace object before binding
captures wrapper closures. Ordinary frozen JSON/runtime semantics are assumed;
this is not a compatibility layer for arbitrary serializer/backend mutation.
"""
from types import BuiltinFunctionType, ModuleType


def make_trace_type(backend, native_encoder_module):
    """Return a trace subclass with the original before/receipt boundaries.

    ``_h25_native_entries`` exposes the exact owner/name/function triple that
    must be checked by the parent's RuntimeGuard at every original live check
    boundary. It is metadata, not a cached PASS. This factory neither patches
    backend.ComplementTrace nor changes any existing guard or native kernel.
    """
    require = backend.require
    _TYPE = backend._TYPE
    _LIST = backend._LIST
    _INT = backend._INT
    _LEN = backend._LEN
    _DICT_GET = backend._DICT_GET
    json = backend.json
    reference_type = backend.ComplementTrace
    require(_TYPE(native_encoder_module) is ModuleType,
            "Unexpected trace encoder module type")
    native_entry = _DICT_GET(native_encoder_module.__dict__, "encode_record")
    require(_TYPE(native_entry) is BuiltinFunctionType and
            native_entry.__self__ is native_encoder_module,
            "Missing or replaced trace encoder entry point")

    class EncodedComplementTrace(reference_type):
        __slots__ = ()
        _h25_native_entries = ((native_encoder_module, "encode_record", native_entry),)
        _h25_reference_type = reference_type

        def after(self, inputs, output):
            us, vs = inputs
            if output is not None:
                require(_TYPE(output) is _LIST and all(_TYPE(value) is _INT for value in output),
                        "Trace requires an exact integer list or None result")
            # Read count once at the same encoding boundary. Unsupported values
            # use this same object in the literal JSON fallback.
            call = self.count
            encoded = native_entry(call, us, vs, output)
            if encoded is NotImplemented:
                if output is None:
                    result = {"type": "None"}
                else:
                    result = {"type": "list", "values": output}
                record = {"call": call, "us": us, "vs": vs, "result": result}
                encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
            self.hasher.update(encoded)
            self.bytes += _LEN(encoded)
            self.count += 1

    return EncodedComplementTrace
