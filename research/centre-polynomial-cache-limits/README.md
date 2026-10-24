# Two limits for historical centre encodings

This package retains two results that were outside the 22 October campaign
publication closure. It adds no native supplier and does not change the
complete kappa calculation.

- The actual doubled centre Gram has scalar minimal-polynomial degree at
  least 409 at every positive tensor size. An exact scalar-polynomial
  inverse of `aI+bA`, when it exists and `b != 0`, has degree at least 408.
- The smallest scalar row space that contains a query and is closed under
  specified diagonal updates has dimension equal to the sum of its fiber
  ranks. The historical query needs 56 rows for the stated normal-character
  family and 112 rows for six specified coordinate characters.

These are different models. The first result does not bound general ADD
circuits or native decoder cost. The second result assumes a common scalar
input representation. It does not supply or price native source access.
Neither result closes the physical caller, helper, terminal, precision,
hosting, or recursive admission obligations of the historical campaign.

Read [the proof and claim limits](PROOF.md), [source pins](SOURCES.json), and
[credit and predecessor comparison](NOTICE.md). The original proof,
certificate, checker, and independent Bell review are retained without edits
under `frozen/`. Other statements in those historical notes are context.
This package adopts only the two results stated above.

## Replay

Use Python 3.10 or later with NumPy. The source check uses exact rational
and integer arithmetic. No Git checkout, source archive download, or
network service is needed at runtime. Use a new output directory.

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -B replay.py --out /tmp/centre-polynomial-cache-check
```

Expected final line:

```text
PASS_CENTRE_POLYNOMIAL_CACHE_LIMITS
```

The replay checks every frozen source digest. It runs the retained Bell
producer and the separate sparse-operator reviewer. Their receipts must
equal the retained receipts byte for byte. The reviewer derives the query
matrix from the original scalar word, checks 57,344 Bell columns, reproduces
all 817 moments, and uses separate determinant arithmetic. The producer
rejects a duplicate row. The reviewer rejects a duplicate column.

The scalar-cache check uses rational elimination. It checks both dimension
sequences and the 512-character rank histogram. It also checks an explicit
fiber row basis and rejects a basis with one necessary row removed. The
written proof supplies the general theorem. A finite check does not prove
the general theorem by itself.

No full supplier, native decoder, selected frontier, or outer kappa replay
is part of this check. No human review or formal-kernel proof is claimed.

## Open next questions

- Does the historical Gram have minimal-polynomial degree exactly 409?
  The first step is to find and check an annihilating polynomial for the
  full operator. The present certificate proves only a lower bound from
  one invariant block. No annihilator is supplied here.
- Can the 56-row scalar cache be loaded, updated, and cleared within a
  useful native bill? The first step is to specify the physical source
  access and helper contract. The current row-space theorem does not
  supply those operations or their cost.

These questions are outside this package. This replay does not perform
either proposed investigation.
