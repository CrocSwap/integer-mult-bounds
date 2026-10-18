# Evidence and reproducibility limits

I use Python 3.12.15 on macOS arm64. I authenticate both immutable source
archives, PR2809's 97 exports and eleven transitive repository inputs, and
the stock-fit proof before executing a suite. I retain exact source pins in
SOURCES.json and source.py. The archives are immutable inputs; replay does
not regenerate or compare newly compressed containers.

I passed all eight registered commands with exit code 0 on 2026-10-16 after
merging canonical main a1bfbc677fdcbc2a27a9b3bf6c78cac8fd6da9e2. The launcher
reported PASS_REGISTERED_RESEARCH_PACKAGE. I ran setup, selected ROOT and
failure controls normally and with assertions disabled. I retain the complete
typed receipts in RESULT.json; wall-clock timings are observations rather
than acceptance conditions. The guidance and all twelve declared runtime/proof
input paths had no changes during this submission refresh.

I repeated the complete registered replay after adding consumed-output-marker
restoration to Binary.run. All eight commands passed again at 09:00 UTC; the
final engine took 165.53 seconds. I treat this as simulator evidence, not a
practical speedup or an independent proof of the asymptotic estimate.

The engine checks two 1,024-column fitted invocations separated by a 192-column
elementary invocation on the same fixed roles. Each fitted invocation performs
two separately padded roots and 24 residuals. The whole sequence reaches four
completed roots; each individual return reports two because I reset the session
at reuse. I additionally check a 1,024-column binary call through a fitted native
engine, adding two roots and exercising all three factory scopes together.
The direct fitted cases also compare each padded F endpoint before cancellation.
I use a separate affine mask for each input variable and a separate
constant bit, while physical payload cells retain their binary values. A wrong
equal-valued origin, a cancelled origin and an added affine constant all fail
the intended independent-column condition.

The physical engine disables the source recursive Invocation constructor,
Word construction, numerical decoding, and new Tape/Arena construction during
execution. It verifies closed numerical live maps, erased work markers and
templates, and empty parking tapes. The reduced grammar has no recursive child
at n=2; PR2809's separate complete recursive fixture and its source-level argument
remain predecessors. I do not describe this outer fixture as a selected GL64 run.

The setup suite checks 552 integer pairs against independent Python integer
oracles, seven selected ceil-power relations, six reduced stock selections and
five template extents. The stock fixtures change the source dimension/rank and
row factor; they check the encoded algorithm rather than the selected numerical
stock. I bind the latter in the written proof to the retained exact formula and
fit theorem. The selected ROOT suite separately uses the actual 64-dimensional
coefficient grammar, newly initialized physical banks and the runtime encoder.

The binary suite checks fifteen complete rectangles using elementary native
backends. I erase the consumed binary output marker after each width-1 case,
then require the width-2 call to restore it on reuse. Those fixtures establish
the padding/restriction junction and reuse,
not the faster backend's all-size rate. The composition proof retains that
separate mathematical dependency. I have not run a selected full cold replay,
Linux replay, hosted-CI job or proof assistant for this package.

During integration I found two ownership errors before publication. Passing an
outer Lease into Machine.load_root let its canonical commit consume a borrowed
input. The adapter now passes physical views and preserves the outer ownership
map. At final return the retained transfer erased the payload cells but left
the lease active; I now close it after transfer. The completed fixtures check
both boundaries. These were errors in this new integration, not findings about
the predecessor's declared physical-input contract.

PR2809's source record preserves its earlier seven-suite pass and later local
timeouts after an upstream metadata refresh. I do not convert those timeouts
into a fresh predecessor pass here. This package uses that exact archived
head and exercises the interfaces named above. The all-width statement still
requires assessment of its written source dependencies and refinement argument.
