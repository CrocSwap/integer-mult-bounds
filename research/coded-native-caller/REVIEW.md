# Independent agent review of the physical adapter

Reviewed by a separate OpenAI Codex agent. This is neither independent human
acceptance nor a formal proof-kernel audit. The review covers PHYSICAL.md,
normalizers.py and the emitted normalizer receipt, with PR4929's frozen producer
theorem retained as a premise.

## Findings

The initial receipt displayed Gaussian-containing expressions for wrappers whose
operators were monomial. That was an implementation presentation gap: executing
those expressions literally would not justify the stated Gaussian-free wrapper
bill. The revised receipt emits all 896 wrappers as P/D/X/phase words. The main
checker separately compares each compiled word with its defining expression,
including absolute phase. The independent finite checker rejects any other
opcode in those emitted words.

No mathematical counterexample was found to the scoped local adapter theorem.
In particular:

* Binary orthogonality alone is insufficient. The stated row-weight sign makes
  the full Gaussian commute with K exactly. The explicit mod-four weight identity
  controls the kernel's phase, not merely its Lagrangian or rank.
* At width f, the owner code is
  `C_f = diag(K_i,f)^-1 (A tensor I) diag(K_i,f)` with
  `K_i,f = K_i tensor ... tensor K_i`. The owner matrix A is applied once.
  This directly preserves the quadratic polynomial and code inverse; tensoring
  the entire one-column owner operator would be a different construction.
* For `F = diag(D,D) L(C Q^-1)`, symmetry of C, D and Q gives
  `F^-T = diag(D^-1,D^-1) U(-Q^-1 C)`. Output D-squares followed by X-only
  Q-squared conjugation yields `diag(D,D) U(-Q C)` in that order. No commutation
  between C and Q is needed. The older Y-only convention fails for the actual
  supplied code in the independent finite control.
* The eight owned mode fields hold all source sums before main fields are
  updated. They therefore do not require erasing or aliasing any of the 408
  arbitrary helper inputs. The inverse coefficient is exactly -1/52; its
  denominator and finite-precision implementation remain visible obligations.

## Separate bounded evidence

`independent.py` imports no retained Clifford implementation. It interprets the
actual signed binary permutations, rational owner matrix and Gaussian pair gates
over the prime field of order 65537, with 256 representing i. Two deterministic
112-owner banks contain 512 addresses per owner. It checks the signed-map and
code inverses, commutation with DQ, noncommutation with Q, the X-only raw-dual
conversion, and rejection of the old Y-only conversion. It also checks the
Gaussian-free opcode alphabet of all 896 emitted wrappers. The default command
is read-only and compares INDEPENDENT.json; every substantive check remains
active under Python `-O`.

These finite checks corroborate the proof and catch concrete order/phase errors;
they are not exhaustive tests on every input and do not establish the universal
claim by themselves. They do not replay PR4929's native word or independently
verify the inherited 632-input producer theorem.

## Remaining obligations

The local adapter does not establish the complete controller endpoint, resolve
the unmatched middle junction and terminal gauges, or certify a favorable whole
moment. Fixed rational arithmetic still needs its caller's actual precision and
machine-cost implementation. Supplier admission, recursive precision closure
and outer multiplication recovery remain outside this package's result.

Credit remains with Dugongue's PR4929, Cinna Davis's cache/helper work, Cao Yifan's
native word, and the retained Clifford, compiler and controller contributors.

After this local review, a separate research agent completed the exact rational typed p16 caller in GAUGE.md; another agent independently checked its global conjugation and boundary-parity argument. The earlier local review does not claim that the coded negative-half outputs are admitted Gaussian jobs. The middle-junction concern of the initial per-pair proof is superseded by that whole-word proof.
