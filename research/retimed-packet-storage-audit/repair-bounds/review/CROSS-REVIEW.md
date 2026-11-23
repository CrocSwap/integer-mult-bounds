# Independent review of the interrupted local byte census

## Decision

Accept the source-local historical byte bounds in `../PROOF.md` under the
stated installed-layout and valid-call premises. The source route bound
`V+5P+5T+(32/3)R+5b<8V` and padded type-route bound `<9V` are supported by
the literal allocation/erasure loops. The production repair bound is valid;
`SHARP-REPAIR.md` independently improves it to `<=6V` and makes the generic
counterexample boundary precise. No complete `precision_tape` or
`owned_erasure` contract is discharged.

Reviewed original proof SHA256:
`d21a68af1cd9720b691fdd4866452c909955557e211a75f93ead381db88f64cc`.
Source PR #8042 head: `dfd25d553a843a946ca0b94130a5ff8943e98fdd`.
Canonical main: `e54523517d0f03e58352e647c403a5af3e525a57`.
The original source and author proof bytes remain unchanged. Only the
README's generic-counterexample wording and replay registration are
clarified; the new lemma is separately identified.

## Independent source argument

`Receiver.transition` computes the complete compensated body from older
coordinates, both native blocks, the gap and the byte suffix. Its high
packet multiplies that body by the complete high-coordinate cardinality;
the quotient route retains all lows. `OwnerBanks.route` allocates one
complete return owner in addition to that already-backed input bank. Thus
the author's `b`, `R`, `P` and `V` are actual incoming byte extents.

For quotient sorting, the two data roles and three data buckets are each
at most one complete low group. Their five tag counterparts are each at
most the exact `Q*N^2` tag bytes. Distribution erases both old input roles;
merge erases every bucket; final delivery erases both final inputs. This
last observation handles odd `N^2` pass parity and proves that serial
groups cannot accumulate longer tails. All ten fixed positions, not the
largest set of simultaneously nonempty buckets, are charged.

The `high_packet` two roles each hold one complete high packet; each
exposed-prefix `affine_packet` invocation is no larger than that packet
and has three positions. In `unit_scale`, the invariant
`front*3^v*tail=incoming_size` gives three permanent positions of at most
that size. Every seven-position odd site is at most one third per
position; every carry site is also at most one third. The finishes list
holds descriptors, not nested open scaler files. This gives `17R/3`
over all scaler sites, including maxima reached at different times.

Each compensation callback consumes exactly one original body. Its two
named pages and three `lower_tape` roles therefore cost `5b`, rather than
five whole high packets. The exact total is the stated route envelope.
The monotone sequence `N^2/3^(2N)` is at most `4/81` for `N>=2`, and
`Q>=16`. The final coefficient check is
`5+20/81+47/48<7`, leaving a strict margin before `8V`.

For `type_route`, the least ternary extent is less than three times the
true type count. Both full roles fit the padded volume and each radix
bucket fits one third of it, for a sum of three padded volumes. This is
less than nine true volumes. The zero-row, zero-suffix and one-type paths
return without opening those roles.

The Gaussian repair analysis requires byte-sized tags, not one nominal
field per scratch role. The original bound correctly retains those tags.
The independent injective-label argument, zero-bit boundary and exact
sharpness family are proved in `SHARP-REPAIR.md`.

The historical composition requires an additional distinction. Under only
`t<=a`, the sharp six-volume consequence is per invocation; varying good
sets can make a fixed clean role and dirty roles peak in different calls,
giving seven volumes after role-wise maxima. The production header instead
implies `t<=a/2`, so its individual role bounds sum to six volumes even
across arbitrary varying calls. Separate actual all-bad/all-good pairs
confirm both boundaries. The original author's eight-volume per-call proof
is preserved unchanged.

The actual production `Product` constructor enforces `P>=6b` and true
axis product at most `2^b`. The integer inequality
`2^bit_length(side-1)<=side^2` for `side>=2` gives the total padded bit
dimension at most `2b`. The stored Gaussian record has at least `2b`
bytes; spectator packing decreases dimension, the positive entrance only
widens components, and child arenas reduce dimension while preserving
component width. Hence every actual descendant tag is no larger than one
grouped payload. This argument deliberately leaves the original/root
entrance fields and all other live owners separately charged.

## Executed checks and negative evidence

The original complete byte replay was run from a separate copied package
and passed, including the 2,834,352-byte full-high owner, rank-three odd
pass parity, type padding, all unit-scaler sites, physical erasure, source
bindings and all three source mutations. This is regression evidence.

The separately written `check_review.py` supplies independent exact
arithmetic and a label-count oracle for actual repair endpoints; it imports
none of the author's checker or meter functions. It passes 59 valid repair
fixtures, 5,216 bound cases, and a malformed-label control. The 17-bit
example is exactly seven volumes; the 33-bit nine-volume calculation is
marked symbolic and unexecuted. `RESULT.json` contains the receipt.
Eighteen complete small enumerations also check the literal installed row
callback for injectivity and suffix preservation, with payload operations
stubbed and no numerical row-action claim.

## Remaining obligations

The source-selected role inventory is inherited, not a new whole-program
call-graph certification. This package still needs the rest of the ordinary
adapter byte census, the nesting cap, outer CRT/control storage, the
analytic mass enclosure and actual movement tariffs before it can justify
a complete space constant or activation threshold. Historical parent
prefixes, borrowed banks and earlier-stage scratch keep their separate
charges. Source correctness and the complete five-assumption theorem are
not inferred from finite traces.

Ali Romman and the retained predecessor authors retain priority for the
runtime and stage-space architecture. The earlier session's owner and byte
authors retain credit for their proof and checks. This independent review
was prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance;
it is not human peer review or kernel verification.
