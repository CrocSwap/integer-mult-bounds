# Inversion slack bounds dirty spectator workspace

**A new quantitative formal reduction; no new κ.** A normalized m-call S4
word with active endpoint width w and ordered-pair crossing rank L can be
restricted to **at most w+m-L total roles**. The extra roles remain arbitrary
dirty inputs and are restored. One scalar basis change on spectators fixes
all original active coordinates; the restriction preserves every paid label,
call order, rank-one idempotent and full formal endpoint.

The new premise is positive inversion slack `δ=m-L`, beyond the zero-slack
lemma of [PR4765](https://github.com/CrocSwap/integer-mult-bounds/pull/4765)
at `62ae3a67d931f73cb7980e69b8185b44c2679241`. The active endpoint can be an
arbitrary invertible formal block obtainable by the normalized word, not just
the previously studied mixed tuple. No fixed-target optimum or finite exclusion
is recomputed, and no C++ engine is run.

## Exact result and proof

Work in `M_r(F2[S4])`, with paid factors
`G_s(u,v)=I+([s]+[e])uv^T`, `v^T u=1`, and simple adjacent labels
`s∈{(12),(23),(34)}`. Only scalar binary GL mixing is free. The endpoint is
`Q_A ⊕ I_S`, including every dirty input and off-diagonal coefficient.
Free scalar mixing is normalized as in the predecessor. A general Q_A must
satisfy the word premise and therefore has identity augmentation.

Let `φ(P)=rank(π_K P|_H)` for the ordered-pair positive/negative-root cut,
and `L=φ(Q_A⊕I_S)`. For diagonal permutation targets, L is the sum of their
inversion counts. [PROOF.md](PROOF.md) proves the local charge

```
1[u_S ≠ 0] + 1[v|_S ≠ 0] ≤ 1 + φ(PG) - φ(P)
```

whenever the current P fixes S. A two-sided spectator coupling forces φ to
rise by one in a right peel. A one-sided coupling prevents it from falling.
An explicit split `S=U⊕S'` contains u_S in U and annihilates S' with v,
using at most the charged number of dimensions. Nested splits preserve the
residual full formal endpoint, and their total growth telescopes to m-L.

The proof constructs a single final `B=I_A⊕B_S` and the actual embedding and
projection intertwiners for **every full formal factor**. Thus the same word
and all label prices survive restriction. A representation is used only for
the necessary rank charge, never to admit a formal endpoint.

The coefficient one is sharp **for this preserved-factor basis restriction**:
a three-call word with slack two can contain nonzero orthogonal dirty image
and functional components, which cannot both live in one dirty dimension.
The example contains a cancellable pair and its endpoint has a one-call
realization. It is not an optimal-circuit workspace lower bound.

## Constructive checks

`verify.py` constructs the nested bases and restricted projectors using exact
binary arithmetic and full formal S4 coefficients. Its receipt stores actual
basis columns, reduced words, peel charges and endpoint hashes.

| Control | Coverage |
|---|---:|
| Local quantitative charge | 20,160 arbitrary invertible active 4×4 binary maps × 120 projectors = 2,419,200 peels |
| Spectator splitting | All 341 vector/functional pairs in dimensions 0 through 4 |
| Full formal compression fixtures | 8 words, up to 10 roles and 7 calls |
| Independent per-factor regular-action checks | 4,968 complete input columns |
| Independent whole-word regular-action checks | 1,440 complete input columns |

The local charge control uses a two-address crossing-pair abstraction with
two active and two spectator roles. It is not a new S4 word census and does
not prove the quantified theorem by sampling. Both zero and positive slack,
image-only and functional-only coupling, nonzero and orthogonal dirty pairings,
noncommuting nested roundtrips, a non-diagonal active endpoint and empty active
spaces are covered.

For example, the sharp positive-slack fixture reduces 8 roles to 3 at w=1,
δ=2, while a nested noncommuting fixture reduces 10 roles to 6 at w=2, δ=4.
The zero-slack coordinate fixture reduces 7 roles to its 2 active roles.

`independent.py` imports no primary verifier. It propagates every regular-basis
input through the literal original and reduced gates, checks the full scalar
basis and factor intertwiners, and recomputes the crossing rank through the
ordered-pair action. Seven semantic boundary groups reject illegal labels,
nilpotents, bad bases and unreturned dirt; eight real optimized-CLI mutations
reject damaged constructive evidence.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/s4-slack-workspace-bound
python3.12 -I -O -B research/s4-slack-workspace-bound/verify.py
python3.12 -I -O -B research/s4-slack-workspace-bound/independent.py
python3.12 -I -O -B research/s4-slack-workspace-bound/test_controls.py
```

The primary finite controls take about three seconds locally. Verification is
read-only. Direct scripts work in the committed Git-free export; no external
input or historical executable is imported. `SOURCES.json` binds predecessor
and comparison notes as provenance, not runtime dependencies. The selected
baseline binding check passed; it is not a selected-construction replay.

## Family decision and limits

This bounds dirty workspace at a fixed **unweighted call excess** and preserves
every label count, so any label-only prices are retained. It does not find a
new target word, price a physical basis conversion, or improve a native supplier.
The abelian `k-d+s`, Q8 character/Sylvester and UT4 one-slack reductions use
different algebraic hypotheses; this result does not replace those theorems.

Stop after this reduction. Non-simple labels, higher-rank paid maps, clean
ancillas, unreturned spectators and free address operations are outside its
proof. Native address realization, frames, scalar/physical work, tape/precision,
ownership and supplier admission remain unknown, not zero. The selected
conditional κ remains `60403/20000000`. No full multiplication theorem,
formal-kernel or independent human acceptance is claimed. Separate coordinating
Codex review checked the written proof; the two implementations were prepared
in this session. No C++, Lean, Docker, hosted-CI or historical heavy replay
result is asserted here.

## Open next questions

- Can an explicitly chosen non-simple label support a comparable local charge?
  First derive its exact positive/negative subspace action. The one-crossing
  hypothesis fails, and no replacement dimension bound is proved here.
- Which changed target and paid budget makes the finite role bound useful?
  Specify an excess-call budget and compare existing tariffs before a search.
  This package supplies no new target saving or physical caller allowance.

## Sources, overlap and credit

Scientific base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2570#discussioncomment-19131478).
Entry overlap covered 299 open PRs, 3,695 Discussion records and 6,319 local
notes with complete pagination and committed-note inventory. Specific matches
were the prior zero-slack package's open-question statements. Cached snapshots,
unretained closed work, arbitrary nested diffs and unpublished investigations
remain outside that coverage; no novelty guarantee is made.

Credit PR4765 for the zero-slack spectator lemma, Sagar Thakrar/#3888 for the
cut-window S4 work, Arham Tahir/#2998 and Nick Petalas/#2583/#3408 for its
model and cut boundaries, Ross Richardson's permutation-cut lineage, and all
predecessor credits retained there. Tuafo, Nick Petalas and the credited
abelian/Q8 image/kernel reductions, and the UT4 span-compression lineage,
remain distinct source context. The new result is the positive-slack local
charge, nested global restriction and its preserved-factor sharpness.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
