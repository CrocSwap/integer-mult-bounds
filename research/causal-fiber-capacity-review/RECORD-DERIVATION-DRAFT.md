# Abstract simultaneous bit-fiber and recovery-capacity derivation

## Verdict, role and source exposure

**Verdict: the supplied causal certificate obligations imply the simultaneous zero-endpoint fiber and the stated symbolic recovery-capacity bound.** This is a target-known written derivation for external review of PR6594, not a new fiber theorem, selected-word membership result, recovery floor or physical minimum. In particular, any specialization to the source's sixty selected fields remains conditional on its unreplayed certificate membership.

The coordinator supplied the model and proof obligations. No current6594 proof, `verify`/`causal_certificate` code, word file, current peer draft or coordinator derivation was opened before sealing. My prior context includes the6546 retained-record review and summary references to6547/6594 recovery work, not a fresh blind history. Historical familiarity beyond that is not claimed absent. The source owns its numerical values and claims.

No source/new scientific program, import, word fetch/scan, NumPy operation, test, enumeration, numerical experiment or proof kernel was executed. Only this written note and metadata hash/time seal were authored. No error/bill/native operator result is accepted merely from the fiber argument.

## 1. Exact deterministic word and certificate hypotheses

Fix a positive width N and grid spacing h>0. Store each complex coordinate as two integer cell counts, so a field is a Gaussian-integer array of length N. The instruction word is fixed, finite and has a valid value/shape/ownership grammar. Its live-slot layout is determined by the word, not by the payload. There are initially K distinct selected **public** fields whose real and imaginary entries may vary independently; every other initial field is zero. The selected fields are unrestricted at this input interface. Whether a particular outer/physical caller can reach all these entries is not assumed.

For a scalar coefficient p/D, p is a nonzero signed integer and D>0. Set its fixed seed before evaluating the input by

    u=0       when p>0,
    u=D-1     when p<0.

The coordinate quantizer is exactly

    Q_(p,D)(x)=floor((p*x+u)/D).                         (1)

Thus for integer coefficients D=1 the seed is zero in either sign case. Native seeds, if any, are also fixed valid retained values independent of the chosen input bits. There is no claim that this deterministic schedule is a fresh uniform stochastic experiment; the floor is a pointwise property on one allowed schedule.

The causal certificate must establish the following for the fixed word, without relying on a basis-only numerical test:

1. Each selected field has a static active tag until its first killing instruction. A tag does not disappear merely because a particular chosen bit assignment gives zero values.
2. Before that tag is killed, an ADD reading it as source has a strict fractional coefficient `0<|p|<D`, and otherwise has the ordinary additive destination update. ADD may target an active field only by an increment established to be zero.
3. No other instruction reads or changes an active field before its kill: COPY source/destination, INIT/CLEAR, native MOVE or another scalar change must be excluded where relevant. The permitted kill is SCALE with p=+/-1,D=2 on that field. All selected tags are eventually killed.
4. A MOVE reads only its declared one field, which is inactive/zero when used, and maps zero exactly to zero under its fixed seeds. No hidden read of another active field is granted by the opcode name.
5. INIT creates zero, COPY moves only currently inactive zero data, CLEAR removes only inactive data, and other permitted scalar/structural operations preserve the zero value on inactive fields. Every access has the valid live field/shape required by the word.

These are proof hypotheses, not observations that the source word has passed them. They imply the result for every positive N where the word's declared operations have those shapes. If an actual implementation permits only tensor widths such as512^f, the source-bound application must use that admissible width family rather than advertise a different array API.

## 2. Two exact quantizer facts

First, (1) always maps zero to zero. For positive p its numerator is zero. For negative p it is D-1, whose quotient floor by positive D is zero.

Second, when0<|p|<D it maps both binary inputs to zero. At x=0 this is the first fact. At x=1:

- If p>0, the numerator p lies strictly between0 and D.
- If p<0, the numerator D-1+p lies between0 and D-2, since1<=-p<=D-1.

In both cases its floor quotient is zero. The negative seed is essential to this particular annihilation statement. It is not justified by treating floor division as odd or by assuming a rounded negative equals the negative of a rounded positive.

At the signed-half killing SCALE, p=+/-1,D=2 also satisfies these inequalities, so it kills either bit value exactly. No limiting or small-error argument is used.

## 3. One simultaneous invariant for the entire mixed family

Assign independently a bit to each real and imaginary coordinate of each selected field. Write b_(r,j,c) in{0,1}, with selected label r, coordinate j and component c. There are2KN such choices. Initial stored entries are those bits; physical values are h times them. No probability distribution is needed for the family count.

We prove by chronological induction on the fixed word that, for **every simultaneous assignment** of these bits:

- every currently active tagged field still equals its own original binary array, component by component;
- every currently inactive live field is zero;
- tags/lifetimes follow the same certificate event sequence for every assignment.

