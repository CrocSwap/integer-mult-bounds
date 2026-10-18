# Native fused queries at the ordinary BIT boundary

This package gives an enabling algebraic theorem and scoped obstructions.
For every odd prime-power modulus m>=11, exactly two separately encoded
PR840 fused DATA blocks suffice for three genuine ordinary-interchange rows
if arbitrary binary linear encoders and their inverses are free. The proof
constructs the factors. It does not supply cheap uniform tape encoders, an
admitted BIT supplier, or a new kappa.

A single fused block cannot give any positive number of whole ordinary rows
under this encoding contract, even with arbitrary restored dirty helpers.
The comparison uses full binary VALUE operators. It includes short orbits
of prime-power order and all spectator coordinates. Physical helper frames
must first be normalized. Different entry and exit adapters need a separate
cost and rank analysis.

[PROOF.md](PROOF.md) gives the quantified proofs and all cost terms.
[CERTIFICATE.json](CERTIFICATE.json) records the exact finite evidence.
[SOURCES.json](SOURCES.json) pins the copied source bytes.
[NOTICE.md](NOTICE.md) gives attribution and the AI-assistance disclosure.

## Main results

Let one complete row have U=S m^6 bits, with m=p^b for an odd prime p.
Let h be the six-field native ADDRESS map of PR521. Its exact orbit count is

    K = S m^5 [1+b(1-1/p)].

The PR840 centered shear has difference rank r=U-K. One ordinary three-field
bank interchange has difference rank t=S(m^6-m^3)/2. At m=3, r<t. At every
other odd prime power, t<r<2t. Thus r is never a positive integer multiple
of t. Conjugation preserves this rank, so one fused block cannot implement
whole ordinary rows with restored helpers.

Two blocks escape that obstruction. For three genuine rows and m>=11, put
`t3=3t`, `z=t3-r`, and `e=2r-t3`. Then z>=0 and e>=2. In a Jordan basis of
the ordinary endpoint minus I, use the complementary blocks

    A=diag(0_z,I_z,C_e),       B=I+A.

Choose C_e and I+C_e invertible by direct sums of blocks of sizes two and
three. Both factors have rank r. They give square-zero maps with zero mutual
products and the required sum. Thus both factors are conjugate to the native
fused block. No extra helper row is needed. One block is impossible, so two
is the exact optimum in this model with free encoders.

The native orbit quotient also gives a separate obstruction. Same-h power
queries and constant role XORs cannot transport bits between native orbits.
The ordinary endpoint must do so. For q genuine rows, arbitrary added linear
adapters A_i must satisfy

    sum_i rank(A_i-I) >= q(K-S m^3)/2.

This is a rank charge, not a general time lower bound. It gives a time
obstruction for the explicit implementation that uses a complete tape scan
for each individual bit-XOR transfer. A structured encoder could group many
transfers in a scan. That route remains open.

## Literal construction and complete cost

The checker constructs two encoders at m=3 for one genuine DATA row and two
arbitrary dirty helper rows. It lowers both fused blocks to actual ordinary
children and ordered-affine events. It executes every independent VALUE
column, checks both helper endpoints, and executes the literal inverse.
It then repeats the program on two full spectator fibers. No row is copied,
cleared or initialized.

| Program | Genuine bits | Dirty bits | Input columns checked | Ordinary children |
|---|---:|---:|---:|---:|
| m=3, S=1 | 729 | 1,458 | 2,187 | 6, each of volume 729 |
| m=3, S=2 | 1,458 | 2,916 | 4,374 | 6, each of volume 1,458 |

For S=1 the literal word has 36 affine events, four full-row XOR scans, and
21,606 individual bit-XOR transfers. The transfer count doubles at S=2.
Each recursive child retains the full spectator volume. The complete cost
also includes source access, encoder generation and storage, primitive
scratch, routing, parking, counters, head returns and restored child work.
Equations (9) and (10) in the proof state these costs.

