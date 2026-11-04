# Two individually sharp lower bounds can add

Over the ternary field, a full pencil may require **both** the entire slope-separation budget and the entire scalar-imbalance budget. This failure can be arbitrarily large in a single pencil.

Let $r,n\ge1$, $m=2r+3n+1$, and take $u$ to be all ones. Put $r$ entries $+1$ and $r$ entries $-1$ in $w$, followed by $3n+1$ zeros. Put zeros in the first $2r$ slots of $b$, and ones in the others. Then $wu=0,bu=1$. Use all three rows $b+a w$. The separation distance is $r$ (opposite pairs), and the signed scalar imbalance bound is $n$ (initial imbalance $3n+1$). The full guard distance is exactly **$r+n$**.

For sufficiency, cancel the $r$ pairs within the slope slots. Merge $n$ pairs of ones within the scalar slots into $n$ negative charges and $n$ zeros. The resulting slope charges vanish and the scalar imbalance is one. The ternary ordering rule supplies a passing permutation.

For necessity, commute monomial operations to the end and form the graph of paid additions as in PROOF.md. A component contains $a$ original nonzero slope slots and $l$ original scalar-one slots. Its conserved slope total must be zero, so $a$ is zero or at least two. Write $D_C$ for its final signed scalar imbalance, using the lifts $0,+1,-1$ of field elements. Its initial imbalance is $l$, so $(l-D_C)/3$ is integral. We claim each nonempty component requires at least $a/2+(l-D_C)/3$ additions.

If $l=0$, the entire restriction of the scalar row $b$ to this component stays zero, so $D_C=0$ and connectivity requires at least $a-1\ge a/2$ additions. Otherwise $l\ge1$. There are $a+l$ slots, each contributing at least $-1$ to $D_C$, whence
$(l-D_C)/3\le\lfloor(a+2l)/3\rfloor$. For $x=a+2l$ the possibilities are $2$ or integers at least $4$. On this domain $\lfloor x/3\rfloor\le x/2-1$ (check 2, 4, 5 and use $x\ge6$ for the rest). Hence the claimed bound is at most $a+l-1$, the number of edges needed to connect the component. Zero-cost final scalings preserve all individual charges. A final permutation just relabels the components.

Summing gives at least $r+(3n+1-D)/3$ additions, where the final scalar imbalance $D$ must be either $1$ or $-2$. This is at least $r+n$. In particular, taking $r=n$ gives a gap of $n$ above the larger of the two separate lower bounds. For $r=n=1$, the six-coordinate instance already needs two paid additions even though each bound alone is one. This example lies beyond the three- and four-coordinate ternary pencil censuses, where that gap was zero throughout.

## Even the sum of the two bounds can underestimate the price

A second ternary pencil has an arbitrarily large excess **above their sum**. Put $r\ge1$, $n\ge0$, and $s=2r+3n+1$. The first $2r$ slots carry $r$ slopes of each sign and scalar coefficient $-1$. The next $s$ slots have slope zero and scalar coefficient $+1$. As before $u$ is all ones, so $wu=0$ and $bu=1$. The separate lower bounds are $r$ and $n$, but the exact full price is $2r+n$.

For an upper bound, merge the opposite slope pairs. Each pair of scalar negatives becomes a scalar positive and a zero. All slopes are now separated and there are $3(r+n)+1$ scalar positives. Merging $r+n$ pairs of these positives attains scalar imbalance one.

For the lower bound write $a,l$ for a component's counts of slope slots and pure positive slots. Its original scalar imbalance is $l-a$. If $a>0$, its slope row is nonzero and stays nonzero under invertible operations on the component. At a passing endpoint the slope charges vanish, so at least one of its final image coordinates is zero, and its scalar charge there is zero. Thus $D_C\ge-(a+l-1)$ and $((l-a)-D_C)/3\le\lfloor(2l-1)/3\rfloor\le l-1$, including $l=0$. Connectivity now costs at least $a+l-1\ge a+((l-a)-D_C)/3$. For a pure component $a=0$, $l\ge1$ and $\lfloor2l/3\rfloor\le l-1$ gives the same conclusion. Summing yields at least $2r+(3n+1-D)/3\ge2r+n$.

At $r=1,n=0$ this needs two operations where separation costs one and the scalar ordering in isolation costs zero. The census in ORBITS.md shows that five coordinates is the first possible dimension of a positive gap over the larger bound for a ternary full pencil.

## The best possible budget from the two diagnostics

For **every** ternary full flat, let $S=h-Z$ be its separation distance, $L=\min(|D-1|,|D+2|)/3$ the initial scalar-imbalance distance, and $C$ the true full guard distance. Then

~~~text
max(S,L) <= C <= 2S+L.
~~~

The lower bounds follow from PROOF.md. For the upper bound, apply an optimal slope-separation word, costing $S$. A single addition changes the integer lift $D$ by at most three, so the distance to the set 1$, measured in units of three, can grow by at most one per addition. The resulting flat is separated and has scalar price at most $L+S$. Paying this and choosing a final permutation attains a full guard. This proof also covers multiple slope rows.

Both endpoints can be attained for **every** pair of prescribed nonnegative integers $S=r,\ L=n$, allowing the dimension to vary. For $r>0$ the second pencil family above attains the upper endpoint $2r+n$. To attain the lower endpoint, use $r$ opposite slope pairs and put scalar $+1$ on both slots of exactly $a=\min(r,n)$ pairs, scalar zero on the remaining pairs. Add $3n+1-2a$ pure scalar positives. The initial scalar imbalance is $3n+1$. Cancel the $r$ pairs. Each of the $a$ positive pairs changes the imbalance by $-3$, and the other pairs do not affect it. There are enough pure positives to make another $n-a$ pair merges, yielding imbalance one. The cost is $r+n-a=\max(r,n)$. When $r=0$, take $3n+1$ pure scalar positives and a spare zero-image slot supporting a nonzero slope. The flat is already separated and costs exactly $n$. This is a sharp envelope from $S,L$ across inputs and dimensions. Fixing both diagnostics can still yield different prices.
