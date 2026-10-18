# Paired input/output extraction

Let M denote the complete non-target forward operator of the pinned PR2894
word: the A gates after the entry prelude, the B gates and formal invertible
warps, and the restore gates. Target writes are omitted in this definition;
they are checked separately by the full independent word auditor. Operators
are noncommuting formal symbols, so the argument uses no numerical sampling.

Let H contain zero-entry helper registers which are neither existing restored
helpers nor sources of the initial operator corrections. For a terminal
hyperplane E, let R consist of registers whose current terminal frames lie in
E. Seek a column y and a row alpha, supported on R, such that

- v = M^-1 y is scalar and supported on H;
- u = alpha M is scalar and supported on H;
- alpha y = u v = 1.

These are two exact nullspace conditions with a nonzero pairing. Finite-field
linear algebra can nominate candidates, but every published identity here is
replayed over rational coefficients in the free operator algebra.

Choose an invertible dyadic input change S and output change T with
`S e_h = v`, `u S = e_h^T`, `T y = e_h`, and `e_h^T T = alpha`.
Then the h column and h row of `T M S` are both the corresponding identity
column and row. Register h is restored exactly for every arbitrary dirty
helper input and is not read by other output registers. This supplies the
cold endpoint needed by the inverse-reverse cleanup contract.

For h=408, E is the binary hyperplane perpendicular to 52, with canonical
basis `(256,128,64,36,20,8,2,1)`. The output certificate is especially small:

```
alpha = e_408^T + (1/2)e_42^T + e_105^T
y = 2 e_42

408 += (1/2) * 42
408 += 105
42  -= 2 * 408
```

All three terminal additions use frame E. The 24 input gates in
`data/TRANSFORM.json` act at frame zero. They include one scaling by 2 and
otherwise dyadic additions. `structure.py` derives S, T, M, u, v, alpha and y
from the literal gates and checks all seven identities, independently of the
word producer. `verify.py` also checks both full target maps and the dual
orientation with the inherited exact auditor.

The target correction becomes `C S`. The initial operator corrections retain
their inputs because S acts only outside their source set. Warps, the cut,
ports, target levels, removed helpers and the entry prelude are unchanged.
The changed sections are exactly A, restore, helper_final, compensation,
report and cleanup. Inverse-reverse cleanup is regenerated and checked from
the full new word; its new private buffer is allocated, cleared and charged.

The complete per-call profile changes from
`{1:2404,2:642,3:262,4:128,5:26,8:8}` to
`{1:2407,2:640,3:262,4:128,5:26,8:8}`. Helper408 changes width 9 to 8;
there remain 408 live helpers and 632 independent inputs, with **73** private
zero buffers instead of 72.

# Owner allocation and cost

Keeping PR2894's fill is worse despite the local improvement. The shipped fill
starts from that literal T74 allocation, makes 545 same-call width exchanges,
then 222 whole-role relocations. The exchanges preserve the set of physical
owner families at each call. Every relocation explicitly checks the owner
window and rejects a family already used in the call; the final independent
auditor rechecks all 271,728 roles, compact offsets, capacity, chronology and
family distinctness. These are discovery heuristics, with no optimality claim.

The actual paid profile is
`{1:1620344,2:426241,3:180732,4:85248,5:25700,6:120,7:1,8:5328,23:1,32:14,48:26837}`.
Its rank mass is exactly `65088*74`. It includes every unused owner remainder.
The complete physical stock is `66304 + 408 + 8 + 73 + 2 = 66795`.
The inherited owner-only checker has a historical 72-buffer display field;
our wrapper explicitly replaces that field and labels its provenance. The
complete rebind, block-norm certificate and outer invoice independently check
the actual 73-buffer namespace, endpoints, stock and prefix reserve.

The admission adapter preserves all inherited tests, with the new source pin
and buffer constants bound explicitly. In particular, the dimension-72
symplectic-group stock factor is unchanged: it is not a private-buffer count.
The old source/parent artifacts are read-only. Both new providers run the full
five native stages; retained providers and the 16-stage retained parent may be
reused only through exact complete-cache/source/claim receipts, and the replay
records this distinction.
