#!/usr/bin/env python3
"""Run the complete unchanged PR917 verifier with opt-in row acceleration.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fast_rows import accelerated
from support import predecessor


def run():
    _, independent, verifier = predecessor()
    with accelerated(independent):
        result = verifier.verify()
    print("PASS_CK_DYADIC_ACCELERATED_FULL_REPLAY no_new_kappa")
    return result


if __name__ == "__main__":
    run()
