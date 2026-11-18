"""Exact source-domain checks. JoyboyBrian with OpenAI Codex assistance; Apache-2.0."""
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(value, label):
    if not value:
        raise ValueError(label)


def reject(action, label):
    try:
        action()
    except ValueError:
        return
    raise ValueError('control accepted: ' + label)


def authenticate(data, row):
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source sha256')
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source git blob')


def product(p, q):
    return ((1-p)*(1-q), (1-p)*q, p*(1-q), p*q)


def signed_law(s):
    q, r = divmod(s, 52)
    return q, Fraction(r, 52)


def verify_basis(columns):
    pairs = list(zip(*columns[:2]))
    require(pairs[2] == (1, 0) and pairs[12] == (0, 1), 'unit minor')
    exclusive = [[i for i, pair in enumerate(pairs)
                  if pair[axis] and not pair[1-axis]] for axis in range(2)]
    require([len(v) for v in exclusive] == [32, 32], 'exclusive owner supply')
    return exclusive


def owner_for_pair(a, b, columns, exclusive):
    owner = [0] * 112
    for axis, residue in enumerate((a, b)):
        target = residue if residue < 26 else residue - 52
        for i in exclusive[axis][:abs(target)]:
            owner[i] = (1 if target > 0 else -1) * columns[axis][i]
    return owner


