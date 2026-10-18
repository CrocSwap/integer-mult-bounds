# Explicit storage allowance for canonical source directories

This is a directory-storage theorem under an explicit caller contract. It
does not construct the complete caller or bound its maximum live payload.
PR2569 supplies the producer and the root/body coupling; PR2590 already
derives its serialized field extent and corrects the producer's runtime
setup cost. We retain those sources unchanged and claim neither result anew.

## Contract and exact extent

Let `q >= 2^80`, `1 <= m <= 64`, `w,n,C >= 1`, and `h >= 0` be integers.
There are `C` old physical positions, including repeated or empty tuples,
`h` frozen fields per position, and one new field. Fix one vocabulary of
`1 <= R0 <= 28278` requests, and use its same minimal code width for all
frozen and current fields. Define

```
N = product_(k=0)^(m-1) (q^m-q^k),
B = bitlength(2 R0 N-1),   L = bitlength(q^w)+1,
H = q^(m²(w-1)),          J = B + m²(L+1) + 2.
```

For a source-correct GL interpretation, q must additionally be an odd prime
and the predecessor's other source premises must hold. The storage inequality
itself only uses the stated integer inequalities, so it does not establish
primality or source correctness by checking a large integer fixture.

The unchanged `append_finite` emits B bits and `WORD_END`; `append_word`
emits L bits and `WORD_END`; each field then emits `RECORD_END`. Thus J is
the exact field extent derived in PR2590. `directory.produce` emits every
old position and every high key exactly once. Counting the tape's initial
`LEFT` cell as well, the occupied directory extent is exactly

```
D = 1 + C H (h+1) J.
```

There is no allocated trailing blank cell in the retained `Tape.cells`.
This is a count of its fixed-alphabet symbols, not Python object overhead.

Let each complete Boolean fibre have R bits and impose

```
R >= q^(2nw),             17(h+1) <= 20051 w.
```

The packet payload is `V = C H R` bits. In particular it includes the entire
body, unused stock and suffix spectators of the predecessor's complete-fibre
contract. R is not just the small slice modified by one local operation.
The depth inequality follows from PR2569's retained coupling
`w=ceil(e^(17/10000))`, `2^(h+1)<=8e²`: taking logarithms gives
`h+1 <= 3+(20000/17)log2(w) <= (20051/17)w`. It is a sufficient envelope,
not a claim that every pair satisfying it is realized by a caller.

## Uniform numerical inequality

Write `ell=bitlength(q)`, so ell>=81 and `2^(ell-1)<=q<2^ell`.
Since `2R0<2^16` and `N<q^(m²)`,

```
B <= 16 + m² ell,             L <= w ell+1,
J+1 <= 8192 w ell + 8211 < 8300 w ell.
```

The last inequality uses `w ell>=81` and `8211<108*81`. Because
`CH(h+1)>=1`, the leading LEFT cell can be absorbed without dropping it:

```
D <= CH(h+1)(J+1) < 8300 CH(h+1)w ell.
```

For integers w>=1 and q>=3, `w<=q^(w-1)`: it holds at one and induction
uses `w+1<=q w`. Therefore

```
D/V < (8300*20051/17) ell * w²/q^(2nw)
    <= (8300*20051/17) ell/q².
```

The sequence `ell/2^(2(ell-1))` decreases for positive integer ell, since
the ratio of successive terms is `(ell+1)/(4ell)<1`. Hence

```
ell/q² <= 81/2^160,
8300*20051*81 < 17*2^30,
D < 2^-130 V.
```

This proves the all-input statement. The strict constant is convenient and
not asserted optimal. No numerical logarithm, enormous high-cube materialization,
sampling assumption or empirical asymptotic fit is used in the proof.

## Physical encoding and use in a caller ledger

The retained record machine has symbols 0 through 13. A fixed four-bit
encoding therefore occupies exactly `4D` bits for this directory. Consequently

```
4D < 2^-128 V,        5D < 2^-127 V,        20D < 2^-125 V.
```

The last two inequalities bound the **directory term** `5D` in the
predecessor's parking formula, in symbol cells and in the four-bit encoding.
They do not include separately mentioned role markers or other caller state.
The smaller directory-only allowance is a constructive storage upper bound;
it is not a runtime bound or an admission of the old literal reserve constants.

For any nonempty finite collection of simultaneously live directories satisfying the
same premises separately, summing gives `sum D_i < 2^-130 sum V_i`, with the
analogous encoded and parking bounds. In particular a live parent and returned
child directory must both be counted. There is no conclusion here that
`sum V_i` equals one current packet, is bounded by the root payload, or follows
the old `V+4v`/`5V+19v` expressions without a new caller occupancy argument.

The caller must still supply those live volumes and lifetimes; route buckets,
odometer and cardinality tapes, control headers, child-private workspace, owned
and borrowed dirty buffers, and restoration state have separate bills. The
finite source executions below validate directory serialization, not those
global peak or numeric reserve obligations. No directory is free.

## Boundaries and evidence

The verifier executes the unchanged producer on complete small high cubes,
repeated/empty old tuples and the selected m=64/w=1 format. An independent
literal serializer checks every returned symbol, the exact J/D formulas,
the LEFT cell and physical multiplicities. Large-q checks use arithmetic
only; the source's fixed-q compiler is not executed at astronomical q.

The countermodels keep the distinctions effective: tiny q, a header-only
fibre, unbounded frozen depth, or arbitrary padding of the supposedly minimal
code can defeat the numerical fraction. Dropping delimiters or the LEFT cell
understates actual serialized storage. These examples do not refute PR2569,
whose complete-body/root-coupling and fixed-format premises are retained.
