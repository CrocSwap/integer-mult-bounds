# Attribution and scope

This supplementary tool, independent finite circuit oracle, controls and
documentation were prepared with substantial OpenAI Codex assistance. They are
new verification-engineering work under the repository's Apache-2.0 license.
Independent implementation and review here mean separate implementations and
review within this assisted research campaign; external human acceptance is
not claimed.

The unchanged runtime sources descend from the retained PR531/552/558 exact
Clifford compiler and scalar lineage, credited to icekylinx and earlier authors
in their source notices. The copied phase driver credits icekylinx's
heterogeneous adaptation of PR425 with Codex assistance. The fixed U8 word
descends from JeremyKothe's PR869/870 construction. These sources, word and
existing phase assertions are inherited work, rather than newly authored
compiler or construction algorithms. Their existing license and notice files
must accompany any standalone source archive.

Charles Bethin's PR662, head
`458744109003e0958798f27c1f04be78f03663ce`, is the closest inspected performance
predecessor. It uses gate tables to accelerate this same source-bound state
evaluator. This contribution removes one repeated evaluation within the
monomial phase check; it does not incorporate that gate-table kernel.

The sole generated compiler change reuses the already computed `(vec, den)`
on the right side of one final equality. This package does not modify frozen
construction sources, select a new record, change kappa, or discharge inherited
supplier-hosting and multiplication-theorem assumptions. Source-only reviews,
finite oracle controls, complete-word phase checks and measured timings are
distinct evidence categories.