def run_source(code, columns, owner):
    ns = {}
    exec(compile(code, 'authenticated-kernel.py', 'exec'), ns)
    bound = max(map(abs, owner))
    width = ns['word_width'](bound)
    words = [ns['encode'](v, width) for v in owner]
    scratch = [[0] * width for _ in range(9)]
    numerators = [sum(c*x for c, x in zip(col, owner)) for col in columns]
    owner_ids = {id(w) for w in words}
    rounds = []
    raw_add, raw_round, raw_clear = ns['add_into'], ns['round52_into'], ns['clear']

    def add(target, source, sign):
        if id(target) in owner_ids:
            require(len(rounds) == 8, 'early owner write')
        raw_add(target, source, sign)

    def clear(word):
        require(id(word) not in owner_ids or len(rounds) == 8, 'early owner clear')
        raw_clear(word)

    def rounding(word, work):
        require([ns['decode'](w) for w in words] == owner, 'owner changed before rounding')
        if not rounds:
            require([ns['decode'](w) for w in scratch[:8]] == numerators,
                    'all original numerators available')
        rounds.append(ns['decode'](word))
        raw_round(word, work)

    ns.update(add_into=add, round52_into=rounding, clear=clear)
    ns['recode'](words, columns, bound, scratch)
    require(rounds == numerators, 'source numerators')
    # Independent rational nearest rule, including negative ties away from zero.
    rounded = [int((abs(Fraction(s, 52)) + Fraction(1, 2)) // 1)
               * (1 if s >= 0 else -1) for s in numerators]
    expected = [x - sum(col[i]*v for col, v in zip(columns, rounded))
                for i, x in enumerate(owner)]
    require([ns['decode'](w) for w in words] == expected, 'source output oracle')
    require(not any(map(any, scratch)), 'source clean scratch')
    return numerators


def main():
    source = json.loads((PACKAGE / 'SOURCES.json').read_text())
    inputs = [row for row in source['files'] if row['usage'] == 'input']
    for row in inputs:
        authenticate((ROOT / row['path']).read_bytes(), row)
    reject(lambda: authenticate(b'changed input', inputs[0]), 'source drift')
    columns = json.loads((ROOT / 'research/coded-native-caller/NORMALIZERS.json').read_text())['mode_columns']
    require(len(columns) == 8 and all(len(c) == 112 for c in columns), 'source shape')
    exclusive = verify_basis(columns)
    reject(lambda: verify_basis([columns[0], columns[0]]), 'rank collapse')
    counts = Counter(zip(*columns[:2]))
    require(counts == {(1,0):24, (0,1):24, (0,0):24, (1,1):10,
                      (1,-1):10, (-1,0):8, (0,-1):8, (-1,-1):2, (-1,1):2},
            'pair multiplicities')
    image, subclass, nonzero, adapter_branches = set(), 0, 0, 0
    for a, b in itertools.product(range(52), repeat=2):
        owner = owner_for_pair(a, b, columns, exclusive)
        require(max(map(abs, owner)) <= 1, 'H=1 witness bound')
        reached = tuple(sum(c*x for c,x in zip(col,owner)) % 52 for col in columns[:2])
        require(reached == (a,b), 'bounded source realization')
        image.add(reached)
        applicable = all((Fraction(r,52)*13).denominator == 1 for r in (a,b))
        require(applicable == (a % 4 == b % 4 == 0), 'exact denominator13 subclass')
        subclass += applicable
        nonzero += applicable and a != 0 and b != 0
        # Enumerate independent two-bit selectors; conditional tables must have
        # the product law. This checks the adapter contract, not a physical sampler.
        mixture = [Fraction(0)]*4
        for u, v in itertools.product(range(4), repeat=2):
            pa = Fraction(a//4 + (u < a%4), 13)
            pb = Fraction(b//4 + (v < b%4), 13)
            require(0 <= pa <= 1 and 0 <= pb <= 1, 'conditional endpoints')
            for k, p in enumerate(product(pa,pb)):
                mixture[k] += p/16
            adapter_branches += 1
        require(tuple(mixture) == product(Fraction(a,52),Fraction(b,52)), 'adapter joint law')
    require((len(image),subclass,nonzero,adapter_branches) == (2704,169,144,43264), 'domain totals')
    signed_cases = 0
    for s in range(-208,209):
        q,p = signed_law(s)
        require(q+p == Fraction(s,52), 'unbiased signed reconstruction')
        magq,rho = divmod(abs(s),52)
        magnitude_law = {magq: 1-Fraction(rho,52), magq+1: Fraction(rho,52)}
        signed = {(-v if s < 0 else v): prob for v,prob in magnitude_law.items() if prob}
        floor = {v: prob for v,prob in {q:1-p,q+1:p}.items() if prob}
        require(signed == floor, 'signed magnitude/floor equivalence')
        signed_cases += 1
    require(signed_law(1) == (0,Fraction(1,52)), 'positive minimal witness')
    require(signed_law(-1) == (-1,Fraction(51,52)), 'negative minimal witness')
    reject(lambda: require(Fraction(1//4,13) == Fraction(1,52), 'dropped low bits'), 'dropped low bits')
    reject(lambda: require(Fraction(abs(-1)%52,52) == signed_law(-1)[1], 'wrong signed flag'), 'wrong signed flag')
    reject(lambda: require(Fraction(1,52) == Fraction(1,52)**2, 'shared output flag'), 'false independence')
    reject(lambda: require(Fraction(1,4)*Fraction(1,13)**2 == Fraction(1,52)**2,
                           'shared selector'), 'shared selector')
    code = (ROOT / 'research/coded-inverse-fixed-grid/kernel.py').read_text()
    fixtures = []
    for value in (0,1,-1,4,-4,25,-25,26,-26,27,-27):
        fixtures.append([value]+[0]*111)
    fixtures.extend(owner_for_pair(a,b,columns,exclusive) for a,b in ((1,51),(26,26),(51,1)))
    for owner in fixtures:
        run_source(code, columns, owner)
    first = json.loads((ROOT / 'research/coded-inverse-fixed-grid/FIRST-FIXTURE.json').read_text())
    require(run_source(code, columns, [4]+[0]*111) == first['mode_numerators'], 'first source fixture')
    marker = '    for column, target in zip(mode_columns, modes):'
    require(code.count(marker) == 1, 'mutation anchor')
    early = code.replace(marker, '    clear(owner_words[0])\n'+marker)
    reject(lambda: run_source(early,columns,[1]+[0]*111), 'early owner write')
    drop_low = code.replace('4 * remainder + low >= 26', '4 * remainder >= 26')
    require(drop_low != code, 'low-bit mutation anchor')
    reject(lambda: run_source(drop_low,columns,[26]+[0]*111), 'source low-bit deletion')
    result = {'status':'PASS_INVERSE_RESIDUE_DOMAIN','source_inputs':len(inputs),
              'residue_pairs':len(image),'H1_realizations':len(image),
              'denominator13_pairs':subclass,'nonzero_table_pairs':nonzero,
              'adapter_branches':adapter_branches,'signed_cases':signed_cases,
              'kernel_fixtures':len(fixtures)+1,'rejection_controls':8}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
