# Six shears attain the sixteen-lane Clifford correction bound

PR1920 proves that sixteen independent forward rank-one lanes cannot be one
rank-five tensor child under a reciprocal basis change. Even allowing a left
correction F, it proves `rank(F-I)>=6`, expressly without attaining six.
This package attains that lower bound with **six explicit disjoint linear
shears**, and gives the sharp correction rank for every power-of-two lane count,
every fourth-root global phase, and both native child directions.

This is a completed algebraic adapter result. It is **not** six recursive
children or six native ADDs. Encoding, linear-form reads, frames, physical
storage, routing, precision and restoration have not been priced. The known
joined-volume upper expression still loses even when these are granted free.
The task card's favorable physical construction gate is not met; no new
supplier or kappa is claimed.

## Exact result

For `q=2^s`, let `T=I_q tensor C`, where
`C=((1+i)I+(1-i)X)/2`, and let `H=i^u C_(s+1)^eta`, `eta=+/-1`.
On the complete `2q`-dimensional space, allow any invertible square encoder E
and a nonreciprocal correction satisfying `T=F E^-1 H E`.

If H has eigenvalue multiplicities `(m_0,m_1,m_2,m_3)` at `(1,i,-1,-i)`,
the exact minimum of `rank(F-I)` is `max(m_2,m_3)`. Optimizing the phase gives

| Lane exponent s | Minimum correction rank |
| --- | --- |
| 0 | 0 |
| odd | `2^(s-1)` |
| even, at least 2 | `2^(s-1)-2^((s-2)/2)` |

Each paired -1/-i eigenspace uses
`J=I+2i*[[-1,1],[-1,1]]`; `J-I` has rank one and square zero, while
`J diag(-1,-i)` has eigenvalues 1,i. Any unmatched unwanted eigenvectors
use singleton sign changes. The resulting eigenspace dimensions are exactly
those of T. The full proof, encoder orientation, arbitrary-scale extension,
spectator accounting and cost limitation are in [PROOF.md](PROOF.md).

For sixteen lanes, choose `H=-C_5`. The unwanted multiplicities are six each,
so six shears suffice and six is necessary. [WITNESS.json](WITNESS.json) retains
every entry of the 32-dimensional Gaussian-rational encoder E and native-basis
correction F_H, satisfying `F_H H E=E T`. The two correction placements are
related by `F=E^-1 F_H E`. The explicit difference `F_H-I=UV^T` has rank six,
with `V^T U=0`. No conjugate transpose is substituted.

An unchanged spectator of dimension t multiplies the algebraic correction rank
by t. Thus sixteen nine-axis local arrays with eight unchanged spectator axes
give rank 1536 on 8192 coordinates, not rank 6 on the whole physical array.
Under the inherited tariff, the joined child alone has upper-budget ratio
`(s+1)^sigma>1` for s>=1; this compares upper expressions, not optimal runtime.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/clifford-sharp-correction-rank
```

The registered commands are:

```sh
python3.12 -I -O -B research/clifford-sharp-correction-rank/verify.py
python3.12 -I -O -B research/clifford-sharp-correction-rank/independent.py
python3.12 -I -B research/clifford-sharp-correction-rank/test_integrity.py
```

The main verifier checks 1032 phase/direction spectra through s=128,48 complete
operators through dimension 64, invertibility and correction-rank minors, and
all 10,920 native kernel entries against the pinned literal interpreter. It
authenticates source bytes and Git blobs before executing the retained kernel.
Wrong phase, wrong shear sign and a missing shear fail on arbitrary-input
columns. Default verification is read-only; `--write NEW_PATH` exclusively
regenerates the receipt and never overwrites an occupied file.

The code-separated checker imports neither builder nor native interpreter.
Direct tensor coefficients, dense Gaussian-rational multiplication and
elimination check all 1,024 entries of the 32-dimensional identity, encoder and
correction invertibility, exact rank 6, nilpotence, six outer products, and
the spectator rank multiplier. Four semantic controls include a wrong encoder
and omission of the sixth shear. The integration tests check normal/optimized
Git-free relocation, unchanged input bytes, source corruption before execution,
typed receipt corruption, an independently detected wrong scientific witness,
missing evidence, exact regeneration and exclusive output.

These finite checks corroborate a written all-size proof; they do not imply
one by extrapolation. Independent human review, formal-kernel proof, hosted CI,
full selected cold replay, native adapter implementation and all-size admission
are not claimed.

## Provenance and scope selection

Started from canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4. Picker seed `34d8bbeeb8cab9445c61358304382898` selected
complex-mechanisms and included the rank-shape decoder card. Its first working
ceiling check passed. The initial diagonal batching idea was retired after
reading PR679, Ross Richardson's source audit, PR1920 and PR1924. The chosen
scope changes from physical synthesis to closing PR1920's precise unproved
attainment, with the failed inherited cost gate stated above.

PR1920 head `057b214aea45c65926b93ad8b95693c80f0f79c9` is the direct
predecessor. [SOURCES.json](SOURCES.json) pins its retained README and the kernel
and tariff sources. [TASK.json](TASK.json) records selection, overlap, source
freshness and limits. A complete REST snapshot of 710 open PR bodies found no
matching sharp-correction result. The last complete Discussion snapshot was
retained with its timestamp because GraphQL was rate limited; this limits
freshness and is not a novelty certificate.

## Credit

Arham Tahir/PR1920 supplied the reciprocal-basis theorem, eigenmultiplicity
lower bound and exact sixteen-lane rank 6 gap. Greer Guthrie/PR679 supplied the
monomial obstruction and joined-volume tariff; Ross Richardson's audit at
`8a3900c84213fd7603b99beaceaff48f501b4232` applied it to the proposed batches.
ToikY/PR1924 and Douglas R. Colkitt/PR665 developed the distinct clean-injection
spectral/Walsh boundary. Jose Manuel/jmbarrancoml and publishing account Cinna
Davis/1337isnot1337 (PR1779), and Josie Elliston (PR1817), supplied the batching
motivation. Their original identities, counts and physical gaps are unchanged.
The kernel and selected construction lineage includes DreamingOfClouds,
icekylinx, Rohan Arun, Jeremy Kothe and Hao Yan. Prior source stays in place.

Prepared for ywz65 with substantial OpenAI Codex assistance in mathematical
analysis, implementation, proof, writing and separate peer review. The two
checker implementations are code-separated, not independent human work.
New files use the repository's Apache-2.0 license. No priority is asserted for
elementary spectral perturbation, Walsh diagonalization or rank telescoping.

## Open next questions

- Can a physical boundary realize these particular nonreciprocal linear forms
  more cheaply than the inherited joined-volume tariff? Start with the exact
  q=16 witness and name a legal changed volume/encoding contract before pricing
  native operations. This algebraic optimum does not supply such a contract.
- Can a different physical tensor/spectator split retain an advantage after
  preparation, native chart conversion, dirty restoration and every output are
  charged? Fix one actual caller cut and its permitted input subspace first.
  The present tensor-with-identity extension keeps spectators unchanged.
