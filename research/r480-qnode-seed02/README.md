# R480 Q-node2: 52 to 43 XORs, including paid reverse cleanup

**Status: finite bit-supplier construction; no new kappa.** One twelve-source
block in the historical PR503/510 R480 word uses 43 rather than 52 XORs.
Rebuilding its literal reverse cleanup saves **18 ADDs per complete local
word: 33,958 to 33,940**. The 480 helpers, nine copies, register frame paths
and paid recursive histogram remain unchanged.

The replacement preserves the fixed F2 outputs on arbitrary inputs. It does
not preserve the positive integer transfer: the local forward bound grows
from 25 to 99. Separate complete-word positive-prefix checks admit the
replacement within the inherited 104-bit allowance. This is a useful small
construction on a historical supplier, not an updated selected exponent.

## Reproduce

From the repository root, with Python 3.10 or newer and no Python dependencies:

```sh
python3 -I -B research/r480-qnode-seed02/verify.py --replay-search
```

Expected final line:

```text
PASS_R480_QNODE_SEED02 block=52->43 ADDs=33958->33940 columns=720 payload_bits=102 no_new_kappa
```

This verifies the pinned source closure, regenerates all 1,000 search trials,
checks every fixed output, runs two separately implemented whole-word
interpreters on all 720 persistent columns, checks exact positive bounds and
negative controls, and compares the complete receipt to `EXPECTED.json`.
The same command works under `python3 -I -O -B`; its checks use explicit
exceptions, not removable assertions.

To export both complete canonical words without modifying inherited files,
add `--emit /absolute/path/to/a/new-directory`. Existing output directories
are refused. Regenerated gzip bytes need not match across compression
implementations; comparisons use the complete canonical JSON payload.

Additional package regression checks:

```sh
python3 -I -B research/r480-qnode-seed02/test_package.py
```

For the unchanged retained C++ legality, 5/9/11-stage column, mutable-source,
interface and Gram checks, use a C++17 compiler and Boost headers:

```sh
BOOST_INCLUDE=/path/containing/boost CXX=c++ \
  python3 -I -B research/r480-qnode-seed02/native.py \
  --out /absolute/path/to/a/new-native-directory
```

The default Boost include root is `/usr/include`; it must contain
`boost/multiprecision/cpp_int.hpp`. See [VALIDATION.md](VALIDATION.md) for the
executed native results, environment and exact scope. The native wrapper
writes all raw logs and receipts into the new output directory and compares
the normalized mathematical results with `NATIVE.json`.

## Evidence and limits

- [RECIPE.json](RECIPE.json): the exact replacement, fixed matrix, search
  domain, seed, full length histogram, improvement sequence and local bounds.
- [PROOF.md](PROOF.md): substitution argument, full local cost, precision
  admission, controls, inherited assumptions and outstanding obligations.
- [EXPECTED.json](EXPECTED.json): two-implementation finite replay receipt.
- [SOURCES.json](SOURCES.json): 21 immutable input hashes and Git blobs at
  base `407d52ff15b2217b6e22bce44728b4c3907b6515`.
- [CLAIM.md](CLAIM.md): assignment seed2, alternatives, overlap review and
  completed search coverage.
- [NOTICE.md](NOTICE.md): predecessor attribution, license and AI disclosure.

No lower bound or optimality claim is made for the 43-XOR word. The selected
PR942 U8/T37 record remains conditional kappa `0.001661960547713947`, using
the unchanged PR589/555 bit supplier at this base. A global hosted-parent
invoice, outer assembly and all-size realization are outside this result.
Finite certificate success is not a formal proof of the multiplication theorem.
