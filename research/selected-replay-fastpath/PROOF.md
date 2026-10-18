# Exact support updates

This argument applies to the valid gates from the pinned `clifford_exact.py`.
The input is a basis index `0 <= basis < 2^n`. Each state has Gaussian integer
numerators and a common denominator `2^den`. A missing dictionary key has
numerator zero. The output contains all `2^n` numerators, including zeros.

## Induction over the circuit

The initial dictionary has the one entry `basis -> (1, 0)`. It is the same
state as the retained dense evaluator.

For `P`, the validated binary matrix is invertible. Its index map is a
permutation. Thus no two nonzero entries collide, and omitted zero entries
contribute no value. For `X`, translation by XOR is also a permutation.

For `D` and `phase`, each amplitude is multiplied by a power of `i`. The
four rotations of `(a, b)` are `(a, b)`, `(-b, a)`, `(-a, -b)`, and `(b, -a)`.
Zero remains zero. The `D` phases and `P` index maps use the unchanged PR662
tables. Those tables depend on the dimension and all gate coefficients.
They do not depend on a state or on a previous check result. The source pins
retain their exact formulas and bounded caches.

For `C`, put `y = x xor q` and let `s` be the sign. If the numerators at
`x` and `y` are `(a, b)` and `(c, d)`, the new numerators are

```text
x: (a - s*b + c + s*d, b + s*a + d - s*c)
y: (c - s*d + a + s*b, d + s*c + b - s*a).
```

The denominator exponent increases by one. These are the two rows of the
retained dense update. XOR partitions the index set into pairs when `q != 0`.
The loop visits a pair once if either entry is nonzero. If both entries are
present, it skips the larger index. If only one entry is present, its partner
has value zero. A pair with two zero entries contributes two zeros and need
not be visited. Exact cancellation removes a zero output entry. When `q = 0`,
both formulas give `(2*a, 2*b)` at the same index; the update is the identity
after division by two.

The common-factor test after `C` gives the same answer on the dictionary as
on the dense vector: omitted entries are zero and are divisible by two.
The other gates only permute entries or rotate their Gaussian coordinates.
They cannot change the common power of two. Thus those gates need no further
normalization. This proves equality of both the complete vector and `den`
after every gate. It also covers circuits whose support shrinks after a
`C` gate. A valid Clifford circuit cannot map a nonzero input to the zero
state, because each gate is invertible.

## The compiler checks

`lowering.py` retains the algebra and checks of the pinned lowering routine.
It passes a state evaluator through ordinary function arguments. It changes
no retained module, method or global value. The reference mode calls the
original lowering routine. The dense and sparse modes use the same explicit
lowering code with their respective evaluators.

Every tableau equality, off-support zero check, denominator check, and global
phase check remains. The final comparison still checks the complete compiled
state against the complete input state. No phase is inferred from a tableau.

`run.py` retains the frame-span, frame-rank, edge-rank and endpoint-rank checks
of `phases_full.py`. It visits every frame, every directed edge including
center transitions, and every source and target adapter. Its public entry
point rejects optimized Python before it loads the retained assertion-based
algebra. It also rejects source drift and an existing output directory.

## Work and storage

Let `s` be the current number of nonzero amplitudes and `N = 2^n`. A state
update now visits `s` entries, or at most `s` XOR pairs, in place of all `N`
entries. Dictionary operations have their usual expected constant lookup
cost. Integer arithmetic remains exact. A first use of a PR662 gate table
still takes `O(N)` work, and the final full output also takes `O(N)` work.
Each of the two retained table caches has at most 64 entries.

This is a support-sensitive improvement. It is not a polynomial-size
stabilizer representation: the support can be all `N` indices. The benchmark
measures the complete selected dimension-nine phase command, including table
construction, source admission, parsing, lowering, checks and output writing.
It makes no claim about multiplication runtime or the full cold replay.
