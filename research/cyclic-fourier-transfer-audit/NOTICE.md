# Attribution and assistance

Contribution prepared for Thiago Costa (@ThiagoCAltoe), with substantial
OpenAI Codex assistance in mathematical derivation, programming, documentation,
verification, and separate agent reviews. No independent human review or
maintainer acceptance is claimed. Licensed under Apache-2.0.

Ali Romman's incorporated PR621 supplies the kernel-conditioning theorem,
prime-power circle separation, coefficient height and derivative bound,
previous Fourier transfer, and cyclic-inverse context. Its source head is
520774462b19b29af41554b74def31f9d01e997e. Source hashes are in SOURCE.json.
We import no predecessor implementation; its mathematics remains a dependency.

The predecessor credits OpenAI's exact-DFT preprint at
adc7f1241b42e322a6451854ab7e4b4c146bf78a, section local.tex, anchors loc:newton
and loc:fourier-factorization, and Alexey Kuznetsov's classical q-calculus work,
https://arxiv.org/abs/1507.02959v2. Its prior unpublished cyclic stability and
inverse notes remain credited. Those sources are not represented as proving
this particular bound refinement.

The general proof uses standard Fourier/Parseval, periodic Sobolev, variation
and Cauchy-Schwarz arguments. It claims no new general inequality, optimal
constant, optimal separation exponent, or literature priority. For primary
literature context on periodic Carlson-type inequalities, see Boris Baeumer,
Mihaly Kovacs and Harish Sankaranarayanan, "Higher order Grunwald approximations
of fractional derivatives and fractional powers of operators",
https://arxiv.org/abs/1210.2792 (2012; Trans. AMS 367, 2015, 813-834).
That contextual citation is not used as a substitute for the self-contained
proof or claimed to establish exactly the constant used here.

Concurrent related work is acknowledged in README.md. No source code from
those pending PRs is incorporated or certified by this package.

Publication overlap: Rafael Guevara (@alephnan), PR803, head
`d213ac12d4a1ab8f717d942e844df318ceb395fb`, proposes a stronger degree-controlled
conditioning estimate for the same inherited PR621 transfer problem. Its root
reflection, arc-length and Hardy argument is distinct from the Sobolev argument
retained here. No PR803 code is imported and no independent certification of
that pending proposal is claimed. This package claims neither priority nor the
best currently proposed bound.
