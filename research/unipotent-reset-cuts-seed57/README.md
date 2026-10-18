# Exact reset cuts for the fixed infinite-order dirty echo

**Scoped recursive-interface construction and finite optimum; no new kappa.**
The fixed 53-child example in Sagar Thakrar's [PR1537](https://github.com/CrocSwap/integer-mult-bounds/pull/1537)
can retain its complete **2,114 ADD + 120 SCALE** invoice while reducing its
maximum prefix row-L1 norm from **4,195 to 3,932**. Reset after child 52, then
execute child 53 as a singleton. Both directions restore all dirty state.
This saves one magnitude bit under the same conservative power-of-two envelope,
without changing either instruction count. The forward address-travel score
also falls from 50,186 to 50,174; it is a score of the emitted address sequence,
not a physical tape implementation or a measured runtime.

The package resolves PR1537's explicit question about intermediate reset cuts
for this one ordered fixture. A 1,431-edge graph covers all **2^52** contiguous
partitions, giving **31** exact cost/growth breakpoints. The minimum cap that
retains all 260 operations of the predecessor's saving is **3,932**. Any
feasible cap below **788** forces the eager cost, 2,494 instructions, within
this partition class. In particular, the seed-selected cap **255** has no
arithmetic saving. These are finite optimum statements with the domain below;
they are not barriers for other return circuits or multiplication algorithms.

## Fixed object and complete prices

The byte-pinned source is PR1537 head
`407f00df6ca0bf86b455b5640f18ec2f62ee77b9`. Its unchanged reader generator uses
`fixture(k=53, m=5, seed=53)`. Assignment seed **57** selects the follow-up and
highlighted cap, not a new reader instance. The inherited contract over exact
rationals is

    Q = [[1,1],[0,1]],  P = diag(Q,...,Q),  N = 2m,
    C_i(D,W) = (D + R_i W, P W),  R_i P = Q R_i.

The output has two coordinates. Source X, output D and dirty workspace U are
disjoint. Each fixed child includes its trailing P. Its other scratch, if any,
must be restored. We keep child order, child instructions and the predecessor's
binary power implementation unchanged. The only choice is which of the 52
gaps receives a full canonical reset. No child is deleted, fused or rewritten.

A segment of length l is the predecessor's carried group G: Q on D between
children, followed by paid binary returns P^(-l) and Q^(1-l). It has exact map
`(D,W) -> (D + (sum R_i) W, W)`. A singleton is the eager child followed by its
workspace return. Set a(t)=popcount(t), s(t)=2 floor(log2(t)) for positive t,
with a(0)=s(0)=0. Its boundary invoice is

    b_A(l,m) = (l-1) + m a(l) + a(l-1),
    b_S(l,m) =         m s(l) + s(l-1).

All source doubling and halving is paid. Each halved source still contains
the factor of two introduced by that same ladder; every literal prefix and
inverse prefix is integral on integer-grid inputs. No initial zero low bits
or clean workspace are assumed.

For a partition pi, concatenate its canonical groups to form G_pi. Execute

    U += X; G_pi(D,U); U -= X; G_pi^(-1)(D,U).

The final map is `D += (sum R_i) X`, with X and U restored. Every inverse is
the literal reversed and inverted word. At any node, with complete child
invoices (A_i,S_i), the fully charged recurrence is

    A_root = 2 sum A_i + 2N + 2 sum_(l in pi) b_A(l,m),
    S_root = 2 sum S_i      + 2 sum_(l in pi) b_S(l,m).

For a nonroot child add m ADDs for its required trailing P. A leaf costs
`sum |R_ij| + m` ADDs. With constant arity k and partition pi at each internal
level, T_h=2k T_(h-1)+g for T=alpha A+sigma S, where
`g=alpha(2N+m+2 sum b_A)+2 sigma sum b_S`; the root omits `m alpha`.
This is a complete finite-depth recurrence. No contracting recurrence in the
selected multiplication input size is supplied. The optimized growth graph
here contains leaves only; nested child prefix growth would require new edges.

