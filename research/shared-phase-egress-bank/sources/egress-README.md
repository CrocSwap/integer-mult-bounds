# Normalize and truncate the selected complex layer on literal fixed tapes

**Scoped constructive precision/tape interface; no new kappa.** One fixed
18-tape, four-symbol program reads the actual nine-Gamma layer header and
turns the complete exact C-output packet on the conservative p+d grid into
`Q_p(((1-i)/2)^D z)` in the original w-bit format. Q_p truncates real and
imaginary components toward zero. It stages all output, checks signed range,
then installs the result on the original DATA owner and erases its old tail.

The program has **17,814 literal instruction locations**. Runtime uses only
local-symbol branches, writes, unit moves and fixed jumps. It has no decoded
p,d,D,w,N, host payload arithmetic, address oracle or input-sized source table.
It preserves the original header, exterior contexts and all successful head
origins, and erases every private marker and body. Numerical range rejection
leaves DATA unchanged but does not promise cleanup or head return.

## Exact source boundary and budget

The source's **global d and actual selected dimension D are distinct**.
With input fractional width F=p+d and signed component width H=p+2d+4, the
normalizer first forms exact signed rows (a,c) or (a+c,c-a), rotates them
according to D modulo eight, and drops

\[
s=d+\lceil D/2\rceil
\]

bits of their absolute numerator before restoring sign. This supplies the
single final toward-zero projection, including negative fractions, signed
endpoints and odd-D numerators that overflow H bits before division. It does
not require exact same-grid divisibility at an intermediate boundary.

For N complete Gaussian pairs and header length E, the universal written
bound, including parsing, all copies, source access, staging, installation,
returns and erasures, is

\[
T\le65536(E+p+d+D+w+N(H+w+1)+1).
\]

Private historical backing is at most
`K0+4N(H+w)+16(H+w+E+1)`. Erased cells remain charged. Wider output w>H is
explicitly covered, including the reused source/commit trace. Both costs are
O(V) in the selected source bands, V=2Mrw and N=Mr. Finite precompilation of
the fixed program is separately acknowledged.

Toward-zero projection commutes with multiplication by i^k. Consequently the
supplied final S sweep can run on the projected w-bit return. The **S sweeps
and recursive C supplier remain supplied services**, so this is a literal
numerical egress, not a complete layer implementation. A different coded/LSB
internal packet must be converted and charged before calling this MSB API.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -I -W error -B research/literal-layer-egress/verify.py
python3 -I -W error -O -B research/literal-layer-egress/verify.py
```

Both print `PASS_LITERAL_LAYER_EGRESS` in their identical JSON receipt.
`RESULT.json` records 771 generic packet cases, 515 acceptances and 256 exact
range rejections over 5,125,983 literal transitions. These include every D
modulo eight, most-negative H-bit input, longer output, shrinking payload,
nonintegral negative results and 64 exact signed endpoint cases. Twelve
complete small C/S/H0 tensor fixtures contain 252 fields. Six semantic mutants
are detected: incorrect odd shift, missing absolute conversion, wrong phase
rotation, missing header return, retained old tail and missing source rewind.

The large skipped-header test is a generalized numerical-packet fixture,
not an actual huge selected array: the program deliberately does not verify
N=Mr. Finite checks corroborate the [all-input proof](PROOF.md); they do not
prove its unbounded quantifiers by extrapolation. [SOURCES.json](SOURCES.json)
authenticates seven unchanged source/machine files by bytes, Git blob and SHA256.

Independent dense-machine and universal/source reviews are in [REVIEW.md](REVIEW.md).
Their separate executable commands are:

```sh
python3 -I -W error -B research/literal-layer-egress/independent/dense_check.py research/literal-layer-egress/egress.py
python3 -I -W error -B research/literal-layer-egress/independent/algebra_source_check.py
```

They respectively report PASS_INDEPENDENT_DENSE_EGRESS and
PASS_INDEPENDENT_LOCAL_ALGEBRA_AND_SOURCE_CHECK.

## Novelty and retained obligations

[#2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287) already
specifies the Gaussian normalization identity and linear scan algorithm.
Tekalign's [#3127](https://github.com/CrocSwap/integer-mult-bounds/pull/3127)
already implements an encoded one-pass structured normalizer with exact
same-grid division; its proof explicitly leaves literal lowering and root
truncation. The contribution here is their source-bound **literal numerical
egress**, consuming all nine original header fields, projecting once and
committing the complete result to the same owner. The actual caller proves
its output fits from the retained disk property and w>=p+2.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`. The selected
conditional kappa remains **0.00363005817**. The five assumptions remain;
this resolves one explicit numerical implementation implication inside
precision_tape. Header/layout validity, packet cardinality, common-grid
production, disjoint reserved backing and successful C/S services are
premises. No supplier admission, unconditional multiplication theorem or
replay of the astronomical selected word is claimed.

## Open next questions

1. Join an actual completed C consumer to this original-header/MSB packet
   interface, then execute the final S sweep on its w-bit result. Identify
   and price any internal coding/grid conversion first.
2. Complete the caller's root allocation/stock and source-length witnesses.
   The arithmetic program intentionally does not authenticate N=Mr or
   construct its blank workspace from an allocator theorem.

## Credit

Prepared for **Jerry Chen / @CubeJerry**, with substantial **OpenAI assistance**
in construction, proof, code and verification. Credit Tekalign / #3127,
Jose Manuel / #2287 and #3087/#3091/#3098, the upstream layer/stream authors,
CubeJerry's selected #7000 application, #7349 literal controller framework,
#7350 nine-Gamma header-decoding precedent, and all retained notices. New work is Apache-2.0. Independent model-assisted
reviews are separate from human or formal-kernel acceptance. See `NOTICE.md`.

TASK.json and SOURCES.json are standalone task/provenance records, not the
optional registered replay schema. Exact standard-library commands and
independent-review receipts are documented above and in REVIEW.md.
