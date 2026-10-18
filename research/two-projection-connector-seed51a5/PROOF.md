# Exact construction and charged boundary

## 1. Contract

Work over the field F2 with five arbitrary source rows x0..x4, 31 arbitrary dirty output rows y_m indexed by masks m=1..31, and two arbitrary dirty helper rows z0,z1, all of common length L. The source and output maps B_j and A_m are arbitrary compatible exact F2-linear maps. The required map is

```text
y_m <- y_m + sum_{j in mask m} A_m B_j x_j
```

with every x_j and both helper rows unchanged. The old targets are arbitrary and are only incremented. The operation schedule is independent of row contents.

The inherited one-row multiplication calls, acting in the current physical helper frame, are

```text
B_j: z0 <- z0 + B_j x_j
A_m: y_m <- y_m + A_m z0
```

The changed interface permits paid invertible linear frame changes on the two helper rows. Each inherited B_j and A_m operation still acts on physical row z0; the frame maps it to a logical direction. The only extra operations are the charged row XORs u0 and u1. No product is combined with another product; no copy, clean row, overwrite or observation is used.

## 2. Global frames and conjugated calls

Represent the helper pair as a column z=(z0,z1)^T and a physical frame as p=Fz for an invertible 2x2 matrix F over F2. In the current frame, the base B_j call updates p0. In logical coordinates this injects

```text
F^-1 e0 * B_j x_j, where e0=(1,0)^T.
```

A base A_m call reads physical p0, so its logical readout covector is the first row e0^T F. The helper state is unchanged by A_m.

Use the two one-CNOT frame generators

```text
u0 = [[1,1],[0,1]]    (physical z0 <- z0 + z1)
u1 = [[1,0],[1,1]]    (physical z1 <- z1 + z0)
```

The identity frame gives source direction (1,0) and readout covector (1,0). Frame `u1` gives source direction (1,1). Frame `u0` gives readout covector (1,1). The implementation maintains a global frame instead of returning to identity after each call. A transition from current frame F to next frame G applies G F^-1 to the physical helper pair. Each generator used in this transition is charged as one full-row XOR. The final frame is identity.

`EXPECTED.json` gives the frame action at each readout group and source call. At every boundary, readouts with the same covector are contiguous; when both covectors occur, both group orders are considered. The two covector classes require disjoint frame sets, and the target updates at one boundary commute, so interleaving the classes cannot shorten a frame path. A dynamic program over all six elements of GL(2,F2), the permitted frame sets for each action, and shortest generator paths finds the minimum transition cost for this fixed boundary-pair table: 10 full-row XORs. It does not minimize over alternative boundary pairs.

## 3. Source path and projections

Use the fixed source word

```text
0,1,0,1,2,3,4,2,4,3
```

Sources 0,1,2,4 use injection vector (1,0); source 3 uses (1,1). Each source therefore occurs twice in one fixed direction, so its complete contribution to the two helper rows is zero. This restores both helpers for every dirty incoming pair.

For boundary t=0..10, let q_t in F2^5 be the XOR of source labels seen before that boundary. The (1,0) readout sees every source, so paired readouts at s,t contribute q_s+q_t. The (1,1) readout pairs with the injection vectors as

```text
(1,1) dot (1,0) = 1
(1,1) dot (1,1) = 0
```

and therefore sees exactly sources 0,1,2,4. Its prefix is q_t^reg, the source-3-deleted path.

Direct XOR of the eleven listed prefixes gives

```text
|D(q)| = 26
|D(q^reg)| = 16
D(q) union D(q^reg) = F2^5
```

The all-source projection misses exactly `10001`, `10010`, `10011`, `10101`, `10110`, and `10111`. All six occur as differences in the regular-source projection. `EXPECTED.json` records one strict pair s<t for each of the 31 nonzero masks and the readout covector used there.

For output m, make two A_m calls at its certified boundaries using the same covector. The arbitrary incoming helper contribution appears in both calls and cancels in characteristic two. The remaining source contribution is exactly the boundary-difference mask. Since readout calls leave helpers unchanged and target rows are distinct, all 31 pairs can be interleaved with the fixed source word. Each target receives its requested map and nothing else.

## 4. Lower bound and exact query count

Every active source operator B_j must occur at least twice: one nonzero vector injection cannot restore an arbitrary dirty helper pair, and zero occurrences cannot produce the A_m B_j x_j term. Each nonzero output operator A_m needs at least two readouts: with all B_j=0, the aggregate readout covector on an arbitrary dirty helper pair must vanish, which a single nonzero covector cannot do. Therefore any schedule in this complete-call interface uses at least

```text
2*5 + 2*31 = 72
```

multiplication calls. The construction uses 10 source calls plus 62 readouts, meeting the bound. This is an exact lower bound only for the stated fixed-physical-port, two-row complete-call interface; no broader circuit lower bound is asserted.

## 5. Full cost invoice

The pinned one-row child prices in `research/universal-connector-boundary/CERTIFICATE.json` are

```text
B prices = (1,4,10,16,28)
A_m price = 1 for all 31 outputs
```

Every B_j occurs twice, so the source-side invoice is 2*(1+4+10+16+28)=118 rank-one children. The 62 readouts cost 62, for 180 total. The pinned one-row `five_extra_output` schedule has ten source calls, 64 readouts and 182 children. Thus the two-row construction saves exactly two rank-one children and two complete calls relative to that schedule. PR #1770 at head `caae2d1a0b4497fbd5a7cd2d057d9a9b099f8873` reports the exact one-row weighted optimum 182 for these source/readout prices; that open PR is a comparator, not an imported dependency.

The globally scheduled fixed-port frame charge is 10 full-row XORs, or 10L bitwise XORs, plus one additional L-bit dirty helper row. PR #1812 at head `e43abcde1c98c718f5b4d0b25cf4cd9c04200bd8` has a different two-root alphabet: B/A calls may choose either physical root, and its one-way transfer count is eight. Here every B/A call stays on physical row z0 while both shear directions implement the two projections. The contracts are not ordered without port-access and row-XOR prices. Independently conjugating each special B call and each nontrivial A readout would use 28 row XORs; frame persistence removes 18 of them for this fixed boundary table. The shortest-path proof is only for the certified pair choices. If P(L) denotes the value of a rank-one child and X(L) the value of a full-row XOR, the local arithmetic advantage over the pinned one-row optimum is 2P(L)-10X(L), with one additional helper row of storage. This break-even inequality leaves linear-operation constants and helper placement explicit. The package does not assert a finite-size win, supplier adoption, or a change to the accepted kappa.

## 6. Bounded search and controls

`verify.py` generates all 945 restricted-growth pair words and tests all 32 assignments of the two source directions. Across the full 30,240-candidate domain, it finds 175 two-projection full covers; this count is a bounded search result, not a universal impossibility statement. The selected witness is then checked by a literal physical-row replay whose seven basis symbols are the two arbitrary incoming dirty helpers and the five formal products B_j x_j.

The verifier includes four negative controls: remove the second projection; make all source directions equal; corrupt one certified boundary pair; or omit a required frame-transition XOR. Each causes a mask failure or an invalid frame/helper state.
