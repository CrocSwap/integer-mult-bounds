# Exact two-row nonunit dirty-fanout tariffs

For two arbitrary dirty rows and a preserved common source, this proves the
exact cost for **every pair of demands with comparable principal left ideals**,
including all demands over Z/p^k. The five-term price formula covers arbitrary
positive, stationary, coefficient-independent source and directed-ADD prices.
It includes zero demands and noncommutative coefficient rings.

This answers the structural two-row part of Nick Petalas's
[#4916 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134896).
The predecessor's unit-demand theorem and its Z/4 optimum-four example are
retained and credited. The new result is an all-price theorem with attaining
words, including a regime in which one source insertion and four ADDs beat
both valid forests and repeated source insertion. No new κ is claimed.

## Contract and result

Write the required outputs as `A_i = a_i + λ_i p`. Each original `a_i` and
the disjoint source p is arbitrary; p is preserved. Allowed calls are
`P_i(β): A_i += β p`, price μ_i, and `E_i(α): A_i += α A_(1-i)`, price c_i.
Coefficients multiply on the left. There are exactly two rows, no extra
workspace, free basis changes, clearing or intermediate observers.

For j=1-i, let `x ≼ y` mean `x ∈ Ry`. Assume `λ_0 ≼ λ_1` or `λ_1 ≼ λ_0`.
Define

```text
D   = [λ_0 != 0] μ_0 + [λ_1 != 0] μ_1
S_i = μ_i                     if λ_j = 0
      μ_i + 2 c_j             if λ_j != 0 and λ_j ≼ λ_i
      μ_i + 2(c_i+c_j)        otherwise
T_i = 2 μ_i + 2 c_j

OPT = min(D, S_0, S_1, T_0, T_1).
```

The [proof](PROOF.md) counts source insertions and uses a two-row return
lemma: a nonzero ADD direction cannot occur exactly once if arbitrary dirt
must return. It then constructs every price option. This elementary proof
does not invoke the predecessor's disjoint-branching theorem.

For Z/4 demands `(2,1)`, μ=(1,9), c=(1,1), the credited optimum is four,
using two source insertions at the cheap row. With μ=(100,1000) and the
same demands/ADD prices, the optimum is 104: one insertion and four ADDs.
Repeated insertion costs 202. The two constructions trade off at μ_i=2c_i;
neither can be omitted from the general optimum.

## Exact evidence

- **522 independent shortest-path runs:** all demand pairs over Z/2, Z/3,
  Z/4, Z/5, Z/8 and Z/9, for all 81 price vectors in `{1,2,3}^4` plus six
  asymmetric vectors. All **17,313 optimum comparisons** agree. The oracle
  visits 179,845 settled affine states and scans 5,080,872 transitions in
  total; these are sums over runs, not distinct global states.
- **2,591 attaining words:** all comparable pairs over seven modular rings,
  F2[e]/e² and M2(F2), checked on all three formal input columns and their
  inverses (7,773 column checks). The 58 incomparable pairs are rejected.
  Literal complete dirty/source domains add **4,800** execution/inverse checks.
- Controls cover the already-known nonunit boundary, the new mixing regime,
  omitted preparation, unreturned dirt, wrong mixing sign, wrong coefficient
  order, left/right ideals, zero demands, a zero-demand temporary anchor,
  and ten malformed/out-of-scope inputs.

`shortest_path.py` directly explores exact six-coefficient affine states with
every legal nonzero modular coefficient. It imports no tariff code, applies
no depth cap, and stops only when all target distances are settled. Its
returned paths are also replayed by the primary literal interpreter. A
separate supporting agent implemented this oracle; the primary agent reviewed
and integrated it. This is automatic corroboration, not independent human
acceptance. The universal theorem rests on the written proof.

`RESULT.json` is generated and binds the local proof/code/metadata bytes and
the pinned predecessor README. It excludes timings. Normal and optimized
verification compare the full typed receipt; bool/int changes are unequal.
The direct checker loads exact source bytes without consulting `.pyc` files.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/two-row-nonunit-fanout --check-only
python3.12 -B scripts/research_package.py --package research/two-row-nonunit-fanout
python3.12 -I -W error -B research/two-row-nonunit-fanout/verify.py
python3.12 -I -O -W error -B research/two-row-nonunit-fanout/verify.py
python3.12 -B scripts/check_research_commit.py --package research/two-row-nonunit-fanout --check-source-history
```

The direct marker is `PASS_TWO_ROW_NONUNIT_FANOUT`; each registered command
has a 120-second cap. To generate a new receipt after an intentional source
change, use `verify.py --write-receipt NEW_PATH`; it refuses to overwrite any
existing output. Do not hand-edit the receipt.

Scientific base is canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`,
priority revision 7. Exact source pins and the explicit changed task scope are
in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json). The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5030)
records the claim and publication. The selected-source orientation passed;
that is a metadata binding check, not a selected operator replay.

## Scope and limitations

The proof permits arbitrary rings with comparable demand left ideals and
positive real tariffs. The reference code uses explicit finite rings and
positive rational tariffs. The finite shortest-path census is only the six
named modular rings and price vectors. More rows and incomparable demand
ideals are not solved. No complete physical tariff matrix, native caller,
frame/hosting/precision/tape implementation, compiler or outer admission is
provided. No Lean, selected scientific cold replay, independent human review
or full multiplication theorem is claimed. Selected κ remains 0.00302015.

## Open next questions

1. **Incomparable demands.** Start with `(2,3)` over Z/6 and one asymmetric
   price matrix. A general one-insertion orbit/cost criterion is missing;
   the reverse-divisibility construction need not exist.
2. **Three dirty output rows.** Start with `(2,1,1)` over Z/4 and one full
   price matrix, deriving a word and cut bound before a larger search.
   Shared temporary use can evade the two-direction classification.
3. **An actual caller.** Charge every source access, coefficient, frame,
   movement, lifetime, restoration and precision operation. That missing
   physical invoice blocks any inference of a recursive supplier gain.

The structured relevance, first steps and blockers are also in TASK.json.
This contribution stops at the proved two-row algebraic result.

## Credit

Prepared by Krzysztof Wójt (@krzysztofwojt) with substantial OpenAI Codex
assistance in derivation, implementation, verification and writing. Apache-2.0.
Credit Nick Petalas #4916 for the unit-ring extension, explicit nonunit
handoff and optimum-four example; Ross Richardson #3121/#3063 for directed
XOR tariffs and the dirty-output model; Cinna Davis #1944/#1968, Anthony
#774, Oscar Fennell #759, Tekalign #3130 and the retained fanout lineage.
No predecessor executable or full census is rerun as a new contribution.
