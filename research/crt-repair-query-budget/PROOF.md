# Current-state CRT queries in an exceptional repair key

This is a scoped audit of the handoff in Ryanson Jonathan's PR4409,
[`crt-evaluator-independent-check`](../crt-evaluator-independent-check/README.md).
It connects Cinna Davis's PR4100 CRT controls to the explicit reverse word
in PR4169 and amends one accounting expression from unpaidmoon's PR4377.
The exact retained inputs are pinned in [SOURCES.json](SOURCES.json).
There is no new multiplication saving or selected-frontier change.

## 1. Three query sites in the literal key evaluator

Use the complete modular address domain and hypotheses of
[PR4169](../crt-arbitrary-source-repair/PROOF.md): the compact controls are
arbitrary dirty fields, the target intervals are disjoint, and every Boolean
source function omits every active target and the borrowed controls. Write
`L(y)=sum_i f_i(y) B^i`. The raw compact word and its literal inverse are

```text
S:       F; u += L(y); F; u -= L(y)
S^-1:    u += L(y); F^-1; u -= L(y); F^-1.
```

Each assignment is reduced in its complete cyclic field. The existing proof
establishes this inverse for every address, including exceptional addresses;
it does not replace `F^-1` by the guarded XOR formula.

For an input address `z`, name the successive y fields `y0`, `y1` after
the first `F^-1`, and `y2` after the second. Evaluating the correction key
`R(z)=T(S^-1(z))` therefore has exactly these three source-query sites:

```text
L(y0), L(y1), and (f_i(y2))_i for the final ideal switch T.
```

These are three evaluations of a vector of controls, not three queries per
elementary modular assignment. The current y field must be supplied at each
site. On exceptional addresses, carries can alter non-target coordinates;
the source-independence hypothesis does not make these three vectors equal.
This is a property of the literal evaluator, not a lower bound on every
possible implementation of the same permutation.

PR763's exceptional-stream theorem already proves that this correction key
places each payload at its ideal destination. We reuse that theorem and
PR4169's explicit inverse; neither generic repair nor inverse correctness is
claimed as a new result here.

## 2. What can be cached, for every residue vector

Fix a left child A with m>=1 pairwise coprime integer moduli
`s_0,...,s_(m-1)>=2`. For a target modulus s>=2 outside A, let Q be the
product of the earlier moduli in its right child. Assume all these moduli
are pairwise coprime. Put

```text
S_A = product_j s_j,       P_j = product_(k<j) s_k,
C_j = S_A/s_j,             alpha_j = C_j^-1 mod s_j,
mu = (S_A Q)^-1 mod s,     w_j = P_j C_j alpha_j mod S_A.
```

These quantities depend only on the fixed modulus list and target position.
In particular, their inverses can be prepared independently of every address
and payload: m inverses for the alpha_j and one for mu suffice. Multiple
targets sharing A may share its alpha_j. This is an available construction,
not a minimal inverse count.

For every valid current left vector `0<=a_j<s_j`, the retained
`decode_group` formula and a fixed-weight reconstruction agree:

```text
k_A(a) = sum_j ((a_j P_j) mod s_j) C_j alpha_j mod S_A
       = sum_j a_j w_j mod S_A,
c(a)   = k_A(a) mu mod s.
```

Indeed, replacing `(a_j P_j) mod s_j` by `a_j P_j` changes its term by a
multiple of `s_j C_j=S_A`. Reducing the constant coefficient modulo S_A
also preserves the sum. This proves the identity for all valid vectors,
without assuming that the coordinates arose along a particular CRT run.

On the full padded domain, first test the current left coordinates. If any
`a_j>=s_j`, set the offset to zero, as PR4100 requires. Thus a total query is
`c(a)` on valid left vectors and zero otherwise. Both reconstruction and
the validity test concern the current state. Cached alpha_j, mu, products
and weights remain valid through changes of state; a cached k_A or offset
need not. The target tail remains fixed by the padded rotation.

One may instead retain the literal `decode_group` arithmetic and replace
only its modular-inverse calls by these cached constants. The budget below
allows a fresh full reconstruction, including fresh inversions, at each
query. It consequently requires no unproved saving from a cache, nor a new
tariff for the fixed-weight formula. In particular, three source-query sites
do **not** imply a lower bound of `3(m+1)` modular inversions.

## 3. Conditional seven-term source-table allowance

