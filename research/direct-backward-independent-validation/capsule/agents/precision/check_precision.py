#!/usr/bin/env python3
"""Independent bounded literal/precision/compiler screen for PR5398.

No submitted Python is imported or executed. The all-n result is the written
induction in REPORT.md; finite checks below corroborate its inequalities.
Apache-2.0. Chris R/Clear1nsight with substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import resource
import time

HERE = Path(__file__).resolve().parent
HEAD = '174fb211493b43a42210434083e9702b4fb7a2ce'
PACKAGE = 'research/kappa-backward-controller-20261023'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == '.gz' else b)


def scalar_allowance(g):
    if g[0] in ('copy', 'clear'):
        return 2
    q = Q(*g[3:]) if g[0] == 'add' else Q(*g[2:])
    a, b = abs(q.numerator), q.denominator
    need(a and b & (b - 1) == 0, 'nonzero dyadic scalar')
    if g[0] == 'scale':
        need(a & (a - 1) == 0, 'dyadic unit SCALE')
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    need(g[0] == 'add', 'known scalar opcode')
    return 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)


def scalar_height(g):
    if g[0] in ('copy', 'clear'):
        return 0
    q = Q(*g[3:]) if g[0] == 'add' else Q(*g[2:])
    v = 1 + abs(q) if g[0] == 'add' else max(Q(1), abs(q))
    k = 0
    while v > 1:
        v /= 2
        k += 1
    return k + q.denominator.bit_length() - 1


def signed_swap():
    # a+=b; b-=a; a+=b implements (a,b) -> (b,-a).
    a, b = [1, 0], [0, 1]
    norms = []
    a = [x + y for x, y in zip(a, b)]
    norms.append(max(sum(map(abs, a)), sum(map(abs, b))))
    b = [y - x for x, y in zip(a, b)]
    norms.append(max(sum(map(abs, a)), sum(map(abs, b))))
    a = [x + y for x, y in zip(a, b)]
    norms.append(max(sum(map(abs, a)), sum(map(abs, b))))
    need(a == [0, 1] and b == [-1, 0], 'exact signed rotation')
    need(norms == [2, 2, 1], 'three-ADD transient amplification')
    return norms


def gaussian_multiply(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def rejects(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('mutant accepted: '+label)


def main():
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_AS, (128*1024**2, 128*1024**2))
    p = ArgumentParser()
    p.add_argument('--root', '--repo', dest='repo', type=Path, default=HERE.parents[1]/'repository')
    p.add_argument('--prior-root', type=Path, default=HERE.parents[2]/'swarm-execution-sol-high-20261024')
    p.add_argument('--prior-word', type=Path)
    p.add_argument('--prior-native', type=Path)
    p.add_argument('--prior-witness', type=Path)
    p.add_argument('--finite-precompilation', type=Path)
    p.add_argument('--finite-template-closure', type=Path)
    p.add_argument('--specialization', type=Path)
    p.add_argument('--framework-proof', type=Path)
    p.add_argument('--reuse-manifest', type=Path, default=HERE.parent/'provenance/5396-REUSE-MANIFEST.json')
    p.add_argument('--sources', type=Path, default=HERE/'SOURCES.json')
    p.add_argument('--out', type=Path, default=HERE/'CHECK.json')
    args = p.parse_args()
    manifest = read(args.sources)
    need(manifest['candidate_head'] == HEAD, 'exact candidate pin')
    overrides = {
        'repository/research/kappa-joint-relations-20261023/WORD.json.gz': args.prior_word,
        'repository/research/kappa-joint-relations-20261023/native.py': args.prior_native,
        'repository/research/kappa-joint-relations-20261023/WITNESS.json': args.prior_witness,
        'agents/applicability/FINITE-PRECOMPILATION.md': args.finite_precompilation,
        'agents/applicability/FINITE-TEMPLATE-CLOSURE.md': args.finite_template_closure,
        'agents/sources/pr5241/research/final4610-independent-admission/SPECIALIZATION.md': args.specialization,
        'agents/sources/pr5241/research/final4610-independent-admission/PROOF.md': args.framework_proof,
    }
    resolved = []
    for row in manifest['rows']:
        rel = row['path']
        prefix = 'swarm-next-gain-sol-high-20261024/repository/'
        oldprefix = 'swarm-execution-sol-high-20261024/'
        if rel.startswith(prefix):
            file = args.repo/rel[len(prefix):]
        elif rel.startswith(oldprefix):
            oldrel = rel[len(oldprefix):]
            file = overrides.get(oldrel) or args.prior_root/oldrel
        else:
            need(rel.endswith('/provenance/5396-REUSE-MANIFEST.json'), 'known provenance mapping')
            file = args.reuse_manifest
        b = file.read_bytes()
        need(sha256(b).hexdigest() == row['sha256'], 'source SHA256 '+rel)
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == row['git_blob'], 'source Git blob '+rel)
        resolved.append(dict(path=rel, sha256=row['sha256']))
    pkg = args.repo/PACKAGE
    priorpkg = args.prior_root/'repository/research/kappa-joint-relations-20261023'
    for name in ('native.py', 'WITNESS.json'):
        priorfile = (args.prior_native if name == 'native.py' else args.prior_witness) or priorpkg/name
        need((pkg/name).read_bytes() == priorfile.read_bytes(), 'unchanged independently validated5383 '+name)
    priorword = args.prior_word or priorpkg/'WORD.json.gz'
    word = read(priorword)
    need(sha256(gzip.decompress(priorword.read_bytes())).hexdigest() ==
         '2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d', 'source word payload')
    back = word['programs']['backward']
    owned = {tuple(r) for r in word['owned']['backward']}
    need(len(owned) == 17 and ('L', 0) not in owned, 'seventeen owners, borrowed main remains borrowed')
    for e in back:
        if e[0] == 'scalar' and e[1][0] in ('clear', 'copy'):
            need(tuple(e[1][1]) in owned, 'only owned destructive targets')
    local_scalar = sum(scalar_allowance(e[1]) for e in back if e[0] == 'scalar')
    height = sum(scalar_height(e[1]) for e in back if e[0] == 'scalar')
    need(local_scalar == 158744 and height == 29183, 'fresh local scalar allowance and height')
    ctl = read(pkg/'CONTROLLER.json')
    source_ctl = read(args.repo/'research/joint-helper-lattice/CONTROLLER.json')
    expected, sites = [], []
    for i, e in enumerate(source_ctl['physical_events']):
        if e[0] == 'LOCAL' and e[3] is False:
            _, stage, pair, _ = e
            x, y = 2*pair, 2*pair+1
            sites.append(dict(source_index=i, stage=stage, pair=pair))
            expected += [['SIGNED_SWAP', y, x], ['Q_POWER', x, 2], ['LOCAL', stage, pair, True],
                         ['SIGNED_SWAP', x, y], ['Q_POWER', y, -2]]
        else:
            expected.append(e)
    need(ctl['physical_events'] == expected and ctl['wrapper_sites'] == sites, 'fresh literal direct caller wrappers')
    need([s['stage'] for s in sites] == [0, 32], 'both actual wrapper stages')
    count = Counter(e[0] for e in expected)
    need(count['LOCAL'] == 18 and all(e[3] is True for e in expected if e[0] == 'LOCAL'), 'eighteen unchanged backward suppliers')
    source_count = Counter(e[0] for e in source_ctl['physical_events'])
    need(count['SIGNED_SWAP']-source_count['SIGNED_SWAP'] == count['Q_POWER'] == 4 and
         count['QUERY_SHEAR'] == 15, 'four new wrappers plus sixteen retained signed swaps')
    # Q=aI+bX, X^2=I. Exact Gaussian arithmetic proves Q^2=X with phase+1.
    a, b = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    aa, bb, ab = gaussian_multiply(a, a), gaussian_multiply(b, b), gaussian_multiply(a, b)
    need(tuple(x+y for x,y in zip(aa,bb)) == (0,0) and tuple(2*x for x in ab) == (1,0), 'Q squared is phase+1 translation')
    # conjugate(Q)=XQ: the coefficients of I and X are exchanged.
    need((a[0],-a[1]) == b and (b[0],-b[1]) == a, 'signed helper conjugation absorbed in monomial adapter')
    norms = signed_swap()
    raw_local_banks = count['LOCAL']*len(owned)
    need(raw_local_banks == 306, 'new complete simultaneous LOCAL banks')
    rho, k, tested = Q(1,10**12), Q('.00302728823'), Q('.00302728824')
    gap = (tested-k)/7
    j, H = 55099, 38569300000000000
    need(gap == Q(1,700000000000) and H == j*gap.denominator, 'fresh exact compiler grid')
    need((H+1)**1000 < 2**j, 'fresh winning compiler comparison')
    need((gap.denominator*(j-1)+1)**1000 >= 2**(j-1), 'fresh preceding compiler grid fails')
    normalized = 1/(1+1024*rho)+Q(4,2**32)
    need(normalized < 1 and 1/(1+1024*Q(1,10**13))+Q(4,2**32) > 1, 'funded reserve and rejecting control')
    need(20**64 < 21**63 and Q(97,100)**128 < Q(1,16), 'strict split and tail-block guards')
    need(4*Q(97,100)**1024 < Q(4,2**32), 'both conservative tail powers')
    need(2*20**(1024*64) <= 145**(1024*63), 'shifted-exit rank capacity')
    need(H > 8*1024 and 1000*gap > Q(1,H+1), 'initial rank and eventual logarithmic derivative')
    # The all-n proof is algebraic. These exact checks are sanity controls,
    # with no astronomical F(n) or N instantiated.
    strictified_log_bound = 2*(82*1024+10+2*8192)+6+3*8193
    need(strictified_log_bound == 225309 and strictified_log_bound < 262144, 'fresh strictified unit majorant')
    for n in range(1,1001):
        need(16*(n+1)**2 >= 9*n+20, 'universal exponent inequality probe')
    proof_polynomial = [16,23,-4]
    need(sum(proof_polynomial) == 35 and proof_polynomial[0] > 0 and proof_polynomial[1] > 0,
         'positive increasing induction polynomial on n>=1')
    arithmetic = read(pkg/'RESULT.json')['arithmetic']
    need(arithmetic['compiler']['H'] == H and arithmetic['compiler']['integer_test_exponent'] == j,
         'independent result compared to submitted receipt only after computation')
    need(Q(arithmetic['strictification']['normalized_paid_upper']) == normalized, 'normalized receipt comparison')
    need(arithmetic['nonrecursive']['raw_scalar_upper'] == 181586816, 'separate invoice raw cap binding')
    rejected = [
        rejects(lambda: need(('L',0) in owned, 'borrowed erase'), 'borrowed_erase'),
        rejects(lambda: need(18 >= raw_local_banks, 'missing live banks'), 'one_bank_per_depth'),
        rejects(lambda: need(274 >= raw_local_banks, 'stale LOCAL banks'), 'unchanged_274_bank_cap'),
        rejects(lambda: need(1 >= max(norms), 'swap prefix underfunded'), 'completed_swap_norm_for_prefix'),
        rejects(lambda: need(30 >= 262144, 'raw cap is not expanded stock'), 'raw_1e9_expanded_cap'),
        rejects(lambda: need(1/(1+1024*Q(1,10**13))+Q(4,2**32) < 1, 'rounding reserve underfunded'), 'insufficient_reserve'),
        rejects(lambda: need((gap.denominator*(j-1)+1)**1000 < 2**(j-1), 'preceding grid insufficient'), 'preceding_compiler_grid'),
    ]
    result = dict(schema='5398-precision/1', status='PASS_SCOPED_DIRECT_CALLER_PRECISION_STOCK_COMPILER',
        candidate_head=HEAD, source_bindings=len(resolved),
        source_manifest_sha256=sha256(args.sources.read_bytes()).hexdigest(),
        retained_5383_supplier=True, source_word_payload_sha256='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d',
        backward_scalar_allowance=local_scalar, backward_scalar_height=height,
        full_backward_calls=18, local_owned_banks=17, raw_LOCAL_owned_banks=raw_local_banks,
        signed_swap_three_ADD_prefix_sup_norms=norms, signed_swap_total=count['SIGNED_SWAP'],
        signed_swap_new=count['SIGNED_SWAP']-source_count['SIGNED_SWAP'], translation_phase=1,
        conjugate_gaussian_is_monomial_times_positive_gaussian=True,
        helper_full_signed_two_sided_factorization_required=True,
        compiler=dict(H=H,j=j,gap=str(gap),tested=str(tested),kappa=str(k),reserve=str(rho),
                      normalized_paid_upper=str(normalized),remaining_rounding_margin=str(1-normalized)),
        expanded=dict(unit_bound='D0=2^262144',unit_log_bound=225309,
                      recursion='F(0)=D0; X_n=(n+1)*(D0+1)*(F(n-1)+1); F(n)=X_n^(16*(n+1)^2)',
                      bound='M=F(2^38569300000000000)',counts=['W','P','U','O','R','G'],
                      all_n_proof='REPORT.md; strong induction, not the finite probes',
                      numerical_majorant_materialized=False,raw_cap_used_as_expanded_stock=False),
        precision=dict(C1=1,constants='Zbar=2M; Ebar=64*(Zbar+N+2M+1)^3; Bbar=M+Ebar; C0bar=32*N*Bbar^2',
                       arbitrary_interval_recurrence='Jamp(e)<=2*Jamp(floor(e/N))+Pbar*floor(e/N)+Ebar',
                       intermediate_swap_factor_paid=True),
        stock=dict(complex='[W*(O+1)]^Dord(d)',simultaneous='S_complex*S_BIT*every additional independent stock',
                   all_suspended_owners_distinct=True,owned_productive_credit=False,BIT_atom='1/250'),
        controls=dict(kind='algebraic_underfunding_and_grammar_sentinels_not_mutated_circuit_semantic_replays',
                      rejected=rejected, count=len(rejected)),
        assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
        complete_conditional_admission=False, independent_interval_or_native_replay=False,
        seconds=time.monotonic()-start, max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Fresh literal/scalar/guard checks plus written constructive all-n closure; independent caller physical/phase/invoice and numerical moment/outer gates remain separate.')
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'],raw_LOCAL_owned_banks=raw_local_banks)))


if __name__ == '__main__':
    main()
