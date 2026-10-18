# Intervening data work at an open phase bank

**Scoped restoration criterion and counterexample; no new κ.** Returning every
bank address does not imply that the bank has been released independently of
the data. This package states exactly when data-only work between two controlled
Pauli words returns identity on an arbitrary dirty bank.

## Result

Let the first word on data label d be `W_d=X(b(d))Z(a(d))`, the second word
on output label e be `W'_e=X(b'(e))Z(a'(e))`, and let U be any complex data
matrix. The chronological sequence W,U,W' equals **some** `V tensor I_bank`
if and only if every nonzero `U[e,d]` satisfies

```
a'(e)=a(d),   b'(e)=b(d).
```

Then necessarily `V=U D`, with `D[d,d]=(-1)^(a(d) dot b(d))`.
The proof checks each bank block, so it allows singular U and arbitrary
correlated data/bank amplitudes. With identical controls this is precisely the
block-diagonal condition. With a changed consumer it is an explicit support
test: each output row may receive inputs with only one control pair.
[PROOF.md](PROOF.md) supplies the quantified proof and physical-frame bridge.

For Gareth Davidson's unchanged PR2850 producer P, the controls are **Fourier
labels**, not physical addresses. Physical C, Q and translation preserve those
labels and pass. Physical S and Z on x do not: for one bit, the new interposition
P,S_x,P equals `Q diag(i^(x xor c))`. Every bank address c returns, but c=0
and c=1 see different data maps. P,Z_x,P has the analogous unwanted bank sign.
These reject proposed new interpositions; neither predecessor asserts they work.

Z admits a transported consumer: the chronological program
`P, Z_x, Z_bank, P` equals `Q, Z_x`. The extra bank phase must precede the
consumer; putting it after closure fails. S is dense in the control frame,
so changing only the second Pauli labels cannot repair it. This is a restricted
interface obstruction, not an impossibility for arbitrary joint consumers.

## Evidence and reproduction

`verify.py` hashes and executes the unchanged predecessor source bytes without
loading predecessor bytecode or calling its reference routines. At f=1,2 it checks
18 physical fixtures, all 648 basis columns and 37,440 coefficients, plus six
positive comparison programs. S/Z each differ from the intended endpoint at
16 coefficients for f=1 and 512 for f=2. Exact residual formulas and the full
`V tensor I` test establish the stronger bank-dependence failure.

Controls reject source corruption, address-only acceptance, prepared-bank-only
acceptance and moving the repair past its closing consumer. `independent.py`
uses separate Gaussian-rational matrix code, with no predecessor/primary imports,
to check the abstract criterion and reconstruct the physical Fourier bridge.
It checks 272 Pauli edge blocks (1,056 bank columns), 16 data matrices
(192 columns), 100 omitted-commutation-phase controls and full 8-by-8 physical
matrices, including four residual identities and two nonfactorable endpoints.
Finite checks corroborate the written theorem; they do not prove it by exhaustion.

From repository root, using Python 3.12 and only its standard library:

```sh
python3.12 scripts/research_package.py --package research/phase-bank-intervening-work-audit --check-only
python3.12 scripts/research_package.py --package research/phase-bank-intervening-work-audit
```

The registered commands run with `-I -O -B`; checks use explicit exceptions and
remain active under optimization. The sole external runtime input, unchanged
`research/phase-accumulator-tensor-closure/model.py`, is pinned and declared in
[SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json). The selected record
and catalogue are historical provenance; full Git history resolves their pins.
Direct checkers print their detailed counts and do not write artifacts.
Registered replay passed on Linux x86_64 with CPython 3.12.13.

## Scope, overlap and limitations

This refines the `uniform-transfer-audit` restoration card under priority
revision 5; [TASK.json](TASK.json) records the draw, scientific base, live overlap,
checkpoint and open questions. Coordination is in the
[scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2842#discussioncomment-18966303).
The addition is necessity and frame-correct caller witnesses for P009's existing
sufficient condition. PR2872 and its active independent audit concern fixed-label
paired schedules and bank dimensions; those results are not repeated here.

No selected files, frontier, predecessor program or frozen evidence change.
There is no native cost bound, all-size physical compiler, precision/hosting
proof, complete supplier, selected cold replay or improvement to κ. The paid
Z correction is an algebraic escape with an unproved completed implementation
bill. Arbitrary joint consumers, bank charts and noninvertible cleanup are
outside the theorem's two-controlled-word/data-only interface.

## Open next questions

For a proposed actual caller, pin its intervening program and test its support
in the Fourier control frame, starting with one label-changing edge. A caller
that passes still needs a complete implementation and budget. For a transported
consumer, bind its added bank correction to an actual call site and charge
native execution, full operand movement, precision, hosting and restoration
before expanding the construction. Those obligations remain unknown; structured
questions and first steps are in TASK.json.

## Credit

Prepared by kumagi with substantial OpenAI Codex assistance, including parallel
proof review and a separately implemented checker. These are independent
implementations in one AI-assisted session, not independent human review.
New work is Apache-2.0. Standard Pauli algebra is not claimed as new theory.

- **Gareth Davidson / bitplane**, [PR2850](https://github.com/CrocSwap/integer-mult-bounds/pull/2850),
  `a007c32f992195ad372806db38c9359dd49382ad`: physical producer, exact primitives
  and classical array model. Original source and attribution remain unchanged.
- **Dugongue**, [PR2871](https://github.com/CrocSwap/integer-mult-bounds/pull/2871),
  `894a3edbcd90fc379a277eb07a5ae2b706c7a8e1`: P008/P009 transport and sufficient
  invariant-block contracts, and P095 mutable-output example. Pending collection;
  this audit does not review or adopt its other claims.
- **Tekalign / tekuuu**, [PR2872](https://github.com/CrocSwap/integer-mult-bounds/pull/2872),
  `cc5c2398505447a321fb9f9826163825e3b269fd`: adjacent reviewed encoded-bank and
  paired-schedule results; no code or theorem imported.
