# Joint frame and packing search

The exact certificate excludes `kappa = 0.001600620000000000` for every
monotone frame assignment and every enlargement of existing helper entrances
on PR569's three four-cold scalar words, even with fractional provider mixing
and unrestricted capacity-pattern packing. This is less than 0.035% above
PR569. A materially larger gain therefore needs a scalar word, basis, boundary
or architecture outside this explicitly fixed family.

This strengthens the earlier finite list of promotion experiments: it does
not enumerate a selected collection of completed providers. It simultaneously
allows every subspace in each gate's dependency interval and every compatible
transition between adjacent gates. It preserves the scalar operations and
their order, the initial entrance lower bounds, center cuts, target levels and
final caps. The physical-owner chronology and integer provider multiplicities
are relaxed, so an exclusion here applies to that more restricted hosting
problem too. It does not exclude replacing a prefix, choosing new kernels or
gauges, changing output bases, or allowing a separately costed nonmonotone word.

## Experiments

`optimize_frames.py` first optimized all gate frames while keeping the
width-seven eight-provider's entrances fixed. There were 48,136 variables,
42,567 constraints and 2,129 variable gates. Its floating LP returned an
integral assignment with exactly the existing paid profile. Seventy-four
frame changes were cost-neutral; no new provider is claimed from them.

`joint_packing.py` then unlocked every existing entrance up to its exact
future dependency cap on all three four-cold words. The resulting relaxation
has 152,742 variables, 133,135 constraints and all 1,163 patterns for widths
4, 5, 7, 8 and 9 in capacities 8, 16, 32 and 48. Its solution has fractional
local states and is not a physical construction. The numerical nomination is
retained only to make discovery reproducible.

`certify_joint_bound.py` independently converts the nominated messages into
an exact lower bound; it does not import SciPy. The retained
`JOINT-EXCLUSION.json` records a positive rational rejection margin at the
stated kappa. Both unchanged PR564 rational moment engines bound every child
cost. Five controls reject missing provider, edge, state and width information,
and an unjustified smaller exclusion target (`kappa = 0.00160000`).

## Certificate argument

For `b = kappa/(1-kappa)`, use a rational lower bound on

`c_b(r) = r * ((73/r)^b - 1) / b`.

Each register-chain edge joins gate frames `F <= G` and pays
`c_b(dim(G)-dim(F))`. At each edge the checker adjusts the two endpoint
messages until their sum is at most that cost for **every** compatible pair
of states. Summing these inequalities and minimizing each node potential
over **all** of its states gives a valid local lower bound. A helper start
state also receives the dual price of its residual width. Fixed center
descent costs are included once per local invocation.

For each capacity, the checker enumerates every packing pattern and takes
the minimum of its remainder cost minus its width prices. Taking the minimum
local potential over the three suppliers permits arbitrary mixtures. The
width-price terms cancel between helpers and bins. This proves a global
cost lower bound without relying on solver success, tolerances or an alleged
optimal basis.

Changing an entrance removes the same rank mass from its paid path and its
residual width. Thus each supplier retains paid-minus-residual mass 1856;
pending capacities plus 72 suppliers retain total rank mass 520704. The live
stock is 7168 at dimension 73, giving deficit 2560. The certificate checks
`b * lower_cost > 2560`, which rejects the recurrence moment at the target.

## Replay

From this worktree's root, with the pinned PR564 source checkout available:

```sh
python3 -B research/structural-gain/frame-optimization/certify_joint_bound.py \
  --word research/larger-gain/providers/words/zero/FULL-WORD.json.gz \
  --word research/larger-gain/providers/words/four/FULL-WORD.json.gz \
  --word research/larger-gain/providers/words/eight/FULL-WORD.json.gz \
  --plan /path/to/PR564/research/complex-allcold/data/PLAN.json \
  --source /path/to/PR564/research/complex-allcold \
  --messages research/structural-gain/frame-optimization/DUAL-MESSAGES.json.gz
```

The same command works under `python3 -O`: checker failures use explicit
exceptions. Discovery uses NumPy 2.5.4 and SciPy 1.18.1; these are unnecessary
for the certificate replay. File and external-engine hashes are retained in
the receipt. `NUMERICAL-NOMINATION.json` contains the original local paths as
provenance, not as required replay locations.

Prepared by Dominik Scholz with substantial OpenAI Codex (GPT-6 Astra)
assistance. The dependency-chain implementation is retained unchanged from
PR569, which credits icekylinx's frame coalescing and the inherited compiler
and scalar-word authors. See the parent package's attribution and
`research/larger-gain/NOTICE`. Apache-2.0.
