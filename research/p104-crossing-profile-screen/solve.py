"""Optional exact simplex proposal generator. Replay never imports this file.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import verify as v


def solve(a, b, costs):
    m, n = len(a), len(b)
    table = [[Q(x) for x in row] + [Q(i == j) for j in range(m)] + [Q(c)]
             for i, (row, c) in enumerate(zip(a, costs))]
    objective = [-Q(x) for x in b] + [Q(0)]*(m+1)
    basic = list(range(n, n+m))
    for _ in range(1000):
        entering = next((j for j in range(n+m) if objective[j] < 0), None)
        if entering is None:
            y = [Q(0)]*n
            for i, index in enumerate(basic):
                if index < n:
                    y[index] = table[i][-1]
            x = {str(i): str(objective[n+i]) for i in range(m) if objective[n+i]}
            return {'dual': list(map(str, y)), 'primal': x}
        eligible = [i for i in range(m) if table[i][entering] > 0]
        if not eligible:
            raise ValueError('unbounded proposal LP')
        leaving = min(eligible, key=lambda i: (table[i][-1]/table[i][entering], basic[i]))
        pivot = table[leaving][entering]
        table[leaving] = [x/pivot for x in table[leaving]]
        row = table[leaving]
        for i in range(m):
            if i != leaving and table[i][entering]:
                factor = table[i][entering]
                table[i] = [x-factor*y for x, y in zip(table[i], row)]
        factor = objective[entering]
        objective = [x-factor*y for x, y in zip(objective, row)]
        basic[leaving] = entering
    raise ValueError('bounded proposal pivot limit')


if __name__ == '__main__':
    v.authenticate()
    rows = v.histories()
    demands = [row['forced'] for row in v.demands_from_sources()]
    selected = v.read(v.ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json')
    for proper in (False, True):
        certs = {}
        for p in [Q(1), 1-Q(selected['complex_lower']), Q(98, 99)]:
            costs = [sum(v.power(r, p)[0] for r in row['jumps']) for row in rows]
            cert = solve(v.matrix(rows, proper), demands+[208], costs)
            result = v.check_certificate(cert, rows, demands, p, proper)
            print(proper, str(p), float(Q(result['lower'])), flush=True)
            certs[str(p)] = cert
        name = 'CERTIFICATES.json' if proper else 'COUNT-ONLY.json'
        Path(v.P/name).write_text(json.dumps(certs, indent=2)+'\n', encoding='utf-8')
