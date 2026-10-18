# Complete relay composition and a later-read-aware departure floor

The construction is Philippe Van Velzen's literal relay-v2 word at commit
`fac9e821d31bc199b49e8ed463074a50d1264311`, using 1,031 helpers. His earlier
2,185-helper word at `d35dd88e3bd344600e879af3427c104a95b1ff05` is retained
and independently replayed as a historical comparison. Both constructions
and the 208 floor are credited results. PR2594 already supplies the v2
correction-only endpoint and growth audit; no such result is claimed new.
This package supplies a missing geometric step in the all-network departure
argument and independently binds each entire relay to the original channel.

## 1. Exact composition of the retained words

Each initial persistent register has its own independent formal input. There
are 280 original inputs and 1,031 new dirty inputs: 1,311 total for v2. A register has
a rational row in those inputs and a binary frame. Its physical interpretation
is the frame's canonical chart applied to that row. The original channel's
native chart interpretation is inherited; no new native compiler is asserted.

An ADD is accepted only at equal frames, and adds the specified rational
multiple of the source row. A transport changes the frame but not the logical
row. The original private zero/copy/erase semantics are retained explicitly.
New relay helpers all start at ZERO with independent dirty rows and may only
move to strictly larger containing frames. Relay reads use only X; writes
only add to Y; shears use only the new helpers at equal frames.

A cut c means after exactly c events of the 4,058-event original channel.
Relay accesses carry explicit cut labels; the checker advances the original
channel to that cut before executing the access, and checks its actual frames.
Move/shear operations occur at the most recent access cut. In the supplied
word the only cuts are 0 and 4058. There are 17,624 relay operations after its
inventory header, so the combined v2 sequence has 21,682 events. No source is
assumed available at its entrance frame after channel completion.

Induction over this merged sequence checks the exact rows and frames at every
event. Its endpoint is

    X_s -> X_s,       Y_t -> Y_t + X_t,
    every original and new dirty helper -> its original input.

All source/helper endpoint charts and each target endpoint chart match the
original declarations. Sparse row equality checks every coefficient, including
absent coefficients as exact zeros: 1311^2 = 1,718,721 comparisons represented
by 1,415 nonzero entries. The second implementation independently parses both
words, reverses all event adjoints, and checks the full transpose using exact
dyadic integers. Every division must be exact; it is neither modular testing
nor floating-point approximation. No predecessor executable is imported.

This is a finite rational identity for arbitrary independent data. It does
not rely on scalar samples, zero helper entrances, endpoint-only frame
matching, or the predecessor checker's success.

The v2 relay profile is 2427 H1 + 1094 H2 + 998 H3 + 96 H4 + 66 H5 + 157 H6
+ 2 H7, of rank mass 9,279 = 9*1031. With the original channel, the rank
mass is 11,647. These are boundary transport ranks, not global recursive
excess costs. All 1,031 new helpers live across the base channel. The retained
v1 comparison has 28,156 combined events, 2,465 inputs, 6,076,225 coefficients,
and combined rank mass 22,033; both full-matrix interpreters check it too.

Eight original private erasures remain nonzero, each with a 53-term logical
row. They use the inherited owned private-copy disposal contract. The relay
does not silently convert those erasures into strict-zero restoration. A
native implementation, global owner/idle/residual bill, precision contract and
all-size supplier admission remain unproved here.

## 2. Model for the all-network lower bound

Fix the same original source and target frame paths. A correction may add any
finite number L of new helper lifetimes. Each begins in ZERO with arbitrary
independent dirt, moves monotonically through nested frames, mixes linearly
only with helpers at the same frame, reads immutable X only at a source's
actual frame at that cut, and writes additively to Y only at the target's
actual frame. It cannot read Y or original G/Q/D/private helpers. All new
helper values restore at FULL. Arbitrary rational coefficients and cancellation
are permitted. The desired correction matrix is C=I-G/2.

The original channel neither writes logical X nor reads Y. Thus inserted
additive target changes do not create extra feedback routes through the base
word. The correction's dependence on an independent X_s must originate in
one of its permitted reads of that X_s.

Let ell_s be the source's initial line and H_t the target's final hyperplane.
Every source frame contains ell_s; every target frame is contained in H_t.
The source lines are distinct. No frame on any target path equals any source
line. Both facts are checked from the complete frozen chronology, not inferred
from dimensions alone. In particular useful source information must leave its
line before it can be written to a target.

## 3. Remove the demands that later source reads can serve

Let T_s={t:C_ts != 0}. These 48 targets are exactly those with ell_s contained
in H_t. Define

    R_s = {t in T_s : some source frame V on X_s's path has
                      dim V > 1 and V contained in H_t},
    F_s = T_s \ R_s.

Granting EVERY frame on the source path is favorable: it even ignores whether
the timing would permit a particular relay. Thus a later read can influence
a target in F_s only if a dependence could subsequently move from a frame
not contained in H_t into H_t, which monotonicity and equal-frame mixing
forbid. A source-to-target dependence path never decreases its frame. For
t in F_s, every contributing read of X_s must therefore occur at ell_s.

There really are later-frame opportunities: sum_s |R_s|=336. A global
line-only assumption would be false. The retained predecessor checks plane
covers on all T_s and states that its floor survives later reads. The additional
witness needed for that implication is

    intersection_(t in F_s) H_t = ell_s      for every s.        (1)

LINE-WITNESS.json records every F_s, every R_s, the full intersection and a
two-plane cover of all T_s. Two implementations check the data: reduced
binary bases and literal enumerated subspaces. The forced-target sizes are

| Forced targets per source | Number of sources |
|---:|---:|
| 36 | 12 |
| 44 | 24 |
| 45 | 8 |
| 46 | 24 |
| 47 | 24 |
| 48 | 12 |

This certificate is specific to the frozen P104 paths. The argument below
quantifies over all finite permitted correction networks on those paths.

## 4. Two departures per source, despite arbitrary later reads

Fix s. Consider dependence on X_s along the permitted linear computation DAG.
Every nonzero output coefficient has at least one directed dependence path;
cancellation may remove paths' combined coefficient but cannot create a path
where none exists. For t in F_s, that path must start with an ell_s read.
It must then leave ell_s, since no target ever visits that line.

Suppose at most one helper lifetime leaves ell_s. If none does, no forced
target can receive X_s. If exactly one does, call its first strictly larger
frame W. Every dependence path from an ell_s read to any forced target must
pass through that departure. Later branching or mixing cannot leave the
superspaces of W. Consequently W is contained in H_t for every t in F_s.
Equation (1) gives W contained in ell_s, contradicting dim W > 1.

Hence at least two helper lifetimes depart from each ell_s. A monotone helper
lifetime can visit at most one of the 104 distinct one-dimensional source
lines. Summing the disjoint departure counts proves L >= 208.

The explicit two-plane covers corroborate sharpness of this per-source cover
relaxation only. They do not construct a 208-helper complete correction.
Neither the 1,031-helper v2 word nor the historical 2,185-helper word attains
the lower bound. No stronger
floor, global optimality, or universal merge-loss accounting identity is
claimed. In particular the predecessor's design-dependent loss count is not
used to prove a bound for arbitrary networks with redundant births or exits.

## 5. Scope of the independent result

The added result is independent complete composition evidence plus the
later-read-aware implication (1), not a new relay design, improvement of 208,
or discovery of the already reported 336 entries. It preserves the valid
lower bound without assuming that all useful reads occur on source lines.
It does not close the large gap between this construction and a favorable
supplier allowance. The selected frontier and source packages are unchanged.
