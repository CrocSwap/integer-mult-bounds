# Six interleaved queries cannot fund one fragment in two binary modules

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0. This is a scoped application of the inherited shortest-query normal form and the body-support argument in `HEADER-SATURATION.md`; no new general shortest-word theorem or κ is claimed. Ali Romman's #6398 and thu-nmrc's #6717 retain credit for the shortest scalar/coupled normal-form lineage. The elementary derivation below makes the exact implication used here independently inspectable.

## Exact contract

There are two binary modules with active pairs `(X1,Y1)` and `(X2,Y2)`, distinct formal body symbols `L1,R1,L2,R2`, and one shared formal central involution S. At body variables one, normalization at S=1 gives

```
I+(S-1)K,      K=E_X1Y1 + E_X2Y2 + I_E,
```

where E is four-dimensional: two S-target directions E1 associated with module one and two E2 associated with module two. Ordinary spectator directions are allowed. Thus rank K=6. The word has exactly six rank-one square-zero central queries, in arbitrary chronological interleaving, with arbitrary ordinary invertible controls.

It retains one atomic native query/body factor for each of L1,R1,L2,R2. Body factors are positive unit-exponent projectors and the final body targets have degree zero or one, so determinant saturation and the common-suffix support argument apply. Each native body's final projector on E is supported inside its own module's two-dimensional Ei. In a single auxiliary fragmentation of module one, precisely one of L1 or R1 omits the S direction assigned to the other side of that fragment; its carrier on E therefore has dimension at most one. The other module's body/target contract is retained. These are substantive hypotheses, not a claim about every coupled producer or compiler.

**Claim:** no such six-query word exists. In particular one fragment in this class needs at least a seventh rank-one central query and cannot pay for it from its gain below one.

## Proof

Rank saturation of the normalized header factorization `K=UTV` puts every query image in `imK=span(X1,X2)⊕E` and every query row in `rowK=span(Y1*,Y2*)⊕E*`. Consequently every query induces a rank-at-most-one square-zero Ai on E, and their six factors multiply to `S I_E`.

The affected native body's query is supported on a carrier of dimension at most one in E. Its quotient Ai must therefore be zero. The remaining five factors have endpoint S I4. Five is minimal: fewer than four cannot supply rank-four coefficient I4, and four give an invertible `I4=UTV` whose implied diagonal `VU=T^-1` contradicts the zero nilpotent self-pairings. Hence exactly one of the six quotient factors is zero and the remaining five are nonzero.

In any shortest `(n+1)`-factor word for `S I_n`, every cross-pairing between distinct rank-one factors is nonzero. Here is the needed normal-form consequence directly. Put `B=VU` and let `B_<` be its strictly lower triangular part, ordering factors chronologically. Expansion using `(S-1)^2=-2(S-1)` gives

```
I_n=U T V,       T=(I+2 B_<)^(-1).
```

The matrix TB is a rank-n projector on an `(n+1)`-dimensional space. Write `TB=I-ab`, with `ba=1`, and set `c=T^-1 a`. Then

```
B=I+2 B_< - c b.
```

Its zero diagonal forces `c_i b_i=1` for every i. Above the diagonal, `B_ij=-c_i b_j`; below it, `B_ij=c_i b_j`. Every such value is nonzero, in every field, including characteristic two. Thus distinct query nilpotents cannot have zero cross-products.

Choose the unaffected native query of module one and either native query of module two. Both quotient queries are nonzero, since the one zero quotient factor has already been identified. Their images and rows are supported inside disjoint subspaces E1 and E2, so both cross-products vanish. This contradicts the shortest five-factor property and proves the claim.

The fragment orientation does not matter: a pure-L prefix makes the affected L1-native quotient zero, while an SL prefix makes the affected R1-native quotient zero. In either case the counterpart native query and a native query in module two provide the disjoint nonzero pair.

## Scope and price

One fragment has signed gain `i(a)-i(a+b)` or `i(b)-i(a+b)`, both below one for the power tariff. A necessary additional rank-one central query costs one, so this exact changed-history class loses even when ordinary work is granted free.

The proof allows arbitrary interleaving of the six rank-one queries and therefore goes beyond a three-block width-two restriction. It retains distinct body symbols, atomic native query/body factors, and module-specific body target projectors. Replacing the bodies by a shared new provider, merging native query roles, changing productive/helper targets, introducing inverse body calls or noninvertible operations, or adding more than two modules changes the contract. No construction or global exclusion is claimed in those larger classes. The five selected framework assumptions are untouched.

## Exact corroboration and a scope control

`interleaved.py` rebuilds the canonical five-query four-dimensional word from its skew-sign Gram, checks its full formal S endpoint, all twenty nonzero directed cross-products, and the rank-one complement of its Gram projector. Q, F2, F3 and F5 rank checks preserve the characteristic-two distinction.

The essential negative scope control is constructive: the two original three-query auxiliary words can be placed in disjoint two-dimensional banks. All twenty order-preserving chronological interleavings of their six factors have endpoint S I4, despite zero cross-products between the banks. Thus shortestness cannot be dropped from the Gram implication. Removing any one factor in any of these twenty words fails; five analogous omissions fail in the canonical shortest word, for 125 omitted-query controls total.

These exact finite fixtures corroborate the stated lemma and guard its scope; they are not an exhaustive search of coupled six-query words and do not establish the universal theorem by enumeration. The checker reuses only the local matrix/central-ring helpers in `saturation.py`. Normal and optimized isolated runs produce identical output and canonical receipt SHA256 `6e34f7061dcb13561974c3a9e70765e85bb6c6e8977aeec6cb0cc64bc98e14e1`.

The body identities are formal Laurent identities. An identity valid only
after imposing a physical relation such as D^4=1 is outside this determinant
argument; a quotient identity is not silently promoted to a formal one.
