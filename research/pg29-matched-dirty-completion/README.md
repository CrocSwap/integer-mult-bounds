# A finite dirty completion of the PG(2,9) scalar code

This package gives an exact boundary transfer and a scalar completion for
the Braverman-He 182-vertex code. It replaces the former zero-valued C stubs
by independent formal inputs, obtains an invertible 175-input transfer, and
identifies a 166-input matched-stub subspace on which all 157 message outputs
remain correct. An explicit nine-value inverse correction restores the junk.

This is a new finite interface calculation, not a physical supplier or a
kappa improvement. It identifies exactly which arbitrary-input coupling a
future physical construction must handle. [PROOF.md](PROOF.md) states the
identity and its boundary. The local transcript and all correction matrices
are included, so the result can be checked without a network fetch.

## Result

The 175 by 175 transfer is `M=[[I157,F],[G,H]]`, with F and G of rank nine,
H of rank 18, and `H-GF` invertible. M is invertible but is not a permutation.
If the two inputs of each C pair are equal, the 157 message outputs are
independent of that junk. Both outputs in every J pair then agree. Taking
one output per pair gives `(x,z)->(x,Bx+Dz)` with D invertible, of size nine.
The included inverse correction gives the identity on all 166 formal inputs.

The correction matrix `D^-1 B` has rank nine and 1,243 nonzero coefficients.
The original transcript has 735 physical edge transmissions. Neither count
is a recursive paid bill. Matched-input preparation, legal rational frames,
physical return, correction cost, hosting, and the complete compiler remain
unproved. There is no complex companion or verified kappa improvement.

## Reproduce

From the repository root, Python 3.10 or later and its standard library:

```sh
python3 -B research/pg29-matched-dirty-completion/verify.py
```

Expected final line:

```text
PASS_PG29_DIRTY_PACKAGE independent_stubs=175 matched_inputs=166 no_new_kappa
```

The wrapper checks source hashes, runs both separate-field replays in a
temporary copy, and compares their complete receipts. The first replay
checks local invertibility, every boundary coefficient, full rank, and
matched-pair identities. The second computes and compares the inverse
factors and checks all 166 identity columns. The supplied scripts remain
active when the wrapper is run with `-O`, because it starts ordinary Python
child processes. These are exact finite checks, not a Lean theorem, a
complete supplier replay, independent human review, or hosted CI success.

## Sources and credit

Publication base: `cef4b52f2a59009865bf8eabde1be3f159063703`.
Braverman and He supplied the code in
[arXiv:2610.10108v1](https://arxiv.org/abs/2610.10108v1), section 4, and its
[companion source](https://github.com/zhongtianhe/multiple-unicast-counterexample/tree/3436359a85d13a1bf6e87c3a3dbdaa64788277f4).
The transcript was derived from that exact source and checked against its
original verifier. Its source and input hashes are recorded in `SOURCES.json`.
The original companion implementation is not redistributed here. The
mathematical transcript and separate replay code are sufficient to verify
the stated boundary map. The source derivation is provenance, not a claim
that the present verifier independently derives the published code from
the projective geometry.

The known common-target sign-gauge obstruction in
[PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288) concerns a
physical frame embedding. It is not supplied or resolved by this scalar
completion. Its compiler and network-coding lineage retain their credit.

Ali Romman directed this work with substantial OpenAI Codex assistance,
including separate research agents for field replay and completion review.
New work is Apache-2.0. `ORIGINS.json` records each local source and the
limited publication changes. The original conditional price experiment was
omitted because its proposed physical profiles remain unbuilt. Attribution
does not imply review or endorsement by Braverman, He, or any predecessor.

## Open next questions

Can the matched-input injection and nine-value correction be realized at
legal rational frames? First give a concrete physical implementation of
one correction map with arbitrary dirt restored, then count its complete
recursive children. The absence of a frame embedding and a paid invoice
is the present blocker; the scalar inverse does not remove it.
