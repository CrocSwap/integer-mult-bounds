# Two changed owner protocols, with explicit negative admission gates

intqwq; substantial OpenAI Codex assistance. Apache-2.0.

**TL;DR:** A new 128-owner dyadic order-three completion and a restored dirty
helper protocol pass exact arbitrary-input algebra and three scoped Lean
checks. Neither improves kappa. The standalone order-three adapter is cheap
owner mixing, not a Gaussian resource; its naive shared-owner split fails.
The dirty protocol has a strictly worse complete paid/helper invoice.

These change the operation being computed, rather than retiming the old
center charts. PR4700's retained monotone center protocol and PR4696's
fixed-subspace phase grammar do not give their costs or their correctness.
Those predecessors are not asserted to exclude all changed protocols.

## The new order-three completion

For the authenticated 8-by-112 matrix R, put `B=R^t/2`, `C=R/2` and
`J=I-BC`, so `CB=14I`. On three owner groups of sizes 112,8,8, define

```text
A = [[J,    -B,    26B],
     [-16C, -15I,  449I],
     [-C,   -I,    28I]].
```

The exact 128-by-128 calculation gives `A^3=I`. The generic Lean proof
requires only additive homomorphisms B,C satisfying CB=14I, and holds on
arbitrary inputs. It does not assume zero auxiliaries. This order-three
identity is new to this package; the underlying finite-order conjugation
method and dyadic elimination are not claimed as new mathematics.

There is an actual in-place scalar adapter. Using the eight authenticated
selected ports, D is the orthogonal 8-by-8 dyadic submatrix of C. Transform
each auxiliary bank by D^t and extract `u=D^t C X` into the selected main
coordinates. In these coordinates each query direction uses

```text
[[-13, -14, 364],
 [-16, -15, 449],
 [ -1,  -1,  28]].
```

The matrix has dyadic-unit pivots and is emitted using reversible ADDs,
negations and swaps. Updating the ordinary coordinates and reconstructing
the selected ones uses B,D,C only. There is no odd division, cleared field
or hidden owner. All 128 output rows match A. Repeating the complete emitted
adapter three times restores every arbitrary owner.

The emitted word has **2,356 scalar operations**, inherited scalar tariff
**26,632**, maximum prefix row-l1 norm **4,032**, and maximum coefficient
denominator **32**. Those bounds also hold during all three consecutive
adapters. Thus its exact scalar prefix bound fits twelve magnitude bits
and five fractional bits; this is not a full rounded execution theorem.
All scalar operations act on a fixed number of owners at one common frame.
They use charged whole-field scalar primitives, with inherited strided
movement overhead, and **zero Gaussian oracle calls**.

That last fact is an admission gate: **A itself earns no productive Gaussian
credit**. A relevant expensive main operator would have to include its
actual endpoint frames, `diag(F_final) A diag(F_start)^-1`, or the negative
bank's `Q^-1 M Q`. This package does not remove those frame conjugations or
relabel the cheap owner matrix as a recursive supplier.

The owner-sharing tensor split also fails. A operates once on the owner
factor of `owners tensor digits1 tensor digits2`. Applying A separately on
both digit factors while retaining one owner bank applies **A twice**.
The verifier exhibits `A^2-A != 0`, with coefficient difference 3 at owner
0,input owner 0. Ordinary tensoring instead produces two owner factors and
has the wrong type. This rejects this specific proposed split; it does not
exclude a different typed split/merge or cross-stage relation.

For comparison with the retained clean-J caller, reclassifying 32 cold
helpers would give:

| Quantity | Rank mass |
|---|---:|
| Unchanged inherited paid mass | 5093 |
| Remaining independent helpers | 3013 |
| Unconverted coupled main | 2080 |
| Unconverted deficit | 0 |
| Ordinary converted main | 2048 |
| New paid rank-one conversion calls | 32 |
| Target rank lost in that conversion | 32 |
| Converted deficit | **64** |

The retained p1/p2 controller's conditional surpluses before direct heads
are 64/192. The 256/512 rank-one heads leave **-192/-320**. These are only
conditional comparison ledgers; no new native caller or independent
Gaussian-job admission is claimed. Full native expansion was deliberately
withheld after these gates. Finite order alone supplies no recursive saving.

## Restored dirty helper instead of an owned center

Let F be the actual center Gaussian operator, and let x,y,h all be arbitrary.
The new mixed-reference scalar/oracle word is

```text
h += x
h  = F h
y += h
h  = F^-1 h
h -= x
h  = F h
y -= h
```

Its exact result is `(x, y+F x, F h)`. The helper is independent of x,y and
its reserved output is returned as the specified ordinary F job. No owned
zero input or erase is used. Lean proves both the desired main response and
the uncontaminated helper return for every additive equivalence F.

The actual first center of the selected word has rank eight. The verifier
uses its literal canonical Clifford circuit and its true adjoint, checks
all Pauli generators and the exact zero-state phase of their round trip,
and rejects replacing the adjoint by the same circuit. Its square is a
nontrivial Pauli. Omitting the helper decontamination also fails.

There are **three paid F/F^-1 calls and four charged scalar ADDs**. The
maximum prefix sum of operator l2 norms is three. For every f, use
`F=C_r tensor f`: the paid child widths are `r*f,r*f,r*f`, and the one
independent helper width is `r*f`. At moment exponent t the net bill is

