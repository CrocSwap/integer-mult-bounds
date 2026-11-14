# Executed local verification

Environment: Python3.12.14, Linux; no third-party packages. Canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`.

Executed:

```sh
python3 -I -W error -B verify.py --write
python3 -O -I -W error -B verify.py
```

Both completed with `PASS_SELECTED_OWNED_GAMMA_INIT`. The second command
authenticates the frozen source files and compares the full deterministic
receipt. The first non-writing receipt comparison initially compared JSON
lists with in-memory tuples; that verifier-only normalization bug was fixed
and the entire optimized command then rerun successfully. No scientific
result or transition graph depended on that bug.

Evidence retained in `RESULT.json`:

- Nine complete scientific packet runs, including the full f=2, F=524300
  allocation/INIT/CLEAR case with18350585 literal transitions.
- Four arbitrary inactive-body runs: all1, equal to donor, complement of
  donor, and a final-cell1. All preserve donor and return the exact typed zero.
- Three separately checked exact local transition counts, matching
  `3A+V+2F+20` and the uniform bound `4F+8`.
- Real inherited SUB composition from a nonzero initialized donor, followed
  by complete header/DATA CLEAR, with a third correlated parked HOME intact.
- All54 exact source INIT/CLEAR lifetimes,51 raw labels and1480 public rows;
  source frame/liveness verification and repeated-label inventory.
- Differently framed donor1349 accepted for INIT28037; incorrect nonzero
  scalar frame, inactive donor, alias, live-target overwrite and wrong source
  binding rejected.
- Incomplete Gamma header rejection and a partial-CLEAR mutation caught by
  the complete-body result oracle despite its otherwise clean return ABI.

Every successful complete run checks heads, origins, private body retirement,
opaque exteriors and retained earlier history. The fixed unary graph proof
establishes the universal claim; finite cases and source inventory are not
a universal scientific execution of the selected multiplication program.
