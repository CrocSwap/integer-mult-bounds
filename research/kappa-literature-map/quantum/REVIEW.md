# Phase-aware circuit synthesis and borrowed workspace: a tested literature transfer review

Prepared for Dugongue with substantial OpenAI Codex assistance. Review date: 22 October 2026. This lane selects 18 primary papers; 15 were read beyond their abstract at the definition, theorem, construction or argument-excerpt level. The labels in SOURCES.json distinguish that work from a whole-paper proof audit. No new κ, complete supplier or five-input/fourteen-call unit is established.

The strongest immediately usable transfers are a phase-refined search representation, an explicit distinction between operator-word cost and paid supplier cost, and scoped ownership/restoration checks for borrowed arrays. These are constructive tools with exact tests. The literature does not supply a cost-preserving conversion of our nonunitary two-bank shear into an ordinary quantum Clifford circuit.

## The actual project interface being assessed

The source model comes from Jacob Alan Sussman's [PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628), the original prefix from lee-phys's [PR #4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), and the phase repair and residual identities from Yiyang / Lyy-iiis's [PR #4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710). The frozen cp22f full-input port is read as a predecessor, with hashes in PROJECT-PINS.json; no source is silently replaced by a projectively equivalent matrix.

For a base address bit j, put

    C_j = α I + β X_j,   α = (1+i)/2,   β = (1-i)/2.

An individual letter G_f means G raised to its f-fold tensor power. In the repaired prefix, P and Q are the actual phase-bearing monomial words, A_f = C0_f and L_f = P_f + 2 Q_f. The complete two-call map on independent arrays x and y is

    U_f(x,y) = (A_f x, A_f y + A_f L_f A_f x),
    U_f = [[A_f,0],[A_f L_f A_f,A_f]].

Its reverse is [[A_f^-1,0],[-L_f,A_f^-1]], also two paid calls. Its norm and inverse norm are at most 4. The third-call lift has the separately tensorized target-bearing residual M_f C2_f + 2 K_f a_f, but the arbitrary second input remains additively present. These are already proved cp22f interfaces, not new findings of this review. No additive sum is tensorized as a single letter.

Three different objects must remain separate: the small base operator, the full address-array transform, and the independent banks of the supplier. A qubit wire is a tensor factor of an amplitude space; a bank in U_f is a direct-sum component carrying an arbitrary independent input array. Confusing those representations gives incorrect ancilla and productive-output accounting.

## 1. A phase-refined finite synthesis kernel is the highest-priority transfer

[Dehaene–De Moor](https://arxiv.org/abs/quant-ph/0304125) identify binary linear/quadratic descriptions of Clifford operators. [Bravyi–Maslov](https://arxiv.org/html/2003.09412), Theorem 1 and equations (1)-(3), give a constrained canonical factorization into Hadamard-free pieces, a Hadamard layer and a permutation. Their counting convention ignores overall phase. [Maslov–Roetteler](https://arxiv.org/html/1705.09176), Theorem 13, give a constructive Bruhat-based normal form. These are useful coordinates for enumerating individual base-letter words and quotienting free monomial changes.

The positive implementation recipe is to store a word's symplectic action, the Pauli/sign lift and an explicit central phase. Compose this data before collecting equal terms in a sparse coefficient dictionary. Only literal matrix equality, including its phase, permits coefficient collection in a width-independent identity. Projective equivalence is a screening key, never the final equality key. The cp22f proof already requires this discipline: a base minus sign becomes (-1)^f after tensorization and can alter a residual cancellation at even widths.

A minimal verified core is provided here. With the convention i^k X^a Z^b, the exact multiplication law is

    (a,b,k)(c,d,l) = (a+c,b+d,k+l+2(b·c))

with binary addition in the first two entries and phase modulo 4 in the last. This follows by commuting Z^b past X^c. test.py checks all 4,096 products of the 64 two-qubit phase-bearing Paulis on all four basis vectors: 16,384 exact phase checks. This is a complete finite Pauli-cocycle test, not a complete Clifford-kernel implementation. A full phase-refined Clifford dictionary remains an explicitly untried extension.

The same test checks the quadratic refinement

    x xor y = x + y - 2xy  (mod 4).

The checker also exhausts all 128 two-variable constant/linear/quadratic phase functions under all 24 affine reversible changes of address: 3,072 exact compositions. It reconstructs every resulting phase polynomial with its constant term and even quadratic cross coefficient.

It is the elementary mechanism behind the CZ correction when a quarter-phase is pulled through a parity computation. Forgetting that term preserves a Boolean map while changing the complex operator. The relevant phase-polynomial framework is [Amy–Maslov–Mosca](https://arxiv.org/html/1303.2042), Lemma 3; its CNOT+T region is a linear reversible map decorated by Z8 parity phases. The native application is to the free address/phase stream, not to an unpriced replacement of Gaussian recursion.

A concrete next experiment is to canonicalize each actual base word in the repaired prefix, retain the exact phase lift, and enumerate short controller products as coefficient dictionaries. Every candidate must then reconstruct a literal physical program on all independent banks. Passing a tableau-rank test alone does not complete that program.

## 2. Hadamard optimization supplies a real synthesis coordinate, with a different invoice

[Vandaele–Martiel–Perdrix–Vuillot](https://arxiv.org/html/2302.07040), Definition 1 and Theorems 1-2, optimize a specified Pauli diagonalization-network problem using a binary rank expression. Their final-Clifford and internal-H objectives are distinguished. That is a useful exact synthesis objective; it is not the supplier's objective.

Our independent positive test constructs the entire two-qubit symplectic group with generators H, S and CNOT. A 0-1 shortest-path search charges 1 for H and 0 for Hadamard-free generators. For each of all 720 symplectic matrices M, its exact minimum H count agrees with the rank of the upper-right block in our (x,z) convention. The histogram is 48 classes at cost 0, 288 at cost 1 and 384 at cost 2. This validates a complete small search coordinate, while explicitly omitting the phase lift handled by the preceding test. It is neither a global lower bound for our additive supplier nor an exhaustive controller search.

There is a direct model-mismatch example using the actual project primitive. C = H S H also has a one-H realization, with its scalar phase retained. With H0 the unnormalized Walsh matrix and S = diag(1,i),

    C = α S^-1 H0 S^-1.

Equivalently C = exp(iπ/4) S^-1 H S^-1 for normalized H. test.py verifies the exact Gaussian-rational version. At tensor width f this lowers the displayed H count from 2f to f, while the native supplier invoice remains one rank-one Gaussian call before and after. This is an actual strict H-count improvement that establishes no paid-call saving. A compiler that equated those two metrics would report an incorrect κ improvement.

Even a valid large-qubit Hadamard-free normal form needs a native address bill. A fixed base monomial repeated over f digits has an amortized O(V) address/phase odometer, V = 8^f, as in cp22f. A newly synthesized dense transformation on all 3f address bits is a different implementation problem; its per-address matrix/phase evaluation and workspace cannot automatically be called free. Base-word canonicalization is the safest initial transfer because its alphabet and per-digit table remain fixed.

## 3. ZX rewriting can certify more identities, provided scalars and extraction remain explicit

[Backens 2014](https://arxiv.org/abs/1307.7025), Section 5.4, supplies the stabilizer normal-form completeness route. [Backens 2015](https://arxiv.org/abs/1507.03854) is specifically relevant because it repairs scalar-free reasoning into scalar-aware completeness. For our additive prefix, exact scalar equality is required. test.py rejects replacing C by -C inside I+C, although their projective Clifford actions coincide.

[Duncan–Kissinger–Perdrix–van de Wetering](https://arxiv.org/html/1902.03178), Theorem 5.4 and Corollary 5.5, give terminating graph simplification while retaining focused gFlow for extraction. This suggests an explicit workflow: simplify a real operator fragment, extract a concrete word with boundary maps, and replay that word with its phase. A smaller diagram without an applicable extraction theorem is not yet a runnable native program. The graph reductions are an algorithmic tool, not a claim that every extracted gate metric matches the paid profile.

[Cowtan et al.](https://arxiv.org/abs/1906.01734) supply a phase-gadget representation aimed at CNOT/depth optimization. That can shorten free parity-phase streams. [Jeandel–Perdrix–Vilmart](https://arxiv.org/abs/1705.11151) extend exact diagrammatic completeness to Clifford+T; this is a possible certificate language for more general identities, without an automatic optimality theorem. For these two papers only their primary abstracts were read here, because full HTML retrieval hit size limits. They are not proof-audited dependencies.

A state-only certificate is insufficient even within the unitary model: S fixes |0> but differs from I on |1>. This exact rejecting control is included, reflecting the operator-versus-state distinction noted in Aaronson–Gottesman, Theorem 8.

The complete U_f is not a unitary map on the direct sum of its two array banks. If F = A_f L_f A_f is nonzero, the inner product of U_f(x,0) and U_f(0,y) contains the nonzero coupling <F x,A_f y>. Thus ordinary unitary Clifford synthesis cannot directly take U_f as its input specification. test.py gives an exact nonzero-coupling example and rejects U*U = I. This does not say general ZX diagrams cannot express nonunitary matrices: postselection, scalar gadgets or explicit direct-sum encodings may do so. Their semantics, extraction and native resource bill would then have to be supplied; a free quantum-unitary implementation does not follow from matrix expressibility.

## 4. Dirty-workspace literature yields a useful positive native echo, with its full cost

[Gidney's dirty-arithmetic construction](https://arxiv.org/html/1706.07884) specifies unknown borrowed bits that must be returned, with reversible Boolean arithmetic and range assumptions. [Khattar–Gidney](https://arxiv.org/html/2407.17966), Sections 3-4 and Figure 2, distinguish conditional cleanliness from unrestricted dirt and give laddered toggle detection. Its involution and no-control-as-borrowed restrictions matter. An array cannot be declared conditionally zero without a caller-proved invariant and a complete restoration argument.

Here is a sufficient all-input linear analogue, proved directly rather than asserted as an automatic quantum-to-RAM reduction. Let F and G be arbitrary linear maps on compatible array spaces. Starting from arbitrary independent x, y and dirty d, execute

    d <- d + F x
    y <- y + G d
    d <- d - F x
    y <- y - G d.

The output is exactly (x, y + G F x, d). Indeed the two additions into y contribute G(d+Fx)-Gd = GFx, and d is restored before the last update. No commutativity of F and G is needed. This is a universal constructive dirty-workspace theorem over any field; it does not assume d starts at zero.

The update z <- z+F x is not a free oracle when F is paid. When F and G are invertible transforms on equal-sized fields, one explicit implementation applies F to the source array, adds it, and applies F^-1 to restore the source. Under unit-cost forward/inverse Gaussian calls, that is two calls. Consequently the four-update echo costs four F calls plus four G calls, eight calls when each transform is rank one. test.py executes 64 exact arbitrary-input cases with two noncommuting Gaussian-rational transforms and counts all 512 calls. It preserves x and the original dirty array, and produces the claimed y output. This is useful restoration infrastructure; it is not a call-saving supplier by itself.

The native free work is a fixed number of full-array additions and monomial conjugations, O(V) for fixed-digit maps, in addition to those eight charged calls. Fixed-precision execution needs the chosen Gaussian accuracy contract and a propagated guard; the exact algebra test does not invent such an implementation. A different caller may amortize or cancel literal adjacent transform/inverse pairs, but that saving must appear in its physical trace.

## 5. Current 2026 uncomputation work suggests an ownership-aware event compiler

[Liu–Zhou–Meng](https://arxiv.org/html/2608.09578), version 2 updated 11 October 2026, give explicit clean/dirty uncomputation semantics and a sufficient normalization/synthesis route. Theorems 6.5-6.6 concern successful normalization in their circuit language; the method may fail, and its stated sufficient normal form excludes H gates targeting ancillas. This is a soundness pattern to transfer, not a universal optimizer for arbitrary native array programs.

[Xu et al.'s Bona](https://arxiv.org/html/2608.08765), Theorem 4.4, models borrowing as endpoint-DAG edge splicing. Its frozen-topology Theorem 5.1 has a linear-time width computation. General rescheduling is a different problem, and the reported benchmark safety checks are sampled. The practical transfer is to separate symbolic ownership from role numbers, retain allocation/borrow scope and input/output contracts, and reject cyclic lifetime splices before attempting algebraic replay.

Our positive ownership test implements a small native arena with fresh named allocation and an owned-only CLEAR operation. By induction over allocations and clears, fresh allocation does not alias an existing independent input, and CLEAR never changes a borrowed field. This is a precise safety property, not a proof that arbitrary other arithmetic is correct. Last-use liveness and each borrowed operation's restoration still require their own exact algebraic contracts.

The test accepts initialization, mutation and return-to-zero of a fresh owned center while preserving an arbitrary helper input. It rejects clearing a borrowed helper, clearing an unallocated center, allocating over an independent input, and the concrete bad parser pattern center = -1 followed by helper = 632 + center. That pattern aliases helper 631 and had produced a false positive in the preceding campaign. A symbolic owner handle makes the invalid access reject before scalar support or paid-profile optimization. The four rejected controls and four explicit initialization/clear stores are recorded in EXPECTED.json. This is an executable ownership guard, not a claim to have ported Bona or RwUn completely.

A useful next implementation is a typed event IR with distinct BorrowedInput, OwnedZero, OwnedDirty and Returned roles. An authorized borrower can temporarily change a borrowed field only through an operation with a checked restore contract; it cannot acquire permission to CLEAR it. The event compiler should emit initialization/clear array passes and require the same immutable role-to-owner map during forward support, backward liveness, exact scalar replay and paid profiling. This directly addresses a real failure mode rather than merely improving a gate-count benchmark.

## 6. Catalysis and fermionic tools have narrower but concrete transfer contracts

[Gidney–Fowler](https://arxiv.org/html/1812.01238), Section 3, derive a reusable T-state catalyst construction by inverting a state-conversion circuit and feeding a retained output into the next iteration. The productive lesson is an explicit seed, invariant and amortization invoice. Its known nonstabilizer resource state and measurement/injection model are not an arbitrary independent dirty bank, so its factory savings do not transfer numerically to Gaussian calls. A native catalyst proposal must state the exact reusable array relation, preparation cost, error accumulation and returned joint endpoint.

[Jozsa–Miyake](https://arxiv.org/html/0804.4050), Theorem 3, show that a quadratic Majorana evolution closes on the generator span; Theorem 4 attaches product-input and bounded-observable-degree hypotheses to efficient simulation. [Bravyi](https://arxiv.org/html/quant-ph/0404180), Definition 1 and Theorem 1, gives explicit fermionic Gaussian descriptions and conditions. These offer a compact symbolic algebra for a genuinely closed family. They do not by themselves apply a dense operator to every arbitrary complex input array at the desired paid cost.

A cheap exact filter is implemented here: the actual one-bit C primitive does not commute with standard fermion parity Z. It is therefore not a standard even-FLO operation in that encoding. This rejects only that particular import. It does not rule out extended odd/linear Majorana models or the Clifford-twisted representations discussed in the literature. A positive future transfer should exhibit one common anticommuting-generator basis preserved by every required letter, prove its closure, and separately price the arbitrary-array input/output transformation. That common-basis search was not run here.

## Local DAG and Lean-tree reuse, with its actual evidence level

The federated source catalog was queried for Clifford, Pauli, symplectic, catalytic and fermion, at a limit of 8 hits per query. Those searches also found registered downloaded algebra/quantum modules, but only source-record metadata was inspected there. They do not establish executable compatibility, completeness of retrieval or any new theorem audit. A filename scan and targeted reads identified the following canonical project precedents; hashes and safe project-relative names are in LOCAL-PRECEDENTS.json.

| Canonical module | Actual reusable content inspected | Limit |
| --- | --- | --- |
| Mathproof.BinarySymplecticGroupOrder | Binary transvection involution, form preservation and symplectic-group counting declarations | Source-only; no new kernel or phase-lift audit |
| Mathproof.Meta.Problem18CharTwoSymplecticBasis20260929 | A complete paired basis for a finite-dimensional nondegenerate alternating form in characteristic 2, reusing Ogdoad's frame decomposition | Not arbitrary-subspace extension or a costed synthesis algorithm |
| Mathproof.AlmanWalshHadamard20260806 | Walsh matrix definitions and finite entry-change infrastructure | Paper-scale Claim_Theorem1 is stated as a proposition, not silently proved or assumed as an axiom |

The first two precedents can ground a formal representation of the binary symplectic search space. Neither supplies the missing Pauli/global-phase lift, nor a native controller. The Walsh infrastructure is relevant to structured matrix testing, but importing its paper-scale claim as an established rigidity theorem would be incorrect. No canonical file, live DAG or imported module was edited; no Lean build or kernel verification is claimed. This is targeted source-level retrieval, not a search of every registered theorem.

## Read-depth and priority register

SOURCES.json supplies all 18 titles, authors, years, primary URLs, exact passages read and model assumptions. D1 means abstract/introductory passages, D2 a selected definition or theorem/outline, and D3 a selected construction/theorem plus an argument excerpt. None means every proof in the paper was audited. The 15 D2/D3 entries are Q01-Q07, Q09 and Q12-Q18. The others are honest discovery-level pointers. SEARCH.json preserves the queries, follow-up chains, failed HTML fetches, negative transfers and untried experiments.

| Priority | Concrete next action | Evidence already supplied | Admission to a κ claim |
| --- | --- | --- | --- |
| 1 | Build an exact phase-refined Clifford coefficient dictionary for the current base alphabet | Exhaustive Pauli cocycle and two-qubit synthesis-coordinate tests | An actual all-width word with independent outputs and a paid invoice |
| 2 | Use typed owners and endpoint lifetimes in specialization/reuse compilation | Positive owned-clear trace and four alias/borrow rejection controls | Exact physical replay after optimization; no changed frozen input |
| 3 | Scalar-aware ZX simplification of individual prefix words | Relevant completeness/extraction theorems read; relative-phase rejection test | Extracted literal word, phase replay and native cost |
| 4 | Search a caller-proved conditional-zero or common fermionic subfamily | Explicit semantics and encoding filters; no such new caller exhibited | Constructive caller, restored owners, precision and whole-program pricing |

Novel-to-project status remains unknown for each literature technique outside the inspected precedents. Phase-aware matrices, tensor-width discipline and some symplectic geometry were already used in #4688/#4710/cp22f. No claim that these concepts were previously unused is made. The recent 2026 scheduling papers are newly located by this lane; that is a retrieval fact, not a worldwide novelty or κ claim.

## Reproduce the exact transfer tests

From this directory, run `python -I -O -B test.py`. Python's standard library suffices; there is no network, solver, GPU, Lean process, downloaded source dependency or absolute campaign path. EXPECTED.json is the deterministic receipt. The implementation uses explicit rejecting checks rather than assertions, so optimized mode retains them. The tests cover useful complete finite subproblems and explicit sufficient linear/ownership constructions; they do not replace the written all-input arguments or certify the full multiplication recursion.
