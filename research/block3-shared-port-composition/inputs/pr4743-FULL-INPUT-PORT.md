# Reversible two-call and three-call full-input triangular ports

Prepared for Dugongue with substantial OpenAI Codex assistance. This is an exact, all-width native building block on two arbitrary independent input arrays. It does not claim an improved complete supplier or multiplication exponent.

## Leading two-call theorem

Let A_f = C0_f and L_f = P_f + 2 Q_f, with the individually tensorized phase letters pinned below. For two arbitrary independent initial registers (x,y), execute

    t <- A_f x,
    y <- y + P_f t + 2 Q_f t,
    s <- A_f y.

Only the first and last lines are paid calls. The complete output is

    (t,s) = (A_f x, A_f y + A_f L_f A_f x).

This is an actual dirty-target extension of the predecessor prefix: replace its initial copy by additive injection into the existing target. To implement a term P_f t using only per-register maps and ordinary mixing, apply P_f to t, add it into y, and restore t using P_f inverse; do the same for Q_f. No original y value is overwritten and no hidden clean copy is needed.

The exact two-call block and its inverse are

    F_f = A_f L_f A_f,
    U_f = [[A_f, 0], [F_f, A_f]],
    U_f inverse = [[A_f inverse, 0], [-L_f, A_f inverse]].

The reverse program applies A_f inverse to s, subtracts the two separately applied monomial terms using retained t, and applies A_f inverse to t. Thus it costs exactly two inverse paid calls, each equivalent to one forward paid call plus a free X0_f. Both block multiplication orders verify the inverse. This result is valid for arbitrary x and y and every positive f.

There is also an explicit free inverse for the coupling L_f. Set R_f = P_f inverse Q_f. The actual predecessor letters satisfy R^4 = I, hence R_f^4 = I. Then

    L_f inverse = -(I - 2 R_f + 4 R_f^2 - 8 R_f^3) P_f inverse / 15.

Multiplying by P_f(I + 2 R_f) proves the formula. Every summand is applied separately; the four-term sum is never tensorized as one letter. The fixed denominator 15 requires explicitly charged fixed-precision scalar arithmetic for numerical execution. Since R_f is unitary with fourth-root-of-unity spectrum, L_f has singular values between 1 and 3. In addition, every R_f power times P_f inverse is monomial, so the explicit formula gives infinity norm(L_f inverse) <= (1 + 2 + 4 + 8)/15 = 1 uniformly in f. The forward and reverse two/three-call schedules do not execute this division by 15; it is an optional coupling inverse. If that optional inverse is used numerically, its fixed odd division and rounding must be charged explicitly, for example by ordinary bounded-word DIV with a sufficient common-grid guard. This well-conditioned free coupling is concrete controller material, rather than an unknown gadget or an inverse asserted from a numerical rank.

The two-call block is a product of unitary layers and the shear (t,y) -> (t,y + L_f t). Its norm and inverse norm are at most 4, so its condition number is at most 16 uniformly in f. The three-call block below is this same block followed by another unitary layer, and inherits the identical bound.

## Constructive full-input theorem

Use the actual base letters and phases of the pinned PR #4710 residual identity, with notation as in SECTOR-COMPLETION.md. At every positive width f, each individual letter G_f means G raised to its f-fold tensor power. Put

    A_f = C0_f,
    L_f = P_f + 2 Q_f,
    D_f = J_f W_f C0_f,
    B_f = M_f C2_f + 2 K_f a_f.

For arbitrary independent complex arrays x and y of length N = 8^f, the following exact program uses three paid rank-one calls:

1. Replace x by t = C0_f x. This is the first paid call.
2. Add P_f t and 2 Q_f t into the existing y register, obtaining y + L_f t. Each summand is a separately applied free monomial. The original y is retained additively; no zero-scratch precondition is used.
3. Apply C0_f to the second register. This is the second paid call.
4. Apply W_f and J_f to that register. Only the C2_f inside J is paid, giving the third call.

The resulting two-register output is exactly

    (t,u) = (C0_f x, D_f y + B_f x).

Indeed u = D_f y + J_f W_f C0_f (P_f + 2 Q_f) C0_f x, and the pinned predecessor identities, tensorized separately before addition, identify the two x summands with M_f C2_f x and 2 K_f a_f x. Nothing tensors the sum P + 2 Q as a single matrix. Absolute Pauli phases remain those of the source.

