"""Bind the freshly replayed PR377 template, finite invoice and exact moments.

Prepared with OpenAI Codex assistance. Apache-2.0. This adapter uses PR377's
degree-two halving model and exact source engines, with no half-rank assertion.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json


def read(p): return json.loads(Path(p).read_text())
def digest(p): return sha256(Path(p).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(source, output):
    source, output = Path(source), Path(output)
    verified = read(output / 'VERIFICATION.json')
    assert verified['status'] == 'PASS_PORTABLE_NINE_STAGE_COMPLEX_FINITE_COMPONENT'
    assert verified['source_manifest_sha256'] == digest(source / 'MANIFEST.json')
    assert len(verified['fresh_stages']) == 8
    assert all(s['returncode'] == 0 for s in verified['fresh_stages'])
    directory = output / 'work/complex-nine-native'
    for relative, want in verified['receipt_sha256'].items():
        assert digest(directory / relative) == want, relative
    invoice = read(directory / 'GLOBAL-REVIEW.json')
    audit = read(directory / 'INDEPENDENT-TEMPLATE-AUDIT.json')
    local = read(directory / 'local-admission/UPSTREAM-GUARD.json')
    assert local['precision_guard']['semantic_C1'] == 1
    assert invoice['status'] == 'PASS_NINE_STAGE_SOURCE_BOUND_TEMPLATE_OWNERS_PROFILE_AND_FINITE_INVOICE'
    assert audit['status'] == 'PASS_INDEPENDENT_EMITTED_TEMPLATE_AUDIT_AND_TWO_MOMENTS'
    raw = gzip.decompress((directory / 'GLOBAL-TEMPLATE.json.gz').read_bytes())
    template_sha = sha256(raw).hexdigest()
    assert template_sha == invoice['template_sha256'] == audit['template_sha256']
    assert invoice['profile'] == audit['paid_profile']
    H = {int(r): n for r, n in invoice['profile'].items()}
    m, stock = invoice['m'], invoice['live']
    assert (m, stock, invoice['physical']) == (73, 14727, 15520)
    assert sum(H.values()) == invoice['paid_calls'] == 310455
    assert sum(r*n for r,n in H.items()) == invoice['rank_mass'] == 1072575
    assert m*stock-invoice['rank_mass'] == invoice['deficit'] == 2496
    assert invoice['cover_correction_calls'] == stock
    assert invoice['bank_padding_calls'] == 7047
    assert invoice['whole_residual_assignments'] == 56376
    assert invoice['work_lifetimes_freshly_revalidated'] and invoice['owner_injections']
    assert audit['next_grid_rejected'] and audit['all_eight_signed_data_columns']
    assert audit['bridge_omission_controls'] == 9
    assert set(audit['structural_controls_rejected']) == {
        'missing_cover_phase', 'aliased_helper_route', 'missing_padding',
        'wrong_reverse_local', 'omitted_terminal_exchange'}
    pg = invoice['finite_invoice']
    assert (pg['G_exponent'],pg['E_exponent'],pg['C0_exponent']) == (30000,100000,210000)
    assert pg['router_bits'] < 30000 and pg['literal_bits'] < 100000
    assert pg['required_C0_bits'] < 210000
    assert pg['halving_degree'] == 2
    assert pg['halving_integer_inequality'] == [m*m, 2*max(H)**2]
    assert m*m > 2*max(H)**2
    assert pg['induction_gap_multiple_B'] == 2*(m-max(H))-1 == 49
    assert pg['physical_row_coefficient'] == 2*pg['physical_stock_bits']+9909+252 == 15445
    assert pg['retained_row_coefficient'] == 20161 > pg['physical_row_coefficient']
    engines = source / 'work/pr361/code/engines'
    M = load('nine_composition_moment', engines/'moment.py')
    B = load('nine_composition_independent', engines/'base_two_moment.py')
    b = Q(audit['coarse_complex'])
    assert b == Q(verified['complex_coarse']) == Q(999240641319551,10**18)
    fallback = 32*m*m*sum(H.values())
    bounds = []
    for saving in (b, b+Q(1,10**18)):
        original = M.moment(H,m,stock,saving,True)
        low, high = B.moment(m,stock,list(H.items()),saving)
        bad_low, bad_high = B.moment(m,stock,[(1,fallback)],saving)
        independent = (low+Q(1,10**16)*bad_low,high+Q(1,10**16)*bad_high)
        bounds.append(dict(saving=str(saving),original=list(map(str,original)),
                           independent=list(map(str,independent))))
    assert Q(bounds[0]['original'][1]) < 1 < Q(bounds[1]['original'][0])
    assert Q(bounds[0]['independent'][1]) < 1 < Q(bounds[1]['independent'][0])
    return dict(status='PASS_FRESH_NINE_STAGE_COMPLEX_INTERFACE',b=str(b),m=m,W=stock,
                histogram=H,bounds=bounds,template_sha256=template_sha,
                finite_invoice=pg,semantic_C1=1,
                source_manifest_sha256=digest(source/'MANIFEST.json'),
                pricing_sha256={name:digest(engines/name) for name in ('moment.py','base_two_moment.py','outer.py')},
                proof_sha256=digest(source/'work/complex-nine-native/PROOF.txt'),
                scope=verified['scope'],invoice_scope=invoice['scope'],audit_scope=audit['scope'])
