# Catalytic computation, transposition and priced information

This lane reviewed 21 primary works to ask a specific implementation question: can an arbitrary-dirty, phase-sensitive prefix turn its reversible structure into more independently useful outputs per paid Gaussian call? The positive results below are identities on every input, with exact tests of the actual prefix. They extend the available interface; they do not establish a new multiplication exponent. [SOURCES.json](SOURCES.json) records each paper's read depth and locator, including abstract-only entries and failed full-text fetches.

## The interface and its predecessors

Fix a positive width f and N = 8^f. Let A = C0_f be the actual unitary Gaussian tensor letter, and L = P_f + 2 Q_f be the actual phase-sensitive sum of two signed address permutations. Tensor each letter individually before taking this sum. Thus L is not generally the tensor power of P + 2Q. The existing two-call port is

    U(x,y) = (A x, A y + A L A x).

Both x and y may contain arbitrary dirty data. Its inverse is

    U⁻¹(t,s) = (A⁻¹ t, A⁻¹ s − L t).

The source is the frozen native-prefix package cp22f, built on Yiyang's [#4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710), lee-phys's [#4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), and Jacob Alan Sussman's [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628). Our test independently implements the actual C0, P and Q words using rational real/imaginary pairs; it does not import the earlier verifier or trust a numerical comparison. General dirty-echo and complete recursive accounting precede this package: androolloyd's [#673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) already constructs and prices such adapters. The contribution here is a specialization to the repaired arbitrary-input prefix and a literature-to-interface map, not discovery of catalytic computation or dirty echo.

## Positive theorem 1: a two-call Hermitian-adjoint port

For all complex arrays u and v,

    U†(u,v) = (A†u + A†L†A†v, A†v).

Its inverse is

    (U†)⁻¹(u,v) = (A u − L†v, A v).

Proof. Take the block adjoint of U = [[A,0],[ALA,A]], reversing products and conjugating coefficients. Multiplying the displayed matrices gives the identity because A†A = I. Operationally compute w = A†v, then A†(u + L†w), retaining w. This uses two A† calls. Each A† is X0_f A for this particular Gaussian letter, so a forward call and a free signed permutation implement it. L† is the sum of the two reversed monomial words with conjugated phases. The inverse-adjoint likewise needs two forward calls and a monomial linear combination. This proves the identities on arbitrary inputs; the exact finite checks are supplementary evidence, not the universal proof.

This is an application of the transposition principle, not a generic assertion that every forward routine is its own transpose. [Bostan–Lecerf–Schost (2003)](https://mathexp.eu/bostan/publications/BoLeSc03.pdf), §3 and §4.3, explain how reversing a linear program produces its transpose, with particular attention to initialization, accumulation and the chosen computational model. In our complex inner product the relevant operation is the **Hermitian adjoint**. The test verifies the conjugate inner-product identity and rejects treating the forward port as its adjoint in nine cases.

The operator norm and inverse norm are unchanged by adjunction. Hence this theorem preserves the previous two-call invoice and conditioning; it does not lower its paid moment. It is useful when a joint encoder requires a dual action, because it supplies an actual all-input reverse interface rather than an assumed dual oracle. A future construction may use it inside a new encoder, but must count its calls and arrange the physical output ownership.

[Baur–Strassen (1983)](https://web.vu.lt/mif/s.jukna/tropical/Baur-Strassen.pdf) is a related automatic-differentiation precedent. Its original threefold statement concerns nonscalar multiplications/divisions in the stated arithmetic model. It is not permission to multiply or divide a paid Gaussian-query invoice by three, nor a license to erase memory traffic or phase words. That distinction prevents an attractive but incorrect shortcut from reverse-mode arithmetic to this supplier model.

## Positive theorem 2: transparent conjugated translation

Let δ be an independent read-only array. Run U on arbitrary x,y, add δ to its first output, then run U⁻¹. The result is

    (x + A⁻¹δ, y − Lδ).

Proof. The first output becomes Ax + δ. Substituting it and the unchanged second output into U⁻¹ gives x + A⁻¹δ in the first coordinate and

    A⁻¹(Ay + ALAx) − L(Ax + δ) = y − Lδ

in the second. No zero-initialization assumption is used. Four Gaussian calls are paid, two in each direction; δ is preserved. Intermediate registers and the source of δ still have to be hosted. Taking δ = 0 restores the original inputs exactly, as expected.

This realizes the transparent-register idea of [Buhrman–Cleve–Koucký–Loff–Speelman (2014)](https://iuuk.mff.cuni.cz/~koucky/papers/catalytic.pdf), §3.1 Theorem 2 and §3.2 Lemma 4, for a concrete prefix. Their catalytic-space simulation and the earlier [Ben-Or–Cleve three-register simulation](https://epubs.siam.org/doi/pdf/10.1137/0221006) make borrowed memory mathematically useful. Their time overhead is part of their theorem, however. A space simulation does not automatically improve time, and restoration does not turn the borrowed input into an additional independent completed job.

[Bennett's reversible pebbling](https://mathweb.ucsd.edu/~sbuss/CourseWeb/Math268_2013W/Bennett_Tradeoffs.pdf), the Li–Tromp–Vitányi pebble analysis, and Lange–McKenzie–Tapp address related time/space tradeoffs. They distinguish controlled checkpoint storage from arbitrary pre-existing contents. The project must retain that distinction: a temporary blank array, a dirty borrowed array and a completed transform are different endpoints with different obligations.

The 2024–2026 catalytic literature sharpens possible future encodings. [Williams (2025)](https://arxiv.org/html/2502.17779v1), including Appendix A's tree evaluation, exposes the interpolation mechanism behind space-efficient computation. [Henzinger–Pyne–Ragavan (2026)](https://arxiv.org/html/2602.14320v1), Theorems 3.1 and 3.5 and §§3.1–3.3, study catalytic compression. [Cook–Pyne (2025)](https://arxiv.org/html/2509.06209v1), §1.4 and the local-reversion theorem, is relevant to restoring a complicated auxiliary state in a local interval. The dossier records these as techniques to investigate, with their actual resource models. None is a proved sublogarithmic-cost Gaussian multiplier.

## Positive theorem 3: character decoding, including its full query count

Let a field contain a primitive m-th root ω with m invertible. For vectors u_i,v_j over Z/mZ, suppose ⟨u_j,v_j⟩ = 0 and each off-diagonal inner product is nonzero modulo m with vanishing full character sum. Define E(z) = Σ_i ω^⟨u_i,z⟩ x_i. For every linear map G,

    G(x_j) = (1/m) Σ_(t=0)^(m−1) G(E(t v_j)).

Proof. Interchange the two finite sums using linearity. The coefficient of x_j is one; every other coefficient is a geometric character sum equal to zero. The hypothesis about a vanishing sum matters for composite m and general rings; merely saying nonzero is not enough there.

Our exact example uses F₁₃, m = 3, ω = 3, four inputs, u_i the coordinate vectors and v_j the all-ones vector with coordinate j set to zero. The decoder recovers all four G(x_j) exactly for a fixed nontrivial linear G. The union of requested encoded points has size 1 + (3−1)·4 = **9**, since the zero query is shared and the other queries are distinct. Thus even a hypothetical rank-three query would pay 27 calls, against 12 for four direct rank-three jobs. This is a working coded decoder with an unfavorable invoice, not a new supplier or a claim about the actual Gaussian primitive over F₁₃. It illustrates why decoding success and profitable recursion are separate checks.

The connection to the matrix-valued encoding in the algebra volume is actionable: move beyond scalar phase labels only if the new encoded query simultaneously carries enough independently recoverable information to offset its number and widths. A proof should expose the full query union and the rank of every decoded job. Neither favorable local cancellation nor compression of a description suffices.

## Conditioning, lower bounds and model-specific guidance

[Ailon (2014)](https://arxiv.org/pdf/1403.1307), Definition 2.1, Theorem 3.1 and Lemma 3.2, connects entropy growth with well-conditioned in-place linear circuits. The relevant condition is on intermediate states in the specified gate model. A well-conditioned final matrix does not control a factorization whose intermediate norms are huge. For a perturbed prefix, bound every partial product or its error recurrence before choosing a guard budget. Our adjoint theorem preserves an existing norm bound; it does not supply a missing bound for an arbitrary newly synthesized word.

Morgenstern's bounded-coefficient Fourier lower bound and Ailon's unitary-gate variant concern different permitted gates. They are valuable design constraints, but do not give lower bounds on a model that treats an entire Gaussian tensor transform as one recursive call. Conversely a quantum circuit using few Hadamards is not automatically a cheap classical amplitude-array algorithm. The quantum volume makes that distinction explicit and tracks scalar phases that a symplectic tableau alone forgets.

[Hong–Kung (1981)](https://perso.ens-lyon.fr/loris.marchal/docs-data-aware/hong_kung_red_blue_pebble_game_STOC81.pdf) explains how a fixed computation DAG can force data transfers. Its red/blue pebble theorem is useful for deciding whether an implementation is merely hiding array movement. It is not a universal lower bound for different algorithms or changed encodings. The more recent Papp–Sobczyk–Yzelman paper is version-sensitive: its arXiv v1 was explicitly incomplete/incorrect; SOURCES.json points to the corrected v2. Abstract-only reads are labelled accordingly, rather than used to assert uninspected theorem hypotheses.

The local linked Lean tree supplies two modest precedents. `Mathproof.BreakthroughPatterns` records sufficient inequalities under which reuse beats storing all outputs; the precise inequalities are useful bookkeeping templates, not an algorithm for this problem. `Mathproof.Meta.RankNotCircuit20260902` exhibits matching tensors with exponential flattening rank but a small arithmetic formula. Its lesson is the precise counterexample to inferring general arithmetic-circuit size from that rank, not that every tensor-based lower-bound route is impossible. Both files were inspected as source and hash-pinned in LOCAL-PRECEDENTS.json. No fresh Lean elaboration or kernel audit is asserted.

## What was tested and what to attempt next

`test.py` checks 27 exact port identities at f = 1, 2, 3, nine transparent translations, nine wrong-adjoint controls, and recovery of four encoded arrays from nine queries. Rational arithmetic avoids rounding tolerances. These cases can falsify our implementation and verify the receipts; they do not exhaust all input arrays or prove a favorable asymptotic invoice. The displayed algebra proves the all-input identities. Other volumes independently reviewed the adjoint and conjugation formulas and replayed the tests.

The next constructive task is a joint native encoder using operator-valued coefficients and both forward/adjoint ports. The algebra lane supplies an explicit invertible anchored-Pauli block, while the quantum lane supplies phase-aware synthesis machinery. Freeze its entire input/output map, owned workspace and lifetime schedule before optimizing. Test its literal action on arbitrary dirty baselines, derive an all-width identity, and compute all paid rank terms with precision and fallback included. Compare the complete moment against the unchanged selected baseline. Only then would a κ claim be justified.

This search combined primary-paper queries, citation chains, local DAG retrieval and current-project overlap checks. The 427-result open-PR search snapshot is search-indexed and non-atomic; cached GitHub pages disagree about status and counts. All-state phrase searches found older catalytic contributions, including #673, so absence from the open snapshot was not evidence of project novelty. Full text was inaccessible for several sources and is explicitly labelled. Neither this finite search nor its source-only DAG retrieval proves global exhaustiveness.

Prepared for Dugongue with substantial OpenAI Codex assistance. New prose and code: Apache-2.0. Predecessor results and literature retain their original attribution and licenses.
