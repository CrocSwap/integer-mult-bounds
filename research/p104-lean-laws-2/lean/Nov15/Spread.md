# Spread: subscription / spread identity, kernel-checked
File: Nov15/Spread.lean (Module K M). Axioms: propext, Quot.sound (+choice in the counterexample); no sorry.
Model: z = zt + lam*r; events other c (zt += c), read c (lam += c, z += c r), hrow y (r += y, z fixed, zt -= lam y). `val_step`: z only moves by other/read.
- `spread_identity`: with no h-reads in the window (lam constant): zt_end - zt_0 - sum(other) = -lam*(r_end - r_0).
- `spread_neutral`: r_end = r_0 => zt_end = zt_0 + sum(other); `no_hrow_neutral`: no h-row change events => content-neutral.
## Scoping correction
The note's §2 says "window where z~ is untouched by h-reads". The identity needs lam CONSTANT, i.e. no h-read inside the window (a read changes lam). With an h-read inside, the single-lam formula is false: `varying_lambda_counterexample` (hrow 1, read 1, hrow 1 from (0,0,0): true channel -1; formula with lam_0 = 0 gives 0, with lam_end = 1 gives -2). The general statement is the time-weighted sum -sum_t lam_t y_t.
