"""Measure transfers and occupied files through a complete finite Fourier product."""

from contextlib import ExitStack
import json
from pathlib import Path
import sys
from time import perf_counter
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiplier import Product, RetainedProduct
from tape_meter import Motion


def measure(factory, bits):
    start = perf_counter()
    machine = factory((3, 5), 8, bits)
    setup_seconds = perf_counter() - start
    motion = Motion()
    with ExitStack() as workspace:
        tapes = [
            workspace.enter_context(motion.tape(content))
            for content in ((741503).to_bytes(3, "little"), (466013).to_bytes(3, "little"), b"")
        ]
        for module in ("streaming_routes", "stack_tapes", "product_path", "spool"):
            workspace.enter_context(patch(module + ".TemporaryFile", motion.tape))
        start = perf_counter()
        sign, size, _ = machine.multiply_tapes(
            tapes[0], 3, tapes[1], 3, tapes[2], left_negative=True
        )
        execution_seconds = perf_counter() - start
        value = int.from_bytes(tapes[2].stream.getvalue(), "little")
        if not sign or size != 5 or value != 345550037539 or motion.live != 11:
            raise ValueError((sign, size, value, motion.live))
        if tapes[0].tell() or tapes[1].tell():
            raise ValueError("An input head failed to return")
    if motion.live:
        raise ValueError("The product retained an open data file")
    return dict(
        product=-value,
        working_bits=bits,
        H_calls=machine.h_calls,
        setup_seconds=round(setup_seconds, 3),
        execution_seconds=round(execution_seconds, 3),
        peak_occupied_file_bytes=motion.peak,
        transfers=dict(motion.bytes),
        total_traversal_bytes=sum(motion.bytes.values()),
    )


if __name__ == "__main__":
    for name, factory, bits in (
        ("previous", RetainedProduct, 136),
        ("completed_packs", Product, 72),
    ):
        print(name, json.dumps(measure(factory, bits), sort_keys=True), flush=True)
