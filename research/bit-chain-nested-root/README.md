# Chain-nested root caller on the BIT native word

**BIT dependency bound only; no overall κ.** An integral chain-nested root caller (n=20, 3 thin queries, 18 local calls, 16 merged idles, no supplier tree) transfers to the retained BIT native word (SHA-256 `51203e7f…cad78`). Its complete invoice has a raw crossing in **(0.0038525393934, 0.0038525393935)**, against 0.0037667234776 for the two-fragment caller of #6726. The package admits an ordinary BIT saving **0.00385248** (tested 0.0038525), an increase of 0.00008579 over the ordinary saving 0.00376669.

Result summary (`verify.py`, exact):
* 670-event binary caller (240 ADD, 393 SWAP, 18 LOCAL, 16 IDLE_ONE, 3 QUERY), 20 inputs, 18 native stages; derived from the 1237-event integral complex caller by dropping the ordinary normalisations, keeping odd ADD as XOR, dropping even ADD and unit SCALE.
* 400 coefficients checked by three engines: forward over F2 with stage monomials, forward over Z[q,D]/(q²−1), and the retained independent reverse audit. The complex caller is also replayed over Z[i] with its normalisations (400 coefficients).
* Complete invoice: 10,086 productive fields, 53,787 paid jobs, rank-mass surplus 753. Crossing certified by the retained interval engine and an independent Decimal engine.
* Finite admission at power 768, paid cutoff 15, productive floor 16 and uniform gap 1e-10; ordinary work 182,425,128 visible plus 371,526,328,320 routed records below 10^12; owned bank 3,051,882 below 10^7; ordinary wrapper two steps 0.00374998 → 0.00385 → 0.00385248 with atom 0.004.
* Controls: missing input/output basis, LOCAL, QUERY, IDLE_ONE, normalisation, even ADD (integer engine), stray XOR, shrunk merged idle, dyadic (non-integral) basis, and a saving above the crossing.

Scope: the same five framework assumptions as #6726 (native_all_columns, owned_erasure, compiler, precision_tape, analytic_recovery); the native theorem is unchanged. The complex companion (#6833, chain-nested root) supplies the caller; this package does not claim its κ.

Reproduce (CPython 3.12, standard library): `python3 -B research/bit-chain-nested-root/verify.py`; expected `PASS_BIT_CHAIN_NESTED_ROOT`.

## Open next questions

Does a changed root with fewer thin queries or a different chain length improve the BIT crossing further? The all-ones chain was selected on the complex side; the binary invoice differs in its native histogram, so the binary optimum may differ. A binary scan of chain sizes with an admission for each would settle it within this family.
