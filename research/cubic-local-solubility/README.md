# Three cube queries survive every finite odd-modulus test

**Scoped obstruction-method result; no new κ.** Prepared by apoursh with
substantial OpenAI Codex assistance. Apache-2.0.

For every integer arity r>=3 and every odd modulus m>1, the fixed cubic-reader
defect has a representation modulo m by at most three weighted cubes. The
source forms can be reached using **integer determinant-one shears**, with
both arbitrary incoming sources restored **exactly**. Output repair is only
modulo m. One explicit construction uses at most 31 source shears and three
query slots; zero events can be omitted.

Consequently, failure of unrestricted three-query feasibility in a finite
odd quotient cannot prove a four-query lower bound. The same conclusion holds
for any finite collection of odd moduli by using their least common multiple.
This answers one possible route in Open next question 1 of Nick Petalas's
[PR6653](https://github.com/CrocSwap/integer-mult-bounds/pull/6653), which
suggests testing odd-prime valuations at the unresolved arity 15.

**It does not settle exact dyadic feasibility at r=15 or classify all arities.**
Arguments coupling prime valuations of a single global rational representation
remain possible. Local solutions are allowed to differ between primes; a
modular certificate need not give an exact output identity over Z[1/2].

## The construction

Let S=r(r-1)/2 and n=2r-1. The defect from the retained original children is

```
f_r = 3S A^2 B + Sn A B^2 + S^2 B^3.
```

The [proof](PROOF.md) derives a three-cube identity on directions
0,1,(3r-1)/4 whose coefficients are integral at 3. The rational extension of
apoursh's PR6215 pure-B identity is integral away from 3. Split
m=3^v*b, gcd(b,3)=1, and combine the three weights and five shear slots for
each source frame by CRT. This produces integer instructions with literal
inverse instructions; no unproved source-frame lifting assumption is used.
The construction is independent of the input values, retains all children,
and needs no source snapshot, clean scratch, output feedback or child access.

The discriminating case is r=15:

```
f15 = -(245/11) A^3 + 14(A+B)^3 + (91/11)(A+11B)^3
    = 315(A+5B)^3 - (35/3)(3A+14B)^3 + (10990/3)B^3.
```

The first identity works modulo powers of 3; the second works modulo every
integer coprime to 3. Neither displayed rational identity is a dyadic repair.
CRT solves every finite odd-modulus test, without supplying one exact global
repair. The independent checker exhibits an actual modulo-33 repair that
restores A,B but misses the exact eager output by -13472019.

## Evidence and replay

CPython 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-local-solubility
python3.12 -I -W error -B research/cubic-local-solubility/verify.py
python3.12 -I -W error -B research/cubic-local-solubility/independent_check.py
```

The registered replay runs both checkers normally and with `-O`; explicit
checks remain active under optimization. No network, solver or generated
artifact is needed by either direct checker.

- [verify.py](verify.py) proves both displayed coefficient identities by exact
  polynomial arithmetic in Q[r] after clearing the nonzero denominators.
  It checks the complete three-case denominator argument modulo 3, constructs
  3,682 integer-shear modular certificates, and symbolically executes every
  retained child, query and inverse. Seven algebra/program rejection controls,
  eight domain controls and three source-byte mutation controls must fail.
- [independent_check.py](independent_check.py) imports neither the primary
  checker nor predecessor code. It directly expands both rational identities
  for r=3..128; its distinct construction combines source rows, then uses
  primitive integer lifts and Bezout frames. It checks 1,344 certificates,
  5,376 literal dirty-input executions, three rejected faulty variants and
  the exact-versus-modular counterexample.
- [PROOF.md](PROOF.md) supplies the all-arity/all-modulus argument. The finite
  check domains are corroboration, not an extension by enumeration. The two
  implementations are separate Codex-agent work; independent human and
  formal proof-kernel review are not claimed.

The symbolic event inventory includes the initial restoration, every frame,
every inverse and all query slots. Physical pricing, coefficient preparation,
precision, storage, routing and a matched caller invoice remain unknown.
No bound improvement, priced supplier, shear optimality or modular query
minimum is claimed. The selected construction and its five assumptions remain
unchanged.

## Scope and coordination

[TASK.json](TASK.json) retains the exact `joint-query-controller` contextual
card and declares changed scope: a limitation on the finite-congruence
obstruction method, rather than a complete physical query-controller supplier.
The family decision is **narrow**: close this particular obstruction route,
then stop. This differs from the exact r=24 certificate in
[PR7475](https://github.com/CrocSwap/integer-mult-bounds/pull/7475) and the
fixed-weight Pell family in
[PR7478](https://github.com/CrocSwap/integer-mult-bounds/pull/7478).
Neither pending contribution is a mathematical or executable dependency here.

Canonical upstream was pulled at entry to
`e54523517d0f03e58352e647c403a5af3e525a57`; guidance is unchanged from the
preceding round. Selected-baseline source orientation passed, not a scientific
cold replay of the selected supplier. Live all-state PR title/body searches on
2026-11-12 for `cubic local solubility`, `cubic odd moduli`, `three-query CRT`,
`cubic finite quotient` and related phrases found no duplicate. The nearest
modular obstruction, PR6215, explicitly requires a nonzero original-B query;
our 3-primary construction need not retain that restriction.
The dedicated overlap helper lacked remote corpora because `gh` was absent;
accessible Discussion pages were cached and did not certify current claims.
No absence-of-overlap guarantee or public reservation is asserted.

## Open next questions

1. **Global arithmetic at r=15.** Can one exact rational three-cube
   representation have all actual form coefficients and weights dyadic?
   Start with the predecessor node equation and compatibility of valuations
   across one fixed triple, or exhibit a primitive-row certificate. This
   matters because three versus four remains unresolved. Mere nonexistence
   in a finite odd quotient is now excluded as a method.
2. **Restricted direction families.** Which additional constraints on a
   three-query program create a valid modular obstruction? Start from
   PR6215's original-B restriction and check whether the constraint survives
   CRT patching. A precise contract is required: the unrestricted theorem
   does not erase existing restricted-family lower bounds.

Concrete first steps and blockers are also in TASK.json. Physical pricing of
these modular witnesses is not proposed as a supplier-development task.

## Attribution and exact sources

Nick Petalas's PR6200 supplies the fixed reader and defect; his PR6653 supplies
the node lemma and open classification question. apoursh's PR6212 supplies
the dyadic general-frame contract and lower-bound context. apoursh's PR6215
supplies the pure-B identity and its explicitly restricted modulo-nine
obstruction; we use that identity rationally outside its dyadic attainment
classes and retain that distinction. The new result is the complementary
prime-local identity and the universal CRT consequence with legal integer
source frames, not a claim to the Chinese remainder theorem or classical
binary-form decomposition.

[SOURCES.json](SOURCES.json) pins the exact predecessor bytes at the canonical
base, alongside historical provenance for the task catalogue and selected
record. All three proof-relevant inputs are declared in VERIFY.json. Frozen
sources, predecessor code and shared infrastructure are unchanged.
