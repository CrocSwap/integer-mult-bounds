Independent Unit13 semantic-control design. This file is design only, prepared before parent P1 release. No checker, fixture program or original source was executed. No implementation is supplied here.

Scope: exact G/C/K/U producer-event relations. G is the named get_random_bytes request into the 16-byte kernel array. C requests the same object and length at the STACK_ALLOC-computed destination; zero denotes the completed primitive-transfer event under its stated interface contract, and nonzero follows the immediate -EFAULT exit. K writes AT_RANDOM=25 with the native conversion of the same computed destination into saved_auxv. U is the later saved_auxv transfer only when control reaches it. There is no instantaneous, atomic, persistent or userspace-handoff memory-equality claim, fabricated seed, runtime admission or ownership flag.

Independent source oracle: retained fs/binfmt_elf.c declares unsigned char k_rand_bytes[16], calls get_random_bytes(k_rand_bytes,sizeof(k_rand_bytes)), computes u_rand_bytes using STACK_ALLOC(p,sizeof(k_rand_bytes)), tests copy_to_user(u_rand_bytes,k_rand_bytes,sizeof(k_rand_bytes)) and immediately returns -EFAULT when nonzero. NEW_AUX_ENT stores tag then value in mm->saved_auxv; AT_RANDOM's value is (elf_addr_t)(unsigned long)u_rand_bytes. Later p is reused for argument/environment strings, while the saved random pointer remains u_rand_bytes. The final copy_to_user uses source mm->saved_auxv and length ei_index*sizeof(elf_addr_t), with its own nonzero -EFAULT exit. Native ELF definitions and applicable configuration, not a guessed pointer-width axiom, must qualify the conversion before P1 release. Source get_random_bytes is a named void interface dispatch; entropy strength or independence is outside this claim.

API requirements sent to the author before freeze:

- Provide a pure semantic-relation entry point separate from outer file/source-hash authentication. Tests must be able to submit coherent, newly serialized toy DATA and observe a semantic rejection, rather than only a bad digest.
- Preserve distinct G request/provider/object, C object/destination/length/return, K tag/native pointer, and optional U source/length/return events. The order and local failure edges must be checked.
- Keep the source-qualified numeric relation separate from actual instance, ownership, valid userspace stack range and no-writer assumptions. In particular unsigned subtraction modulo the native width is not evidence of a nonwrapping owned interval.
- The source-qualified semantic profile is fixed from exact retained source. Caller data must not declare itself the approved effective configuration or mint authority.
- Return or expose specific rejection categories so controls distinguish changed provider, request length, destination/tag relation, source object and failure ordering. Exact exception spelling may be coordinated; expected logical decisions come from the source above.
- The canonical witness has bounded exact integer arithmetic and no seed bytes, actual-exec binding, handoff-memory equality or success claim after a failed local transfer. Arbitrary later failure must not erase an earlier completed transfer event.

The five required independent literal counterexamples are:

| Case | Coherent toy change | Source relation contradicted |
|---|---|---|
| NEG_REQUEST_LENGTH | Change the RNG request from 16 to 15 while retaining a 16-byte declared array/copy. Recompute any toy serialization digest. | G request must be sizeof(k_rand_bytes)=16. |
| NEG_PROVIDER | Substitute a distinct provider identity while keeping the 16-byte buffer/copy/tag relations internally consistent. | The genuine named producer is get_random_bytes for this call. |
| NEG_ARGV_POINTER | Use an independently valid-looking argv-string pointer as the AT_RANDOM value, with C still targeting the computed random span. | K binds u_rand_bytes, not a later/reused p or arbitrary pointer in a plausible user range. |
| NEG_COPY_SOURCE | Copy from a different 16-byte kernel object while the RNG request still targets the original object. | C source is exactly the G destination object. |
| NEG_FAILURE_SUCCESS | Record nonzero C copy result but append K/U or mark the local transfer/table as successful. | The nonzero branch immediately returns -EFAULT before K/U. |

Positive and boundary controls are independently required so rejection is not achieved by refusing every trace:

- A coherent G16/C16-zero/K25 trace with optional U not yet reached is a valid producer-event prefix; it grants no completed table or handoff claim.
- A G/C-nonzero/-EFAULT prefix is a valid failure path with no K/U. A partial failure may have effects; no unchanged-destination assertion is allowed.
- A G/C-zero/K trace followed by a later pre-U -EINTR/-EFAULT is valid. Earlier completed C and K events remain recorded; later failure grants no U/table/handoff success.
- A G/C-zero/K/U-nonzero/-EFAULT trace is a valid partial later failure. It does not erase the earlier completed C event or assert completed U/table/handoff.
- A G/C-zero/K/U-zero local-return-zero flow is a valid local producer/table-transfer sequence only. A separately fabricated handoff-equality or persistent-memory assertion must still be rejected or outside the accepted schema.
- Native casts must preserve a source-qualified pointer value above 2^32 on the selected native 64-bit path; a truncated 32-bit K value must fail. This is conditional on P1's exact native aliases/context and has no actual address-space admission meaning.
- For illustrative down-stack arithmetic, cursor4096 minus16 gives4080. For cursor8, unsigned64 subtraction gives18446744073709551608; that modular relation does not establish a nonwrapping interval or an owned valid destination. A checker scoped to valid nonwrapping cases may explicitly refuse the latter; it may not silently call it an owned span.
- Reject noninteger/bool substitution or out-of-domain native values where the canonical arithmetic schema requires exact integers. Do not use disabled Python assertions for safety checks.

These numbers and object identities are toy model literals, not observed kernel addresses, seeds, auxv lengths or exec traces. U's source-derived ei_index*sizeof(elf_addr_t) relation may be challenged symbolically or with a clearly synthetic local arithmetic model; a fabricated whole auxv catalogue is not an oracle. Exact U numeric length and argv/environment state are not guessed.

After explicit parent P1 release only: implement the owned literal fixtures/tests against the agreed new API, run a serialized bounded normal and -O pair, preserve every failure, and report semantic decisions plus exact hashes. No original/kernel/native/target/compiler/Popen/namespace/policy/process inspection is authorized. Full C05/V03 false, all Units01–12 closed, original43.5%/denominators/caps unchanged, costs OPEN_NOT_ZERO.
