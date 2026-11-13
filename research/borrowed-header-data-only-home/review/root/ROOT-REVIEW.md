# Root review of the borrowed-header DATA-only adapter

Base: e54523517d0f03e58352e647c403a5af3e525a57.
Author freeze:0f3f4bae39a8f630c56799912c41f2babecf0493531e043d6a6e0cb21ef717a7.

## Decision and reviewed boundary

The adapter's supplied-entry composition proof and a fresh rank-two physical
execution pass this review. The fixed-rank positive core remains unchanged.
One borrowed immutable Gamma6 header is distinct from DATA-only HOME, whose
extent is V rather than E+V. This fixes the representation-level dependence on
header length. It supplies no root-to-native header producer, actual address
view, packing, cutoff derivation or selected caller admission.

Single-header service uses34 tapes. HEADER enters at B-relative1; native
DATA and private ports enter at2, leaving a blank guard at1 and permanent^0.
Mapping native port0 to HEADER3 and t>=1 to3+t is injective. The borrowed
header is not a native private bank and is never erased. The old B1 reservation
prefix uses tape3 as scratch but is unreachable from the declared already-
reserved execution entry. This entry restriction is necessary; the checker
independently traverses every reachable rule and rejects a HEADER write.
No claim is made that the original reservation prelude can borrow this header.

The wrapper clones the V-bit operand into native DATA, restores the required
origins, runs the unchanged core, then installs exactly one returned DATA bit
per existing operand bit. Its sole successful end branch requires native
blank and operand delimiter simultaneously. Thus no incomplete returned
extent can reach successful B1 scatter. The original operand delimiter serves
as the length guide; no E-sized header is embedded into HOME. After local
cleanup, B1 returns the complete body to the same supplied owner.

The prelude/postlude are bounded by6V+160, hence256(V+1); decoded-parameter,
cutoff and arithmetic work remain inside the unchanged2^24(fV+E+1) core bill.
Primitive history is bounded by entry+2112(V+E+1), retaining prior maxima.
B1 bank gathering/return, typed reservation, setup/origins and complete opaque
storage remain separate. E is not silently assumed O(V). At fixed f the
primitive is O(E+V), and no accelerated nonleaf tariff follows.

## Separate physical and arithmetic check

The root sparse CPU and closed two-axis Gaussian Hamming kernel are separate
from the author's interpreter, input fixture and oracle. It checks every core
instruction's injection and all Graph states reachable from the actual entry.
The fresh packet has rho2, f=r=P=1, S=2, width7 and a130-bit positive cutoff.
V=14,336, E=270, and each component is divisible by4 with magnitude at most8.
Two C axes therefore remain integral and bounded by32, inside signed7bits.
An immediate opaque suffix starts at the cell after the sixth Gamma code.

The full34-tape execution takes13,698,674 transitions. It writes exactly
14,336 HOME bits after primitive return, zero HOME bits earlier, and zero
borrowed HEADER bits. Header read positions are exactly1..270, so the immediate
opaque suffix is not read. All34 heads/private bodies/guards/exteriors return,
the full borrowed header/suffix remain identical, and the parked HOME is
unchanged. The independently derived rank-two answer differs from the input
and from omitting the second C axis. This last check discriminates the fixture;
the author's separate suite provides actual emitted faulty-return mutants.

Recorded head-span history grows from98,987 to278,941, retaining a prior
larger private extent. The checker separately includes a conservative B1 term
in its full time/history comparison. These recorded spans do not claim to
measure every supplied opaque exterior's past allocation. RESULT.json pins
the shapes, exact output and unchanged core instruction hash.

Run with the explicit implementation directory:

```sh
python3 -I -B -W error review/root/check_borrowed_root.py implementation
```

The author's two-header physical reuse (E10 and268 on the same V6144 body)
provides complementary evidence. Both headers are supplied initially; this
is not host-simulated production. Failure cleanup, interruption/retry and a
universal malformed-input validator remain unclaimed. Finite executions
corroborate the written all-size wrapper proof, not a full large-f replay.

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance.
This is disclosed separate implementation/arithmetic checking, not blind or
human review or formal-kernel verification. All five selected assumptions,
the actual source producer/view/cutoff obligations and kappa remain unchanged.
