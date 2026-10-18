# Exact cold-end and entrance-promotion composition

The starting word is PR659's 504-helper no-triangle construction with 56 rank-four cold ends, six pivot swaps, eight entering-end extensions and ten dimension-eight cold ends. The changed word adds six cold ends and four entrance-promotion groups. All mathematical local and global admission predicates remain unchanged.

## Six cold ends

Raw helpers 510, 511, 512, 513, 522 and 523 previously ended at dimension nine. For each helper h, an exact row-span relation supplies a partner at a dimension-six frame whose noncold row projection cancels h's. Their frame union has dimension eight. One new tail gate performs the cancellation there. The full inverse column is checked to be supported only on cold coordinates; existing low ends are excluded from this tail.

Let F be the resulting exact state matrix. Elementary dyadic operations at the cold helpers' entrance frame choose a basis so row h and the non-target part of column h become the identity row and column. The target block is retained rather than assumed to be the identity: in general, remaining target compensation solves J*c + H = 0 using the target entries of the full inverse. These frozen repairs need no target compensation or basis swaps. They add respectively 3, 3, 2, 3, 2 and 3 rank-zero gates, for 16 in total.

Exact dyadic Gauss-Jordan elimination inverts the remaining high-frame submatrix. Cleanup touches neither low-ended helpers nor targets. Each new helper keeps entrance frame zero and terminal dimension eight; all 66 inherited cold ends and all entering ends remain. Each end changes the paid profile by `{1:+1, 2:+2, 3:-2}` and reduces residual width nine to eight. `data/COLD72-RECIPE.json.gz` freezes the complete recipe and word hash; `data/NEW-ENDS.json` identifies the six tail gates and repairs used by the 30 focused controls.

## Four entrance promotions

PR664 promotes three four-helper groups from dimension-four entrance frames to dimension-five frames. Its recipe changes only frame annotations and entrance frames, preserving every scalar gate. Our cold-end repair prepends 16 rank-zero gates to A; the rest of A and all of B are exactly the original no-triangle layered word. Its early-tail prefix is also unchanged. We therefore shift PR664's A indices by 16, retain all original old-frame checks, and apply its three promotions to the 72-end word.

The fourth group is raw helpers 659, 661, 662 and 663. Their entrance frame `[298,170,102,30]` is extended by vector 1. Exact span closure changes twelve early gate frames. The new frame remains contained in every subsequent frame and the original centre and terminal frames. Independent admission checks the full scalar maps, entrances, cones, ordered centre interface, phase identities and wrappers after this change.

The fourth group changes the profile by `{1:+8, 2:-8, 3:-4, 4:+4}` and reduces total width by four. The complete four-group recipe has 16 promoted entrances and 120 frame annotations: 48 entry-gate raises plus PR664's 72 retained price-neutral frame choices. It leaves the scalar program of the 72-end input byte-equivalent gate by gate, excluding frame annotations. `data/PROMO4-RECIPE.json` pins the input bytes, every old frame, recomputed profile/widths and final output bytes. The unchanged promotion constructor checks those pins. Eleven mutations test the promoted frames, each group's entry gate, scalar tampering and recipe/input bindings.

The resulting local profile is `{1:2572, 2:326, 3:430, 4:194, 5:56, 8:8}`, with rank mass 5634 and residual width 3778. The full native and independent audits check all 728 arbitrary-input columns in both orientations. The final word also passes 59 inherited end mutations and the 30 focused cold-end mutations.

## Literal physical assignment

For each inherited idle window and width multiset q, the certificate gives an integer bin count N and integer flows f(t,w). They satisfy `sum_t f(t,w) = N*count_q(w)` and `sum_w f(t,w) <= N`. Every time/width inventory equals the complete local helper demand, and each pattern fits its inherited capacity.

Split each width into `count_q(w)` clones of degree N. Time vertices have degree at most N. Add dummy clones and edges until the square bipartite multigraph is N-regular. Counting edges out of a vertex subset proves Hall's inequality; removing a perfect matching leaves an (N-1)-regular graph. Repetition constructs N bins with one occurrence of each real clone and at most one helper from each call per bin.

Search nominated bin counts with a mixed integer relaxation. The selected flow vector was rounded and every resulting integer constraint was checked exactly before expansion. The committed certificate stores only integer marginals and explicit matching slots. Replay invokes neither the optimizer nor a matching library. It checks every physical family, complete helper inventory, window, capacity and byte-exact owner output; seven corruptions must fail. The unchanged controller auditor supplies actual 73-dimensional charts, spectator orthogonality, busy-family intervals and phase chronology. Its one-owner-per-complete-call rule remains.

The 72 local calls use rank mass 405648, leaving 115056 idle units within global mass 520704. The literal assignment has idle profile `{48:2396, 44:1, 3:1, 1:1}`. This is a constructive certificate; it makes no claim that other owner maps cannot improve the moment.

Both retained rational interval engines certify the complex endpoint and reject the next 10^-24 grid point. A separate literal-map checker computes a strict rational interval without importing either engine. The outer assembly retains all 47 strict constraints and the PR589 bit surcharge. All-size realization and analytic transfer remain assumptions.
