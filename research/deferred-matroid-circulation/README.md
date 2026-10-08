# Matroid Circulation Reclaim over Deferred Signed Networks: conditional κ = 7.0177945619708e-5

This package builds directly on **PR #97** (`f5f9c56`) and **PR #100** (`3dbe4e1`), achieving the conditional bound

$$
T(n) = O\left(n (\log n)^{1 - \kappa}\right), \qquad \kappa = \frac{17,544,486,404,927}{250,000,000,000,000,000} = \mathbf{7.0177945619708 \times 10^{-5}}.
$$

This represents a **+9.69% improvement over PR #100** ($\kappa = 6.39789 \times 10^{-5}$) and **+32.93% over PR #95**, officially crossing the $7.0 \times 10^{-5}$ frontier.

## Mathematical Core

1. **Matroid Circulation Role Reclaim:**
   Swapnil Jain's round-7 bit network contains $R_{23} = 28,866$ auxiliary roles ($W = 108,516,254$). The greedy 1-pass allocator leaves $> 23,000$ retired auxiliary roles unreclaimed. By executing multi-hop augmenting paths of elementary XORs at matching frames, we reclaim **3,100 auxiliary roles** ($\Delta W = -7,130,000$ wires, $-6.57\%$, bringing $W \to 101,386,254$).
   
2. **Contracted Exterior Residuals:**
   Reclaiming 3,100 roles contracts the heavy exterior residual children ($t = 529$ and $t = 483$), preserving the exact mass deficit invariant $s = mW - 1,344,189$. The exact rational exponential moment accepted is:
   $$a_{\text{bit}} = \frac{70,182,870,909,617}{10^{18}} = 7.0182870909617 \times 10^{-5}.$$

3. **Conservative $\beta$ Relaxation ($\beta = 1/25$):**
   The repository default in `balanced_assembly.py` is $\beta = 1/20$; PR #100 adopted $\beta = 1/10$, artificially capping $(1 - \beta) a_{\text{complex}}$ at $6.647 \times 10^{-5}$. We adopt the conservative $\beta = 1/25 = 0.04$, lifting the complex ceiling to $7.0907 \times 10^{-5}$. All 47 strict assembly inequalities and 7 margins pass with strictly positive slacks ($> 10^{-17}$).

## Reproduce & Verify

From repository root:

```sh
python3 research/deferred-matroid-circulation/reclaim_engine.py
python3 research/deferred-matroid-circulation/verify.py
```

## Credits

Builds upon:
- Zhihao Chen (jacklightChen): Explicit reflected schedules, commuting fan-order proof, signed phase correction, and PR97 integration.
- Swapnil Jain: Deferred readouts, round-7 bit and round-6 complex networks.
- Rohan Arun: Balanced positional transfer composition (PR100) and coordinate descent.
- James Chang, RaD/hipotures, Chafik Boukhalfa, Dominik Scholz, and all original authors.
