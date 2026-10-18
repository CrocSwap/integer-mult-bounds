# P104 relay crossing capacity

This package proves a necessary joint constraint on the transport ranks of
monotone P104 correction helpers. It follows the actual-contact pricing handoff
from [PR2604](https://github.com/CrocSwap/integer-mult-bounds/pull/2604), which
correctly allows a dirty `{1,7,1}` carrier and refutes a uniform shape exclusion.
A legal carrier alone does not show that an entire cheap-shape network is small.

For the frozen PR1972 source and target frame paths, **4,680 correction entries
must cross the dimension-4/5 boundary on a new helper**. A rank-`r` crossing
can carry paths for at most `2^(7-r)` such entries. Thus the numbers `n_r` of
useful new-helper crossings necessarily satisfy

```text
64 n_1 + 32 n_2 + 16 n_3 + 8 n_4 + 4 n_5 + 2 n_6 + n_7 >= 4680.
```

This gives two consequences in the stated model:

- If every helper lifetime has rank multiset `{1,1,7}`, at least **4,680
  lifetimes** are necessary. All three chronological permutations are included.
- If there are at most **482 lifetimes**, at least **67** must have another
  rank multiset. This is conditional on that proposed count, not a proof that
  482 is attainable or a universal upper limit.

The unrestricted consequence, at least `ceil(4680/64)=74` lifetimes, is weaker
than the predecessor's 208 floor. This result adds a profile constraint and
**does not strengthen the unrestricted floor**, exclude all designs below 483,
produce a complete price, or establish a supplier or new kappa.

## Model and evidence

[PROOF.md](PROOF.md) specifies the model and proves the program-to-path and
path-to-capacity implications. Original X registers are immutable; original Y
registers receive additive correction writes and are never read by the new
network. New helpers have arbitrary source-independent dirty inputs and nested
ZERO-to-FULL lifetimes. Relays, cancellation and arbitrary rational scalar
coefficients are allowed. Original helper/private reads, target feedback,
changed original data paths, descending new helpers, source-dependent
initialization and cross-chart ADDs are outside this theorem.

The bound relaxes chronological availability. For each dimension cut it removes
all entries that might use an original source or target crossing. At cut 4,
168 source bypasses and 168 target bypasses have union 312, leaving
`4992 - 312 = 4680`. Omitting either bypass would incorrectly claim 4,824.
Both affine parity properties used in the capacity proof are reconstructed from
the frozen labels, rather than assumed from an ordinary dot-product convention.

[EXPECTED.json](EXPECTED.json) binds every cut count and the exact forced-entry
set hashes. `verify.py` checks those finite premises, all 256 positive
compositions of nine, a legal dirty carrier on the actual frozen X/Y paths and
four faults in its execution. It also checks a capacity-64 affine rectangle
and a capacity-225 countermodel when the odd-label premise is removed.
`independent.py` imports no candidate executable and separately reconstructs
all seven counts, the source/normal parity and four predicate controls.
These finite checks support the written proof; they do not check every relay
network by enumeration or constitute a proof-assistant formalization.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -I -O -Werror -B research/p104-relay-crossing-capacity/verify.py
python3.12 -I -O -Werror -B research/p104-relay-crossing-capacity/independent.py
python3.12 -Werror -B scripts/research_package.py --package research/p104-relay-crossing-capacity
```

When `python3.12` is not on PATH, `uv run --python 3.12 --no-project python`
selects it. Direct replay needs no Git or network. Both original JSON inputs
must remain at the paths pinned in [SOURCES.json](SOURCES.json). No predecessor
executable is imported or copied. `--out PATH` writes the primary receipt
exclusively to a new file; normal replay writes nothing. The registered hook
also runs seven public-CLI tests covering optimized Git-free/read-only export,
missing/corrupted/oversize input, receipt corruption, duplicate keys and output
overwrite rejection.

## Remaining limitations

The path argument applies to the **added correction network**. The inherited
`G/2` channel's original helpers cannot supply new correction dependencies in
this model. If a proposal reads them or feeds targets back, it needs a new
argument. The theorem counts lifetimes, which may exceed simultaneous storage.
The scalar-path argument also assumes input-independent coefficients.

No native transport/phase regeneration, complete added-word endpoint replay,
rounded precision, ownership/idle/residual pricing, full recursive moment,
all-size/compiler lift, outer proof or selected cold replay is performed here.
The selected frontier and frozen predecessors are unchanged. A separate
assistant reviewed the written implication and implemented the independent
finite checker; no independent human or formal-kernel review is claimed.

Python requires allocation during these finite calculations, a Power of Ten
rule-3 deviation bounded by two
fixed inputs, 208 paths of at most ten frames, at most 512 vectors per frame,
10,816 source/target pairs and 256 rank compositions. There is no steady service
or unbounded queue. Static diagnostics use Ruff E/F/I/B/UP with 100-column lines;
repository-wide tooling changes are outside this package. See TASK.json for the
exact run environment, review evidence and unrun obligations.

## Open next questions

Use these inequalities in a source-bound optimization over complete helper
histories, alongside the existing departure/arrival floors, then test any
surviving fully charged bill. A feasible relaxation is not a construction.
The first step is to enumerate the 256 rank compositions with all seven cut
capacities and their actual paid moment; coupling compatible geometric paths
and the chronology remains the blocker. Reopening the homogeneous shape class
requires changing a named model assumption. Structured questions are in TASK.json.

## Credit and sources

Philippe Van Velzen supplied the relay-v2 screen and pricing question at
`fac9e821d31bc199b49e8ed463074a50d1264311`. Nick Petalas's PR2604 supplied the
arrival-shape counterexample and joint-contact handoff. ywz65's PR2614 supplied
the later-read/departure audit; its 336 later-readable entries are predecessor
work. kumagi's PR2353 supplied the explicit monotone-lifetime relay model and
208 floor. The no-relay 4,580 cover of PR2392 has a different premise and is
not asserted here for relay networks.

Rohan Arun / PR1972 supplied the frozen scalar/frame word, retained through
Chafik Boukhalfa / PR1991's native channel. Adam Gall / PR1940 supplied its
schedule; Josie Elliston / PR1071 supplied the fixture, with Ali Romman / PR1125
and the retained PR968/717/446/595/620 geometry lineage. Their existing source
notices remain unchanged. [TASK.json](TASK.json) records exact predecessor heads,
assignment, scope refinement and overlap limits.

Apache-2.0. Substantial AI assistance was used for analysis, implementation,
independent checking and prose. This disclosure is not a claim of human review.
