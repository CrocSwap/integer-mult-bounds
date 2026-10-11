Mutable-basis Hamming E8 complex network — reproducible finite research

Run with Python 3.11 or newer, standard library only:
    python3 reproduce.py

No network, optimizer, external executable, saved PASS receipt, or package
installation is required. The exact Clifford phase step takes about two minutes.
All six steps regenerate their own results. Four canonical byte hashes must
match EXPECTED.json, in addition to all mathematical assertions passing.

The full construction and its retained assumptions are in
work/complex-network/hamming/PROOF.txt. Source notices remain in the pinned
input directories. This is a conditional finite result, not an unconditional
theorem or a Lean kernel proof.

The entry point writes REPLAY.json and retains all regenerated intermediate
programs and receipts under work/complex-network/hamming/. A failed assertion
stops the run and prevents a PASS result.