The fixed root contributes 1,964 instructions before its twice-paid boundary.
Thus at alpha=sigma=1 its price is `1964 + 2 sum (b_A+b_S)`. Every complete
word uses 22 data coordinates. The inherited recursive storage bound is
`2+(h+1)N` for leaf height zero. Selected-word emission reads the fixed reader
descriptions and cuts and materializes the word; no runtime cut oracle is
assumed. Each emitted instruction reads one instruction record and writes one
data coordinate. ADD reads two data coordinates; SCALE reads one. All those
counts and the source-then-destination travel score are in the certificate.
Compiler work, descriptor layout and physical hosting remain separate from
this scalar execution bill.

| Row-sum cap | Complete ADD | SCALE | Total | Saving from eager | One attaining partition |
|---:|---:|---:|---:|---:|---|
| 255 (seed-selected) | 2,494 | 0 | 2,494 | 0 | 53 singletons |
| 1,023 | 2,188 | 260 | 2,448 | 46 | 1,1,1,18,16,1,1,1,1,12 |
| 2,047 | 2,138 | 192 | 2,330 | 164 | 28,25 |
| 4,095 | 2,114 | 120 | 2,234 | 260 | 52,1 |
| 8,191 | 2,114 | 120 | 2,234 | 260 | 53 |

Caps 2^B-1 are a conservative convention, not an exact machine precision
contract. If every input magnitude is below 2^b and F<2^B, every prefix
magnitude is below 2^(b+B). The 52+1 word has forward/inverse peaks 3,932/2,391;
the unsplit word has 4,195/2,391. This comparison preserves both ADD and SCALE
counts for every fixed positive pair of prices, but the **31-point optimum
frontier** uses equal prices. Width-dependent arithmetic, rounding, overflow
and hosting need their own admission proof.

## Why the interval graph covers every partition

Let S_i be the sum of the first i reader matrices, and T=S_53. At every
canonical cut the complete linear state is independent of preceding reset
choices. For an interval [i,j), its four possible execution contexts have the
following entrance state, with all expressions in the original D,X,U:

| Context | Output | Workspace | Interval word |
|---|---|---|---|
| Forward echo, forward half | D + S_i(X+U) | U+X | G_[i,j) |
| Forward echo, inverse half | D + TX + S_j U | U | G_[i,j)^(-1) |
| Inverse echo, forward half | D + S_i U | U | G_[i,j) |
| Inverse echo, inverse half | D - (T-S_j)X + S_j U | U+X | G_[i,j)^(-1) |

The canonical group identity proves these by induction over segments; in the
inverse half later reader contributions have already been subtracted. The
verifier checks each interval's entrance-to-exit matrix in all four contexts.
It traces every primitive prefix, so accumulated output, dirty state and
temporary scaling all affect the interval bound. Tracing an isolated segment
from zero accumulated output is unsound: the retained negative control has
local bound 17 but actual bound 55 for interval [1,2).

Define F_ij as the largest absolute row sum among those four traces, including
their entrances and exits. Copy/unload operations cannot exceed the maxima
already present at their adjacent canonical states (workspace row sum at most
two). Hence the complete bidirectional word bound for any partition is
**exactly** `max F_ij` along its path from 0 to 53. Linearity and the sign-input
witness establish the actual infinity-operator norm, not just an estimate.

For cap F, retain precisely edges with F_ij<=F and weight
`w_ij=b_A(j-i,5)+b_S(j-i,5)`. Every contiguous partition is a unique path in
this acyclic graph, and every such path emits a legal partition. The recurrence

    d(0)=0; d(j)=min_(i<j, F_ij<=F) [d(i)+w_ij]

therefore gives the exact minimum complete bill `1964+2d(53)`. Unreachable
vertices are explicit. The certificate supplies distances and an attaining
path for every frontier point and displayed cap. A separate checker verifies
`d(j)<=d(i)+w_ij` on every allowed edge; telescoping makes d(53) a lower bound
on every path, and the displayed path attains it. This checks the optimality
claim without trusting the optimizer's choice of path.

