# Independent review of the actual query information bounds

Result: accept the package in its stated scopes. No material finding
remains after the summary correction below. This review does not accept
a universal circuit, native-cost, or storage lower bound.

The reviewed `PACKAGE-MANIFEST.json` has SHA-256
`7317a4956c2d734d4a7376d252f12a8543ba5d7977572ea3c17758c74e9f8aca`.
It lists 109 files; the manifest itself is a 110th file. All listed
hashes and sizes match. The package stayed unchanged during the cold
replay. [REVIEWED-PACKAGE-HASHES.json](REVIEWED-PACKAGE-HASHES.json)
binds every reviewed file, including the manifest.

## Resolved finding

The first new summary of the residual theorem said that the kernel of
V has dimension d. The correct space is `ker(V*)`. The source proof
already had the correct statement. The producer changed the summary
before the reviewed freeze. No executable or frozen source change was
needed. The corrected proof hash is
`898388f738b6857e176831629d03a18734beca2d3732a15c1e80081e6c366ad0`.

## Mathematical review

The fixed-source theorem uses the full logical module `C[G] tensor W`.
It does not use only constant payloads. The right regular action has
trace zero on a nonidentity group element. An honest unitary payload
action can be removed by the fieldwise change `f(d) -> V_d f(d)`.
Thus all trace and field-capacity factors include `dim(W)`. The actual
chart binding uses the complete linear and quadratic phase forms.
This binding remains distinct from a new complete native phase audit.

The positive-singleton rule is valid: all other factors fix that
stage's fresh block pointwise. If the full product is the identity,
the one remaining factor must also fix it. The actual port bases then
force equal port indices. The factor is exactly `4/48=1/12`.
The fourth- and fifth-order contractions, cyclic reductions, weighted
Cauchy calculation, and positive four-atom moment witness give
`rank(S)/N >= 15560/273`. This implies 57 whole fields, or 64 when
storage is restricted to whole eight-field cohorts. Sharpness is only
for the stated continuous moment problem. The theorem requires nine
queries of one fixed source and cannot be applied directly to changing
controller sources.

The support distance proof applies to every nonzero complex scalar
combination of the eight actual rows. A generic real projection keeps
the nonzero coefficients and preserves each zero signed sum. Equal-sum
subsets of positive coefficients form an antichain. The resulting
quartet bounds and all 255 support cases give 53, and all 112 stated
root directions attain 53. The snapshot bound uses the separate
support limit of 20 ports for each eligible birth field. For block
fields, a linear section of the reconstruction map gives a code of
dimension `kd`; deleting two field blocks is injective. This proves
`m>=k+2` under that support premise, with no extra source reads. It
does not price a multilevel shared network.

The one-cone argument uses the valid test inputs `X=JY`, with every
helper and private input zero. All granted observations and completed
X/helper baselines vanish on the excluded-port test. The exact query
minor has rank eight for each of the 1,002 positive proper actual
frames. Thus no nonzero required query lies in that one cone. The
argument does not grant the unchanged Y bank as a free terminal
observation, and it does not cover captures from incomparable cones.

The general cut lemma follows by induction through a finite causal
linear circuit. It includes every free observation inside the cut
and charges re-entry. Nonnegative weights can be summed only after
checking every allowed edge. The global flag argument gives 42 in the
same-content monotone model. It does not sum eight separate tree
bounds. The twelve rank-five certificates give `9k` only in their
specified contained-frame model, with a common merge and no later
observation. The rank-eight certificates give `8k` for proper frames
inside one chosen cone, 983 or 991. Their FULL extension correctly
charges all direct completion edges. Neither cone can be combined
with the other without a new edge and observation check. The package
does not claim a global bound of 64.

The residual factorization preserves chronology and does not commute
the routed projections. The nine bank rows have one relation with
every coefficient nonzero. The space `ker(V*)` is identified with the
common routed image, and the form of `4I-L` there is `-47/14` times its stated
inner product. Its nonsingularity excludes further rank loss. Thus
the full residual rank is `72|G|-d`; every proper omitted-stage set S
has rank `8|S||G|`. The separate cover calculation gives
`d<=8|G|/183`, so the full residual channel needs 72 whole arrays per
replica, or 1,152 across all 16 replicas. Tensoring the logical source
and its field capacity by the signal space preserves these normalized
counts. The native application remains conditional on the included
local lift and global endpoint normal form. The result is a channel
dimension bound, not a bound on peak workspace, native children, or
a computation with later source reads.

## Source and execution checks

I compared all eight portable adaptations with their hash-pinned
originals. The edits change only source loading, the corresponding
source hashes, and one CLI argument name. The extracted source-matrix
routine retains the reviewed reverse propagation. No mathematical
operation changed. The original versions are retained in `frozen/`.

I read the historical archive from the exact Git object at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, verified all 19,299,540
bytes against SHA-256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`,
and checked all four bundled members. Each is the unique regular
archive member at the stated path, and each matches byte for byte.
All 44 local links in the new package documents resolve.

The package was copied to a fresh directory under `/private/tmp`.
Its full portable command ran from `/private/tmp`, with one Python
child process at a time. The runtime was Python 3.14.7 with SymPy
1.14.0. All 17 checks passed in 46.329 seconds:

```text
PASS_ACTUAL_QUERY_INFORMATION_BOUNDS_PACKAGE
```

The run rebuilt the source matrix and all 712-input snapshot rows,
enumerated the 194,400 fifth-order triples, checked all support and
cut certificates, repeated the independent 73-axis cover calculation,
and ran the separate exact residual algebra. Every complete JSON
receipt matched its declared target, including JSON types. The only
removed comparison fields are the five explicitly named optional
sixth-moment fields. Source-hash changes are recorded separately.

The replay used no Git, network, or external campaign source. Git was
used only for the separate source audit. The evidence is in
[SOURCE-AND-REPLAY-CHECKS.json](SOURCE-AND-REPLAY-CHECKS.json) and
[cold-replay/REPLAY.json](cold-replay/REPLAY.json).

## Remaining limits

No material dependency gap remains for the scoped algebraic claims.
The inherited local native lift and controller endpoint normal form
are explicit application premises; this review does not establish
them through a fresh native supplier replay. It does not repeat the
optional sixth-moment extension, cut searches, or LP searches. It
does not establish a new cache, a chronological capture word, ownership,
finite precision, tape cost, or a complete recursive invoice.

The package retains the historical source and states that applicability
to the changed PR4470 construction is unproved. No kappa improvement
or selected-frontier change follows. Link-target checks on GitHub,
the final PR description, its rendered Markdown, and the published
readback remain the coordinator's publication work. This review made
no commit, push, PR, merge, or frozen-source edit. OpenAI Codex supplied
this independent agent review; it is not a human review.
