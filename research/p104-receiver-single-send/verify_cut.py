"""Four rational inputs and a directed tariff bound. apoursh with OpenAI Codex, Apache-2.0."""
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require

OLD_IN, OLD_OUT, RECEIVER = 95914, 88, 127
INPUTS = (
    {674: 1, 722: 1},
    {722: 1, 780: -1},
    {674: 1, 825: -1},
    {674: 1, 722: 1, 1288: -F(1, 845660160)},
)


def binary_rank(frame):
    pivots = {}
    for label in frame:
        require(0 < label < 512, 'frame outside the ambient binary space')
        while label:
            top = label.bit_length()
            if top not in pivots:
                pivots[top] = label
                break
            label ^= pivots[top]
    return len(pivots)


def live_on_input(word, rows, routes, terminal, public):
    values = {~j: public.get(j, 0) for j in range(len(word['initial']))}
    detected = {word['initial'][j] for j, x in public.items() if x}
    retained = [k for k, (_, b) in routes.items() if b == RECEIVER and k != OLD_OUT]
    for k in word['schedule']:
        if k not in routes and k != terminal:
            continue
        values[k] = sum(q * values[s] for s, q in rows[k].items())
        if k in routes and k not in (OLD_IN, OLD_OUT) and values[k]:
            detected.add(routes[k][1])
    require(len(retained) == 901 and all(values[k] == 0 for k in retained),
            'all surviving receiver inputs must vanish')
    require(values[terminal] == values[OLD_OUT] == 1, 'unit output separation')
    return detected


def log_box(d):
    # log(d) = 2 * atanh((d-1)/(d+1)). Bound the tail by a geometric series.
    x = F(d - 1, d + 1)
    power = x
    low = F(0)
    for k in range(180):
        low += 2 * power / (2*k + 1)
        power *= x*x
    high = low + 2 * power / (361 * (1-x*x))
    scale = 10**50
    return F(low*scale // 1, scale), F(-((-high*scale) // 1), scale)


def alternating_exp(z):
    # At 0 <= z < 1 the odd/even partial sums enclose exp(-z).
    require(0 <= z < 1, 'alternating exponential bounds')
    term = partial = F(1)
    for j in range(1, 16):
        term *= -z / j
        partial += term
    return partial, partial - term*z/16


def price_box(d, kappa=F('0.00387981257853')):
    low_log, high_log = log_box(d)
    return (d*alternating_exp(kappa*high_log/4)[0]**4,
            d*alternating_exp(kappa*low_log/4)[1]**4)


def main():
    word, rows, routes, terminals = read_word()
    check_causality(word, rows, routes, terminals)
    require(routes[OLD_IN] == (278, 288) and routes[OLD_OUT] == (288, RECEIVER),
            'incumbent routes')
    require([k for k, row in rows.items() if OLD_IN in row] == [OLD_OUT] and
            {k for k, row in rows.items() if OLD_OUT in row} == {155442, 155490},
            'only the two terminals see these removed rows downstream')
    require(all(a != RECEIVER for a,b in routes.values()) and
            RECEIVER not in word['initial'], 'no receiver egress or initial input')
    rank = [binary_rank(fr) for fr in word['frames']]
    require(len(rank) == 1103 and all(d == len(fr) for d, fr in zip(rank, word['frames'])),
            'span dimension for every potential donor')
    require(rank[RECEIVER] == 9 and [rank[h] for h in (11,58,278,288,138)] == [1,1,2,4,8],
            'actual chart dimensions')
    require(binary_rank(word['frames'][278] + word['frames'][288]) == 4,
            'the grade-two incumbent transfer has nested endpoint frames')

    hits = [live_on_input(word,rows,routes,155442,public) for public in INPUTS]
    require(hits[0] == {11,58,278}, 'three possible senders at the first witness')
    require(11 not in hits[1] and 58 not in hits[2] and 278 not in hits[3],
            'separate each remaining individual sender')
    require([min(9-rank[h] for h in hit) for hit in hits] == [7,1,1,5],
            'grade floors of the four observations')
    require(all(RECEIVER not in hit for hit in hits), 'complete receiver indistinguishability')
    # The case split in the proof can also be recovered as a shortest weighted
    # set cover on the four tests. A chart need only be used once in this bound.
    lo = {0:F(0)}
    prices = {d:price_box(d) for d in range(1,10)}
    for h,d in enumerate(rank):
        mask = sum((h in hit) << j for j,hit in enumerate(hits))
        if not mask:
            continue
        weight = prices[9-d][0]
        for old, cost in list(lo.items()):
            new = old | mask
            candidate = cost + weight
            if new not in lo or candidate < lo[new]:
                lo[new] = candidate
    require(lo[15] == prices[8][0]+prices[1][0] and
            prices[7][0]+prices[5][0] > prices[8][1]+prices[1][1],
            'minimum four-witness cover')
    low = 48 * (lo[15]-prices[2][1]-prices[5][1])
    high = 48 * (prices[8][1]+prices[1][1]-prices[2][0]-prices[5][0])
    unit = 10**24
    # Locate the unique price crossover for power tariffs on (0,1].
    for exponent, sign in ((F('0.25985761'), -1), (F('0.25985762'), 1)):
        box = {d: price_box(d, 1-exponent) for d in (2,5,8)}
        left = 1 + box[8][0] - box[2][1] - box[5][1]
        right = 1 + box[8][1] - box[2][0] - box[5][0]
        require(right < 0 if sign < 0 else left > 0, 'power crossover bracket')
    print('PASS 1103 charts, 901 retained deposits, 4 tests; live counts',
          [len(h) for h in hits], 'least possible grades 8 + 1')
    print('48-call paid increase times 10^24 lies between',
          low*unit//1, 'and', -((-high*unit)//1))
    require(low > F('94.666202960674077138503464') and
            high < F('94.666202960674077138503465'),
            'signed price comparison')


if __name__ == '__main__':
    main()
