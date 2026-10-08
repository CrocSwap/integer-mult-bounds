# Endpoint bit network with semantic precision and bulk resampling

The conditional bound is **T(n) = O(n (log n)^(1−κ))** with
**κ = 119720853/10^13 = 1.19720853 × 10^-5**.
This increases the exponent saving by about 8.93617% over PR23.

The construction combines two already written interfaces:

- [PR24](https://github.com/CrocSwap/integer-mult-bounds/pull/24), pinned at
  `ed90fd940279c336ebc45968631bdebfb087b505`, supplies the endpoint-gauge
  bit network and its exact saving `2993093/250000000000`.
- [PR23](https://github.com/CrocSwap/integer-mult-bounds/pull/23), pinned at
  `661ebabc1076c9f525d7ce4967c876b203fa9827`, supplies the semantic precision
  guard and bulk assembly, with PR21's complex saving `18/10^6` and
  the attributed RaD analytic/tape transfers.

The PR24 complex network is not used. The actual complex circuit, scalar
charge, signed phase wrappers and `C1=1` semantic induction remain exactly
those in PR23. The changed bit interface implements the same arbitrary-width
interchange contract, including arbitrary spectators, padding and restored
dirty auxiliaries. The router consumes that contract, and complex adapters
use it to permute addresses without changing Gaussian-dyadic arithmetic.
The two finite rational setups can use a shared prime outside their finite
union of excluded primes. Their dimensions need not agree.

## New accounting and exact parameters

For the bit circuit, `m_b=38400`, `W_b=9854325632000`, and maximum child
width `r_b=38340`. The least halving depth is 444 and `W_b<2^44`.
The retained complex circuit has depth 544 and `W_c<2^41`. The simultaneous
stock is a product, with coefficient `44×444+41×544=41840`; therefore
`p^86000` suffices, since `41840×51/25<86000`. The temporary nested bit
stock is restored before the next complex child. The complete preceding
row prefix and single padding are retained.

Take `a=2993093/250000000000`, `b=18/10^6`, `h=10^-12`, `beta=1/4`, and

```
tau=1-a                    sigma=1-b
q=a(1-2h)                  c=q(1+h)
epsilon=(1-h)/(1+c+q)       G=epsilon*q
lambda'=1-q                lambda=(tau+lambda')/2
r=(G+1-epsilon)/2          delta=h/8
C1=1                       kappa=119720853/10^13
```

The seven margins are the original-prefix saving `1-epsilon(1+c)`,
coordinate-movement saving `a`, compact-phase saving `G`, bulk-exposure
saving `a`, Gaussian saving `min(1-epsilon-delta,r-delta)`, scalar saving
`1-epsilon-delta`, and dimension saving `epsilon`. Their minimum is `G`.
The strict absorption gap is approximately `3.1445675692 × 10^-14`,
and exceeds `3/10^14` exactly. All 47 strict conditions pass, including
`(1-beta)b>a`, cell/band separation, geometry, reservations and prime packing.

The new [proof extension](../../notes/endpoint-semantic-composition.tex)
contains the dependency argument and exact witness. The generated
[incremental patch](../../patches/endpoint-semantic-composition.patch)
adds that extension to PR23's pinned source using the included TeX fragment.
The original notes and certificates remain unchanged as historical inputs.
No PDF is created or updated by this contribution.

This changes the bit-interface input to the semantic/bulk assembly, rather
than claiming an improvement within PR23's fixed bit saving. At fixed `a`,
letting `h` tend to zero makes this assembly approach `a/(1+2a)`, while
strict inequalities require positive headroom. This is a limit of this
parameter recipe, not an optimality result over other networks or assemblies.

## Reproduce

```sh
make endpoint-semantic-composition
python3 scripts/endpoint_gauge_producer.py --output /tmp/endpoint-producer.json
make verify
git diff --exit-code -- certificates patches
```

The generator verifies immutable predecessor certificate hashes, recomputes
both certificates, and checks exact equality with the PR23 assembly at its
original parameters. It then evaluates the new bit interface, mixed-dimension
stock, all 47 conditions, seven margins and compressed eventual power tests.
Three negative controls reject the old guard, old exposures and `2^-16`.
The numerical cutoff is `log2(input bits) >= 446523314177`; additional eventual
setup, prime existence and logarithmic absorption thresholds remain required.

The finite checks do not formally verify the full theorem. Its generic basis,
analytic, inverse, routing and fixed finite-alphabet multitape proofs remain
explicit mathematical dependencies. This makes no practical speedup claim.

## Attribution

Dominik Scholz contributed this mixed-interface composition, new product-stock
accounting and exact parameter witness, with substantial OpenAI Codex assistance.
Credit icekylinx for PR24's endpoint-gauge bit construction, producers and basis;
Zhihao Chen (jacklightChen) for PR21's complex interface and PR23's semantic
compatibility, literal charge and product-stock argument; and RaD/hipotures for
the semantic, routing, phase-cell inverse and bulk mechanisms, with its recorded
Codex/GPT-6.1-Sol Ultra assistance. Earlier icekylinx, eumemic, Rohan Arun,
Douglas Colkitt and other contributors remain credited in NOTICE.
PR24 source files are imported unchanged without its PDF; their hashes and
original commit are recorded in `references/endpoint24/SOURCE.json`.
All original Apache-2.0 and imported CC0 notices remain in force.
