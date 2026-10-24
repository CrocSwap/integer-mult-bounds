# A conditional controller for varying reciprocal responses

Fix m>=1 pairs. At stage s, assume exact native calls

```text
F_s(x,y)=(x,y+E_s x),
B_s(x,y)=(x-E_s^-1 y,y),
```

with the original physical input and output types and full restoration of
all arbitrary helper contents. Each E_s is an invertible operator on the
complete routed bank. Equal local coefficient matrices do not imply equal
routed E_s. The current historical transpose call does not establish this
reciprocal native premise.

Use the retained sequence F0, then B_(2i+1), F_(2i+2) for each pair i,
with its plus/minus inter-pair bridges and final descending bridges. Insert:

1. E0 on Y0 before F0; E1^-1 on X0 after F0; E0^-1 on Y0 before B1.
2. E_(s+1)^-1 E_s on active X after each B_s.
3. E_(s+1)^-1 on the next X at its first FULL cut before the plus bridge.
4. E_(t+1)^-1 E_t on that next X after the minus bridge at even stage t.
5. E_(2i+2) on every retired X after idle tails and before final bridges.

Items 3 and 4 occur only when a next pair exists. There are 4m+1 code
factors. These are required operators at specified cuts, not a native-cost
count. Before each B_s, active X has code E_s^-1 and active Y is plain.
The backward call preserves this code. Item 2 changes it to the next
forward inverse code. Item 3 makes the two X bridge codes equal. The
forward response cancels that code on Y, and item 4 prepares the next
backward stage. Item 5 removes all retired X codes before the final
bridges. The complete content endpoint is (-y_i,x_i) for every pair.

With W=diag(Q,I), V=diag(I,Q^-1), J0=[[0,-I],[I,0]], and retained terminal
A=[[0,Q^2],[-I,0]], direct multiplication gives A V J0=W. Thus the old
physical terminal is valid under the stated native phase contracts.
No E_s is commuted through Q. If all routed E_s equal one E, the transition
products are identities and the displayed construction has 2m+2 factors.
This is not an optimality claim.

The [unchanged full proof](frozen/lanes/encoded-controller/reciprocal-response-20261018/RECIPROCAL-CONTROLLER.md)
gives the typed four-pair table and the ordered three-call equations.
The [independent review](REVIEW.md) checks the all-m argument. The replay
checks the original free-word verifier for one through eight pairs and its
controls. Reciprocal native words, future and past code access, paid views,
owner schedules, precision, and complete supplier cost remain premises or
open obligations. No complete kappa improvement follows.