There are 1,017 distinct edge bounds. Feasibility can change only at one of
them. The verifier evaluates all of them and retains the 31 strict cost
improvements. This is complete coverage of the fixed finite partition domain,
not a heuristic stopping rule or an enumeration of 2^52 emitted words.

## Reproduction and evidence

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/unipotent-reset-cuts-seed57
```

Expected markers are `PASS_UNIPOTENT_RESET_CUTS`, four passing package tests,
then `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
For a standalone relocated package run `python3 -I -O -B verify.py`.
`verify.py --emit` prints the regenerated certificate without changing files.

[CERTIFICATE.json](CERTIFICATE.json) contains all 1,431 edges, 31 frontier
points, Bellman potentials, attaining cuts, exact full-word invoices, word
hashes and sign-input growth witnesses. The untouched predecessor's eager and
unsplit word hashes, counts and peaks are reproduced before claiming a delta.
The Fraction column interpreter independently checks both full directions of
all 31 frontier words: 1,364 basis columns. A separate complete census of
every partition for k=1..9,m=1 checks 511 words, 6,132 directed basis columns
and 195 cap/tariff comparisons, with SCALE prices 1,2,5.

Ten semantic controls cover false cheaper potentials, a cap one below 3,932,
the unsplit word at cap 4,095, omitted halving/scaling charges, a nonintertwining
child, duplicate cuts, unearned integer halving, lost accumulated output and
forward-as-inverse substitution. Package tests alter actual source and
certificate files and run a full replay after read-only relocation. These
checks support the implementation and the finite certificate; the argument
above supplies the reduction. They are not a formal multiplication proof.

## Source identity, overlap and credit

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected certificate,
assembly, source manifest and review identify conditional PR1094 kappa
`836330098538459/500000000000000000`, with the complex side binding and PR589
on PR555 supplying the bit side. Those files are unchanged. Historical context
is pinned in [SOURCES.json](SOURCES.json); the pending predecessor is pinned by
commit, SHA256 and Git blob in [PREDECESSORS.json](PREDECESSORS.json). Its model,
README and receipt are retained byte-for-byte. No other pending code is imported.

Sagar Thakrar supplies PR1537's infinite-order contract, paid binary return,
fixture, emitter, recurrence and explicit reset-cut question. **This package's
new result is the exact fixed-fixture cut/width tradeoff**, including the 52+1
word and the two threshold values. Ross Richardson's PR1287 supplies the
output-frame/dirty-echo framework, following Sagar's PR1227 sign frames and
the PR889/PR1203 reader lineage. Related finite-order work in PR1391/1410/1499
and PR1488, and paid scaling in PR1526, is not combined numerically here.
PR734 and the retained signed-Horner packages already study other precision
constraints; we change no coefficient-lowering circuit. PR1532 studies a
quadratic reader and is outside this linear fixed-child experiment.

[CLAIM.json](CLAIM.json) records the OS-random assignment, three candidates,
domain and stopping rule. No pinned coordination issue existed, so the claim
is local, as requested. [OVERLAP.json](OVERLAP.json) records search coverage,
closest work and the final refresh. No search result is a novelty guarantee.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in derivation, code, verification and writing. New material is Apache-2.0.
The two checker implementations were written in the same AI-assisted session;
no independent human review or proof-assistant verification is implied.

## Open next questions

An actual indivisible child with this drift is still missing. Inspect a
candidate's emitted boundary and establish `RP=QR`; if its trailing drift can
simply be deleted, this wrapper is unnecessary. This is the inherited blocker
to supplier adoption, not resolved by optimizing the toy fixture.

For a concrete next interface question, include the binary-return scratch
amplification inside a nested child's entry-state norm. Recompute the four
edge contexts using the actual recursive child word before optimizing cuts.
The one-level graph here cannot certify a nested precision budget merely by
substituting endpoint matrices. A fixed tape/rounding contract and actual
width-dependent prices are further prerequisites to a runtime or kappa claim.
