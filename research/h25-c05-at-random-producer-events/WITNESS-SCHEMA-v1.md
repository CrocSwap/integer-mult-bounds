# Unit13 integer witness and model interface

The2617-byte WITNESS-v1.json is static argument DATA, not an actual execution journal. Fixed ASCII keys have only exact bounded integer/list/map values; bool,null,float and string values are forbidden. Raw<=1MiB, nodes<=8192, depth<=24, list/map<=256 and integers within signed126-bit magnitude satisfy the declared conservative envelope. No seed, actual address, admission bit or self-hash is present. Original ordinary source occurrences remain separate rows; the witness does not replace them.

`version=1`. `sources` lists24 `[source_id,byte_count,[eight_u32_SHA256_words]]` rows. IDs are the1-based lexicographic order of the role keys in SOURCE-PINS-v1.json and the module's literal SOURCE_PINS map. The eight words are consecutive big-endian32-bit chunks of the SHA256 digest, not random seed bytes. All production literal pins are checked separately before semantic analysis. No witness field supplies expected source hashes to that gate.

`abi=[8,64,64,64,64]` means byte bits,pointer bits,unsigned-long bits,__u64 bits,elf_addr_t bits. Flat-address roundtrip semantics are an explicit native Linux/GNU interface premise beyond those widths. `G=[1,1,16,16]` means provider1=get_random_bytes, kernel-object1=k_rand_bytes, array byte count16, requested byte count16. Object IDs denote source-bound symbolic MODEL roles, never actual addresses:1 is the local kernel array;2 is the computed seed destination;3 is mm->saved_auxv;4 is the current user auxv table destination sp. Cursor10 is the live unsigned p immediately before seed allocation.

`A=[1,10,2,16,64]` means operation1=unsigned subtraction modulo2^64, cursor10, resulting destination role2, decrement16,width64. This is not an owned-span/range certificate. `computed_destination(q)` returns only that pure integer expression; q<16 wraps and q above2^32 retains its high bits.

`C=[2,1,2,16,1,1]` means copy-provider2=copy_to_user, source role1,destination role2,length16,guard1=nonzero residual,source-failure branch1. `K=[25,2,64,64,1,2]` means AT_RANDOM tag25,destination role2,unsigned-long and elf-word cast widths64,then ordered store phases1=id and2=value. `store_order=[1,2]` asserts source order, not atomicity. `U=[2,3,4,1,8,1,2]` means copy-provider2,source role3,destination role4,length-expression1=ei_index*sizeof(elf_addr_t),native word size8 bytes,nonzero guard1,and failure branch2. It supplies no guessed whole-table byte count.

`branch_rules` rows `[branch_id,reached_mask,completed_mask]` use event bits G=1,C=2,K-complete-pair=4,U=8. Branch IDs1/2 are the immediate C/U return-EFAULT sites;3/4/5 are later pre-U EINTR/EFAULT/EINVAL source sites;6 is local return0 after U zero. IDs are symbolic source-branch labels, not numerical errno definitions. The rows are1:[3,1],2:[15,7],3:[7,7],4:[7,7],5:[7,7],6:[15,15]. Partial copies may already have side effects; masks do not enumerate memory writes or prove snapshots.

`requirements=[1,2,3,4,5,6,7,8]` names conditions/obligations, NEVER their satisfaction:

1. Applicable original genuine OS/loader and named RNG/copy interface meanings.
2. Selected native representation and flat pointer/integer conversion semantics.
3. Well-defined live local C objects/cursors where source events are reached.
4. Separate genuine actual exec/provider/subject/source-context binding.
5. Only for an owned nonwrapping-span corollary: q>=16, mathematical range equality,actual writable owned initial-stack mapping and lifecycle.
6. Only for any stronger memory/handoff corollary: separately justified preservation/exclusivity at the chosen boundary.
7. Original ordinary F inventory/currentness,C07,fixed ELF expectations and source/stage/command/runtime approvals remain separate.
8. Complete physical/approval/final-tail costs,funding and fit remain OPEN_NOT_ZERO.

The event theorem uses conditional interface premises1–3. Requirement4 instantiates it in a future actual execution. Requirements5–6 are not assumed to prove this event theorem; they mark additional obligations for deliberately unclaimed stronger statements. Requirements7–8 preserve the original wider objective and do not grant it credit.

## Pure model-prefix API

`check_event_prefix(profile,events)` accepts only labelled synthetic MODEL projections. G row `[1,1,1,16]` denotes normal RNG return. C row `[2,2,1,2,16,residual]` denotes a normal copy return. K rows `[3,25,2,64,64,1]` and `[3,25,2,64,64,2]` denote the ordered individual tag/value stores. U row `[4,2,3,4,1,8,residual]` denotes its separate normal copy return. A prefix can end after tag phase1. U requires phase2. Failure row `[5,branch_id]` must follow the matching source guard; local return0 row `[6]` requires U zero. Nonzero C cannot reach K/U. U failure preserves earlier completed G/C/K.

An interrupted/in-flight provider or copy can have NO normal-return row and still have side effects. Ending a projection grants no future event and proves no absence of partial writes. `reached_mask`, `completed_mask`, `local_branch` and requirement IDs returned by this API describe only this supplied model, not an observed kernel trace or an admission. Later writer models may preserve every producer relation while invalidating any proposed memory equality.

`analyze_sources` is bounded byte/text semantic projection intentionally independent of literal authentication for inert mutation controls. It is not a general C/preprocessor verifier. Acceptance of arbitrary unpinned text is not source identity or a theorem about that text's complete control context. `make_witness` and `check_witness` require every literal source pin, then these relations. `check_relations` validates a supplied static projection without authenticating it. Exceptions distinguish FormatError,SourcePinError and SemanticError(code).

The reader accepts one package directory and reads only inputs/input-NNN.data by literal source IDs; no arbitrary manifest pathname fallback exists. It imports only the NEW checker. The active reader_v2 imports checker_v2; their preserved v1 predecessors are rejected initial evidence. Neither reader executes any original source, kernel body or target program.
