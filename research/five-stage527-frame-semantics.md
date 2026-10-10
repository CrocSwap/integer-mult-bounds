# Bank routes and the retained frame coordinate system

The full-address bank adapter changes stream ownership. It does not change the cover variable used to interpret an emitted MOVE or ADD frame.

An original stage invocation at class d uses the exact checked global projector d*A*d^-1. Its helper formerly lived at class d*tau_i. The banked helper lives at h=d*tau_i*N^-1. The frame still means d*A*d^-1. A consumer must not substitute h for d or conjugate that frame by N a second time.

This convention gives the required endpoint directly. Write R0=diag(I24-sigma,0,...,0). Since d=h*N*tau_i, the helper residual is

    d*R0*d^-1 = h*N*(tau_i*R0*tau_i)*N^-1*h^-1.

The checked normalizer turns tau_i*R0*tau_i into the assigned coordinate bank projector. Thus the endpoint is the intended block at bank class h. During the actual scalar word, the inherited original d-frame remains the one used for equal-frame additions and paid rank increments. Chart routing and its charged selector factors move complete streams to that invocation; they are not a second change of projector coordinates.

`BankLowerer.iter_stage` delegates to `BankPlan.map_stage_row`, which preserves every original mathematical field and changes only stream operand slots. The same original local cover d is present in every resulting address word. Boundary projectors already contain the original data-route conjugacies and are interpreted at their physical class d. Every idle and bridge remains a separate all-cover phase.

The conditional common ancestor chart is unchanged throughout each bank's completed block schedule, as required by the inherited bank compiler theorem.

This note accompanies `research/five-stage-source527-banks/`. Prepared by eumemic with substantial OpenAI Codex assistance. The five-stage source composition is Henry Grant / hcg890’s PR234; the bank compiler lineage is retained in that package’s notices.
