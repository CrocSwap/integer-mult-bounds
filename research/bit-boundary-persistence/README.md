# R438 bit supplier from a legal source boundary

This finite construction removes one helper from the selected PR589 R439 bit
word. At one late read, source77 is still unchanged and is available at
frame186. Receiver444 can enter that frame before its next operation.
The word reads source77 directly, removes helper470, and rebuilds the literal
cleanup and dirty-target compensation.

The complete nine-stage hosted invoice improves bit `c` from
`0.001733427039589844234749` to **`0.001734176288479865766692`**.
This package does not claim a new kappa. The selected PR942 complex value
`0.001664727258740678855772` is smaller than both bit values. The selected
conditional kappa remains `0.001661960547713947` at the research base.

| Complete charge | PR589 R439 | This R438 word |
|---|---:|---:|
| Local helper registers | 439 | 438 |
| Local native ADDs, including D and C | 24,305 | 24,248 |
| Local native records | 27,234 | 27,175 |
| Local paid rank mass | 5,129 | 5,121 |
| Hosted residual roles, nine stages and 32 replicas | 126,432 | 126,144 |
| Paid recursive children, including idle remainders | 904,896 | 904,320 |
| Emitted local records across all 288 calls | 7,843,392 | 7,826,400 |
| Hosted paid rank mass | 1,808,352 | 1,808,352 |
| Live DATA / physical registers | 28,416 / 28,425 | 28,416 / 28,425 |
| Prefix bits / charged bits | 177 / 192 | 177 / 192 |
| Two-level coefficient bits / charged bits | 393 / 512 | 393 / 512 |

The same upstream word is used on both sides. No local circuit saving from
another PR is included. The source path is unchanged. The only surviving
register whose path changes is receiver444:
`[0,79,509,392,513,1]` becomes `[0,186,509,392,513,1]`.
The removed helper had path `[0,79,1]`.

## Reproduce

Use Python 3.11 or later with NumPy, SymPy and SciPy, a C++17 compiler, and
Boost headers. These are the inherited native pipeline requirements.
From the repository root, run the following command. The output directory
must not exist. Set `BOOST_INCLUDE` if the headers are outside `/usr/include`.

```sh
BOOST_INCLUDE=/opt/homebrew/include python3 -I -B research/bit-boundary-persistence/verify.py --output /tmp/r438-source-boundary
```

The last line is:

```text
PASS_R438_SOURCE_BOUNDARY R=439->438 ADDs=24305->24248 paid_calls=904896->904320 c=0.001734176288479865766692 controls=6 no_new_kappa
```

The command uses one worker. It rebuilds both words, checks all source pins,
compiles and runs the original native checkers, emits both complete hosted
schedules, audits them, and computes both invoices. It compares the new
certificate with `CERTIFICATE.json`. It retains the generated words, native
records, schedules, exact receipts, command list and logs in the output
directory. It does not run a hosting search.

`SOURCES.json` pins the two complete dependency packages and two selected
context records at base `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
The packages include source notices and unused historical controls. The selected
bit head is `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46` (PR589).
Regenerated words are compared by canonical JSON, not gzip container bytes.
`FRAME-PATHS.json` gives each physical register path in register order.

The recorded run used macOS 26.6.1 arm64, Python 3.14.7, NumPy 2.5.4,
SymPy 1.14.0 and SciPy 1.18.1. The command records the compiler command and
Boost version-header hash in `RESULT.json`. Remote CI is not claimed.

## Verification and scope

The local checker covers every arbitrary dirty input column: 661 before the
change and 660 after it. The original checker accepts H1-H5, the interleaved
interface, all nine rank-seven copied totals, and the exact full-frame inverse.
An independent literal record builder agrees with the original exporter.
The native C++ checker covers 5, 9 and 11 stages on both words; all 96 omitted
bridge controls reject. Each nine-stage parent audit rejects 17 mutations.
Each whole-residual hosting audit rejects 16 mutations.

Six new controls reject a changed source77, another carrier use, the late
source read in frame79, omitted restoration, omitted compensation, and a
missing returned idle charge. A neutral ADD pair passes and is charged twice.
The [proof](PROOF.md) gives the boundary and complete invoice derivation.

The caller uses a compressed exact cover schedule. It does not enumerate the
astronomical address cover. The all-size bit/Gaussian compiler, common labels,
mutable-source realization, whole-call correlated-helper hosting, common grid,
tape, precision and analytic contracts remain inherited assumptions. Finite
checks do not prove the full multiplication theorem or a practical speedup.

The inherited `assemble9.py` also checks its historical PR548 outer arithmetic
against a cited complex receipt. This is not a replay of the selected PR942
complex construction or its full outer assembly. The selected record is only
used for the stated comparison. The eleven-stage native scalar check is run;
an eleven-stage hosted invoice is not claimed.

## Relation to other work

The initial candidate was to retain a helper basis between adjacent native
calls. The selected caller alternates the DATA roles and advances to other
hosted slices. A scalar cancellation does not establish a legal retained
source and owner boundary there. This package instead changes one intra-call
source access. It makes no repeated-call cancellation claim.

[PR953](https://github.com/CrocSwap/integer-mult-bounds/pull/953) batches dyadic
queries with a shared unchanged source and target. It does not provide this
selected caller boundary. [PR997](https://github.com/CrocSwap/integer-mult-bounds/pull/997)
has a signed Hadamard recursive interface. Its batch is not composed here.
[PR980](https://github.com/CrocSwap/integer-mult-bounds/pull/980), head
`ba1cf68bef0c97dfb120add04304e2de0db6f29c`, retains R439 and all frame paths.
[PR1001](https://github.com/CrocSwap/integer-mult-bounds/pull/1001), head
`fbf54e6c95c47a3891eb7e8ed063b5198e920f3f`, changes B at frame506. This word
leaves B unchanged after register renaming and changes helper stock and a
source-access frame. Their savings are not added to this result.
[PR1015](https://github.com/CrocSwap/integer-mult-bounds/pull/1015), head
`7588c797f4a4e9f2b9fc663cfa6e35afcac05e06`, changes all ten phase-B blocks
and their literal cleanup. Its pinned `candidate_word` changes B and C only.
It retains R439, A, D and the paid recursive profile. This candidate changes
A, C, D, one path and R, while it preserves every B gate under renaming.
No composition of the two words is tested or claimed.

The full-frame obstruction in PR827 fixes A/scatter/B. The closed class in
PR933 fixes the helper stock and cleanup structure. This construction changes
those restrictions. Source inlining and early helper retirement are prior
ideas; PR429/515 and PR433/437 contain related work. No general mechanism
priority, circuit optimum, or absence of other valid boundaries is claimed.
See [NOTICE.md](NOTICE.md) for contributor credit and AI disclosure.
