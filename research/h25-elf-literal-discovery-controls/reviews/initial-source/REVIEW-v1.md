# Initial literal-to-use source/control/resource review

**Reject the initial helper's two mapping checks; full P1 remains HOLD.** No execution is granted. Exact initial helper11272B SHA256c9044f4926cbcc880eb17b579b2cd6e323f1657bf6b6463138fc0b4310fe4b04 and plan/manual/freeze snapshots were preserved before findings under initial-reviewed-v1/.

M01: unique_va66–81 checks file coverage but not competing virtual LOAD mappings. In the manual1KiB model, originalLOAD(file256,VA0x400000,size768) maps literal640 to0x400180. A secondLOAD(file768,VA0x400180,size18) does not cover file640 but competes at its virtual span with different bytes. Current helper can accept that ambiguity. Require consistent unique reverse virtual coverage, including relevant zero-fill/memory overlap.

M02: entry76–78 maps its VA to file offset then checks PF_X on any LOAD aliasing that file offset. With the originalLOAD made non-X, entry0x400100 maps to file512; a separate X LOAD(file512,VA0x500000,size1) makes any(PF_X) pass at the wrong VA. Test executable permission on the actual unique entry-VA LOAD. These are parser-contract counterexamples in the declared synthetic metadata model, not claims about actual GCC or kernel-loadable fixtures. Nothing was executed.

The parent-operation guard is not yet supplied. The helper authenticates/inspects one read-only input but enforces no queue/lock, global60s, stream/aggregate capture or decoder cleanup. The manual cases are14 designs, not a runnable tested builder. Exact executable source/commands and separate control/guard review are required before P1. Also STOP_CANDIDATE_CAP is printed with exit0; the parent must parse/gate that status before decoder continuation, or a successor must return nonzero.

Positive scope is retained: hash-before-parse, bounded input/tables/report, no subprocess/target/original import, finite candidate locators and explicit false semantic/role/reachability/certificate flags. Pattern hits and zero hits remain discovery data. S11–S13 semantic expectations must not be counted as executed pattern-helper proof. P3 is not needed merely to admit a correctly bounded passive discovery operation with an honest partial result.

Resource arithmetic can fit: specific raw maxima475136B plus256KiB reserved report/certificate/terminal=737280B<1MiB. Actual per-stream limits, shared accounting, cap+1/error retention, deadline/cleanup and current funding still need executable enforcement. No full image copy is authorized. Original180s/command and sampled1GiB remain upper bounds; memory sampling is not hard peak proof. Canonical94.550533479 and supplemental98.950533479 stay distinct; costs OPEN_NOT_ZERO.

Parent declared the sole bounded repair23:42:23–23:52:23 into repair-v2, preserving this initial failure. The next operation is a separate frozen successor helper/control/guard delta review. No success is assumed, no second repair/reroll and no old native pilot resume.

Review first clock23:38:50UTC/fixed stop23:50:50UTC; JSON records freeze and initial review stops now. Round initial no-progress23:57:51.401519/hard00:12:51.401519 unchanged. No imports, tests, decoder/target/compiler/native/process/network/policy work or protected-runtime reads. Full C05/V03/field admission false, original43.5%, original credit0.
