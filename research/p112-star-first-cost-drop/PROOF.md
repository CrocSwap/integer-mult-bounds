# First copy-cost drop versus first frame-hit change on P112

## Object and counting conventions

Use the 120 true E8 root lines in doubled coordinates, with inner product `dot/4`, and puncture the eight specified orthogonal frame lines to obtain P112. The binary label pairing is `N(i,j) = (<r_i,r_j> + 1) mod 2`. The masked decoder's constrained entries are exactly those where N is one, including diagonal entries. The odd entries permit the predecessor's free rank-zero corrections.

For every root-line normal alpha, the two parent supports are `C(alpha) = {i live: <r_i,alpha> != 0}` and `N(alpha) = C(alpha) minus alpha's own line`. For an ordered parent pair U,V let M be the binary label matrix on U x V. We analyze only parents with rank M = 7. A further trim removes S from U and T from V, keeping the live P112 set fixed. Its cost is the rank of `M[U\S,V\T]`.

The deletion budget is `|S|+|T|`: deleting a label from both factors counts twice. This is a term-support deletion, not a global puncture of a root line. The constrained-position loss counts distinct original one-entries of M removed by either axis, counting their union once. It measures support coverage and does not count paid operations or required repair terms.

## Erasure lemma: all subsets from a small code

For any binary matrix M of rank r, its column code `C(M) = {M x}` has dimension r. Let d be the minimum Hamming weight of a nonzero codeword.

**Row erasure lemma.** The minimum number of rows whose deletion lowers rank is exactly d.

Deleting S projects the column code onto the remaining coordinates. Rank falls precisely when this projection has a nonzero kernel: some nonzero codeword is supported wholly inside S. Hence every rank-dropping S contains a nonzero word's support and has size at least d. Conversely, deleting the support of a minimum word kills that word, so it lowers rank. On F2 this minimum-cardinality cut lowers rank by exactly one: another independent kernel word would have support contained in the same size-d set, and minimum weight forces that support to be the entire set. There is only one binary vector with that support.

The same argument applies to any nonnegative coordinate weights. For constrained-position loss, weight row i by its number of one-entries in M. Then the minimum loss under a rank-dropping row deletion is the minimum weighted nonzero codeword. A zero row never appears in a codeword support, so this minimum has positive weight and is attained by a rank-dropping cut. Column deletion uses the transpose code and analogous column weights.

**Joint erasure lemma.** A joint row/column restriction preserves rank r if and only if each corresponding one-axis restriction preserves rank r.

Choose a rank factorization `M = A B`, where A has r independent columns and B has r independent rows. A row restriction preserves rank exactly when the restricted A remains injective; a column restriction preserves rank exactly when restricted B remains onto. If both hold, their product has rank r. The converse follows because the joint rank is no larger than either one-axis rank.

Therefore the minimum *total* support deletions for a joint rank drop is the smaller of the two one-axis minimum distances. For the loss metric, any rank-dropping joint cut includes a rank-dropping one-axis cut, and its union of lost one-entries contains that one-axis loss. Thus the minimum joint loss is also the smaller of the two weighted code minima, attained by a one-axis cut.

This proves that enumerating 127 nonzero codewords per rank-seven orientation certifies **every arbitrary row and column deletion set**, including sets much larger than a first-drop witness. It is not a sampling argument or an enumeration of just small cuts.

## Complete numerical instance

The pinned PR1226 model has 240 tagged C/N supports and 57,600 ordered parent pairs. There are 7,616 tagged rank-seven pairs. Tags can describe identical supports when a normal is punctured; the certificate also reports distinct support sets and distinct ordered pairs.

The complete column-code census gives:

| Minimum rows deleted | Tagged orientations |
|---:|---:|
| 20 | 5,376 |
| 22 | 1,344 |
| 24 | 896 |

Applying the joint lemma and using the transposed orientation gives:

