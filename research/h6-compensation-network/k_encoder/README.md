# Explicit full-width K encoder, scatter and restoration

This package removes the abstract `K_interface` from the bounded composed compensation fixtures. It supplies a canonical compressed **all-port scalar/frame stream** using the frozen PR606 operator factorization, 816 ordinary dirty centers, and 816 separately paid private copy episodes. It preserves the predecessor packages. Attribution: Dominik Scholz's PR606 operator factorization and the earlier complex gauge private-copy emitter; the new polynomial coefficient audit, composed emitter and replay were prepared with substantial Codex assistance.

```sh
python3 -B research/h6-compensation-network/k_encoder/network.py
```

The result is a complete finite local scalar/frame construction. Physical frame representatives, adapter/Clifford compilation, scalar coefficient private-stream compilation, precision and all-size analytic admission remain required before calling it an admitted supplier.

## Complete factor identity

The frozen `e8_sections.py::evaluate_operator_centers` gives integer features E on all 30,960 ports, integer diagonal weights w, and denominator 8192:

```
K = E diag(w) E^T / 8192.
```

There are 112 distinct pure cubic features and, for each of 16 linear coordinates, one unary feature, seven Fano features, 35 traceless Pauli features and one trace feature: 112 + 16×44 = 816. Weights are respectively 16, 32, 4, 1 and −3. The full spectrum/rank proof is separate; the emitter needs the complete factor identity.

The new audit expands every feature as a degree-three polynomial on the doubled-coordinate sphere Σu_i² = 16. Replacing u_i by Σ_j u_i u_j²/16 gives `E = monomials A^T/12`, with A integral. It verifies every entry of the exact integer identity

```
A^T diag(w) A = 384D − 96UU^T,
```

where D contains cubic multinomial coefficients and U expresses Σ_j u_i u_j². This checks all 665,856 coefficients and proves the factor identity for **every pair on that sphere**, including all 958,521,600 ordered shell pairs. It is a polynomial identity certificate, not a sampled dense factor comparison. Additional exact evaluation checks connect the independently expanded recipes to the frozen evaluator on 52 actual rows.

## Emitted logical word

Every ordinary center c begins with arbitrary independent dirt d_c at frame zero. Every source x_s begins at its actual line P_s, and every target y_t begins at zero. The compensation prefix first precompensates and gathers its own ordinary edge helpers while sources remain at P_s. The K center prefix, also at zero, performs

```
y_t += −(w_c E_tc / 8192) c.
```

Sources then climb to FULL. Each ordinary center climbs zero→FULL, paying rank 17, and gathers `c += E_sc x_s`. For each center sequentially: begin a cleared private stream at FULL, copy c, descend FULL→zero paying rank 17, scatter `y_t += (w_c E_tc/8192) private`, and erase that private stream at zero. All private copies are erased before any ordinary center cleanup. Undo each gather at FULL. Targets climb zero→Q_t paying rank 16. The compensation suffix scatters at Q_t and restores its edge helpers at FULL.

Consequently each K center is restored to d_c, each source is logically unchanged, and each target receives Kx with all center dirt canceled. Composed with the explicit I−K edge word, the endpoint map is y += x. Every gate requires identical current frames; ordinary moves are nested and private lifetimes do not overlap ordinary moves.

In the same-order inverse-transpose orientation, ordinary additions dualize `dst += q src` to `src += −q dst`. A private episode instead begins cleared at zero, gathers the weighted targets, ascends to FULL, subtracts its value from the ordinary center and erases there. This is the explicit counterpart of the inherited private-copy emitter; its endpoint map is x -= y. The private rank charge is unchanged.

`event_records(P,packed,range(30960),W,dual)` is the full compressed iterator. It avoids a dense compensation edge list and emits add, ordinary climb, private begin, private transition and private end events. It contains no K operator macro. The full stream is defined and counted but not materialized or replayed event-by-event: it has 3,388,192,272 events. The 8- and 32-port fixtures use actual pinned factor columns, all 816 ordinary centers and private episodes, both orientations, and independent arbitrary dirt/input columns. Fixture construction and the streaming iterator are checked for exact equality.

## Fully charged local accounting

The conservative full-width realization replaces the narrower predecessor support bill with:

| Item | Count / rank charge |
| --- | ---: |
| Ordinary K center roles, each path [17] | 816 |
| Private FULL↔zero episodes, each rank 17 | 816 |
| Private descent bill C | **13,872** |
| Full factor feature incidences M | 6,440,208 |
| K weighted additions, four per incidence | 25,760,832 |
| K forward scalar primitive upper bound | 247,217,040 |
| K dual scalar primitive upper bound | 247,219,488 |

The primitive bounds use the inherited binary Horner weighted-add convention: `3 + bits(|numerator|) − 1 + popcount(|numerator|) + bits(denominator) − 1`. Clear and copy cost one each; the dual copy replacement unit addition costs four. These are scalar primitive counts before any physical real-component doubling. Gathering coefficients have absolute value at most 16; scattering/precompensation coefficients have absolute value at most 1/16. Full coefficient histograms are retained in `RESULT.json`. Signs and denominators are exact dyadics. The forward/dual difference is three primitives per private episode.

The ordinary center roles and private descent episodes are distinct charges. An outer invoice must use C=13,872 and additionally bank **816 ordinary center roles with path [17]**, alongside all compensation edge helpers. It must also include their pads, replication, the data paths, and the actual scalar/precision compiler costs; neither the old C=12,752 nor a free encoder assumption applies to this realization.

Negative controls remove center dirt precompensation, gather, scatter, FULL restoration and private erasure. Both 8-port orientations reject each omission. All fixture replays check every initial ordinary register column, endpoint shear, identical current frames, monotone paths and complete private erasure.

## Open next questions

The next gate is the full outer invoice for the conservative C=13,872 / 816-center realization together with the enormous edge-helper construction. A favorable invoice is not expected, but it gives a concrete legal local fallback. The subsequent physical/compiler gate needs explicit endpoint representatives and adapters, emitted coefficient streams with cleared lifetimes, precision/tape bounds under compensation's enlarged intermediate inputs, and the inherited all-size analytic transfer. This package makes no improved κ claim.
