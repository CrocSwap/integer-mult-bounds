# Classical matrix boundary transfer with the signed-554 T74 supplier

Conditional final saving **κ = 0.001677641731343354**, exactly
`838820865671677/500000000000000000`, in
`T(n) = O(n (log n)^(1-κ))`.

PR1673's faster matrix-boundary variant was presented with the additional
premise omega_C <= 9/4. Its general effective-stability lemma only requires
omega_C < tau. The established Le Gall 2014 theorem omega_C < 2.3728639
already permits tau=12/5. With this fixed exponent, the boundary row has
ample slack, and the matrix variant combines with the admitted signed-554
T74 supplier to give the rate above. The retained all-size assumptions
still apply. This does not use the supplied Nine Fourths preprint.

Read [CLASSICAL-MATRIX-TRANSFER.md](CLASSICAL-MATRIX-TRANSFER.md) for the
finite-formula, precision, tape and boundary-cost argument, and
[COMPOSITION.md](COMPOSITION.md) for the supplier and exact parameter binding.
The published theorem is a cited mathematical input, not re-proved by the
finite verifier. No competitive finite matrix scheme or runtime gain is claimed.

## Exact inputs and comparison

The words have profiles `{1:2348,2:500,3:416,4:130,5:82,8:8}` and
`{1:2340,2:508,3:420,4:126,5:82,8:8}`. PR1319's owner geometry uses 249
and 417 calls respectively. The complete profile is
`{1:1560432,2:336336,3:278724,4:84912,5:54612,8:5328,48:22748}`,
with dimension 73, live width 66304 and 319680 whole-helper roles.
Prefix 1441 bits is charged at 2048; row coefficient 19545 is below 20161.

The certified complex lower endpoint is
`335950991225108904267/200000000000000000000000`.
Let b be that endpoint minus 10^-30, q=b-10^-30 and a=(b+q)/2.
Choose r0=10^-30, zeta=10^-32, union slack=10^-30 and stop=10^-36.
The retained bit saving is 0.001733427039589844234749.
All numbers are exact rationals. The native moment has an outward rational
upper bound below one at b and rejects the larger endpoint 0.00167975495613.
The outer ledger checks 47 positive inequalities, rejects six bad variants,
and a separate exact elimination checks every paid cost power.

The exact intermediate saving exceeds
0.001677641731343354564251058287; the headline deliberately rounds down.
It exceeds PR1688 head 29a1d0183c12e1d05d78160cb74ed4fa283ff1eb's reported
0.001677255458915620663570888508 by more than 3.8627e-7.
The selected-result record is unchanged. The signed-554 local gain was
independently rediscovered here after PR1672 had already published the
same profile. We claim the checked classical-matrix transfer and composition;
PR1672 has priority for that local kernel, and PR1673 supplies the outer proof.

## Reproduce

Python 3.11 or 3.14, NumPy, SciPy, SymPy 1.14.0, a C++17 compiler and Boost
headers are needed. From the repository root:

```sh
python3 -m pip install -r research/t74-signed554-phase-fusion/requirements.txt
CXX=c++ BOOST_INCLUDE=/path/to/boost/include python3 -B \
  research/t74-signed554-phase-fusion/verify.py --work /absolute/new-work
```

The package is self-contained and supports a read-only source directory.
The driver checks every input hash, stages a byte-identical writable copy
for inherited receipt generators, then always replays the retained parent
and both new native words. It reconstructs owners, checks independent raw
maps and leaver premises, rebinds providers, runs strict controller/invoice/
moment/admission/bit checks and rejects geometry mutations. It replays the
original outer evidence, retains the Strassen case as a positive control,
and validates the new classical-matrix composition. There are no native-reuse
flags. Outputs include RESULT.json, platform-independent MATH.json, logs
and exact receipts. SOURCE-PINS.json binds byte-preserved predecessor files.
Prototype evidence is historical; fresh portable replay is required separately.

`check_recipe.py` verifies complete rational maps and rejects 16 broken
recipes. Native replay verifies frames, wrappers, phases and all 704 columns.
The signed edit removes B342, uses a helper-584 window, two direct target
reads and source-holder 74. Its tail correction has the same sign as its
prefix correction because pivot 554 restores to minus its initial value.

## Scope and credit

The final bound remains conditional on the inherited all-size compiler,
common-label and mutable-source realization, whole-call hosting, semantic
precision with C1=1, fixed-tape and prime-packing interfaces, paid arbitrary-width
equal-chunk interchange, exact recovery and analytic transfer. The written
PR1673 Gaussian and layout arguments remain theorem inputs. Passing finite
checks or CI is not an unconditional integer-multiplication theorem.

Prepared by Chafik Boukhalfa with substantial OpenAI Codex assistance.
New material is Apache-2.0. Original vendor notices and manifests are retained.
Credit Francois Le Gall for the published matrix exponent; Vlado Vojdanovski
for PR1673's capped phase-cell fusion, general stability lemma and union layout;
Rohan Arun for PR1319's T74 exact fill and PR1297's four cold kernels;
Marius-Paul Dumitrean for PR1625's pivot-566 supplier and PR1186's frame toolkit;
Jeremy Kothe for PR1672's earlier signed-554 result and PR1681/1683/1688's
compositions and parameter refinements; and all predecessor authors named
in vendor/pr1625/NOTICE.md and the original source notices. Our search used
PR1186 to solve the shipped frame witness. Separate arithmetic implementations
here are from the same session; no independent human or proof-assistant review
is claimed.

## Open next questions

1. Improve the finite supplier's complex rate. Start with additional restored
   pivot windows and exact frame pricing. A complete paid word and full native
   restoration proof remain necessary before using a better endpoint.
2. Independently review PR1673's complete tape schedule and Gaussian precision
   interface. Start with the sparse-union and support-router lemmas; finite
   algebra tests do not prove the all-size implementation.
