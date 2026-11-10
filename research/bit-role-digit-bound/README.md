# Selected BIT role digit is at most 2^(H1+13)

**Scoped comparison. No new κ.** The selected frontier stays
`781451/250000000`. The ordinary BIT stage retained by
`certificates/frontier6030/CLAIM.json` has admitted saving `17/5000` and
rank `2^25986965159937`. Its published sufficient stock guard at
`log2(e) >= 52182660963735` needed `c_B <= N^2`. The compiled role count
`B` is not materialized. Under the nested-width bound already used by the
lockstep audit,

```text
c_B = ceil(log_q B) <= 2^(H1+13) <= N^2
```

for every prime allowed by the recorded rule `q > 2^26*N^5`. The band note
asserts this comparison and does not compute the digit. With the cited
reading `S_old = 1`, the guard no longer needs a role count beyond that
inherited bound. The six-bit gap below the guard is unchanged.

The argument is in [PROOF.md](PROOF.md). The nested-width census is an
inherited hypothesis, not a theorem proved here.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B research/bit-role-digit-bound/verify.py
python3 -B scripts/research_package.py --package research/bit-role-digit-bound
```

Expected marker:

```text
PASS_BIT_ROLE_DIGIT c_B<=2^(H1+13)<=N^2 X=471715391583208384 no_new_kappa
```

The verifier recomputes the role upper bound from the pinned BIT invoice,
checks the prime-rule comparison, and rejects a rank that is too small to
absorb the exponent and an upper bound shifted by the full slack. It does
not run a selected-frontier replay.

## Open next questions

1. Can a `D = 2` depth lemma move the sufficient guard below
   `t = 52182660963735`? The role digit is now at most `2^(H1+13)`, which
   is smaller than the matrix term by a factor `2^(H1-13)`, so a sharper
   `c_B` does not close the six-bit gap. The first step is an exact
   comparison of `D*(N^2*w + c_B)` with `e/4` at `D = 2` and
   `w = ceil(e^(1/250))`. It is blocked by the slack the published band
   proof spends on the exponent arithmetic.

## Credit

The band theorem is JoyboyBrian's PR #4954. The old-leaf reading `S_old = 1`
is James Reed's PR #4970. The nested-width formula is the #4436 bound as
used by Mark (Matarener) in `research/lockstep-live-role-audit`. The stock
formula is the delayed-cover bridge. The selected claim is PR #6030.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or proof-kernel acceptance is claimed.