Initially this is the definition of the family. For ADD, its source is either an inactive zero field or an active original bit field. A zero source gives zero increment by Section2. An active source gives zero increment in every component by the strict-fractional certificate obligation and Section2. Therefore the destination is unchanged, whether it holds another selected binary array or zero. In particular simultaneous bits in two different selected fields do not create a sum2: neither increment is ever copied into the destination.

For a killing SCALE, its field is still the original binary array and both possible component values map to zero. Retire that static tag. All other tags retain their values, and the newly inactive field is now zero.

A permitted MOVE acts on its one declared zero field and returns zero. The no-hidden-read premise is what permits this local conclusion when other fields contain active bits. INIT creates zero, inactive COPY copies zero, CLEAR removes inactive zero, and other permitted zero-preserving events keep the invariant. Valid structural grammar preserves the intended label/shape interpretation through lifetimes.

These cases cover every word event under the certificate. At the end, all K tags have been killed. Every live field is therefore zero, and its live-slot layout is the same fixed layout for every bit assignment. Hence the entire family has **one identical complete forward visible field endpoint**, not merely equal final scores or equal ideal decoded outputs.

This is not a linear extension of basis behavior. The rounded word can be nonlinear on arbitrary inputs; the proof directly treats both possible values at every component at every step and shows the simultaneous stage invariant. Consequently arbitrary mixtures of the independent bits are covered for every compatible N.

## 4. Size and injectivity of the entrance family

Distinct assignments differ at some real or imaginary coordinate of one selected public field. Those fields are distinct and freely specified, so the initial states are different. There are exactly

    M = 2^(2*K*N)                                         (2)

such initial states. All other initial fields and the seed schedule are fixed. Their visible forward endpoint is identical by Section3. Thus the unrecorded fixed-seed forward map has a fiber of size at least M at that endpoint.

This is an input-interface fiber, not a claim that an arbitrary outer caller reaches all M states. It also does not establish the largest possible fiber. A successful basis check or discovery of K labels would not itself prove this size without the simultaneous invariant and distinct unrestricted-entry premise.

## 5. The killing half residues explicitly encode the bits

For the source-style seed-shifted division residue at a kill, write

    r=(p*b+u) mod2.

For positive half p=1,u=0 this is r=b. For negative half p=-1,u=1 it is r=1-b, for b in{0,1}. In either case the map from the original component bit to the retained residue bit is a bijection known from the fixed instruction sign.

Because each tag is unchanged until its first kill, the residues at the K killing events recover exactly its original2N bits, not some linear combination or later modified values. The event/sign order is fixed by the certificate; a zero-valued input still carries its active tag to that same kill. Collectively these half-residue positions give a direct encoding of all2KN bits. Later mutations or deletion of those positions would remove that particular encoding unless another channel retained its information.

This does not say a physically optimal recovery mechanism must use those same residue slots. It proves a source-record manifestation of the information and the lower-bound need for some complete recovery channel. Other nonselected instructions may retain additional data. No new count of source residues or fields is established here.

## 6. Recovery capacity must distinguish all states in the fiber

Suppose a decoder recovers the full initial input from the common visible output, the unchanged fixed seed schedule, and some retained recovery state R. For two different inputs in (2), the recovery states must be different; otherwise the decoder receives identical arguments and cannot return two different inputs. Thus the recovery channel has at least M distinguishable states and information capacity at least

    log2(M)=2*K*N bits.                                  (3)

If that complete channel is implemented by a B-bit register/configuration space of at most2^B states, then B>=2KN. The statement counts *complete distinguishable configurations*, not just a selected payload field. Record lengths, tags, addresses, ordering, variable layouts, integer magnitudes, counters and any overwritten seed values that depend on the input must be included. An uncharged length/tag/address register with M possible values is itself a channel with this capacity, not a way to defeat(3).

The fixed, unchanged seed schedule contains no input-dependent distinctions in this restricted family. If an implementation overwrites seed storage with data, that changed seed storage belongs to the recovery channel. If it relies on different lengths or metadata while claiming a shorter payload, those distinctions likewise count. No fixed physical write/access cost or an exact number of heap objects follows merely from this information-capacity inequality.

The endpoint-plus-record injection in a retained inverse may satisfy(3); it does not show records are erasable from output alone. Conversely a lost-record rounded map is not made injective by saying the stochastic procedure was reversible “with the same seed” when its required recovery information has been omitted.

## 7. A preexisting dirty bank does not provide free additional capacity

Let a dirty bank have Q possible old states, with Q finite, and let every pair of a fiber input and an old dirty state be allowed. This is an unrestricted Cartesian-product domain, not a claim about a probability distribution. Require exact recovery of both the chosen input and the old bank state. Suppose the final visible field endpoint is common and any reused bank still has at most Q final states, while an additional recovery channel has at most H states. Injectivity requires

    M*Q <= Q*H,

