# Sources and finite checks

The general claim is a written proof. The checks below use exact arithmetic and independent counting algorithms. They were designed and implemented in the same assisted contribution. Independent human and formal proof-kernel review remain open.

| Check | Domain and observed outcome |
| --- | --- |
| Four-port source control | Invert and decode every one of the 439 retained signed witnesses from Gonzalo Mier's #3997. Compare the complete code set and Nick Petalas's #6691 counts. The 391 zero-one signatures over the rationals and the 355 signatures in GL4 over the two-element field belong to different domains |
| Construction | 3,485 matrices across all positive block splits of sizes 2–6. Check the input and inverse masks, and both inverse products, over Q, F2, F3 and F4 where applicable |
| All six-port labels | Build and invert all 33,727 rational and 33,727 ternary witnesses, and all 30,547 binary witnesses, in their supplied label order. For the rational and ternary cases the second implementation uses integer fraction-free elimination, verifies the scaled inverse product and then reads the masks |
| Generic perfect matchings | All 65,536 unrestricted four-port supports. The 37,823 structurally invertible ones give exactly the predecessor's 439 codes. All 262,144 six-port 3+3 graph-chart supports yield 2,500 codes for that fixed pivot labeling and 188 profiles under arbitrary relabeling |
| Binary spaces | Enumerate both reduced row-echelon spaces and intersect their actual vector sets for every block split through six ports. At 3+3, all 714,240 complementary pairs among 1,395 three-spaces give exactly the 30,547 predicted codes. At 2+2, enumeration of all 65,536 binary matrices independently recovers all 20,160 invertible matrices, including every code's multiplicity |
| Zero-one entries over Q | A separate census covers all 28,836,612,000 invertible six-port zero-one matrices. They give 179 profiles and 32,287 labels. Exact four-port cofactors check the whole small histogram |
| Shared additive prices across three domains | All 35 candidate pairs for two strict gaps have exact positive dependences. Two positive tariffs realize the two different single gaps |
| Ternary spaces | Enumerate all 33,880 three-spaces in six coordinates. Coordinate permutations and sign changes partition the first space into 31 orbits. For each representative, test every possible second space using projective-line intersections. With exact orbit weights, all 666,860,040 ordered complementary pairs give precisely the 188 predicted profiles. The two-port control accounts for 10,530 complementary pairs in four coordinates |
| Closed formulas | The ordinary count and the three separate binary deficits agree with weighted seven-type enumeration for all 78 splits of sizes 2–13. Larger balanced values, including 32+32, are in RESULT.json |
| Tariffs | Twelve label-dependent monotone price tables are checked on every six-port signature. The nonmonotone parity family is independently minimized at balanced sizes 2–8. The 21 rational certificates cover every missing binary profile and use exact integer inequalities or convex weights |

## Why the finite oracles are independent

[matching_oracle.py](matching_oracle.py) does not call the signature classifier or make an incidence test. For each port-level support it determines whether a full matching exists, and repeats the test after deleting the appropriate row and column for each entry of the inverse. The terms of a generic determinant have distinct monomials. A matching therefore characterizes nonvanishing over the rational function field. Encoding the set of supporting patterns in a bitset makes all the cofactor tests directly reproducible. A fixed pivot labeling does not cover every labeled signature, but permitting all label permutations covers every profile by the simultaneous-pivot proof.

[binary_oracle.py](binary_oracle.py) constructs genuine finite subspaces, with no generic-rank assumption. [ternary_oracle.py](ternary_oracle.py) assigns each line its unique point in projective space and enumerates every row-echelon representative. Two equal-dimensional spaces in complementary ambient dimension are complementary exactly when their point sets do not intersect. Each first d-space has q^(d^2) complements, the graphs of linear maps over one fixed complement. Adjacent coordinate transpositions and independent sign changes preserve the seven-type counts under relabeling. For each orbit, its size times the representative's histogram gives the exact total. The total for a single labeling is the profile total divided by its multinomial multiplicity, with exact divisibility checked. For example, with all six messages mixed the pair counts are 64,560 over F2 and 309,983,240 over F3.

The 12 separating prices and nine convex mixtures were found using numerical linear programming during exploration. The committed verifier checks every certificate with integer arithmetic against the complete binary profile set. No optimizer is needed to reproduce the published result.

## Direct replay

```sh
python3.12 -I -W error -B research/two-block-signatures/verify.py
python3.12 -I -O -W error -B research/two-block-signatures/verify.py
python3.12 -I -W error -B research/two-block-signatures/census_check.py
python3.12 -I -O -W error -B research/two-block-signatures/census_check.py
python3.12 -I -W error -B research/two-block-signatures/label_check.py
python3.12 -I -W error -B research/two-block-signatures/zero_one_census.py
python3.12 -I -W error -B research/two-block-signatures/audit_mutations.py
```

Markers are `PASS_TWO_BLOCK_SIGNATURES`, `PASS_TWO_BLOCK_INDEPENDENT_CENSUSES`, `PASS_TWO_BLOCK_LABELED_WITNESSES`, `PASS_TWO_BLOCK_ZERO_ONE_Q` and `PASS_TWO_BLOCK_MUTATIONS`. The fault audit starts with six private-copy positive controls. Twenty-three actual substitutions are rejected for their named reasons under both interpreter modes. They include losing pivot capacity, relaxing an isolated binary entry, transposing the cofactor, treating four elements as two, ignoring an orbit weight, reducing rational determinants modulo two, corrupting a price certificate and altering a retained source. Normal and optimized scientific receipts agree.

All scientific entry points are standalone, work on read-only package files and need no network or Git executable. In a full Git checkout the source-history check runs separately.

```sh
python3.12 -B scripts/check_research_commit.py --package research/two-block-signatures --check-source-history
```

On a POSIX system add `--check-modes` to check executable-mode provenance.
