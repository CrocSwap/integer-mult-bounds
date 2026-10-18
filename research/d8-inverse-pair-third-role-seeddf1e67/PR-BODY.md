## Result

This package settles one exact three-role formal group-algebra question. For
`D8=<r,s | r^4=s^2=1, srs=r^-1>`, `t=r^-1s`, and paid rank-one factors
`F_g(N)=I+([g]+1)N` with `g in {s,t}`, the endpoint
`diag([r],[r^-1],1)` has minimum paid length four on three arbitrary dirty
roles, even with interspersed free `GL3(F2)` scalar maps. It does not give a
supplier or `kappa` improvement.

## Evidence

- The regular-representation displacement rank is 12 for the endpoint and 4
  per paid factor, so lengths zero through two are impossible.
- The complete exact length-three census checks all 175,616 ordered words over
  the 56 generators and finds zero hits.
- The explicit four-call word reaches the endpoint. A separate tuple-valued
  verifier replays the whole census, positive control, omitted-call control,
  and rank control.

## Reproduction

```sh
python3 -I -B research/d8-inverse-pair-third-role-seeddf1e67/search.py
python3 -I -B research/d8-inverse-pair-third-role-seeddf1e67/verify.py
python3 scripts/research_package.py --package research/d8-inverse-pair-third-role-seeddf1e67 --check-only
```

The scientific base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Predecessors are the two-role inverse-pair result (#1881, commit
`5a51deaaab2746d42eddb454bbb968bda3af02cc`) and the distinct three-role
central-pair result (#1742). The model excludes native third-role hosting,
recursive charges and supplier admission; no selected frontier changes.

Substantial OpenAI Codex assistance in derivation, implementation, verification,
and packaging. No independent human review is claimed.
