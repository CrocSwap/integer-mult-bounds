# Exact local minimum for the R439 frame-509 Boolean endpoint

## Theorem

Fix the four named coordinates `(a,b,h,c)=(33,38,468,77)` at the frame-509 block boundary. In the scalar one-destination ADD model, the Boolean map

```text
(a,b,h,c) -> (a, b+a, h+b, c+a) over F2
```

requires at least three ADDs, and three suffice. In the directed four-register CNOT alphabet (one gate `x_d ^= x_s`, `d != s`), exactly three ordered length-three words realize the map.

## Lower bound and witness

The endpoint changes three distinct destination coordinates, `b`, `h`, and `c`. A scalar ADD writes only one destination, so a word of fewer than three ADDs cannot change all three outputs. This argument allows any register as a source, including dirty helpers outside these four coordinates; it depends only on the one-destination gate contract.

PR #1221 supplies the attaining word:

```text
h ^= b
b ^= a
c ^= a
```

The older four-ADD word is:

```text
b ^= a
h ^= a
c ^= a
h ^= b
```

Both realize the stated endpoint for every Boolean input. The three length-three words found by the fixed four-register census are:

```text
h ^= b ; b ^= a ; c ^= a
h ^= b ; c ^= a ; b ^= a
c ^= a ; h ^= b ; b ^= a
```

They differ only by the position of the independent `c ^= a` gate. The census is a finite exact cross-check; the support-independent destination argument establishes the lower bound.

## Integer transfer distinction

Interpreting each gate as integer addition, the old word has rows

```text
[[1,0,0,0], [1,1,0,0], [2,1,1,0], [1,0,0,1]]
```

and the new word has rows

```text
[[1,0,0,0], [1,1,0,0], [0,1,1,0], [1,0,0,1]].
```

Thus `old - new` is exactly `2 e_h e_a^T`, not zero over the integers. The rewrite is justified by its characteristic-two endpoint inside PR #1221's fully checked splice; this package does not assert integer-map equality or independently replay that splice.

## Exact finite replay

The verifier uses integer row matrices for the two transfers and bit rows for the Boolean circuit. It evaluates all 16 four-bit assignments, checks the old/new Boolean equality and exact integer difference, then enumerates all ordered words of lengths 0 through 3 over the 12 directed CNOTs. It records both word counts and distinct endpoint counts, checks that the target first appears at length three, and verifies the three realizing words. Positive and negative controls exercise a known two-output two-gate target and a two-gate prefix that cannot equal the three-output target.

## Limits

This is a local minimum for one Boolean block endpoint in the scalar ADD model. It is not a shortest-factorization theorem for the original 31-ADD frame-509 block or its 20-ADD post-splice replacement, does not certify a different frame path or boundary map, and does not recheck the complete supplier. No paid recursive profile or κ changes.