| Minimum total row-plus-column deletions | Tagged parent pairs |
|---:|---:|
| 20 | 5,376 |
| 22 | 2,240 |

The minimum constrained-position loss is 560 for 5,376 tagged pairs, 624 for 448, and 656 for 1,792. Each table entry includes both minima, attaining cuts, minimizer counts and a digest of the complete 127-word code. Both implementations replay a rank-six attaining cut for each one-axis minimum. In particular, **fewer than 20 support deletions cannot lower any original rank-seven atom's copy cost**, and every rank drop removes at least **560 constrained positions** from that atom's support. The stored witness attains both global floors.

The finite instance is checked by two implementations. The primary engine enumerates linear combinations of a column basis. The second engine obtains row coordinates and enumerates every nonzero dual functional; it validates the E8 root set independently by Weyl reflections. Their complete ordered tables agree, including codeword digests. The erasure lemmas supply the inference from those finite code tables to arbitrary support cuts.

## Geometry changes earlier: exact threshold four

Every factor used in an original cost-seven parent is self-trimmed N(alpha), or an identical C/N support whose normal is already punctured. This is checked over the entire parent census. Let F be a live orthogonal eight-frame. If alpha belongs to F, N(alpha) misses F. Otherwise every nonzero `<alpha,f>` has absolute value one, and Parseval in the orthogonal norm-two frame gives

`sum_(f in F) <alpha,f>^2 = 2 ||alpha||^2 = 4`.

Consequently a self-trimmed support meets F in either zero or exactly four lines. Fewer than four deletions on a factor cannot change whether it meets a frame. A total joint budget of at most three therefore preserves every atom frame-hit indicator.

Each live normal belongs to 90 of the 1,260 live frames; a punctured normal belongs to none. Each factor therefore meets at least 1,170 frames, and every parent pair meets at least 1,080. The primary replay checks this over every cost-seven parent. In a met frame, erase its four row-support members. The atom then misses that frame. Since four is below the first row-rank drop threshold, its copy price remains seven. The certificate gives the frame and deleted rows, and the second engine checks orthogonality, the lost hit and unchanged rank independently.

Thus the first frame-hit change has exact total-deletion threshold **4**, while the first copied-information drop has threshold at least **20**. One extra live-line trim changes neither quantity. Removing 4 to 19 support members can change geometry without obtaining a copy-cost saving.

## Relation to decoder assembly and physical cost

A cost-six atom exists after a minimum cut, but assembling such atoms into an exact masked decoder is a further obligation. A rank-zero correction has no one-entry of N on its support, so it cannot restore an affected constrained entry. Other costly terms may cover many such positions at once; the 560-position floor is not a lower bound of 560 repair operations or terms.

This proof introduces no helper, source access, frame operation, copy, restoration or recursive child. It screens the term-level copy price before a physical construction. It does not establish a favorable complete moment, a decoder below cost 64, or a new kappa. Further trims of original cost-eight/nine parents, other support families, other punctures, shared-copy pricing and coefficient synthesis are outside this result.

## Credit and proof status

Navinor (@navinor), PR1226 at `8b10989e4e45f0f9ce41004d7898a21a32f87e11`, supplies the root-star family, P112 model and parent census. David Arias (@DavidAriasC), PR1236, proves the sharp cost-64 assembly floor for exact parent supports. Hanson Sun (@bbMisk), PR1242, independently corroborates that floor and identifies the further-trim question. The masked model and free odd-entry correction come from DreamingOfClouds/PR717; the root/label geometry retains the PR968 lineage and notices.

The erasure and rank-factorization principles are elementary coding/linear-algebra facts. This contribution supplies their exact application, sharp thresholds and complete census in the enlarged P112 trim family. New work: Cinna Davis, with substantial OpenAI Codex assistance. The two implementations are part of this same AI-assisted contribution and do not imply independent human review. Finite regression tests support implementation correctness; no proof-assistant formalization or full multiplication theorem is claimed. Apache-2.0.
