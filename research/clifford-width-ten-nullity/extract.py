"""Extract exact stabilizer data from the authenticated CTblLib release.

The MOT and ALF record selection extends Nick Petalas's retained parser.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parent
RESIDUES = {x*x % 17 for x in range(1, 17)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduce17(coefficients):
    return [x-coefficients[16] for x in coefficients[:16]]


def period_basis():
    t = [int(i == 0) + 2 * (i in RESIDUES) for i in range(17)]
    square = [sum(t[j]*t[(i-j) % 17] for j in range(17)) for i in range(17)]
    require(reduce17(square) == [17]+[0]*15, 'quadratic period square')
    conjugate = [t[-i % 17] for i in range(17)]
    require(conjugate == t, 'real quadratic period')
    changed = [0]*17
    for i, x in enumerate(t):
        changed[3*i % 17] = x
    require(reduce17(changed) == [-x for x in reduce17(t)], 'Galois period action')
    return reduce17(t)


PERIOD = period_basis()


def scalar(text):
    if re.fullmatch(r'-?[0-9]+', text):
        return 2*int(text), 0
    terms = re.findall(r'([+-]?)(E\(17\)(?:\^[0-9]+)?)', text)
    require(''.join(sign+term for sign, term in terms) == text, 'unsupported table scalar')
    coefficients = [0]*17
    for sign, term in terms:
        exponent = int(term.split('^')[1]) if '^' in term else 1
        coefficients[exponent % 17] += -1 if sign == '-' else 1
    vector = reduce17(coefficients)
    k = next(i for i in range(1, 16) if PERIOD[i])
    b, remainder = divmod(2*vector[k], PERIOD[k])
    require(remainder == 0, 'quadratic period coefficient')
    a = 2*vector[0]-b*PERIOD[0]
    require([a*(i == 0)+b*PERIOD[i] for i in range(16)] == [2*x for x in vector],
            'quadratic period span')
    return a, b


def multiply(x, y):
    a, b = x
    c, d = y
    first, second = a*c+17*b*d, a*d+b*c
    require(first % 2 == second % 2 == 0, 'half-integral character product')
    return first//2, second//2


def bracket(text, start):
    depth = 0
    for i in range(start, len(text)):
        depth += (text[i] == '[')-(text[i] == ']')
        if depth == 0:
            return text[start+1:i]
    raise ValueError('unbalanced table list')


def split(text):
    result, depth, start = [], 0, 0
    for i, char in enumerate(text):
        depth += (char == '[')-(char == ']')
        if char == ',' and depth == 0:
            result.append(text[start:i])
            start = i+1
    return result+[text[start:]]


def parse_table(text, name):
    marker = 'MOT("'+name+'",\n'
    require(text.count(marker) == 1, 'table record identity')
    block = text.split(marker, 1)[1].split('\nARC("'+name+'"', 1)[0]
    numbers = block.split('],\n', 1)[1]
    centralizers = json.loads(numbers.split('],\n', 1)[0]+']')
    start = block.index('\n[[1,1,1,')+1
    raw_rows = split(re.sub(r'\s+', '', bracket(block, start)))
    rows = []
    for raw in raw_rows:
        cells = split(raw[1:-1])
        if cells[0] == 'TENSOR':
            i, j = json.loads(cells[1])
            rows.append([multiply(a, b) for a, b in zip(rows[i-1], rows[j-1], strict=True)])
        elif cells[0] == 'GALOIS':
            i, power = json.loads(cells[1])
            require(power % 17 != 0, 'Galois power')
            sign = 1 if power % 17 in RESIDUES else -1
            rows.append([(a, sign*b) for a, b in rows[i-1]])
        else:
            rows.append([scalar(cell) for cell in cells])
    n = len(centralizers)
    require(len(rows) == n and all(len(row) == n for row in rows), 'character table shape')
    require(rows[0] == [(2, 0)]*n, 'trivial character row')
    order = centralizers[0]
    require(all(c > 0 and order % c == 0 for c in centralizers), 'table class centralizer')
    sizes = [order//c for c in centralizers]
    require(sum(sizes) == order, 'full class-size sum')
    require(sum((row[0][0]//2)**2 for row in rows) == order, 'degree-square sum')
    ordinary_orthogonality(rows, sizes, order)
    return rows, centralizers


def inner(left, right, sizes, order):
    real = radical = 0
    for (a, b), (c, d), size in zip(left, right, sizes, strict=True):
        real += size*(a*c+17*b*d)
        radical += size*(a*d+b*c)
    value, remainder = divmod(real, 4*order)
    require(radical == remainder == 0, 'nonintegral character inner product')
    return value


def ordinary_orthogonality(rows, sizes, order):
    for i, left in enumerate(rows):
        for j, right in enumerate(rows):
            require(inner(left, right, sizes, order) == (i == j), 'ordinary character orthogonality')


def extract(archive):
    metadata = json.loads((ROOT/'EXTERNAL.json').read_text())
    with archive.open('rb') as stream:
        raw = stream.read(20*1024*1024+1)
    require(sha256(raw).hexdigest() == metadata['archive_sha256'], 'release archive hash')
    texts = {}
    with tarfile.open(fileobj=BytesIO(raw), mode='r:gz') as tar:
        for member, digest in metadata['members'].items():
            info = tar.getmember(member)
            require(info.isfile() and 0 < info.size < 1024*1024, 'table member size')
            stream = tar.extractfile(info)
            require(stream is not None, 'table member missing')
            with stream:
                data = stream.read(info.size+1)
            require(sha256(data).hexdigest() == digest, 'table member hash')
            texts[Path(member).name] = data.decode('ascii')
    srows, scenters = parse_table(texts['ctosymp1.tbl'], 'S8(2)')
    require(len(srows) == 81 and scenters[0] == 47_377_612_800, 'symplectic table')
    dims = []
    for j in range(81):
        fixed = 2+(srows[4][j][0]+srows[5][j][0])//2
        require(srows[4][j][1] == srows[5][j][1] == 0 and fixed.bit_count() == 1,
                'symplectic fixed-vector character')
        dims.append(fixed.bit_length()-1)
    groups = []
    for kind, name, member, expected_classes in [
            ('minus', 'O8-(2).2', 'ctoorth3.tbl', 60),
            ('plus', 'O8+(2).2', 'ctoorth2.tbl', 67)]:
        rows, centralizers = parse_table(texts[member], name)
        fusion = json.loads(texts[member].split('ALF("'+name+'","S8(2)",', 1)[1].split('],', 1)[0]+']')
        require(len(rows) == len(fusion) == expected_classes, 'stabilizer table size')
        order = centralizers[0]
        sizes = [order//c for c in centralizers]
        if kind == 'minus':
            bad = [list(row) for row in rows]
            require(bad[44] != bad[45], 'distinct Galois rows')
            bad[45] = bad[44]
            try:
                ordinary_orthogonality(bad, sizes, order)
            except ValueError as error:
                require(str(error) == 'ordinary character orthogonality', 'Galois control reason')
            else:
                raise ValueError('omitted Galois action accepted')
        hdims = [dims[j-1] for j in fusion]
        require(rows[1] == [(2*(-1)**d, 0) for d in hdims], 'actual Dickson row')
        records = []
        for row in rows:
            degree = row[0][0]//2
            require(row[0][1] == 0 and row[0][0] % 2 == 0, 'integer degree')
            sums = []
            for d in range(1, 8):
                real = sum(size*value[0] for size, value, dim in zip(sizes, row, hdims, strict=True) if dim == d)
                radical = sum(size*value[1] for size, value, dim in zip(sizes, row, hdims, strict=True) if dim == d)
                require(radical == 0 and real % 2 == 0, 'rational fixed-dimension sum')
                sums.append(real//2)
            restriction = []
            for j, srow in enumerate(srows, 1):
                coefficient = inner(row, [srow[k-1] for k in fusion], sizes, order)
                require(coefficient >= 0, 'negative restriction coefficient')
                if coefficient:
                    restriction.append([j, coefficient])
            records.append({'degree': degree, 'sums_d1_to7': sums, 'restriction': restriction})
        groups.append({'kind': kind, 'table': name, 'order': order,
                       'centralizers': centralizers, 'fusion_to_S8': fusion, 'rows': records})
    return {'schema_version': 1, 'groups': groups,
            'archive_checks': {'ordinary_inner_products': 81**2+60**2+67**2,
                               'restriction_coefficients': 81*(60+67),
                               'omitted_galois_action_rejected': True,
                               'quadratic_period': 't^2=17; conjugation fixes t; Galois(3) negates t'}}
