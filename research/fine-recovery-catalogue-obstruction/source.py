"""Authenticate complete source bytes and inspect the named AST bindings.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
AST inspection is not execution, a Count emulator or a physical replay.
"""
import ast
from hashlib import sha1, sha256
import json
from pathlib import Path
from textwrap import dedent

from audit import need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = "research/physical-gaussian-tensor/tensor_plan.py"
CATALOGUE = "research/physical-gaussian-tensor/tensor_catalogue.py"
SANDWICH = "research/physical-tensor-crt-sandwich-recovery/sandwich.py"
BOUNDARY = "research/arbitrary-bit-sandwich/boundary.py"
SIGNED = "research/physical-ring-product/ring_words.py"
FIXED = "research/physical-complex-compact/compact_counts.py"


def authenticate():
    counts = []
    for filename in ("SOURCES.json", "DEPENDENCIES.json"):
        rows = json.loads((HERE / filename).read_text())["files"]
        for row in rows:
            path = ROOT / row["path"]
            need(path.is_file() and not path.is_symlink(), "regular exact source input")
            raw = path.read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "source SHA-256: " + row["path"])
            need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"],
                 "source Git blob: " + row["path"])
        counts.append(len(rows))
    return counts


def method(tree, class_name, name):
    node = tree
    if class_name is not None:
        matches = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == class_name]
        need(len(matches) == 1, "unique source class")
        node = matches[0]
    matches = [x for x in node.body if isinstance(x, ast.FunctionDef) and x.name == name]
    need(len(matches) == 1, "unique source function")
    return matches[0]


def contains(node, snippet, count=None):
    targets = ast.parse(dedent(snippet)).body
    dumps = [ast.dump(x, include_attributes=False) for x in ast.walk(node)]
    for target in targets:
        number = dumps.count(ast.dump(target, include_attributes=False))
        need(number > 0 if count is None else number == count,
             "source AST obligation: " + snippet.strip().splitlines()[0])


def contracts(texts):
    trees = {path: ast.parse(texts[path]) for path in (PLAN, CATALOGUE, SANDWICH, BOUNDARY, SIGNED, FIXED)}
    sites = 0
    def check(path, owner, name, snippet, count=None):
        nonlocal sites
        contains(method(trees[path], owner, name), snippet, count)
        sites += len(ast.parse(dedent(snippet)).body)
    check(PLAN, "TensorPlan", "__init__", '''
        self.keep("dimensions", Count(axes))
        self.dimensions.increment()
        self.keep("d", Count(self.dimensions))
        self.d.increment()
        self.keep("u", Count.product(alpha, alpha))
        self.keep("component_bits", Count(p))
        self.keep("record_bits", Count(self.component_bits))
        self.record_bits.multiply_small(2)
    ''')
    check(PLAN, "TensorPlan", "__init__", "self.component_bits.increment()", 2)
    check(PLAN, "TensorPlan", "__init__", '''
        if production:
            self.production_axis(s, t)
        if production:
            self.production_common()
    ''')
    check(PLAN, "TensorPlan", "production_axis", '''
        with owned(Count.product(self.d, gap)) as (lower,):
            lower.multiply_small(4)
            need(compare(lower, s) > 0, "production tensor strict lower ratio")
    ''')
    check(PLAN, "TensorPlan", "production_common", '''
        with owned(Count(self.p)) as (eight_p,):
            eight_p.multiply_small(8)
            with owned(ceiling_log(eight_p)) as (minimum,):
                need(compare(self.u, minimum) >= 0, "production tensor logarithmic concentration")
        with owned(Count.product(self.u, self.d), Count(self.w)) as (weighted, separated):
            separated.multiply_small(4)
            separated.increment()
            separated.increment()
            need(compare(weighted, self.p) <= 0 and compare(self.d, separated) > 0,
                 "production tensor similarity and cell separation")
    ''')
    check(CATALOGUE, "Catalogue", "__init__", '''
        self.plan = TensorPlan(sources, flags, header.axes, header.ell, header.p,
            header.alpha, header.inner_bits, header.P, header.sigma, header.radius,
            header.expansion_capacity, header.halo, header.w, factory,
            production=not header.mode.zero())
    ''')
    run = method(trees[SANDWICH], "Sandwich", "run")
    need(run.args.args[-1].arg == "require_recovery" and
         isinstance(run.args.defaults[-1], ast.Constant) and run.args.defaults[-1].value is True,
         "default mandatory recovery policy")
    sites += 1
    check(SANDWICH, "Sandwich", "run", '''
        book=Catalogue(catalogue,self.pool.acquire)
        plan=book.plan
        if require_recovery:
            self.admit(plan,b)
    ''')
    check(SANDWICH, "Sandwich", "admit", '''
        need(not plan.mode.zero(),'production coefficient/locality contract required')
    ''')
    check(BOUNDARY, "ArbitraryBits", "invoke", '''
        result = self.child.run(*self.packed, catalogue, b, q)
    ''')
    check(SANDWICH, "Sandwich", "ingress", '''
        for _ in indices(plan.source_product):
            magnitude=read_fixed(source,b) if compare(index,q)<0 else Count.literal(0)
            with owned(Signed(magnitude),Signed(Count.literal(0))) as (digit,zero):
                with owned(scaled(digit,amount)) as (value,):
                    write_signed(value,out,plan.component_bits)
                    write_signed(zero,out,plan.component_bits)
            index.increment()
    ''')
    check(SIGNED, None, "write_signed", '''
        if value.negative:
            with owned(power_two(width)) as (modulus,):
                with owned(subtract(modulus, value.magnitude)) as (encoded,):
                    write_fixed(encoded, destination, width)
        else:
            write_fixed(value.magnitude, destination, width)
    ''')
    check(FIXED, None, "write_fixed", '''
        remaining = Counter(width)
        while not remaining.finished:
            ended = value.read() == RIGHT
            bit = ZERO if ended else value.read()
            need(bit in (ZERO, ONE), "fixed-width key digit")
            target.append(bit)
            if not ended:
                value.step(1)
            remaining.decrement()
    ''')
    check(SANDWICH, "Sandwich", "recover", '''
        with owned(self.arithmetic.multiply(real,S,width)) as (once,):
            with owned(self.arithmetic.multiply(once,S,width)) as (twice,):
                with owned(scaled(twice,shift)) as (numerator,):
                    with owned(nearest(numerator,plan.p)) as (integer,):
                        write_signed(integer,out,width)
    ''')
    check(SANDWICH, "Sandwich", "recover", '''
        shift.multiply_small(2)
        for _ in range(4):
            shift.increment()
    ''')
    check(PLAN, "TensorPlan", "__init__", '''
        with owned(Count(p)) as (scaled,):
            scaled.multiply_small(32)
            self.keep("j", ceiling_log(scaled))
        with owned(Count(self.u)) as (scale,):
            scale.multiply_small(2)
            scale.add(self.j)
            scale.increment()
            self.keep("gamma", Count.product(self.dimensions, scale))
    ''')
    check(SANDWICH, "Sandwich", "admit", '''
        with owned(Count.product(plan.p,plan.p),power_two(plan.outer_bits),Count(plan.dimensions)) as (p2,M,extra):
            with owned(Count.product(plan.dimensions,p2)) as (E,):
                M.multiply_small(6)
                E.add(M)
                extra.multiply_small(2)
                E.add(extra)
                with owned(Count.literal(22)) as (constant,):
                    E.add(constant)
                with owned(Signed(Count(E))) as (signedE,):
                    with owned(scaled(signedE,plan.gamma)) as (restored,):
                        restored.magnitude.multiply_small(3)
                        with owned(Count.literal(2)) as (two,):
                            restored.magnitude.add(two)
                        with owned(Count.product(plan.source_product,plan.source_product)) as (S2,):
                            with owned(Count.product(restored.magnitude,S2),Count(b)) as (bound,shift):
                                shift.multiply_small(2)
                                for _ in range(5):
                                    shift.increment()
                                with owned(Signed(Count(bound))) as (signed,):
                                    with owned(scaled(signed,shift),power_two(plan.p)) as (numerator,denominator):
                                        need(compare(numerator.magnitude,denominator)<0,'strict integer recovery error guard')
    ''')
    return sites


