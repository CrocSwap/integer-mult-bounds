# T104 superior retained-tail allocation

**Complete conditional finite release passed.** κ = `0.0017177952226165877431979999999999999999999998999999999999999999999999`, an exact gain of `62584575635791/1000000000000000000000000` (6.2584575635791e-11) over the delivered T94 point in PR2824. [CLAIM.json](CLAIM.json) contains exact fractions. This is a small certified constant improvement, not a measured runtime speedup.

The new literal allocation has 104 replicas, 936 calls, 381888 owner roles, 408 helpers per call, 93184 live cells and 93674 physical cells, including 72 private cleanup buffers. Every window, family, mask and compact prefix is checked independently. The positive residue remains paid. The native PR2802 words and their seven aliases are inherited, with attribution preserved in [FRONTIER.md](FRONTIER.md).

The actual native scalar/Horner prefix is at most70 bits. Charging a conservative 128-bit local reserve, together with every invocation and bridge, gives128+37+1872+4=2041<2048. The actual invoice is1983<2048. This sharpens the predecessor's192-bit reserve without dropping work or changing the 20161 finite-row ceiling; the fresh full release rechecks the complete invoice.

Run the standard-library source and independent finite checks:

    python -B verify.py
    python -B check_candidate.py --out /absolute/external/fresh-independent

These reject 11 malformed audit reports, 7 owner corruptions and 5 pricing corruptions. Outputs must be fresh and outside the package.

For a complete cold replay, install requirements.txt separately and run:

    python -B portable_frontier_cold.py --work /absolute/external/fresh-cold --jobs 4

The default runs four fresh native chains and retained-parent admission before the complete candidate release. Optional --source supplies authenticated preobtained original source. Normal TLS is required for downloads. This campaign reused all unchanged native chains from authenticated earlier fresh checks; all changed T104 stages ran freshly. No fresh-native claim is made for this invocation. Native checks used mpmath 1.4.1; this release used pinned mpmath 1.3.0, with Python 3.13.5, numpy 2.5.4, scipy 1.18.1 and sympy 1.14.0.

From lean/ in the separately installed pinned Lean 4.34.1/Mathlib environment, run:

    lake env python -B ../replay.py --out /absolute/external/fresh-kernel --cache-project .

The fresh audit rebuilt all three owned modules, covering 62 defining-module declarations and 55 theorem declarations, including generated helpers. Only propext, Classical.choice and Quot.sound occur; four real ownership/axiom fixtures passed. The new universal theorem proves strict normalized paid-moment monotonicity for every positive S<T and 0.99≤p<1. It does not supply the literal allocation, which is separately checked.

The inherited all-size compiler, source-access, hosting, precision/tape, exact-recovery, ordinary-recursion, bit-supplier and analytic-transfer hypotheses remain. Finite release and the Mathlib cost theorem do not prove an unconditional multiplication theorem.

Apache-2.0. Preserve all upstream licenses and notices. The new allocation, sharper reserve, general monotonicity proof, independent checks and integration were prepared with substantial OpenAI Codex assistance using one primary and three agents. Existing native and analytic contributions retain their credited authors.
