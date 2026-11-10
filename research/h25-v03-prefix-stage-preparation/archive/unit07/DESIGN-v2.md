# Unit07 exact Q/request supplement

Versioned clarification of DESIGN-v1.md (10883B SHA5fe1fac04c60681295fff28f617e16897f215ba068dc443a626f876736600508); v1 remains unchanged. No candidate execution before parent gate.

The request additionally REQUIRES `source_closure_admission_sha256` (exact original digest DATA; no value invented). The request contains `outer_policy` EXACT `{shared_seconds,root_seconds,root_address_space_bytes,root_rss_sum_bytes}`; these are distinct from `session_seconds` for the prefix supervisor and `child.root_seconds` for the inner genuine Root. There is no second ambiguous top-level root_seconds. New preparer accepts exact integer bounds: shared<=600, outer root<=190, inner Root<=180, each address-space/RSS bound<=1GiB, allpositive. Actual complete cost/fit remains independently unproved; these integers do not reserve funds.

For canonical R and safe selected label, derive `session_directory = R + '/runtime/runs/' + label + '/science'`. The operation MUST NOT create the run-label directory or science directory. The runner creates the run folder, and actual make_prefix_owner exclusively creates science. Derive inner `output=session_directory+'/producer-output'`. Derive K exactly `R+'/control/'+queue+'-private'` and use Q.round_root=K; never substitute canonical R. Sb=R+'/stages/'+stage and packet=R+'/control/'+queue+'-packet' are exclusive distinct owned new roots. Sc is separately admitted/preexisting and outside Sb/K/packet. New queue is ASCII alphanumeric; stage/job/label are original bounded ASCII letters/digits/underscore/hyphen names.

Q is EXACT original shape:

    schema = 'h25-v03-prefix-parent-plan-v1'
    mode = request.mode
    round_root = K
    session_directory = derived science path
    session_seconds = request.session_seconds
    source_closure_admission_sha256 = required request digest
    source_files = verified all-nine-category base plus real derived inputs
    case = {id,generation,launch_nonce,stage_directory,stage_manifest,
            stage_directories,output,command,root_seconds,address_space_bytes,
            rss_bytes,root_source,driver_source,gate_values,expectation}

case identity/generation/nonce/Sc manifest/directories/source/gate/expectation/resource fields come from the exact validated child record; output is derived above, not supplied/relabelled. The exact command is constructed as the actual Unit05 validator does:

    ['/usr/bin/python3.12','-S','-s','-P','-B'] + (['-O'] if mode=='optimized' else [])
    + [Sc+'/integration/full_driver.py','--root-sha256',
       'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0',
       '--provider',Sc+'/integration/probe_binding_v3.py',
       '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2',
       '--driver',Sc+'/integration/v03_control_driver_v1.py',actual driver digest,
       '--integration',Sc+'/integration','--','--output',derived output,
       '--generation',actual generation,'--launch-nonce',actual nonce]

Actual root pin path/digest/38851-byte size, provider row/path/digest, driver path/bound and independently selected gate-file pin are checked. Neither original Root nor configured driver executes during preparation.

Q mandatory memberships retain actual P/checker/original variant/root/driver/gate pins, each compared by path/hash/bytes/mode with the actual installed/independently selected blob. Q does not reference M, its own path/inode, or Sb/STAGE. Actual source files/readiness/config/policy/selection and all excluded outer manifest bytes remain in the operation/custody bill. Nested STAGE.json is rejected in Sb; Sc is separate. SOURCE-READINESS packet uses exact new caller basename run_queue4_prefix_v2.py plus supervisor.py; all packet files/readiness have final readonly mode before observations.

Actual M is ordinary integration/PREFIX-BOOTSTRAP.json with the exact entry-visible schema/fields from v1. Selection uses unchanged `unit06-prior-caller-selection-v1` exact fields, prior actual blob pins and stages list. Every output is construction DATA awaiting independent T0/source/stage/native/C05/C07/funding/runtime approval; no self-authentication or completeness flag is emitted.
