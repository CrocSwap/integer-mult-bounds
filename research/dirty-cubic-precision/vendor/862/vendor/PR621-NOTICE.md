# Attribution and assistance

The kernel definition comes from the OpenAI exact-DFT preprint at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, at `loc:newton` and
`loc:fourier-factorization`. Its source has the Apache-2.0 license.
The Newton and q-Pochhammer Fourier factorization is classical; see
Alexey Kuznetsov, [Using q-calculus to study LDLT factorization of a
certain Vandermonde matrix](https://arxiv.org/abs/1507.02959v2).
This source is not presented as a proof of the cyclic conditioning result.

The proof extends prior unpublished local cyclic inverse and stability
notes from research directed by Ali Romman. The rational field routines
use that work's exact-arithmetic scaffold. The full proof is included
here; no private file is needed for replay. No literature priority is claimed.

The proof, verifier, and package were prepared with substantial OpenAI
Codex assistance. Separate Codex agents reviewed the proof and checked
it with independent SymPy arithmetic. These are AI-assisted reviews,
not maintainer acceptance or a full Lean multiplication proof.

This contribution uses the repository's Apache-2.0 license.
