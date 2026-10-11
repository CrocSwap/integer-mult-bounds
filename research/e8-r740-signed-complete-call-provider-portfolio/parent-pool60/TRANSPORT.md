# Lossless transport

Run `python3 -B materialize.py` once before `verify.sh` or `python3 -B verify.py`.
The hosted workflow performs this step automatically. The materializer checks the
publication transport and restores the 140 MB owner-matrix JSON to its exact
frozen hash, then checks all 1130 scientific inputs. It leaves the original
SOURCE-MANIFEST and scientific verifier unchanged. No matrix is regenerated and
no numerical or logical check is skipped. The original full V2 scientific replay
passed before compression; the separate transport gate verifies byte identity.
All mathematical and compiler conditions in README remain in force.
