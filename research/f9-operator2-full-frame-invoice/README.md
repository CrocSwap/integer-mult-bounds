# Invoice for one full-frame F9 transport that fixes |0>

**Exhaustive finite census, no new κ.** On the pinned F9 word, the forward
full-frame transport of operator 2 is the monomial

```text
T|x> = i^{q(x)} |Mx>
```

with the rows recorded in [RESULT.json](RESULT.json). It fixes `|0>` with
phase `+1`, and it moves 496 of the 512 computational basis addresses. The
compiled circuit is one diagonal and one permutation, with support rank 0.
Its inverse is the adjoint sandwich, and the signed order is 10. The
selected conditional exponent stays `363005817/100000000000`.

## Scope and evidence

Task `joint-query-controller`, scope **refined**. The card's first experiment
says to audit the PR5745 active-mode claim before another free-injection
search. The merged F9 audit separated `K_G|0>` from the full-frame transport
and named eight classes that fix `|0>`. The open question on that census asks
for the invoice of one of those transports, including frame change,
restoration and target debit. This package prices operator 2. It does not
price the other seven, and it does not build a caller.

[PROOF.md](PROOF.md) gives the circuit, the monomial, the support ranks, the
inverse, and the comparison with one inherited `H8` centre.
[RESULT.json](RESULT.json) records the rows and the program counts. The state
domain is all 512 width-9 basis vectors. The program domain is both finite
word programs. Every element of both domains is evaluated. A failed or partial
search is not this claim.

The three invoice lines are:

* **Frame change.** The compiled transport has support rank 0. The defining
  Fourier sandwich has peak support rank 9 on every basis input, and each
  Fourier factor has support rank 9 on `|0>`.
* **Restoration.** The sandwich with the gate adjoint of `K_G` is the inverse
  on all 512 states. The signed order is 10, so `T` is not its own inverse.
* **Target debit.** `M+I` has rank 5. Its 16-element kernel is the set of
  addresses where `T` agrees with the identity, all with phase `+1`. The
  other 496 addresses move. The value `<0|T|0> = 1` is the address-0 member
  of that 16-element set.

One removed centre job, in the inherited active-mode contract, is one `H8`.
Support rank 0 is not that charge. Both programs contain no `center` opcode
and no rank-8 climb, while `canonical.local_profile` still stores eight
rank-8 units. Those records are not identified here.

## Reproduce

From the repository root, CPython 3.12, standard library:

```sh
python3 -I -B research/f9-operator2-full-frame-invoice/verify.py
python3 -I -O -B research/f9-operator2-full-frame-invoice/verify.py
python3 -B scripts/research_package.py --package research/f9-operator2-full-frame-invoice
```

The direct verifier prints

```text
PASS_F9_OPERATOR2_FULL_FRAME_INVOICE op=2 support_rank=0 sandwich_peak=9 moved=496 fixed=16 order=10 defect_rank=5 no_new_kappa=true
```

`--record` rewrites `RESULT.json` and is not part of the check. Normal replay
only reads it.

## Limits

The census is this one forward circuit of operator 2 on this word. The unique
width-9 warp of class 2 uses opcode `-2`. The scalar core stores that sign and
does not apply the Clifford. The backward-sign sandwich sends `|0>` to
`|352>` with phase `i`, so it is not this transport. The width-4 warp of
opcode `+2`, from frame 292 to frame 3941, is a different occurrence and is
not priced. No compiler, caller, precision, or outer admission is claimed.

## Open next questions

* Which Clifford does opcode `-2` apply on the full-frame event of `L250`?
  The backward-sign sandwich moves `|0>`, so the sign is not cosmetic. The
  scalar core stores only the tag.
* Do operators 16, 17, 41, 44, 61, 62 and 64 have a compiled support rank of
  0 and a non-identity target debit of this same shape? This package prices
  only operator 2.
* Can a legal caller emit this monomial in place of one rank-8 centre and
  still meet the pinned endpoint? The grade-0 invoice shows that the monomial
  is not an `H8`. It does not emit that caller.

## Credit

The F9 word and the scalar observer are Ali Romman's PR5720 and PR5745,
following flyingviper's active-mode restoration and the filtered-native packet
of Cao Yifan, Cinna Davis and Dugongue. The quadratic engine is the copy
pinned by PR5745. The separation of `K_G|0>` from the full-frame transport,
and the list of eight classes, is the merged audit of that word. The request
to price one class is the open question left by the nonzero-address census.
This package starts from operator 2 and does not import either census.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
