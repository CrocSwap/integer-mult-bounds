# PR137 three-way first-stage lockstep: conservative finite screen

## Research status

**Candidate conditional κ = 0.00045019844704** if the proposed
three-core lockstep can be implemented physically. Relative to PR137's
κ = 0.000413596233702, this is +8.8497453% and exceeds the 4×10^-4
research target. **This is not yet a proved or independently replayed
multiplication bound.** The current source only certifies the numerical
consequence of a proposed, unimplemented physical composition.

## Method

Start from exactly PR137's h24 local source inventory, compensated scratch
reuse, padded 72D three-stage cover, and completed sequential triple
sharing. Each group has three mutually orthogonal local 24D spaces.

Instead of running all three first-stage completed cores sequentially,
the hypothesis is to execute the corresponding *auxiliary and centre*
frame transitions in lockstep. Each stage-one trio of rank-r local
increments would be replaced by one rank-3r increment. Keep all three
other (second and third stage) local invocations separate. All sources
and target data fronts remain separate, all physical source gauges and
final completed tails are retained, and both padded rank-two data
finishes remain paid.

The *optimistic* merged full local inventory is adjusted with a
conservative positive exact moment penalty for the source/target data
fronts that cannot be merged. Each local circuit's data rank mass is
D=2v(h-1)=93,104. If a triple rank-r datum is actually three separate
children rather than a rank-3r child, the added normalized moment is
3r(m/r)^a(1-3^-a)/(mW), bounded above by
3r*m^a*a*log(3)/(mW). Sum over every such data front and use inherited
PR130 rational upward log/exp enclosures.

## Exact finite calculations, conditional on implementation

- ambient dimension m=72; total persistent role stock per cell W=91,935
- rank mass 6,612,144; deficit 7,176
- largest combined child 69, smaller than 72
- conservative complex saving 0.000468719485 on 10^-12 grid
- retained PR137 stopped bit saving 0.00045060418316 (now binding)
- candidate assembly κ=0.00045019844704 on 10^-15 grid
- 47 strict assembly constraints, seven margins and next grid rejection
- retained conservative scalar, router, adapter, semantic and row charges

Run from root:

```sh
python3 research/triple-lockstep/certificate.py
```

The verifier regenerates PR137's pinned cover certificate and source
inventory, then recomputes the hypothetical paired histogram and
conservative moment penalty. The original PR137 files remain unchanged.

## Critical missing proof

A valid use of the new rank-3r children requires an explicit **joint
physical scalar and Clifford execution** for three *overlapping-in-time*
cores with the same scratch streams. PR137 proves three fully completed
sequential cores can share scratch, but does **not** prove that their
intermediate scratch dependencies, dirty input amplitudes, compensated
readouts, inverse gates, and signed phases can be interleaved.
PR132 establishes a two-core lockstep in a different first-stage setting;
its argument does not automatically extend to PR137's triple sequential
schedule. This fundamental gate is NOT checked by certificate.py.

Additional review must show the complete literal three-way compiler,
arbitrary-dirty and all-column replay, cross-core noninterference,
normalized frames, signed phases, rank-zero adapters and reflection.
Only then is the candidate κ suitable as a new conditional record.
The current script must not be described as a full mathematical proof.

Credit: PR137 eumemic; PR132 ikeboy; PR130 icekylinx; PR124 jamesyc,
and all original contributors and licenses. New research hypothesis and
conservative numerical screen prepared with OpenAI assistance.
