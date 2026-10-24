# Which coefficients admit exactly two short rows?

**Task:** independent-moment (a complete answer, within the row model, to #4600's open question 1). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## Background

petalas's #4600 (head `44640c4a`, open) works in #4280's row model of balanced unsigned depth-four dirty chain words with modulus m. It proves that two short rows realizing c ≠ 0 force **m | cL** for each short length L. Unit coefficients therefore need at least three short rows. It also gives the family m = 8t, c = 4t. Its open question 1 asks which nonzero coefficients admit exactly two short rows, noting that the annihilator condition is not known to be sufficient.

The model is the following. Profiles λ (row lengths L_q), ρ and β each have m nonincreasing entries in [0, m], with B(L) = β₁ + … + β_L. A triple is correct exactly when

```text
Σ L_q = Σ ρ_q = Σ β_p = 0,   Σ ρ_q L_q = Σ B(L_q) = 0,   Σ ρ_q B(L_q) = −c   (mod m).
```

## Results

### Theorem: gcd(c, m) = 2 is impossible, with a written proof

If exactly two short rows realize c ≠ 0, then **gcd(c, m) ≥ 3**.

**Proof.** Let g = gcd(c, m). By #4600, m/g divides L₁ and L₂, and L₁ + L₂ = m. If g = 2, then L₁ = L₂ = m/2, and the congruences become

```text
(r₁ − r₂)·m/2 ≡ 0,   2·B(m/2) ≡ 0,   c ≡ −(r₁ + r₂)·B(m/2)   (mod m).
```

The first makes r₁ − r₂ even, so r₁ + r₂ is even too. The second gives B(m/2) ∈ {0, m/2}. Hence c ≡ 0 (mod m), a contradiction. ∎

### Exact enumeration for every m ≤ 12

The enumeration ranges over all nonincreasing ρ and β, and every placement of the two short rows after the full rows. It shows that **the achievable nonzero c are exactly {c : gcd(c, m) ≥ 3}**:

| m | achievable c | allowed by m \| cL but not achievable |
|---|---|---|
| 4 | — | 2 |
| 6 | 3 | 2, 4 |
| 8 | 4 | 2, 6 |
| 9 | 3, 6 | — |
| 10 | 5 | 2, 4, 6, 8 |
| 12 | 3, 4, 6, 8, 9 | 2, 10 |
| 2, 3, 5, 7, 11 | — | — |

- **The annihilator condition alone is not sufficient.**
- **The strengthened condition is exactly right for m ≤ 12**, and the construction below extends this to every m.

### Theorem: gcd(c, m) ≥ 3 is sufficient for every m, with an explicit construction

Let g = gcd(c, m) ≥ 3, d = m/g and c ≡ g·r with 0 < r < d. Take

```text
λ = (m, m−d, d, 0, …),   ρ = (m−g, g, 0, …),
β = ((g+1)^r, g^(d−r), M, 1^r, 0^(d−r)),
```

where M is the balanced nonincreasing sequence of length (g−2)d and sum m − 2r. Its entries lie in [1, g] because g ≥ 3.

- **Profiles valid.** All three profiles are nonincreasing with entries in [0, m].
- **Partial sums.** B(d) = m + r, B(m−d) = 2m − r and B(m) = 2m.
- **Congruences.** Σ L = 2m, Σ ρ = m, Σ ρL ≡ −gd ≡ 0 and Σ B(L) = 5m. The coefficient is −[(m−g)·2m + g(2m−r)] ≡ g·r = c. ∎

The verifier checks the construction for every pair (m, c) with m ≤ 200 and gcd(c, m) ≥ 3, which is 4,626 pairs.

**So within #4280's row model, exactly two short rows realize c ≠ 0 if and only if gcd(c, m) ≥ 3.**
- **Family check.** #4600's family m = 8t, c = 4t is checked directly for t = 1, …, 64: valid profiles, all congruences, exactly two short rows and c = 4t. This agrees with the table, since gcd(4t, 8t) = 4t ≥ 4.

## Verify

```text
python3 -B research/two-short-row-coefficients/verify.py
```

The check takes about 3 s and uses the standard library only.

## Limitations

- **Inherited assumptions.** The row model and its converse (every correct triple comes from a balanced word) are inherited from #4280 and are not re-proved here.
- **Not claimed.** A call-count claim beyond #4600's, a physical caller, a supplier or κ.

## Open next questions

- **Beyond the balanced row model.** Every balanced word uses each call exactly m times, so every coefficient realized here costs exactly #4600's 4m calls. The open direction is unbalanced or signed depth-four words, where short-row counts and call counts can separate. First step: restate #4280's congruences for a word with one call used m + 1 times.

Credit: petalas (Nick Petalas) for #4600 and #4280 (row model). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
