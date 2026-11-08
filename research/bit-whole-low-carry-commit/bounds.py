# SPDX-License-Identifier: Apache-2.0
"""Written-proof resource ledger, evaluated only by the verifier.

No emitted machine instruction calls this module or observes runtime sizes.
"""


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ledger(metadata, Q, Z):
    require(type(Q) is int and Q >= 1 and Q % 2 == 1 and type(Z) is int and Z >= 1,
            'positive odd runtime modulus and positive complete spectator extent')
    D = metadata['d']
    T = len(metadata['types'])
    b = (metadata['q']-1).bit_length()
    C = metadata['local_cells']
    H = Q**D*Z
    V = T*H
    K = T*D*b
    L = Q.bit_length()
    terms = dict(
        full_cache_initialization=5*K+16,
        extent_preparation=128*(D+1)*H+16*T+32*(D+1),
        fiber_staging_and_local_cache=T*(64*H+16*C*b+64),
        all_coordinate_leaves=T*D*((32*D+1024)*H+256*C*b+1024*L+8192),
        carry_workspace_return=16*V+16*K+32*(D+1)*H+32*T+64*(D+1),
        low_commit=128*(T+D+1)*V+16*K+16+128*D,
        fixed_link_and_Q_test=32,
    )
    # Fixed input/output heads are included. Unvisited data on unrelated
    # borrowed spectator tapes is not program-created workspace.
    spans = 64*(D+1)*V+8*K+512*(D+1)
    return dict(D=D, T=T, b=b, C=C, Q=Q, Z=Z, H=H, V=V, K=K, L=L,
                transition_terms=terms, transitions=sum(terms.values()), visited_cells=spans)
