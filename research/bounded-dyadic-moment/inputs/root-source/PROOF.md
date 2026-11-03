# An exact root certificate for the complete current price

## Domain and source

Use the complete PR6453 target and paid histograms, from head
`b1a3e525793eca35c56324aa7ffd0b714cf606d4`. Let c_r be target multiplicity
minus paid multiplicity. Define

    F(k) = sum_r c_r * r^(1-k).

All ranks are positive integers. The input record includes the source
local/native/caller receipts. The retained price module independently
assembles the complete histograms from those inputs and compares its two
invoice methods. This package does not regenerate the native word or
prove those source input contracts. It checks the complete price module,
including strictification, compiler, retained BIT admission, and all
54 strict and four functional outer predicates.

## Why verification does not require root search

The published source result already gives adjacent endpoints on the
10^-26 grid. Treat those endpoints as an untrusted certificate. Check
integer types, the grid, adjacency and containment below the retained
BIT cap. Then compute rigorous enclosures of F at both endpoints.
Require the lower endpoint's lower enclosure to be positive and the
upper endpoint's upper enclosure to be negative.

The retained price code proves F is strictly decreasing on the relevant
interval. The intermediate value theorem therefore gives one unique
root between the certified endpoints. The endpoint checks establish
exactly the same raw bracket as a successful binary search. The method
accepts no approximate root, tolerance test or floating-point sign.

`pricing_fast.py` changes only the retained binary-search block to a
call to `checked_bracket`. A verifier compares the rest of the source
text after standard newline decoding. It keeps both original rational
moment engines, their strict endpoint tests, the derivative proof and
every later cost/compiler/outer check. The complete encoded price receipt
must equal the original source receipt byte-for-byte after canonical JSON
encoding. The new helper also checks the endpoint signs before returning.

## Constructing a new certificate

A changed invoice still needs a root search. The generator uses exact
interval Newton on [0,1/100]. The retained arithmetic engine bounds

    F'(k)  = -sum_r c_r * r^(1-k) * log(r),
    F''(k) =  sum_r c_r * r^(1-k) * log(r)^2.

For each sign of c_r, choose the correct endpoint of the power interval.
The resulting derivative interval is strictly negative on the complete
initial domain. The exact endpoint signs give a root there. The largest
absolute endpoint of the second-derivative interval is a valid global
curvature bound M.

For a current interval I=[a,b] and midpoint m, the mean value theorem gives

    F'(x) in F'(m) + [-M*(b-a)/2, M*(b-a)/2] for x in I.

Intersect this enclosure with the initial derivative interval. The
powers used for F'(m) are the same cached exact powers just computed for
F(m). No acceptance result or numerical root is cached.

For the true root z, another application of the mean value theorem gives

    z = m - F(m)/F'(xi), for some xi between m and z.

Thus the interval m-F(m)/F'(I) contains z. Compute the four rational
quotients, intersect with I, then round the lower endpoint down and the
upper endpoint up to the integer grid. These operations cannot remove z.
The code rejects a derivative interval that meets zero, reversed
intervals, an empty image or a failure to contract. It stops after at most
16 rounds. It does not pretend to return a strict adjacent bracket when
a root lies exactly on the grid or the arithmetic cannot resolve a sign.

For this source, four contractions reach

    328701955375063425072028 / 10^26
      < root <
    328701955375063425072029 / 10^26.

The complete rational trace is in CONTRACTION.json. The two-engine
endpoint checks in the complete price replay then certify the bracket
independently of the construction trace. This is the existing source
crossing, not a new kappa or a claim of more decimal precision.

## Evidence and limits

Registered normal and optimized checks regenerate the four-step trace,
exercise ten failed certificate/derivative cases, and compare complete
baseline and candidate price receipts. The benchmark runs three
alternating fresh-process pairs through the complete price module, with
source authentication. It does not time only a favorable search step.
All consumed sources and inputs are hashed. Timings are host measurements,
not mathematical acceptance conditions.

The source invoice, native/caller validity and five framework assumptions
remain conditional. The selected frontier is unchanged. No full native
replay, physical tape, rounded multiplier, formal proof kernel or
independent scientific acceptance is supplied.

## Attribution

Interval Newton, certificate checking and the mean value theorem are
standard. The source-specific integration and curvature reuse are by
Ali Romman with substantial OpenAI Codex assistance. zxv retains the
strictification interval engine and price lineage; Jacob Alan Sussman
retains mixed-target recursion credit. Cao Yifan and the retained compiler,
outer and elementary-function authors retain their credit. Erwan L., Rohan
Arun, DreamingOfClouds, Cinna Davis, David Arias, Gareth Davidson and the
retained P104/caller lineage keep their construction credit. Apache-2.0.
