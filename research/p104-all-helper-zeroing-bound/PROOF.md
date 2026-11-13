# All cold-helper subsets have nonpositive signed-moment gain

This is the coordinate-zeroing theorem. `SUBSPACE-PROOF.md` separately extends
the obstruction to arbitrary scalar input subspaces within matching entrance/
exit helper groups for `0 <= kappa <= 1/100`.

Scope: exact #7481 WORD.json.gz, SHA256
`acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
Set any subset H of the original 1,101 public helper inputs to zero. Every
main input and every helper outside H remains arbitrary. Retain every other
source operation, and grant removal of any original MOVE whose exact latent
scalar row becomes zero, with zero-frame/storage/ordinary work free.

For every 0<=kappa<=1/2 this gives no positive change in the complete signed
moment T_(1-kappa)-P_(1-kappa). No modified source, supplier or kappa is claimed.

The originating rational census executes all 76,475 source operations on sparse exact rational rows.
The actual 400 main coordinates are live, live+112, hosted.X2 and hosted.Y2;
the other 1,101 public coordinates are helpers. Each final helper row is its
own unit vector and no helper coordinate leaks to a main output. The replay checks literal chart bookkeeping, scalar cochart contacts and
COPY into zero. It does not re-admit every physical source contract.

There are 6,279 MOVEs. Exactly 468 latent rows have only helper support; none
is unconditionally zero. The other 5,811 have a nonzero main coefficient and
cannot vanish when main inputs remain arbitrary. The exact rational replay checks all 468
helper-supported rows. A MOVE becomes zero iff all helpers in that support are cold.

The preliminary single-helper scan has 957 helpers removing no MOVE, 72
removing one MOVE of smaller rank than the lost target, and 72 removing one
MOVE of exactly that rank. Thus no single helper improves the signed moment.

For arbitrary subsets, discovery uses 1,101 negative helper-target nodes and
468 positive MOVE nodes with 10,517 MOVE-to-support-helper implications. At
.003647081039689, .0038 and .004 the float maximum closure returns the empty
set. The following exact certificate does not depend on that float result.

`ASSIGNMENT.json` contains all 468 records, with keys event, rank, assigned_helper
and target_rank. Every assigned helper has a nonzero coefficient in its MOVE
row. Therefore a removable MOVE must have its assigned helper in H.

Each assigned helper funds one MOVE of rank r<=its target rank R, except
helper 666. It funds events 43186 and 43199, both rank 1, with target rank 4.
No MOVE is assigned twice; no other helper is assigned more than once.

Put f(r)=r^(1-kappa) and t=1-kappa>=1/2. Singleton assignments obey f(r)<=f(R).
The only double assignment obeys f(1)+f(1)=2<=4^t=f(4). If E_h is the group
assigned to helper h, then for every cold subset H,

```
sum(e removable) f(rank_e)
 <= sum(h in H) sum(e in E_h) f(rank_e)
 <= sum(h in H) f(target_rank_h).
```

The last expression is exactly the productive-target credit lost by zeroing H.
The complete native change is therefore nonpositive. The actual signed caller
has 17 native calls (caller SHA256
`255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`), so
the complete caller change is 17 times that nonpositive value. The same proof
also allows different cold subsets in the independent native invocations.

The old complete native paid histogram is
{1:4001,2:854,3:827,4:222,5:344,6:16,7:10,8:5}. Every root-caller operation
and main target is retained. No nonzero input/output is erased for credit.

This is a signed-moment theorem. Neutral specializations may change finite
compiler constants; no impossibility claim about those constants is made.
Changed source arithmetic, paid schedules, main inputs, correlated helper
encodings and target boundaries are outside this scope. Physical zero-field
frame updates and owned allocation would still need proof for an actual word;
they are granted free here because the favorable moment already cannot improve.
The five inherited assumptions remain.

## Independent verification and reproduction

`rational_verify.py` replays the complete source with exact rational rows and checks the assignment directly. `modular_verify.py` separately replays over the prime field of order 65,521: a nonzero main coefficient blocks every unfunded MOVE, and a nonzero assigned-helper coefficient forces its helper to be zero for every funded MOVE. Every source denominator is invertible modulo this prime. A nonzero residue therefore proves nonzero over the rationals; no modular zero is promoted to an exact zero.

Run `python3.12 -I -W error -B research/p104-all-helper-zeroing-bound/verify.py`, or the same command with `-O`. The standalone package contains all inputs and uses only the standard library. Both source interpreters, actual 17-call multiplicity, exact rank funding, expected receipts and failure controls are checked. Float discovery and its implementation are not dependencies of the proof or replay.
