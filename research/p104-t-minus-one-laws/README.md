# P104 t = −1 laws (no κ claim)

This package states laws of the **t = −1 per-port contract** on P104: per port
M = [[1, −1], [1, 0]], so X = x − y and Y = x. Each law comes with its scope and
a standard-library checker. It makes no κ claim and builds no word. The E8/P104
numbers use the Gram matrix of the 104 live lines, computed as D Tᵀ/2 from the
pinned PR968 decoder file. Proofs and premises are in [PROOF.md](PROOF.md).

The σ-rank o(N) = rank(σ(N)N⁻¹ − I), the identity o = rank(q-odd part), Lemma E
and the hub bound are in [#7555](https://github.com/CrocSwap/integer-mult-bounds/pull/7555)
(law 4 there). They are cited here, not repeated.

Tags: **[P]** proved in PROOF.md, **[C]** exact check in this package,
**[cond]** conditional on a named premise.

## Setting: the relay family

A d = 0 MONOHUB relay word has the following parts. G is the Gram matrix of the
port roots (rank r), and Z = G/2 − I sits on the partner cells (G_pt odd).

- **Owned registers.**
  - U is y-only with product −G/2.
  - L is a shared E8-type register that deposits G/2·x.
- **Relays.** Each partner cell (p, t) has a relay R_pt. It lumps −y_t, is read
  by X_p, and re-adds a copy of Y_t.
- **L-side helpers.** They clean the L-junk.

A cell is **settled** when its re-add copies Y_t^final. It is **early** (it
re-adds from an anchor) when it copies a parked owned copy O_t of pure y_t.
D is the V-span deficiency: rank(arrivals + targets) − rank(arrivals).

## 1. Charge law and the corrected anchored law (`charge_law.py`)

- **Charge law [P, C].**
  - If every cell is settled, D = n − r. That is A3: 3, A4: 6, E8/P104: 96.
  - The witnesses are the charges ν_k, for k ∈ ker G. Every charge-neutral
    owned deposit leaves ν_k unchanged; this covers U, the shared L and parked
    copies.
- **Corrected anchored law [P, C].** For early cells E and settled cells S,

  D = dim{(k, k′) : k′ ∈ ker G, (I + Z^S)k + Z^E k′ = 0} − dim ker G.

  - The law matches the exact model on 60 + 30 random early sets on A3/A4, and Y
    is exact on every one.
  - The per-cell form dim(ker G ∩ ker Z^E) is wrong on 8 of the 90 sets,
    because it misses witnesses k ∉ ker G.
- **The σ-anchor schedule [C].** Take one early cell (σ(t), t) per column, with
  σ a perfect partner matching. Then:
  - D = 0 on E8/P104 for all three matchings checked;
  - early cells on c columns give D ≥ 96 − c.

  So under this schedule the owned bill of law 2 is zero, and the owned
  deficiency is not a design-independent law. The cost moves to the L side,
  which must deliver all of column t's L-side charge after Y_t passes its
  partner line. That L-side network is open (see the open questions).

## 2. One owned MOVE cuts the deficiency by at most 1 (`kernel_bills.py`) [P, C]

Owned MOVEs are billed at |Δdim| per row. Let D₀ be the deficiency of the same
word with every owned MOVE cut. Then

D ≥ D₀ − #(owned MOVEs) ≥ D₀ − (owned units).

- A register that climbs k stops fills at most k directions.
- A single MOVE with Δdim = d fills at most 1 direction.
- Free INIT/COPY add nothing beyond the move-free world.
- The rate of 1 direction per unit is attained.
- **Checks.** The bound holds on 3,000 random substitution worlds and is
  attained on some of them. The strengthened control D ≥ D₀ − s + 1 fails.

## 3. Hub deficiencies add to dim K (`kernel_bills.py`) [P, C]

Suppose X finals are settled at hubs 1..m. Write K_j = {k ∈ K : k vanishes on the
finals forwarded to hub j} and D_j = rank(K_j|S_j).

- **Nested hubs.** If each hub sees all earlier finals, Σ D_j = dim K
  exactly.
- **Without forwarding.** Σ D_j ≥ dim K.
- **Consequences.** Hubs redistribute the deficiency and never split it.
  Settlement at several hubs is legal under the current specification, and
  nested hubs cost no extra MOVEs; neither point is checked here.
- **Checks.**
  - The law holds on all 4,683 ordered hub sequences at A3 and on 4,000 at A4.
  - On E8/P104, D₁ + D_V = 96 holds on all 510 hyperplane hubs of the label
    pairing.
  - Counting only the last hub gives as little as 36. That is the error this
    law rules out.
  - One hub per port gives 96 nested and 103 unforwarded.
- **Scope.** The per-hub bound D_j ≥ rank(K_j|S_j) uses the same arrival
  formula as law 5, so for hubs below the relay re-add frames it is [cond] on
  Lemma A.

## 4. The per-J odd unit (`odd_unit.py`)

This builds on #7555's statement that the unit is an integer rank deficit, not a
parity.

- **The native [C].**
  - The t = −1 native is H = [[1, −q], [q⁻¹, 0]], which is M at q = 1.
  - o(Hⁿ) = 2, 2, 0, 2, 2, 0 for n = 1..6, with H³ = −I.
  - SW = J·L_q has o = 1, so the t = −1 native costs **17 odd units per port
    per word** more.
- **The three-register lift [C].** On (X, Y, Z = X − qY), H acts as the monomial
  X′ = Z, Y′ = q⁻¹X, Z′ = −qY.
  - It has o = 2 and cube −I.
  - It is q-free (o = 0) only in the gauge frame Y″ = qY, whose gauge diag(1, q)
    has o = 1 and turns q-free transvections odd.
  - So the finite order M⁶ = I is available only inside a gauge that costs the
    same units.
- **Automorphisms [P, C].** σ-fixed global automorphisms leave o unchanged,
  because σ(UNU⁻¹)(UNU⁻¹)⁻¹ = U·σ(N)N⁻¹·U⁻¹. This is checked on 200
  conjugations, and a control that is not σ-fixed does change o.
- **Gauge shifts [cond].** A gauge-shifted contract that is −1 on m roles pays
  ≥ m − 16 odd ops in the word (Lemma E, #7555). It also pays 36 − m odd units
  at the boundary, a figure that rests on the premise that boundary units are
  child-size σ-odd transforms. The total is ≥ 20 per port per word for every m,
  against 3 for the unshifted design.

## 5. Y-atom conservation [cond: Lemma A]

**Statement.** D ≥ dim{k ∈ ker G : k_N = 0} ≥ n − r − N_neutral − N_owned,
where N is the set of atom columns: columns whose y-atom leaves during Y's
neutral period, or through an owned copy.

- **Status.** The inequality is [P] given premise PA (Lemma A), and PA is open.
  Combined with law 2, it gives owned cost ≥ n − r − N_neutral for the relay
  family. That is **96 per call on E8/P104 when N_neutral = 0**.
- **Checks.**
  - [C] dim{k ∈ ker G : k_N = 0} ≥ n − r − |N| for every column set N at A3 (64)
    and A4 (1,024). The bound is tight at every |N|.
  - Not every set of n − r columns spans (4 sets at A3, 85 at A4).
  - The exhaustive 2²⁴ cell-assignment run on A3 is not packaged. Its bound
    follows from the rank inequality rank(Z^E K) ≤ #(columns with early cells)
    in PROOF.md.
- **Scope.** Lemma A is supported only by author runs on A3/A4/D4 relay and
  engine families, which are not packaged here. It is not proved for arbitrary
  programs.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-t-minus-one-laws
```

There are three commands, listed in [VERIFY.json](VERIFY.json), and all of
them use the standard library only.
- Each prints the numbers it reproduces, asserts them, and runs a control that
  must fail.
- The PR968 input is authenticated by SHA256.

## Caveats

- Laws 1, 3 and 5 are stated for the relay family:
  - U-junk is cleaned by lump/read/re-add relays;
  - owned deposits are charge-neutral;
  - X finals sit at V, or at the hubs of law 3.
- In law 1, a cell is either early or settled. Other timings are outside the
  check.
- Law 4's boundary count depends on its stated premise. The 17 stages, 36 roles
  and 96/104 ports enter as parameters of #7113's caller.
- Lemma A is open, so law 5 and the below-re-add-frame case of law 3 are
  conditional.
- No human has reviewed the package.

## Open next questions

- **Lemma A.** Is PA true for arbitrary legal programs?
- **The Y-prefix L side.** Can the σ-anchor schedule's L-side network be built
  at public cost below the U-side relay floor?

See [TASK.json](TASK.json).

## Credit

The E8/P104 Gram comes from PR968's decoder. The t = −1 contract and its
17-stage role pairing are those of Rohan Arun's signed #7113 caller lineage. See
[NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Apache-2.0.