For one genuine row, the six children each have volume V and width N/3.
Their moment is `6/3^(1-c)>1` for every c>=0. This rules out only that
one-genuine-row construction with two restored helper rows. Those helpers
cannot be counted as productive DATA volume.

For three genuine rows, the abstract two-block construction has six children
each of volume V/3 and width N/3. Its child-only moment is `2/3^(1-c)`.
This is favorable for some positive c, before encoder costs. The supplied
Gaussian encoder emission uses individual bit transfers. A complete scan
per transfer costs at least `V * 3(K-S m^3)/2`. For S=1 and fixed p, this has
order at least `b m^11`. It fails the required time bound. Cheap uniform
encoders, arbitrary widths, routing, hosting and recursive admission remain
unresolved. No new c or kappa is asserted.

## Reproduce

Use Python 3.10 or later and its standard library. No network, Git metadata,
solver, predecessor import, or package install is needed after checkout.
From the repository root run:

```sh
python3 -I -O -B research/native-query-boundary/verify.py
```

Expected result:

```text
PASS_NATIVE_QUERY_BOUNDARY full_addresses=665444 prime_power_cases=13 dirty_columns=2187 escape_children=6 no_new_kappa
```

The command compares the complete canonical receipt with the committed
certificate. It checks copied-source hashes before the mathematical replay.
It rejects a missing certificate or a changed field, including an integer
replaced by a Boolean. To emit the complete literal program for inspection,
use a new output path:

```sh
python3 -I -O -B research/native-query-boundary/verify.py --emit-word /tmp/native-boundary-word.json
```

`--emit` can write a fresh receipt to a new path. It does not overwrite the
committed certificate. The ordinary command does not write any files.
[VALIDATION.md](VALIDATION.md) records the checks and their limits.

The finite domain is fixed in the certificate. Full six-coordinate census
uses m=3,5,7,9 and covers 665,444 addresses. A separate two-coordinate census
uses 13 specified prime powers, including widths through five and short
orbits. The three-row theorem has exact two- and three-dimensional block
checks and dimension/rank checks for nine moduli at least 11. The full m=11
encoder matrix is not allocated or replayed. The universal theorem follows
from the written construction; a finite replay is not its formal proof.
There are no random choices or unreported search cutoffs.

## Base, current context, and prior attempts

Exact base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
Its selected record names Jonathan Capalbo's PR942 assembly with
`kappa=1661960547713947/1000000000000000000`. The complex exponent is
0.001664727258740678855772; the BIT exponent is 0.001733427039589844234749.
The complex side binds. The copied selected record is a base reference.

A later live read at main `ba82555c64e1879e4b7decce28186f208fcb8262` selected
PR1042, with `kappa=1672188119205421/1000000000000000000` and complex exponent
0.001674989015937672328468. Its BIT exponent is unchanged. This package uses
the stated base and source pins. It does not change the selected construction.
A BIT improvement alone would not raise either selected kappa.

[CLAIM.md](CLAIM.md) records the three candidate approaches, local claim,
prior negative results, and overlap review. The direct same-h word fails on
the orbit quotient. The one-block encoder fails on full-domain rank. A second
block gives a complete one-genuine-row escape, but its child bill fails. The
three-genuine-row extension removes that child-volume penalty algebraically;
the supplied encoder still fails the tape budget. This is why the result is
an enabling proof with scoped obstructions, not an installed supplier.

PR521 supplies the native map. PR677 supplies restored DATA-shear contracts.
PR840 supplies the fused three-query word and its explicit unresolved ordinary
boundary. PR990 changes the private batching hypothesis but still uses the
same native map. Their source pins and notices are retained. The earlier
seven-map and eighth rank-one archive screens, PR955's fixed complex words,
PR720's abelian formal model, and PR836's complex unitary model are different
classes. This work does not repeat those searches or claim to supersede them.
