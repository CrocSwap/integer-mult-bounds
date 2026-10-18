# Validation record

Date: 2026-10-14 UTC. Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

Local interpreter: CPython 3.14.7.

- `python3 -I -B research/gl3-coordinate-cnot-pair-seed1385e243/verify.py` — passed; exact minimum six, no word through five.
- `python3 -I -O -B research/gl3-coordinate-cnot-pair-seed1385e243/verify.py` — passed with identical state counts and hashes.
- `python3 scripts/research_package.py --package research/gl3-coordinate-cnot-pair-seed1385e243 --check-only` — `PASS_PACKAGE_METADATA_AND_PINS`.
- `python3 -B scripts/research_baseline.py` — `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, selected `κ=836330098538459/500000000000000000`, complex side binding.
- Selected-record SHA-256 checked against the task package: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The registered Python 3.12 replay command was not run: `python3.12` is not installed locally. Invoking the full generic package runner consequently stopped with `run replay with Python 3.12`; the direct verifier ran in both normal and optimized CPython 3.14.7 modes. The selected supplier cold replay `make frontier1094-verify` was not run because this abstract GL3 call-count result does not modify or claim adoption by that supplier.
