# Compact storage preserves the exact census

This is an implementation-equivalence argument for the retained finite
verifier. It does not add an independent proof of its mathematical theorem.

Let `n` be the number of matrices. The original enumeration visits every
ordered triple `(a,b,c)` with `0 <= a,b,c < n`, `a != b` and `b != c` once.
The compact loop has precisely those bounds and conditions. Its `mul` and
`pack` callables are the unchanged authenticated reference functions, so it
computes exactly the same full matrix key for each triple.

## Word encoding

For `n >= 1`, define `e(a,b,c) = (a*n+b)*n+c`. Repeated Euclidean division by
`n` recovers `c`, then `b`, then `a`. Thus this map is injective on three-digit
base-`n` words, including words with leading zero. Code zero is handled by
the storage and decoding helpers, although it cannot arise in a reduced
triple because `(0,0,0)` violates both adjacent-inequality conditions.

For `n=0` or `n=1`, there are no reduced triples. No decoding occurs, and both
implementations return zero total, an empty histogram and an empty relation
set. No division by zero is needed for this degenerate domain.

## Class invariant

After any prefix of the enumeration, each full matrix key has exactly one
of these representations:

- One encoded word if precisely one triple has reached the key.
- The complete insertion-ordered list of encoded words if at least two
  triples have reached it.

The first insertion stores an integer. The second replaces it with a list
containing both the original word and the new word, then adds one reference
to the collision index. Subsequent insertions append to that same list.
These transitions preserve the invariant by induction. The absence sentinel
is `None`, so integer zero does not mean absence. Each non-singleton class
occurs exactly once in the collision index.

The dictionary retains the complete packed matrix integer. Python's hash
table resolves hash collisions by key equality; the program neither stores
truncated hashes nor equates distinct keys with the same Python hash.
There is no assumption that a collision class has size at most two.

## Identical outputs

Subtracting the number of indexed collision classes from the number of full
keys gives the exact singleton count. Adding the lengths of all collision
lists gives the original class-size histogram and total triple count.
The empty histogram is retained when no triples exist.

Singleton classes produce no ordered pair of distinct words. For every
other class, decoding its complete member list reconstructs the original
triples exactly. Both implementations consider every ordered pair `left !=
right`, form `(a,b,c,f,e,d)` from `(a,b,c)` and `(d,e,f)`, and apply the same
six cyclic adjacent-inequality tests. They therefore retain all the same
oriented words, with the same final set deduplication. This argument applies
to duplicate matrices and classes of
arbitrary size, not only the retained instance.

For the retained 112-route instance, 1,379,952 triples form 1,379,852 singleton
classes and 50 two-word classes: 1,379,902 distinct full keys. The original
representation retains a member list for every key; the new representation
retains 50 encoded member lists plus one collision-index list. Decoding each
collision class uses a temporary list of triples. This retained-object count
reduction explains the intended memory benefit. A portable RSS percentage
does not follow from the count; the benchmark measures fresh processes.

## Composition and coverage boundary

The optional composition supplies the same storage object with keys from
Charan's unchanged, byte-pinned PR3219 `prepare` and `product_key` functions.
It preserves that implementation's enumeration and key computation exactly.
The storage proof above applies to either key producer. The pending row-table
code remains separately credited and is used only by the explicit comparison
modes; the canonical and compact workers do not read it.

Every full replay executes the retained source checks, route extraction,
pair uniqueness, involution and relation checks, complete Fano searches and
positive/negative controls. Each run must reproduce the original receipt
byte for byte. The comparison also fingerprints the total, full histogram
and sorted complete relation set, so equality is checked beyond the
aggregate counts present in the original receipt. Small tests use a separate
dense matrix oracle and deliberately corrupt storage transitions and codes.

There is no persistent acceptance cache, skipped triple, sampled relation,
new mathematical conclusion, supplier admission or selected-frontier change.