The three-call map is invertible at every width. Its explicit reverse schedule is: apply J_f inverse, W_f inverse and C0_f inverse to u, subtract P_f t and 2 Q_f t, and apply C0_f inverse to t. This recovers exactly (x,y), with no borrowed copy. Each inverse Cj_f uses one forward paid call followed by Xj_f, since Cj inverse = Xj Cj on the actual base letters. Thus the reverse also uses three paid calls. In block form the forward and inverse are

    [[A_f, 0], [D_f L_f A_f, D_f]]
    and [[A_f inverse, 0], [-L_f, D_f inverse]].

Both multiplication orders give the identity by literal block multiplication. This is a sufficient all-input implementation, not a rank-only test or a subspace assertion.

## Conditioning, native work and precision

Each paid Gaussian letter and each free monomial is unitary. The whole program is a product of unitary block-diagonal layers and the shear

    S_f(t,y) = (t, y + L_f t).

As the two free terms in L_f have unitary Euclidean norm, norm(L_f) <= 3. Writing S_f = I + N_f, with N_f squared zero, gives norm(S_f) <= 4 and norm(S_f inverse) <= 4. Consequently both the complete forward operator and its inverse have Euclidean operator norm at most 4, and their condition number is at most 16, independently of f. This statement concerns the complete two-bank map, without discarding either output.

For an explicit coordinatewise native error budget, let complex input magnitudes be at most 2^H and request coordinate error at most 2^(-P), where H,P >= 0. Let each charged Gaussian call return its exact transform of the stored input with error at most rho per coordinate, and quantize the original inputs with error at most rho. Set L = 2^(f/2), bounding the infinity norm of any Cj_f. Free monomials, integer scalings, copies and additions can be exact on the common grid. The first call's error contributes at most 3 L^2 rho to u, the second at most L rho, and the third at most rho. Initial input errors contribute at most (3 L^3 + L^2) rho to u. Thus the conservative bound 10 L^3 rho covers both output arrays. Taking rho = 2^(-(P + 2 f + 6)) gives error below 2^(-P), since L^3 <= 2^(2 f) and 10/64 < 1. Any chosen Gaussian implementation's internal guard and time costs are separately charged; this theorem does not assume an unproved fast oracle.

Intermediate magnitudes are below 2^(H + 2 f + 4), including these errors. P + H + 4 f + 12 signed bits per real or imaginary coordinate suffice for the displayed arithmetic. If f = O(log p), H,P = O(p) and p = Theta(log n), this occupies a fixed number of ordinary C log n-bit words, for sufficiently large fixed C. No unbounded-word multiplication or whole-array unit instruction is used.

The address/phase odometer and explicit in-place permutation implementation in SECTOR-COMPLETION.md implement every displayed free map and mixed update in O(N) ordinary word operations. O(N) owned address workspace, or one separately owned work field, is initialized and restored in O(N) stores. These are charged native resources, not additional independent productive inputs. The theorem therefore supplies three paid calls plus O(N) native work, with two arbitrary input banks and explicitly accounted workspace.

## How to use the port without changing its claim

A controller may now wire this full-input block into a larger exact block identity, preserving both diagonal channels and the actual rank-three off-diagonal term. This differs from the clean-prefix presentation because the second initial array is arbitrary and its D_f y contribution is explicit. A claimed complete saving must show the actual subsequent block operations, canonical independent outputs, restored owners and total paid calls. This port alone has diagonal ranks one and two and does not establish a three-rank target for both independent arrays. Discarding D_f y, assuming it is initially zero, or counting B_f x as an independent additional Gaussian job would change the theorem.

## Evidence and predecessor credit

verify_full_input_port.py uses the pinned exact Gaussian-rational engine to verify both predecessor word identities, both full-input triangular blocks, both inverse multiplication identities, the order-four free coupling inverse and the one-call implementation of paid inverses. It rejects the false claim that the second output is independent of an arbitrary y. Separately tensorized word algebra proves all widths; the finite checks do not infer universal correctness from a few dimensions.

Credit Yiyang / Lyy-iiis, PR #4710 (b0d5192390af493d626054b060921895df3c94d2), for the repaired phase prefix and residual identity; lee-phys, PR #4688 (264c4b3cb13c82d171de352ecf60486dfb8d2bd4), for the original prefix and rank engine; and Jacob Alan Sussman, PR #4628 (ee4fd87f064017c23e5a86fc1dcfe0a5237caed3), for the complex engine model and small-unit problem. Retain their notices and earlier attribution. This full-input additive schedule, reverse interface and uniform norm bound are the present extension. No worldwide novelty or independent human review is claimed. Exact source URLs and SHA-256 pins appear in SOURCE-PINS.json.
