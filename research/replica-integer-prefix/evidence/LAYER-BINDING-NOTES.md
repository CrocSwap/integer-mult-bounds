# Supplier and headline receipts

The smaller value in `release/verify/RESULT.json` is freshly computed, not a
stale label. The supplier's own bootstrap witness gives
`428927389851269/250000000000000000 = 0.001715709559405076`.
The original PR2833 supplier value was different,
`0.001715708721612444688778900361893235...`.

The full binding is:

1. `code/assemble.py:277` checks the actual paid profile's native complex moment
   at `C=0.001718658277841719898626` and rejects `C+1e-24`. It then evaluates the
   supplier bootstrap witness. The strict assembly, strict result, verifier
   result, generated `CLAIM.json`, and generated `new/SPEC.json` all carry the
   same freshly checked supplier value. `verify.py:137` requires this equality.
2. `verify_release.py:70` binds that strict assembly's exact C, complete paid
   profile and retained bit endpoint to `new/SPEC.json` and `outer/B.json`.
   Here `B.b=C-1e-104` and `B.b_above_endpoint=C+1e-24`.
3. `outer/run_outer.py` regenerates both the modern ledger and independent
   balance artifact in a temporary directory and compares them with the
   package artifacts. All63 modern strict inequalities are positive and
   all17 modern controls reject.
4. `verify_release.py:184` requires the modern headline to equal
   `C-1e-70-1e-46`, and emits that headline in `RELEASE-RECEIPT.json`.
   The admission driver at line364 binds the exact headline and package
   manifest to that receipt before emitting final `RESULT.json`.

`CLAIM.json` inside the generated supplier explicitly explains its two layers
and points to `outer/OUTER-CLAIM.json` for the headline. The published new
package's headline claim should use the full release value.

`LAYER-BINDING.json` checks these equalities and actual control arrays directly:
114 admission,12 BIT,25 controller,8 independent owner and10 geometry; all
names are distinct within their respective arrays. The inherited verifier's
summary still hardcodes `controller=15`; this metadata is not the executed
count. The executed `ASYNC-AUDIT.json` lists25 rejected mutations, covered by
the exact-once merge. The other four reported counts equal their actual arrays.

For native wording, the default portable reproduction freshly verifies both
current PR2833 native providers, both retained native chains, and all16
retained-parent admission stages. The primary research admission reused the
two authenticated retained native chains and parent, while both changed
providers were fresh this round. These are distinct provenance statements.

The read-only checks are implemented in `inspect_layer_binding.py`; no supplier
or upstream source was edited for this inspection.
