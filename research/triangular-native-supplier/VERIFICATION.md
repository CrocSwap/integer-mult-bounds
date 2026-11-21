# Reproduce the construction

Use Python 3.12. The registered suite requires only its standard library. Run the following from the repository root. The runner extracts the checked source bytes to a private temporary directory. It generates the local coefficients and acts on the data. It needs neither the network nor an installed native binary.

```sh
python3 -B scripts/research_package.py --package research/triangular-native-supplier
```

Each of the eight checks prints `PASS_TRIANGULAR` and its case name. The runner then prints `PASS_REGISTERED_RESEARCH_PACKAGE research/triangular-native-supplier outcome=completed`. The measured work is specified below. [Verification manifest](VERIFY.json) · [Recorded results](EVIDENCE.json)

| Case | Evidence | Scope |
| --- | --- | --- |
| prices | Six integer debit inequalities, both entrance recurrences, all 2,382 raw pairs and 111 joint frames. The largest numerator or denominator in a fixed scale is 20. | Fixed word, its finite price margins, old necessary and new sufficient entry, the connected row budget and the uniform occupied-tape bound. |
| body | Independent address calculation on 648 through 52,488 tagged records. Test weights from different ancestors, composite atoms, an upper operation, a permutation and a non-coordinate projector. | Same-order transport, changed payload, peeled coordinates and inverse. |
| raw | Rebuild the complete rank-134 source at moduli 3 and 9. Each run visits 107,460 paid cuts and returns 20,706 owners. Five nonconstant seeds take distinct routes. | Raw-word identity on sparse independent checks. The production receiver pays for every slot. |
| quotient | Run the full rank-two orbit at modulus 27 on 11,664 records, and rank-three tests at moduli 3 and 9. Check 104 variable units and 174,648 records at widths 1 to 8. | Independent pivot-minor oracle, free high ordinal, triangular correction, inverse word and unit carry. |
| whole | Compare the quotient route, a changed projector and its inverse on 10,368 independent payloads. Test 177,147 further independent records on 27 genuine high matrices. Run direct three- and four-atom subtrees. | Actual bank and recursive terminal operations, sinks, gaps, suspended older records, physical owner slots and cleanup. |
| movement | Identical 559,872-byte inputs and outputs on both machines. Count each read, write and absolute reposition, all temporary extents, and releases. | Native body cost at matched rank and shape. Setup and the independent oracle are outside these two movement traces. |
| product | Five public signed tape invocations through 4,333 input bits. On the same two coprime CRT axes 3 and 5, run the previous caller, the new schedule and the new schedule with real rank-two CRT padding and return. | The ordinary public selector uses its finite branch at these input lengths. The three separate Fourier runs use explicit diagnostic dimensions. |
| numerics | Check early geometry before the large-width regime, four exact later geometries, a rational column on all 32 padded wires for both signs, both true mixing layers and a full signed product at 72 working bits. | The raw rational residual exceeds the former transform target and satisfies the target derived for integer multiplication. |

For the signed test the convolution before carry is `[11811, 10996, 4152, 868, 77]` followed by ten zeros. All three pipelines return `-345550037539` with the input intervals and neighboring sentinels preserved. The rank-two diagnostic makes 138 physical CRT exchanges and processes 633,744 padded bytes across their entrances. Each complete Fourier run makes 157,248 H calls. The implementation generates its rational tables. Host multiplication and the address oracle appear only in validation. The rank-134 replay checks the real powered source independently of the small numerical test. Feasible test sizes cannot measure the time or storage of the production ranks. [Integration check](check_integration.py) · [Product tape](multiplier.py) · [Raw word check](check_raw_body.py)

The matched movement control supplies 139,968 independent four-byte records, an older field, a non-radix gap and a remainder. It compares the complete body under the old and the new contracts with the same returned physical order. The output SHA-256 of both is `2c9b8912ab88883cc9bb7cccc6a60a9847e60db8b8846b1d08462dc8d4d390ac`.

