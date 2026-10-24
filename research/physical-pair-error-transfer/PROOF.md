# Exact local error cancellation and a sharper inverse-pair precision guard

FINDING — exact local rounding transfer for the physical inverse-coded pair. This closes one part of the precision question in [PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069). It supplies a precision guard for the two inverse recodings. It does not admit a complete caller or increase kappa.

Use the exact operators and order in the [source pair proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/physical-inverse-pair/README.md). Let e0 be the residual just after the entrance C^-1, e1 the residual just after the thin C^-1 on its actual, possibly perturbed input, and e2 the residual just after the exit C, before the final Q^-1. Other operations are exact in this local statement. Then the output errors are exactly

```text
Delta X = -D Q C e0
Delta Y = Q^-1 (C e1 + e2).
```

In particular, the entrance inverse error cancels from Y. The second inverse need not be linear or have an error independent of its input: define e1 as its actual output minus C^-1 of that input. Thus this formula also applies to the noninjective rounded kernel in [PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035). It has no product of e0 and e1.

Proof: after entrance and FULL,

```text
y1 = C^-1 y + e0
x2 = D x - D Q y - D Q C e0
y2 = D C^-1 y + D e0.
```

The thin adds Q^-1(C^-1 x2+e1) to y2. Use [C,DQ]=0, which the source proves for the actual signed normalizers. Both the original-y term and the e0 term cancel. The remaining value is Q^-1 C^-1 D x+Q^-1 e1. Applying the exit Q^-1 C Q, with e2 injected at the stated site, gives D Q^-1 x+Q^-1(C e1+e2). This proof never commutes C through Q alone.

**Component precision, for every positive tensor width f.** Measure the maximum absolute real or imaginary component. The exact [112-owner code](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/native-center-free-code/CODE.json) has absolute row sum 26. A row of a k-axis canonical complex Gaussian has real-component absolute row sum 2^ceil(k/2): its 2^k coefficients have modulus 2^(-k/2); for even k each is real or imaginary, while for odd k both components have equal magnitude. Right multiplication by a real signed monomial preserves this sum. Each owner block of C_f is A_ij K_i,f^-1 K_j,f, with A applied once across owners. Therefore

```text
||D_f Q_f C_f||_(infinity,real) = 26 * 2^ceil(9f/2)
||Q_f^-1 C_f||_(infinity,real) = 26 * 2^ceil(f/2)
||Delta X|| <= 26 * 2^ceil(9f/2) ||e0||
||Delta Y|| <= 2^ceil(f/2) (26 ||e1|| + ||e2||).
```

These are induced norms for arbitrary residual vectors. They do not assert that a rounded kernel attains each worst case. With exact exit recoding and each inverse error at most 2*2^-P, the two inverse errors contribute at most 52*2^(ceil(9f/2)-P) to any output component. Hence

```text
P = p + ceil(9f/2) + 6
```

makes their combined contribution strictly less than 2^-p. The width-dependent guard cannot be replaced by the width-independent Euclidean norm 13 when the contract is componentwise absolute precision.

**Sharper guard for the actual mode kernel.** The [source kernel](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/coded-inverse-fixed-grid/kernel.py) rounds each of the eight modes before owner updates. In common coordinates its residual is -M delta, where delta contains the eight mode rounding errors. Since A M=-13 M, each physical residual obeys C_f e=-13 e. For these two kernel calls, with exact wrappers and exact other operations, the formula improves to

```text
Delta X = 13 D Q e0
Delta Y = -13 Q^-1 e1          (e2=0).
```

The component bound is then 26*2^(ceil(9f/2)-P), and **P=p+ceil(9f/2)+5 suffices**. This reduces the generic residual guard by one bit. It uses the source kernel's error shape, not a better rounding rule or a new machine tariff. A different inverse implementation must establish that error-shape premise before it uses the sharper guard.

**Evidence.** The checker in verify.py authenticates the declared input files, verifies A^2+12A=13I and all 112 row sums and A M=-13 M, and checks the chronological residual formula with exact rational complex arithmetic in seven actual signed-normalizer Walsh fibers at widths 1,2,3,5. It rejects omitted X error, reversed thin order and the wrong exit injection site. Literal Gaussian tensor rows through 12 axes check the real-component norm; integer guards are checked for f=1,...,100. The written operator and row arguments establish the all-width statement; these finite fixtures do not enumerate every address. Twelve actual finite-kernel invocations also satisfy C e=-13 e and return owned scratch clean. Normal and optimized CPython 3.12.13 give the same receipt.

Run the registered checks with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/physical-pair-error-transfer
```

Expected verifier marker: PASS_PHYSICAL_PAIR_ERROR_TRANSFER.

**Remaining limits and next step.** This is a local residual theorem. It does not fund native or Gaussian rounding, movement, field storage, common-coordinate access, or the whole caller's error budget. The second inverse input bound H must include the perturbed x2. The source kernel uses paid classical destructive writes; no reversible cleanup follows. No full native, compiler, outer-ledger or selected replay ran. First use this guard in a changed or shared-boundary caller with an affordable complete invoice; [the unshared p19 boundary budget](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19149724) already rejects repeated use of the original recipe.

Source-number note: some retained package prose calls the finite-grid kernel PR5037. The actual kernel contribution is PR5035, as its PR body and package paths confirm. Links here use that verified identity.

Credit: JoyboyBrian supplied the physical pair and finite-grid kernel; Dillon supplied the actual normalizers and code factorization; Dugongue supplied the center-free producer; Cayden Burkart supplied the coded controller. Cinna Davis, Cao Yifan, zxv, Jacob Alan Sussman and retained native/precision/compiler contributors keep their source credit. New residual derivation and checker: Ali Romman with OpenAI Codex assistance, Apache-2.0. This is author-checked evidence, not independent human or proof-kernel review.