```text
3*r^t - r^t = 2*r^t,
```

whereas the replaced owned center costs `r^t`. The difference is positive
for every r>0. Scalar movement, guard and restoration costs cannot reverse
that already-negative oracle comparison. No componentwise precision or
physical tape theorem is inferred from the l2 prefix bound.

There is a restricted minimum-call gate. Allow constant invertible mixing
of the three owners and single-owner calls of F or F^-1, with desired
helper output Fh. On a spectral value z, the target owner matrix is
`[[1,0,0],[z,1,0],[0,0,z]]`. Its determinant is z. At z=1, the constant
mixing determinant must therefore be one. With zero or two oracle calls,
the determinant at z=i is real, hence cannot equal i. With one call, the
difference between its z=i and z=1 owner matrices has rank at most one.
The target difference has a 2-by-2 minor **-2i**, so has rank two. Three
calls are attained by the word above.

The determinant/minor argument is stated mathematically and its exact
Gaussian-integer witnesses are checked in Python; it is not one of the
Lean theorems. It does not cover different oracle operators, different
helper targets, arbitrary address-dependent routing, shared multi-owner
paid calls or a different scalar computation. It is not a universal
lower bound for multiplication suppliers.

## Reproduce and dependencies

From the repository root, using global Python 3.14:

```powershell
py -3.14 -S research/kappa-round8-owner-protocol-20261023/verify_lean.py --receipt-only
py -3.14 -S research/kappa-round8-owner-protocol-20261023/verify.py
```

Expected markers are `PASS_LEAN_SOURCE_LOG_RECEIPT_ONLY` with three reports
and `PASS_TWO_CHANGED_OWNER_GATES_NO_KAPPA`. Receipt-only replay checks the
actual source, log, named axiom reports and pinned runtime metadata; it does
not perform a fresh compilation. These commands require neither a Lean
runtime nor an olean. The Python replay needs only the standard library.
Where that launcher is unavailable, use `python3.14` or the installed global
Python 3.14 executable. Actual interpreter provenance is recorded in the
receipts. Replay runs no optimizer, installs no package and modifies no frozen
round-seven file. SOURCES.json retains sixteen exact
commit/path/blob/SHA-256 inputs, including the actual R packet, first-center
native word, exact Clifford compiler, round-five construction sources, and
PR4700 scope/proof/receipt, and the portable Lean auditor and three Lake
setup files. Copies live below sources/. Ordinary replay checks each retained
copy's SHA-256 and self-computed Git blob ID, requiring no absent origin
commit objects or sibling packages. SOURCES.json records origin commit/path
labels from collection; ordinary replay does not establish Git ancestry or
the origin commit/path association. Optional `verify.py --git-provenance`
checks those associations when the recorded origin objects are available.

Fresh Lean replay accepts `--runtime PATH --lake PATH`. The default is the
existing ignored runtime at `research/kappa-lean-verification-20261022`;
it is not required to be a sibling in a publication checkout. An external
runtime must use the exact copied `lean-toolchain`, `lakefile.toml` and
`lake-manifest.json`, with their dependencies installed. The pinned setup is
Lean 4.21.0 commit 6741444a63ee,
executable SHA-256 fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab,
mathlib 308445d7985027f538e281e18df29ca16ede2ba3 and its exact manifest
dependencies. LEAN.json records runtime revisions, source/log/object hashes,
auditor hash and the three standard-only axiom reports. For example, on this
machine a fresh compile from an isolated checkout can be requested with:

```powershell
py -3.14 research/kappa-round8-owner-protocol-20261023/verify_lean.py --runtime C:/path/to/pinned-lean-runtime --lake C:/path/to/lean-4.21.0/bin/lake.exe
```

This produces `PASS_LEAN_SCOPED_OWNER_IDENTITIES` and an ignored local object.
The checker authenticates the copied auditor before loading it. When an
object is present its hash is checked; its absence is permitted for
source/log receipt replay.
No compiler executable, olean, virtual environment or solver package belongs
in this research submission.

RESULT.json.gz records the actual emitted scalar adapter, exact all-owner
checks, split and return controls, scalar bounds and both negative invoices.
It is not a certificate of a new recursive supplier or a kappa increase.

## Open next questions

1. Can a genuinely shared paid operation on several owners be lowered to
   ordinary Gaussian children with a better complete moment, including all
   independent helper outputs and owner returns? A fixed scalar matrix alone
   supplies no such resource.
2. Can a changed native producer supply a useful cross-stage relation for
   the actual phase-conjugated endpoint operators, together with a typed
   owner-sharing split/merge? Finite order and the failed repeated-owner split
   are not that relation.
3. Can a different dirty-helper target or unequal-rank oracle factorization
   beat the owned-center moment while preserving exact phases and arbitrary
   inputs? The three-call minimum here covers only the stated same-F,
   single-owner model. A concrete operator and complete invoice should
   precede any larger search.

Credit the retained intqwq/PR4610 clean-J and S/T construction sources,
their Gaussian/native/compiler contributors and retained attribution;
Cinna Davis/PR4700 for the center-protocol scope and floor; Cinna Davis/PR4696
and Dugongue/PR4654 for the related phase grammar. The dirty-helper
compute/uncompute pattern, determinant argument, matrix ranks and
finite-order conjugations are classical methods, not claimed as new work.
