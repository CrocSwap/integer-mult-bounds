# Bounded predecessor and freshness review

Canonical source: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
This targeted review does not establish absence of all earlier related work.

* `research/current-rounded-scalar-tables` at CubeJerry public
  `6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57` already proves literal fixed-q
  SCALE/ADD by direct carry, builds the 52-SCALE class, and explicitly leaves
  large ADD numerical carry graphs and full source inventory open. We reuse
  its unchanged physical fixture and lifecycle, and replace the numerator
  stage with coefficient-bit Horner passes and a new two-bank marker layout.
* `upstream/build/sections/02-streams.tex`, full-file Git blob
  `088fceea1867abc76271d7efe7532b779fee9039`, supplies signed linear stream
  arithmetic, fixed power-of-two operations, guard bits and charged reversals.
  The reviewed excerpt was lines185..215; we do not present an excerpt's
  hash as that full-file blob or claim a newly invented arithmetic principle.
* `research/rank7-one-carry-scalars/README.md`, blob
  `0a15051fa99b1e7e8af27a1169583fc0691654ef`, NickPetalas/#3094, uses one
  clean Boolean carry for selected dyadic/sign ADD circuits with borrowed
  source restoration. Its circuit model is distinct from this sequential
  numeric numerator/division table; it remains credited.
* `research/scalar-fused-dyadic/README.md`, blob
  `87ff8713a47320af0157146c5f3b5a4fb85c1085`, optimizes host rational/bitplane
  audit normalization, not this literal lifecycle primitive.
* `research/gaussian-scalar-backend-audit/README.md`, blob
  `35d8acdec29207a95dca69f1403c70acd9a307fc`, is an offline interval oracle
  and explicitly not the required physical coefficient producer.
* `research/copy-floor-arithmetic/README.md`, blob
  `5ba5198aa4496d88df88902624a2ab39569d2ad6`, concerns source COPY/rank
  arithmetic, not a rounded binary payload codec.
* DreamingOfClouds' #6937 total RDiv automaton is already credited by the
  rounded-scalar predecessor. Our claim is not first existence of total
  fixed-rational rounded division.

The source census/source witnesses retain #6936 head
`03626137d0bd57f09b0bf9597376183ce6fa9683`. The lead's exact 20:11 UTC
refresh reports head `d360b1182b6d21b1ee2354856abcb50646ad618b`, whose
only delta is the VERIFY.json timeout, with unchanged actual word/claims.
#6937 remains `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`.

Allocation is complementary to the native worker's variable-g rounded
positive leaf. This package has a fixed coefficient and fixed d per table;
it does not implement a runtime-variable shift, divisor or leaf header.
The lead's three-QUERY rank lower bound is likewise a different claim.