The following is conditional on PR4377's credited local arithmetic and
Beneš scan tariffs. It does not independently establish their tape model.
Let integers `p>=2`, `ell>=1`, and `q=p+2` be given. Assume at most `8q`
target axes and `m,W<=8q` per axis. Every left modulus and target modulus
must have at most ell bits, as must each padded current coordinate supplied
for comparison. W must cover the complete modulus-prefix operands,
including the right prefix `S_A Q`; the retained W-bit/2W-bit operand
premises must hold for the reconstruction arithmetic. We assume the
per-axis reconstruction allowance

```text
C_axis = 128 m W^2 + 128 m ell^3 + 16 m W.
```

This tariff is a premise, not a consequence merely of `m,W<=8q`.
In particular, W cannot be interpreted as the left-group width while
ignoring a longer right-prefix operand.

Price the current validity test separately. Assume each copied coordinate
and its fixed modulus are supplied in aligned, zero-padded ell-bit slots,
with both heads at the first prescribed most-significant origin. Sweep all m
slots forward, resetting the local comparison flags at each slot, and return
both heads once after the last slot. A sequential
lexicographic comparison uses two bit reads, two forward head moves and
at most six Boolean/flag operations per bit; returning both heads costs
another two moves per bit. At most four further operations initialize,
retain and combine the comparison flag. Since ell>=1, `12ell+4<=16ell`.
Thus testing all m coordinates and combining their validity flags costs
at most `16m ell` per query and axis, including these local head returns.
This premise supplies the aligned inputs; extracting fragmented coordinates,
copying them into these slots and transporting their descriptors are not
priced by this comparison tariff.

PR4377 charges C_axis once before building networks from one offset.
For the three current-state queries, allow it three times. Conservatively
build both the positive and negative rotation networks at each query, six
networks per axis. This also avoids assuming a network remains usable after
the left coordinates change. Retain its per-network bound

```text
25(ell+2)^2 2^ell + 64 ell 2^(2ell).
```

This bound survives PR4409's correction of the smaller per-wire estimate:
`4(ell+2)+8(ell+2)^2+8ell <= 25(ell+2)^2` for ell>=1.
Allow three descriptor scans, each bounded by `256q^2`. Substituting the
axis cap and m,W bounds, and adding `3 A 16m ell<=3072q^2 ell` for
the current validity tests, gives the conditional seven-term allowance

```text
E_src = 768q^2 + 1572864q^4 + 24576q^3 + 24576q^2 ell^3
      + 1200q(ell+2)^2 2^ell + 3072q ell 2^(2ell) + 3072q^2 ell.
```

For all the stated parameters, `E_src <= B0 = 2^(4ell)q^16`. To prove this,
each term divided by B0 decreases with q because its q-degree is at most
four. It suffices to take q=4. At ell=1 the seven terms are

```text
12288, 402653184, 1572864, 393216, 86400, 49152, 49152;
sum = 404816256,          B0 = 68719476736,
sum/B0 = 3162627/536870912.
```

Each term is at most B0/8. Increasing ell by one multiplies B0 by sixteen;
the seven respective term factors are at most `1,1,1,8,32/9,8,2`. Induction
therefore preserves all seven bounds, and their sum is at most B0. This proves
the full integer tail; finite checks are corroboration, not its justification.

With `G=64(ell+ceil(log2 q))`, the original amortization follows unchanged:
`2^-G E_src <= 2^(-60ell) q^-48`, since `q^64<=2^(64 ceil(log2 q))`.

## 4. Evidence and boundary

[RESULT.json](RESULT.json) records a reduced, genuine CRT switch fixture
after physical reservoir placement. Its literal reverse trace changes a
left reconstruction/offset, and freezing the entry offset gives a different
repair key. This discriminates state refresh from merely recounting calls.
The fixture is not a production-sized parameter instance and cannot disprove
PR4100's asymptotic envelope. Its role is to reject that frozen-offset shortcut.

The allowance above covers three source-table evaluations under the stated
local tariffs. It does not price the complete key evaluator's modular address
updates, arbitrary descriptor movement, payload extraction/sorting, reservoir
placement, or a complete fixed-tape implementation. Evaluating forward S as
well would add its own two source-query sites. No such extra work is silently
included in E_src, and no full multiplication theorem follows from this bound.

Credit Cinna Davis for PR4100, unpaidmoon for PR4377's tariffs and envelope,
Ryanson Jonathan for PR4409's independent check and inverse-query handoff,
and ToikY for the predecessor Beneš audit. PR4169 supplies the explicit reverse
word and PR4174 the reservoir placement used by the fixture. John-Michael Smith
and Douglas Colkitt supplied the prior compact carry/repair argument in PR763
and its construction lineage; the retained source notices remain applicable.
Prepared for Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review or proof-assistant acceptance is claimed.
