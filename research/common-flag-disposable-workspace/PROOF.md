# Designated data demands, with clean and disposable workspace

This is a boundary-contract corollary of Jose Manuel / @jmbarrancoml's
PR1757 outgoing-transcript argument, extending Navinor / PR825. The cut
method, triangular rank inequality and resulting moment argument are theirs.
The change is to remove the all-role permutation/independent-scratch premise:
only the designated data demands must be recovered. This is not a new general
cut-set principle.

## Precise contract

Fix a finite directed acyclic circuit over an alphabet of size q >= 2. Each
physical wire segment carries one symbol. Gates are arbitrary deterministic
functions, with any finite number of input and output ports. In particular,
constant allocation, copying, erasure, nonlinear gates and changing live
width are permitted. Topology and functions cannot depend on the input.

There are W distinct designated source symbols, independently variable over
the full alphabet. Each has a distinct designated sink that reproduces it
on every input. Other sources may be independent dirty inputs or fixed clean
constants; fixing their values must leave the W data symbols independent.
Garbage outputs have no correctness or restoration requirement. A value
which is copied from data is an internal gate output, not another independent
data source. There is no uncharged external observation, side channel,
postselection or shared input-dependent advice.

Give every vertex a rational m by m frame M_v. Every port of one gate uses
its single frame. Every physical wire e=(u,v), including copies, terminal
wires and garbage paths, is charged rank_Q(M_v-M_u). Local constants and
local discards are granted free. They cannot transmit a symbol between
different frames. For each designated source w and its designated sink t(w),

    M_t(w) - M_w = I_m.

Suppose there are a common A and an invertible B over a characteristic-zero
extension K of Q such that B^-1(M_v-A)B is upper triangular for every v.
Then the complete charged sum s satisfies

    s >= W m.

Neither the number of clean/dirty auxiliary roles nor the number of garbage
outputs occurs on the right. No inverse for a gate, whole-circuit injectivity,
fixed width or restoration of auxiliary values is assumed.

## Data-only cut lemma

Assign arbitrary labels ell(v). For a label a, let D_a consist of designated
data sources with ell(w)=a and ell(t(w)) != a. Let E_a contain every physical
edge leaving class a, with multiplicity. Fix all other source values,
including dirty auxiliaries, and all constants. Vary the symbols in D_a.

Record the symbols on E_a in topological order. Given the transcript and
the fixed outside source values, simulate the vertices outside class a in
topological order. Each incoming port is either an earlier outside value or
one recorded outgoing symbol. A zero-input gate is a known constant; an
erasure has no outputs to simulate. Different output arities do not change
this reconstruction. Feedback across the label boundary is allowed because
the underlying graph is acyclic.

The simulation recovers every designated sink for D_a. Two different D_a
assignments must therefore give different transcripts, regardless of the
unconstrained garbage. There are q^|D_a| assignments and at most q^|E_a|
transcripts, so |E_a| >= |D_a|. Summing over classes counts each crossing
edge once and each separated designated demand once. This is exactly
PR1757's outgoing-message argument with its fixed-source set enlarged.

## Common-flag consequence and price

Use the i-th diagonal entry of B^-1(M_v-A)B as the label, for i=1,...,m.
Each designated source/sink pair has label difference one, so the cut lemma
requires W crossings for each i. For each wire the triangular matrix
B^-1(M_v-M_u)B has rank at least its number of nonzero diagonal entries.
Field extension and conjugation preserve the rank of the rational difference.
Summing proves s >= Wm, with precisely the wire bill declared above.

For every 0 < alpha < 1, charging a positive rank-r wire by (r/m)^alpha
gives a data-normalized moment at least s/(Wm) >= 1. This only applies when
the useful-volume normalization is W independent designated data streams.
Counting duplicate copies or free constants as additional volume is invalid.
No selected supplier's coverage law is replaced by this observation.

The bound is sharp. Transport each of W independent symbols once from frame
0 to I_m, and perform any number of local copies or discards before or after
that transport. Designate one correct sink per source. The bill is Wm.

## Necessary boundaries

* A single symbol transported once and then copied to three sinks costs m,
  not 3m. These are three outputs but one independent demand.
* Permitting one gate's source port at frame 0 and its sink port at I_m
  for free gives an immediate zero-bill identity. The common-frame-per-gate
  condition and complete physical-wire bill cannot be omitted.
* A gate x -> 0 can erase an irrelevant copy. Erasing the only information
  carrying a required symbol cannot satisfy the designated endpoint.
* A source supplied with an uncharged second data-dependent copy outside
  its label class destroys the fixed-source step. Such copies must be
  represented as internal operations with their full wire paths.
  Explicitly, let source x have frame 0 and go only to garbage at frame 0.
  Supply another source with the same value x at frame I_m and connect it
  to the required sink at I_m. Every wire has rank zero, yet the designated
  source/sink frame difference is I_m and the endpoint is correct on the
  correlated inputs. This violates the stated independence-after-fixing
  condition. The executable tests this countermodel and rejects it when
  the two source ports are correctly required to vary independently.

This does not resolve PR2167's unrestricted clean-ancilla rational group-
algebra question: that model has no common-flag premise on all circuit
frames. It does not admit free different-frame COPY in the selected R439
stream, prove a compiler, or bound non-common-flag geometry. The proof is
written mathematics; the finite executable below corroborates its changed
contract and failure cases, not all finite circuits.
