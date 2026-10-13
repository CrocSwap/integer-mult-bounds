"""Typed local synthesis catalogue for exact matrix circuits (standard library).

Grounded in Alejandro Zarzuelo Urdiales's July/October composition package.
Known DPS, Rosowski and Strassen ingredients retain their attribution. A count
is never promoted to a tensor rank, block-valid identity or integer-mult kappa.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from fractions import Fraction
from pathlib import Path
import argparse, hashlib, json, math
from functools import lru_cache

HERE = Path(__file__).resolve().parent
MATRIX_PIN = '7203497dc990e47c2391bff1b9863408d817faeb'
PROOF_PIN = '9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd'
OUTER_SHA = 'e04ebfffc4c2f43cb688c856f1f30e5ef1b7c215f76854ab1d75df03f4bff387'
COMMUNITY_PIN = 'b7194b8586844956904b33e9fe18f0c75606c11b'
COMMUNITY_SHA = '33b3373c04e18a7f4cee33ba68da6ed71934acc3e0179cca6197696be4befa22'
MODELS = {'scheduled_products', 'bilinear_rank', 'native_field_products'}


class Ineligible(ValueError):
    """An explicit algebraic, domain or evidence obligation was not met."""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class Domain:
    kind: str
    modulus: int = 0

    @classmethod
    def parse(cls, name: str):
        name = name.upper()
        if name in ('Z', 'Q'):
            return cls(name)
        if name.startswith('GF'):
            p = int(name[2:])
            if p < 2 or any(p % d == 0 for d in range(2, math.isqrt(p)+1)):
                raise Ineligible('GF modulus must be prime')
            return cls('GF', p)
        raise Ineligible('supported targets are Z, Q, GF followed by a prime')

    @property
    def label(self):
        return f'GF{self.modulus}' if self.kind == 'GF' else self.kind


@dataclass(frozen=True)
class Scheme:
    name: str
    order: int
    products: int
    denominator: int
    block_stable: bool
    bilinear: bool
    evidence: str
    source: str


@dataclass(frozen=True)
class Candidate:
    order: int
    outers: tuple[str, ...]
    terminal: str
    product_slots: int
    denominator: int
    target: str
    requested_model: str
    realization: str
    exact_output_quotients: int
    fixed_output_inverse_scalings: int
    target_word_bits: int | None
    lifted_word_bits: int | None
    lifted_modulus: int | None
    block_stable: bool
    bilinear: bool
    evidence: tuple[str, ...]
    route: str = 'exact_factor_chain'
    kernel_order: int | None = None
    kernel_invocations: int | None = None
    classical_fringe_products: int = 0
    padded_order: int | None = None

    def to_dict(self):
        result = asdict(self)
        result['cost_scope'] = 'scheduled input-dependent product slots; fixed operations recorded separately'
        result['unpriced_costs'] = ['additions/subtractions', 'fixed coefficient scales',
                                   'data movement', 'arithmetic bit costs']
        result['strongest_known_or_global_optimum_claim'] = False
        if self.lifted_modulus is not None:
            result['comparison_warning'] = ('lifted-ring products are not native GF products; '
                                            'raw slot totals are not field-operation comparisons')
            result['product_slots_by_realization'] = {
                f'Z/{self.lifted_modulus}Z': self.product_slots-self.classical_fringe_products,
                self.target: self.classical_fringe_products}
            invocations = self.kernel_invocations if self.kernel_invocations is not None else 1
            width = self.kernel_order if self.kernel_order is not None else self.order
            result['scheduled_input_representative_lifts'] = 2*invocations*width**2
            result['scheduled_final_target_reductions'] = self.exact_output_quotients
            result['intermediate_residue_reductions'] = 'all numerator operations in the lifted ring; bit work not priced'
        result['claimed_target_field_tensor_rank_bound'] = (self.product_slots
            if self.requested_model=='bilinear_rank' else None)
        return result


def strassen_tables():
    # Classical seven ordered products; no interchange of block factors.
    a = [[1,0,0,1], [0,0,1,1], [1,0,0,0], [0,0,0,1],
         [1,1,0,0], [-1,0,1,0], [0,1,0,-1]]
    b = [[1,0,0,1], [1,0,0,0], [0,1,0,-1], [-1,0,1,0],
         [0,0,0,1], [1,1,0,0], [0,0,1,1]]
    # gamma[product][output], output row-major.
    g = [[1,0,0,1], [0,0,1,-1], [0,1,0,1], [1,0,1,0],
         [-1,1,0,0], [0,0,0,1], [1,0,0,0]]
    return a, b, g


def verify_ordered_tensor(order, alpha, beta, gamma, denominator=1):
    """Exact ordered A_i B_j coefficients: this implies central block lifting.

    This is an executable coefficient replay, not a new Lean proof of lifting.
    """
    r, size = len(alpha), order*order
    if not (r == len(beta) == len(gamma) and
            all(len(row) == size for table in (alpha,beta,gamma) for row in table)):
        raise Ineligible('coefficient table shape mismatch')
    checked = 0
    for output in range(size):
        oi, oj = divmod(output, order)
        for av in range(size):
            ai, ak = divmod(av, order)
            for bv in range(size):
                bk, bj = divmod(bv, order)
                value = sum(alpha[t][av]*beta[t][bv]*gamma[t][output] for t in range(r))
                expected = denominator*int(ai == oi and bj == oj and ak == bk)
                if value != expected:
                    raise Ineligible(f'ordered coefficient failure at {(output,av,bv)}')
                checked += 1
    return checked


def outer48_tables(path=None):
    path = Path(path or HERE/'inputs/outer48.json')
    if sha(path) != OUTER_SHA:
        raise Ineligible('actual outer48 coefficient source hash changed')
    data = json.loads(path.read_text())
    if data['per_leg_denominator_scales'] != {'alpha':1, 'beta':1, 'gamma':8}:
        raise Ineligible('outer48 leg scaling changed')
    c = data['minimal_integer_certificate']
    return c['alpha_integer'], c['beta_integer'], c['gamma_numerator']


def catalogue():
    source = f'https://github.com/alejandrozu/openmath-2026-judging/tree/{PROOF_PIN}/personal-matrix-hybrid-2026-10-07'
    return {
        'strassen2': Scheme('strassen2',2,7,1,True,True,
                            'explicit ordered coefficient replay: 64 equations',
                            source+'/manuscript/Hybrid_Composition_revised.md'),
        'dps4': Scheme('dps4',4,48,8,True,True,
                       'actual 48-product data; 4096 ordered coefficient equations; source Lean closure',
                       source+'/lean/Outer48Data.lean'),
        'personal16': Scheme('personal16',16,2208,8,False,False,
                             'actual mixed-input circuit; source concrete and integer quotient proofs',
                             source+'/lean/IntegerLateDivision.lean')
    }


def W(n):
    if n < 2:
        raise Ineligible('the cited commutative W formula starts at order two')
    return n*(n*n+2*n-1)//2


def terminal(name, order):
    source = f'https://github.com/alejandrozu/openmath-2026-judging/blob/{PROOF_PIN}/personal-matrix-hybrid-2026-10-07/lean/'
    if name == 'classical':
        return Scheme(f'classical{order}',order,order**3,1,True,True,
                      'ordinary ordered matrix-product definition',source+'BlockComposition.lean')
    if name == 'rosowski_even' and order >= 2 and order % 2 == 0:
        return Scheme(f'rosowski_even{order}',order,W(order),1,False,False,
                      'division-free even-inner P/R/Q/M recipe; general source identity',source+'RosowskiEven.lean')
    if name == 'personal16' and order == 16:
        return catalogue()['personal16']
    raise Ineligible('no supplied certified terminal recipe at this name/order')


def validate_terminal(leaf):
    if leaf.name == 'personal16':
        expected = terminal('personal16',16)
    elif leaf.name == f'classical{leaf.order}':
        expected = terminal('classical',leaf.order)
    elif leaf.name == f'rosowski_even{leaf.order}':
        expected = terminal('rosowski_even',leaf.order)
    else:
        raise Ineligible('an external leaf count is not a component-validity certificate')
    if leaf != expected:
        raise Ineligible('terminal metadata differs from its supplied validated recipe')


@lru_cache(maxsize=1)
def validate_catalogue_coefficients():
    a,b,g = outer48_tables()
    return {'dps4':verify_ordered_tensor(4,a,b,g,8),
            'strassen2':verify_ordered_tensor(2,*strassen_tables())}


def realize(denominator, order, target: Domain, model, allow_charged_lift):
    if model not in MODELS:
        raise Ineligible('unknown requested cost model')
    if model == 'native_field_products' and target.kind != 'GF':
        raise Ineligible('native field product model needs a finite-field target')
    q = target.modulus
    bits = (q-1).bit_length() if target.kind == 'GF' else None
    if target.kind == 'GF' and math.gcd(denominator,q) != 1:
        if not allow_charged_lift:
            raise Ineligible('nonunit output denominator: direct target-field recovery loses information')
        if model != 'scheduled_products':
            raise Ineligible('charged lifted-ring realization does not certify native field products or tensor rank')
        modulus = denominator*q
        return dict(realization=f'charged integer polynomial lift modulo {modulus}, exact quotient then reduction modulo {q}',
                    exact_output_quotients=order**2, fixed_output_inverse_scalings=0,
                    target_word_bits=bits, lifted_word_bits=(modulus-1).bit_length(), lifted_modulus=modulus)
    if target.kind == 'Z':
        return dict(realization='integral numerator, certified final exact division' if denominator > 1 else 'integral circuit',
                    exact_output_quotients=order**2 if denominator > 1 else 0,
                    fixed_output_inverse_scalings=0, target_word_bits=None,
                    lifted_word_bits=None, lifted_modulus=None)
    return dict(realization='target-ring circuit with fixed invertible output denominator' if denominator > 1 else 'target-ring circuit',
                exact_output_quotients=0, fixed_output_inverse_scalings=order**2 if denominator > 1 else 0,
                target_word_bits=bits, lifted_word_bits=None, lifted_modulus=None)


def compose(outer_names, leaf, target, model='scheduled_products', allow_charged_lift=False):
    validate_catalogue_coefficients()
    validate_terminal(leaf)
    registry = catalogue()
    outers = []
    for name in outer_names:
        if name not in registry:
            raise Ineligible('outer coefficient/program certificate is absent from this catalogue')
        scheme = registry[name]
        if not scheme.block_stable:
            raise Ineligible('commutative terminal circuit cannot become a block-stable outer without a new proof')
        outers.append(scheme)
    if model in ('bilinear_rank','native_field_products') and not leaf.bilinear:
        if model == 'bilinear_rank':
            raise Ineligible('mixed-input scheduled products do not constitute a bilinear tensor-rank decomposition')
        # Mixed forms are legitimate native field products when the domain route is direct.
    order = leaf.order*math.prod(x.order for x in outers)
    slots = leaf.products*math.prod(x.products for x in outers)
    denominator = leaf.denominator*math.prod(x.denominator for x in outers)
    route = realize(denominator,order,target,model,allow_charged_lift)
    # Bilinear rank is meaningful over fields, not integer exact-quotient arithmetic.
    if model == 'bilinear_rank' and target.kind == 'Z':
        raise Ineligible('integer quotient realization is not a field tensor-rank certificate')
    direct = route['lifted_modulus'] is None
    return Candidate(order,tuple(outer_names),leaf.name,slots,denominator,target.label,model,
                     block_stable=direct and leaf.block_stable and all(x.block_stable for x in outers),
                     bilinear=direct and leaf.bilinear and all(x.bilinear for x in outers),
                     evidence=tuple(x.evidence for x in outers)+(leaf.evidence,), **route)


def fixed_leaf_recurrence(outer_name, leaf, target):
    validate_catalogue_coefficients()
    validate_terminal(leaf)
    outer = catalogue().get(outer_name)
    if outer is None or not outer.block_stable:
        raise Ineligible('recurrence outer lacks a block-stable certificate')
    if target.kind == 'GF' and (math.gcd(outer.denominator,target.modulus)!=1 or
                                math.gcd(leaf.denominator,target.modulus)!=1):
        raise Ineligible('this native-field recurrence cannot invert an outer or terminal denominator')
    if target.kind == 'Z' and (outer.denominator > 1 or leaf.denominator > 1):
        domain_note = ('integer numerator scale is terminal_denominator * outer_denominator^depth; '
                       'final exact quotients and coefficient/bit growth must be paid')
    else:
        domain_note = 'field/ring compatibility retained at every outer level'
    return {'order_sequence': f'n_t={leaf.order}*{outer.order}^t',
            'product_sequence': f'C_t={leaf.products}*{outer.products}^t',
            'denominator_sequence': f'D_t={leaf.denominator}*{outer.denominator}^t',
            'arithmetic_product_exponent_expression': f'log({outer.products})/log({outer.order})',
            'display_only_exponent_approximation': math.log(outer.products)/math.log(outer.order),
            'terminal_is_fixed_and_never_reused_as_outer': True,
            'domain_note': domain_note,
            'new_matrix_exponent_claim': False, 'integer_bit_complexity_or_kappa_claim': False}


def fringe(kernel: Candidate, n):
    p = kernel.order
    if n < 1 or kernel.product_slots > p**3:
        raise Ineligible('fringe needs positive size and a kernel no worse than cubic')
    q = n//p
    outside = n**3-q**3*p**3
    return replace(kernel,order=n,product_slots=outside+q**3*kernel.product_slots,
                   exact_output_quotients=q**3*kernel.exact_output_quotients,
                   fixed_output_inverse_scalings=q**3*kernel.fixed_output_inverse_scalings,
                   route='fringe: scalar-index block replacement, no recursive block use of mixed kernel',
                   kernel_order=p,kernel_invocations=q**3,classical_fringe_products=outside)


def padded(kernel: Candidate, n):
    q = (n+kernel.order-1)//kernel.order
    return replace(kernel,order=n,product_slots=q**3*kernel.product_slots,
                   exact_output_quotients=q**3*kernel.exact_output_quotients,
                   fixed_output_inverse_scalings=q**3*kernel.fixed_output_inverse_scalings,
                   route='padding: every padded kernel slot paid; no unsupplied zero pruning',
                   kernel_order=kernel.order,kernel_invocations=q**3,
                   padded_order=q*kernel.order)


def factor_candidates(n, target, model='scheduled_products', allow_charged_lift=False):
    if n < 1:
        raise Ineligible('positive matrix order required')
    result = []
    def visit(remaining, chain):
        leaves = [terminal('classical',remaining)]
        if remaining >= 2 and remaining % 2 == 0:
            leaves.append(terminal('rosowski_even',remaining))
        if remaining == 16:
            leaves.append(terminal('personal16',16))
        for leaf in leaves:
            try:
                result.append(compose(chain,leaf,target,model,allow_charged_lift))
            except Ineligible:
                pass
        for name in ('strassen2','dps4'):
            order = catalogue()[name].order
            if remaining % order == 0 and remaining >= order:
                visit(remaining//order,chain+(name,))
    visit(n,())
    return sorted(result,key=lambda x:(x.product_slots,x.denominator,x.outers,x.terminal))


def search(n, target, model='scheduled_products', allow_charged_lift=False):
    result = factor_candidates(n,target,model,allow_charged_lift)
    # Explicit finite set, not a globally exhaustive algorithm catalogue.
    for p in (2,4,8,12,16,24,32):
        kernels = factor_candidates(p,target,model,allow_charged_lift)
        if not kernels:
            continue
        kernel = kernels[0]
        if p <= n:
            result.append(fringe(kernel,n))
        result.append(padded(kernel,n))
    return sorted(result,key=lambda x:(x.product_slots,x.denominator,x.route))


def recover_lifted(residue, denominator, modulus):
    if denominator < 1 or modulus < 2 or not 0 <= residue < denominator*modulus:
        raise Ineligible('invalid lifted residue interval')
    if residue % denominator:
        raise Ineligible('scaled-image certificate absent: residue not divisible by denominator')
    return (residue//denominator) % modulus


def paired_leaf(order):
    """Actual even-order division-free Rosowski scalar recipe, integer forms."""
    if order < 2 or order % 2:
        raise Ineligible('this executable paired recipe requires even order')
    n = order
    A = lambda i,j: i*n+j
    B = lambda i,j: n*n+i*n+j
    gates, outputs = [], [dict() for _ in range(n*n)]
    def form(*variables):
        result = {}
        for index,coefficient in variables:
            result[index] = result.get(index,0)+coefficient
        return {i:c for i,c in result.items() if c}
    def gate(left,right,uses):
        index = len(gates); gates.append((left,right))
        for output,coefficient in uses.items():
            outputs[output][index] = coefficient
    for i in range(n):
        for h in range(n//2):
            u,v = 2*h,2*h+1
            gate(form((A(i,u),1)),form((B(u,0),1),(A(i,v),1)),
                 {i*n:1,**{i*n+j:-1 for j in range(1,n)}})
            gate(form((A(i,v),1)),form((B(v,0),1),(A(i,u),-1)),{i*n:1})
    for h in range(n//2):
        u,v = 2*h,2*h+1
        for j in range(1,n):
            gate(form((B(v,j),1)),form((B(u,0),1),(B(u,j),1)),
                 {i*n+j:-1 for i in range(n)})
    for i in range(n):
        for h in range(n//2):
            u,v = 2*h,2*h+1
            for j in range(1,n):
                gate(form((A(i,u),1),(B(v,j),1)),
                     form((A(i,v),1),(B(u,0),1),(B(u,j),1)),{i*n+j:1})
    if len(gates) != W(n):
        raise Ineligible('paired leaf scheduled count mismatch')
    return gates, outputs


def verify_paired_leaf(n):
    gates, outputs = paired_leaf(n)
    checked = cancelled = 0
    for output, uses in enumerate(outputs):
        polynomial = {}
        for g,weight in uses.items():
            left,right = gates[g]
            for a,ca in left.items():
                for b,cb in right.items():
                    term = tuple(sorted((a,b)))
                    polynomial[term] = polynomial.get(term,0)+weight*ca*cb
        cancelled += sum(c == 0 for c in polynomial.values())
        polynomial = {t:c for t,c in polynomial.items() if c}
        i,j = divmod(output,n)
        target = {(i*n+k,n*n+k*n+j):1 for k in range(n)}
        if polynomial != target:
            raise Ineligible('mixed-input leaf polynomial mismatch, including same-bank terms')
        checked += len(target)
    return {'order':n,'gates':len(gates),'outputs':n*n,
            'expected_mixed_terms':checked,'zero_terms_cancelled':cancelled,
            'commutative_polynomial_identity':True,'bilinear_gate_decomposition':False}


def evaluate_numerator(outer_names, leaf, left, right, modulus=None):
    """Concrete integral numerator interpreter, preserving the factor lineage.

    No intermediate division. Ordered bilinear outers multiply the terminal
    numerator scale once per level. The mixed recipe runs on scalar entries.
    Instrumentation counts actual scheduled product slots, including zero
    products at particular inputs. This interpreter is independently controlled
    against ordinary matrix multiplication in audit_catalogue.py.
    """
    validate_catalogue_coefficients(); validate_terminal(leaf)
    registry = catalogue()
    if any(name not in registry or not registry[name].block_stable for name in outer_names):
        raise Ineligible('numeric recursive outer lacks a registered block-stable certificate')
    n = len(left)
    expected_n = leaf.order*math.prod(registry[name].order for name in outer_names)
    if n != expected_n or len(right) != n or any(len(row)!=n for row in left+right):
        raise Ineligible('numeric input shape does not match typed factor lineage')
    if any(type(value) is not int for matrix in (left,right) for row in matrix for value in row):
        raise Ineligible('integer numerator interpreter requires integer representatives')
    if modulus is not None and modulus < 2:
        raise Ineligible('invalid numerator ring modulus')
    def reduce(value):
        return value % modulus if modulus is not None else value
    def run(chain, recipe, A, B):
        m = len(A)
        if not chain:
            if recipe.name == 'personal16':
                # Same actual 48x46 construction, without importing donor code.
                return run(('dps4',),terminal('rosowski_even',4),A,B)
            if recipe.name.startswith('classical'):
                out = [[reduce(sum(A[i][k]*B[k][j] for k in range(m))) for j in range(m)] for i in range(m)]
                return out,1,m**3
            gates,outputs = paired_leaf(m)
            values = [v for row in A for v in row]+[v for row in B for v in row]
            products = []
            for lhs,rhs in gates:
                lv=reduce(sum(c*values[i] for i,c in lhs.items()))
                rv=reduce(sum(c*values[i] for i,c in rhs.items()))
                products.append(reduce(lv*rv))
            flattened = [reduce(sum(c*products[g] for g,c in uses.items())) for uses in outputs]
            return [flattened[i*m:(i+1)*m] for i in range(m)],1,len(gates)
        outer = registry[chain[0]]
        if not outer.block_stable:
            raise Ineligible('numeric recursive outer is not block stable')
        a=outer.order; b=m//a
        alpha,beta,gamma = strassen_tables() if outer.name=='strassen2' else outer48_tables()
        def block_forms(matrix, coefficients):
            return [[reduce(sum(coefficients[oi*a+oj]*matrix[oi*b+i][oj*b+j]
                                 for oi in range(a) for oj in range(a)))
                     for j in range(b)] for i in range(b)]
        products=[]; count=0; scales=set()
        for ca,cb in zip(alpha,beta):
            X=block_forms(A,ca);Y=block_forms(B,cb)
            value,scale,slots=run(chain[1:],recipe,X,Y)
            products.append(value);count+=slots;scales.add(scale)
        if len(scales)!=1:
            raise Ineligible('nonuniform terminal numerator scales')
        out=[[0]*m for _ in range(m)]
        for oi in range(a):
            for oj in range(a):
                for i in range(b):
                    for j in range(b):
                        out[oi*b+i][oj*b+j]=reduce(sum(gamma[t][oi*a+oj]*products[t][i][j]
                                                     for t in range(outer.products)))
        return out,outer.denominator*scales.pop(),count
    numerator,denominator,slots=run(tuple(outer_names),leaf,left,right)
    return {'numerator':numerator,'denominator':denominator,'scheduled_product_slots':slots,
            'numerator_ring_modulus':modulus,'intermediate_divisions':0}


def community_gate(path=None):
    path = Path(path or HERE/'inputs/community-pr48-certificate.json')
    if sha(path) != COMMUNITY_SHA:
        raise Ineligible('community source certificate hash changed')
    data = json.loads(path.read_text())
    ab = Fraction(data['assembly']['parameters']['a_bit'])
    ac = Fraction(data['assembly']['parameters']['a_complex'])
    k = Fraction(data['kappa'])
    ceiling = Fraction(data['assembly']['scoped_limit'])
    if not k < ceiling < ab < ac:
        raise Ineligible('assumed source bottleneck order failed')
    return {'source_commit':COMMUNITY_PIN,'source_sha256':sha(path),
            'bit_saving':str(ab),'complex_saving':str(ac),'conditional_kappa':str(k),
            'scoped_assembly_limit':str(ceiling),'binding_component':'bit network / assembly absorption',
            'complex_precision_only_implies_new_kappa':False,
            'matrix_slot_count_is_a_bit_interchange_profile':False,
            'required_for_kappa_eligibility':['actual admissible bit/complex child list',
                'exact moments and physical frame/dirty endpoint contracts',
                'all inherited analytic/tape interfaces and new strict assembly margins'],
            'use_of_matrix_results':'typed composition, integer image/late quotient and coefficient audit infrastructure'}


def excluded_catalogue():
    return [
        {'order':9,'reported_outer_products':486,'status':'cited historical exact audit; no coefficient adapter imported',
         'source':'personal manuscript section 9; Perminov source pin 3183c54c754b60311edb1947417bc6060bc04db1'},
        {'order':27,'advertised_outer_products':10045,'downloaded_active_products_reported':10250,
         'status':'quarantined count/artifact discrepancy; no promoted candidate',
         'source':'personal manuscript section 6'},
        {'order':3,'products':23,'support_upper_bound':138,
         'status':'Chandragupt Sharma family; Alejandro formal audit; no coefficient adapter imported',
         'source':f'https://github.com/alejandrozu/openmath-2026-judging/tree/{MATRIX_PIN}/chandra-support138-family-2026-10-07'},
        {'recipe':'odd-order W(b)','status':'published formula comparator only; executable odd leaf not supplied here',
         'source':'Rosowski as cited by the personal manuscript'}]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--order',type=int,default=16)
    ap.add_argument('--domain',default='Q')
    ap.add_argument('--model',choices=sorted(MODELS),default='scheduled_products')
    ap.add_argument('--allow-charged-lift',action='store_true')
    ap.add_argument('--top',type=int,default=12)
    args = ap.parse_args()
    # Validate the supplied coefficient artifacts before admitting their counts.
    checks = validate_catalogue_coefficients()
    target = Domain.parse(args.domain)
    candidates = search(args.order,target,args.model,args.allow_charged_lift)
    report = {'status':'completed_local_finite_catalogue_search',
              'matrix_source_commit':MATRIX_PIN,'proof_source_commit':PROOF_PIN,
              'ordered_outer_checks':checks,
              'target':target.label,'requested_model':args.model,
              'eligible_recorded_candidates':len(candidates),
              'top_candidates':[c.to_dict() for c in candidates[:args.top]],
              'excluded_or_unreplayed_catalogue':excluded_catalogue(),
              'community_eligibility_gate':community_gate(),
              'best_only_within_this_supplied_catalogue':True,
              'no_remote_write':True,'no_new_kappa_or_exponent_claim':True}
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
