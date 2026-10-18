# Retained arithmetic evidence

`ALL-T-BOUND.json` is the U10 all-replica bound (independent/all_t_bound.py). `u10/` holds the
U10 construction receipts (audit_local, 14 controls, 95 end controls, native chain). `strict/` holds the
receipts of the passing strict replay: RESULT, FINAL-BINDING, STAGES, the strict ASSEMBLY, payload controls,
the independent owner check, and the discovery and strict sub-stage lists.

They are review snapshots, not verifier inputs. Run the package verifier to
rebuild ancestry, U8, ownership, the emitted controller, invoice and binding
receipts. The verifier does not substitute these snapshots for computation.
Generated artifact hashes can vary with compression and runtime paths; compare
proof-relevant profiles, exact rational endpoints and inequalities, not unrelated
container metadata. Committed source files retain exact byte pins.

The default CI rebuilds the complete chain on Python 3.11 and 3.14. Local replay
success does not imply a hosted CI result or an unconditional theorem proof.

Note on `strict/RESULT.json` and `strict/FINAL-BINDING.json`: their `pins` record the package manifest at replay time.
After the replay, only this README, the top-level README status paragraph and the `strict/` receipt copies were added,
and MANIFEST.json was regenerated. No code, data or construction file changed, so a fresh replay reproduces the same
exact fields with the current manifest pin.
