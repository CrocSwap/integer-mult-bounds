# Sharper production repair and historical composition

This separate follow-up preserves the census and byte package already landed
at `5b9a3d018f74c835ef87db86ce824d8026257b6b`. Its `PROOF.md` is the earlier
original byte argument, retained under its reviewed SHA-256
`d21a68af1cd9720b691fdd4866452c909955557e211a75f93ead381db88f64cc`.
The landed `../bytes/PROOF.md` and its independent review remain untouched.
The new result is [review/SHARP-REPAIR.md](review/SHARP-REPAIR.md), with the
separate [review](review/CROSS-REVIEW.md) and checker preserved exactly from
the accepted follow-up. Retained source copies authenticate the same #8042
runtime, `dfd25d553a843a946ca0b94130a5ff8943e98fdd`.

For one injectively labelled repair, with `M` groups of `a` payload bytes
and `t` tag bytes, the two fields plus fixed scratch roles use at most
`4V+2Mt`, where `V=Ma`. The zero-bit case has no radix passes and is handled
separately. The literal production correction key is a permutation before
final validation; generic callbacks obtain the needed label property only
within the stated successful-call domain.

The production header gives `t<=a/2`. The individual role caps therefore
sum to **six volumes after historical maxima across arbitrary differing
calls** of volume at most `V*`. Under only `t<=a`, six volumes is a per-call
consequence; an actual all-bad/all-good pair reaches seven volumes after
taking each role's maximum separately. A second pair reaches six under the
half-tag condition. The generic 17-bit fixture totals seven volumes and
disproves tag dominance; the symbolic, unexecuted 33-bit family totals nine
and disproves the unrestricted generic eight-volume claim.

Replay with a restored #8042 runtime:

```sh
python3 -IB repair-bounds/review/check_review.py --runtime /path/to/runtime \
  --output /tmp/sharp-repair.json
```

The parent `verify_followups.py` provides a fresh offline restoration. Its
59 actual repairs, 5,216 algebra checks and 18 address-only callback
enumerations corroborate the separate universal argument. Payload methods
are explicitly stubbed in the callback checks. A malformed generic key
exceeds the injective-label bucket cap before the real source rejects it.

The historical documents mention a then-open mass enclosure; the later
`../mass-enclosure/OWNER-COROLLARY.md` discharges that local numerical
premise without rewriting them. Other source contracts, global ownership,
movement and the five canonical assumptions remain separate. Credit remains
with Ali Romman and the original authors; prepared for Jerry Chen /
@CubeJerry with substantial OpenAI assistance and separate model review.