| Logical tape measurement | Previous body | New direct body |
| --- | ---: | ---: |
| Input bytes | 559,872 | 559,872 |
| Earlier ordinary transfers | 1,668 | 6 |
| Peak simultaneous tape extents in bytes | 10,171,008 | 5,600,664 |
| Bytes read | 502,889,472 | 48,148,992 |
| Bytes written | 1,005,219,072 | 95,738,112 |
| Absolute reposition distance in bytes | 1,509,667,632 | 140,527,872 |
| Transfers plus reposition in bytes | 3,017,776,176 | 284,414,976 |

These numbers show 10.61 times less traversal and 1.816 times lower peak on that body. The complete asymptotic storage comparison comes from the two numerical fields and the stripe backing proof. The route measurement alone gives no complete-product speed ratio. [Tape instrumentation](tape_meter.py) · [Complete storage proof](NUMERICAL-STORAGE.md)

## Matched complete-product file traces

The optional full-product meter runs the same signed operands through the predecessor at 136 working bits and through completed packs at 72 working bits. Both use 48 public bits, the same CRT map, the same 157,248 H calls, both forward transforms, the opposite transform and the signed binary output. The intervals are the smallest canonical input and output byte strings. It counts reads, writes, seeks and simultaneous extents on all the data files used by these calls. The private coefficient compiler runs before timing. Python integer objects, the tiny stopped-H arithmetic workspace and operating-system buffering are outside this file meter.

| Complete finite Fourier execution | Previous at 136 bits | Completed packs at 72 bits |
| --- | ---: | ---: |
| Peak occupied data-file bytes | 4,550 | 2,886 |
| Bytes read | 1,398,559,398 | 824,729,548 |
| Bytes written | 2,183,719,143 | 1,287,775,757 |
| Absolute reposition distance in bytes | 10,134,631,012 | 5,976,863,588 |
| Total byte traversal | 13,716,909,553 | 8,089,368,893 |

The diagnostic returns the same exact integer with 1.70 times less file traversal and 1.58 times lower peak file occupancy. The chosen working widths exercise the two numerical targets at a small explicit geometry. Neither width is a measurement of the large-family selector. One local run took 0.945 and 0.818 seconds for per-geometry setup and 96.394 and 92.066 seconds for execution. These are single host observations. Run `python3 -I -B research/triangular-native-supplier/measure_product.py` for the two complete file traces. [Full-product meter](measure_product.py)

## Lean and source checks

Install Lean 4.34.1 and the mathlib revision in the Lake manifest, or use a matching local cache. From the repository root run the following. A full Git checkout with the pinned predecessor commit objects is needed only for the separate provenance command.

```sh
python3 -I -B research/triangular-native-supplier/verify_formal.py
python3 -I -B research/triangular-native-supplier/verify_sources.py .
```

The first command builds all the listed roots, checks each requested axiom report and runs the standalone kernel checker on each of the eleven new modules. The only axioms in the 64 reports are `propext`, `Classical.choice` and `Quot.sound`. The space checks verify the 446-bit integer comparison for the private auxiliary bound and the depth and stripe inequalities through the whole connected range. The radix replay reconstructs 128 actual destination-tag reads using 17,408 independent key comparisons. Three consecutive rank-three groups check 11,232 further tag reads, 8,004 suffix ties and all ten reused spool cursors. The second command cross-checks 27 direct, 97 nested and 11 retained formal sources against their original Git bytes. [Formal monitor](verify_formal.py) · [Dependency monitor](verify_sources.py) · [Pinned inputs](SOURCES.json)

Lean verifies the uniform numerical storage comparisons, the active-forest injection, layer counts, free-first historical slot identities, complete reserve division and positive child multiplicity at each direct or quotient call, the price and entrance arithmetic, same-order conjugation on independent payloads, the quotient change of representative, the unit-scaler identities, padded mean contraction, the axis partition and the gate-to-carried-product implication under the stated local estimates. Source-specific gate synthesis and interval estimates, code refinement, the full sequential clock, stripe bounds and effective physical entry have written proofs and finite cross-checks. The proof does not extract the Python program from Lean. Scientific acceptance and practical crossover remain open. [Formal endpoint](lean/GatePacks.lean) · [Active fields](lean/ActiveForest.lean) · [Uniform occupied space](ACTIVATED-STORAGE.md) · [Binary proof](BINARY.md) · [Growing-carrier proof](STAGED-CARRIERS.md) · [Formal assumptions and predecessor credit](NOTICE.md)