def source_controls():
    texts = {path: (ROOT / path).read_text() for path in (PLAN, CATALOGUE, SANDWICH, BOUNDARY, SIGNED, FIXED)}
    sites = contracts(texts)
    mutations = [
        (PLAN, 'self.keep("d", Count(self.dimensions))', 'self.keep("d", Count(self.p))', "spacing_dimension_link"),
        (PLAN, 'self.keep("u", Count.product(alpha, alpha))', 'self.keep("u", Count(alpha))', "squared_alpha"),
        (PLAN, 'lower.multiply_small(4)', 'lower.multiply_small(2)', "lower_ratio_factor"),
        (PLAN, 'eight_p.multiply_small(8)', 'eight_p.multiply_small(4)', "concentration_factor"),
        (PLAN, 'compare(weighted, self.p) <= 0', 'compare(weighted, self.P) <= 0', "external_precision_field"),
        (PLAN, 'self.keep("component_bits", Count(p))', 'self.keep("component_bits", Count(alpha))', "external_record_width"),
        (CATALOGUE, 'production=not header.mode.zero()', 'production=False', "catalogue_reconstructs_production"),
        (SANDWICH, 'require_recovery=True', 'require_recovery=False', "default_recovery_policy"),
        (SANDWICH, "need(not plan.mode.zero(),'production coefficient/locality contract required')", "need(True,'production coefficient/locality contract required')", "production_mode_required"),
        (SANDWICH, 'self.arithmetic.multiply(once,S,width)', 'self.arithmetic.multiply(once,plan.target_product,width)', "both_original_source_factors"),
        (SANDWICH, 'scaled(signedE,plan.gamma)', 'scaled(signedE,plan.p)', "actual_gamma_error_guard"),
        (FIXED, 'target.append(bit)', 'target.append(ONE)', "fixed_word_payload"),
    ]
    rejected = []
    for path, old, new, name in mutations:
        need(old in texts[path], "available mutation site")
        changed = dict(texts)
        changed[path] = changed[path].replace(old, new, 1)
        # Deliberately bypass byte authentication: the AST obligations must reject.
        try:
            contracts(changed)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("unrejected source mutation: " + name)
    return {"AST_sites": sites, "source_mutations_rejected": rejected,
            "source_projection_execution": False,
            "physical_runtime_execution": False}