so cancellation of the positive finite Q gives H>=M. Equivalently it needs at least2KN bits of additional distinguishability beyond the unrestricted recoverable old bank. The conclusion also holds, more directly, if the dirty bank must be returned unchanged.

This cancellation needs its actual hypotheses. If the old bank is correlated with the chosen input so not all M*Q pairs are allowed, it can already contain information about that input; the unrestricted-product argument cannot be asserted. If its final capacity increases, that increase is new recovery capacity and must be charged. Infinite unpriced state spaces cannot be canceled as finite information budgets. If the common-output premise changes because bank-dependent data is exposed elsewhere, that output channel must also be counted.

Thus arbitrary preexisting dirt is not a free clean record in an exact-restoration contract. This is a finite-state information statement, not a physical workspace minimum for every architecture.

## 8. Source specialization and quantifier limits

If the unreplayed source membership certificate actually establishes K=60 distinct unrestricted public fields with these obligations, then (3) specializes to120N bits on this one fixed sign-dependent schedule. That number and certificate belong to PR6594; this draft does not rediscover, scan or independently confirm the sixty memberships.

The distinct6547 every-seed86N result has a different seed quantifier and source argument. A larger floor for one selected schedule must not be represented as a stronger every-seed theorem, or as a new result from this review. Neither bound proves a global largest fiber, unavoidable entropy for all samplers, entrance reachability of an actual selected physical caller, record-erasure impossibility for every changed interface or a physical supplier minimum.

Fresh conditional seeds in a forward error analysis and fixed retained seeds in this deterministic fiber are different claims. Choosing one valid fixed schedule is not a proof of stochastic unbiasedness; it is also not a defect in an algorithm whose algebra is defined for every permitted seed value. This review accepts no forward error, precision, concentration, cost or native-source certificate from the fiber alone.

## 9. Written weakening controls — all UNEXECUTED

1. **Wrong negative seed.** For negative half with u=0, input bit1 gives floor(-1/2)=-1, not zero. The sign-specific schedule matters to this particular simultaneous family.
2. **A larger alphabet.** Positive half maps input2 to1, not zero. The0/1 cube proof cannot be applied to arbitrary small integers merely because the input interface allows them.
3. **An exact active-source ADD.** Coefficient1 copies an active source bit into the destination. The claimed strict-fractional zero increment then fails and a visible output may retain information. Distinct operands alone do not make it vanish.
4. **Hidden reads or forbidden structural copies.** A MOVE allegedly acting on a zero target could secretly read an active source; COPY could propagate active bits to another live field. Local zero preservation is insufficient without declared read-set and active-access restrictions.
5. **A tag killed by value rather than by event.** Dropping an active tag whenever its current array happens to be zero makes the certificate depend on the bit assignment and does not justify one common trace or kill-residue encoding. The tag is a structural source label until its permitted kill.
6. **Basis-only evidence.** A nonlinear map on two bits can send00,10,01 to zero and11 to a nonzero output. Individual basis collisions do not prove a simultaneous size-four zero fiber. The stage induction, not linearity, closes this gap.
7. **A retained active field or changed pre-kill value.** If one selected field is never killed, or is scaled/overwritten outside the allowed rules before killing, its bits need not be annihilated. Eventual killing and unchanged active arrays are separate certificate obligations.
8. **Correlated dirty bank.** A bank initially equal to the chosen input can help recover it without an independent M-fold enlargement. That violates the unrestricted-product old-bank premise, rather than refuting finite-Q cancellation. Exact recovery of old dirt must also be required.
9. **Free metadata/seed overwrite or a seed-quantifier jump.** Encoding the input in a record length, selector or overwritten seed still retains information. Ignoring those channels undercounts capacity. Separately, this fixed-schedule family cannot be advertised as an every-seed floor or a new physical bit tariff.

These are deductions about weakened hypotheses, not executed controls, source counterexamples, source-word observations or new numerical values.

## Credit and post-seal obligations

PR6594 retains the causal simultaneous-family result and its fixed-schedule recovery floor;6547 retains its distinct every-seed floor. Ali Romman6546 and the retained stochastic/native/rounding/compiler lineage own the caller and record/error context. Finite-set injectivity, Cartesian-product counting and exact floor/residue arithmetic are elementary prior methods, not newly invented here. Source notices and AI-assistance disclosures must remain.

Post-seal source review must bind the actual causal traversal, selected label list, exact scalar convention, instruction read/write sets, zero-native condition, grammar/lifetimes, input freedom and representation to these obligations. Until then this is an abstract known-target derivation, not actual6594 code acceptance. No word fetch/scan, numerical membership result, native execution, physical capacity implementation, human/kernel acceptance, selected-assumption discharge, kappa or frontier/adoption change occurred.
