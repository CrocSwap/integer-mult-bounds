#!/usr/bin/env python3
"""Exact finite corroboration; no predecessor executable imports. Apache-2.0."""
import argparse
import itertools
import json
from pathlib import Path
import random


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def digits(x, base, count):
    return [(x // base**i) % base for i in range(count)]


def raw(u, t, y, source, base, width, count, high=1):
    """Literal packed updates, including full-field modular wrap."""
    positions = [i * (width + 1) for i in range(count)]
    modulus = base ** (count + high)
    ymod = 1 << (count * (width + 1) + 1)
    for step in range(2):
        z = [d % 2 for d in digits(u, base, count)]
        tau = digits(t, base, count)
        y = (y + sum(2*z[i]*tau[i]*2**p for i,p in enumerate(positions))) % ymod
        t = (t + sum(((y >> p) & 1)*base**i for i,p in enumerate(positions))) % modulus
        live = digits(t, base, count)
        y = (y + sum(z[i]*(1-2*live[i])*2**p for i,p in enumerate(positions))) % ymod
        t = (t - sum((((y >> p)&1)^z[i])*base**i for i,p in enumerate(positions))) % modulus
        if step == 0:
            u = (u + sum(v*base**i for i,v in enumerate(source(y)))) % modulus
    u = (u - sum(v*base**i for i,v in enumerate(source(y)))) % modulus
    return u, t, y


def coordinates(base, width, count):
    # The terminal u digit is deliberately absent.
    return [base]*(2*count-1) + [1 << width]*(count-1)


def masks(base, width, count, phases):
    periods = coordinates(base, width, count)
    rows = []
    for j, period in enumerate(periods):
        delta = 1 if j < 2*count-1 else base-2
        bound = base-2 if j < 2*count-1 else period-base+1
        rows.append([sum(1 << k for k in range(phases)
                         if (x+k*delta) % period > bound) for x in range(period)])
    return rows


def cover_histogram(base, width, count, phases):
    distribution = {0: 1}
    for row in masks(base, width, count, phases):
        freq = {m: row.count(m) for m in set(row)}
        nxt = {}
        for a, n in distribution.items():
            for b, v in freq.items():
                nxt[a | b] = nxt.get(a | b, 0) + n*v
        distribution = nxt
    need(sum(distribution.values()) == base**(2*count-1)*(1 << width)**(count-1),
         'full product count')
    return distribution.get((1 << phases)-1, 0)


def translate(u, t, y, k, base, width, count, sign=1):
    def change(word, n):
        for i in range(n):
            d = (word // base**i) % base
            word += (((d+sign*k) % base)-d)*base**i
        return word
    u, t = change(u, count-1), change(t, count)
    mask = (1 << width)-1
    for i in range(count-1):
        p = i*(width+1)+1
        w = (y >> p) & mask
        y += (((w+sign*k*(base-2)) % (mask+1))-w) << p
    return u, t, y


def good(u, t, y, base, width, count):
    return (all(v < base-1 for v in digits(u, base, count-1))
            and all(v < base-1 for v in digits(t, base, count))
            and all(((y >> (i*(width+1)+1)) & ((1 << width)-1))
                    <= (1 << width)-base+1 for i in range(count-1)))


def ideal(y, values, width):
    for i, v in enumerate(values):
        y ^= v << (i*(width+1))
    return y


def composed(u, t, y, source, base, width, count, transport=True):
    args = base, width, count
    phase = next(k for k in range((3*count-1))
                 if good(*translate(u,t,y,k,*args),*args))
    ut, tt, yt = translate(u,t,y,phase,*args)
    def moved(word):
        return source(translate(0,0,word,phase,*args,sign=-1)[2]) if transport else source(word)
    end = raw(ut,tt,yt,moved,*args)
    out = translate(*end,phase,*args,sign=-1)
    # Selector must be unchanged on the full endpoint.
    again = next(k for k in range((3*count-1))
                 if good(*translate(*out,k,*args),*args))
    need(phase == again, 'selector restoration')
    return out


def run():
    rng = random.Random(20261106)
    hist = []
    for base, width, count in [(4,3,1),(8,5,1),(8,6,2),(16,7,3)]:
        need((3*count-1) <= base and (3*count-1)*(base-2) <= 1 << width, 'geometry')
        need(cover_histogram(base,width,count,(3*count-1)) == 0, 'complete cover')
        need(cover_histogram(base,width,count,(3*count-1)-1) > 0, 'short menu fails')
        hist.append([base,width,count])
    adversaries = 0
    for base,width,count in hist:
        periods = coordinates(base,width,count)
        for size in range(1,len(periods)+1):
            for trial in range(32):
                menu = [[rng.randrange(p) for p in periods] for _ in range(size)]
                x = [0]*len(periods)
                for k in range(size):
                    x[k] = (periods[k]-1-menu[k][k]) % periods[k]
                for k,row in enumerate(menu):
                    need((x[k]+row[k]) % periods[k] == periods[k]-1,
                         'arbitrary menu adversary')
                adversaries += 1
    exhaustive = 0
    # Every Boolean source on all 8 window values, every low control/target/window.
    for table in range(256):
        source = lambda y, table=table: ((table >> ((y >> 1)&7))&1,)
        for u,t,y in itertools.product(range(4),range(4),range(16)):
            need(composed(u,t,y,source,4,3,1) == (u,t,ideal(y,source(y),3)),
                 'all-function full-domain endpoint')
            exhaustive += 1
    sampled = 0
    saturated = 0
    wrapped = 0
    for base,width,count in [(4,3,1),(8,6,2),(16,7,3)]:
        args = base,width,count
        for case in range(2048):
            u = rng.randrange(base**(count+1))
            # Force terminal saturation and exercise both high digits and wrap.
            u += (base-1-digits(u,base,count)[-1])*base**(count-1)
            t = rng.randrange(base**(count+1))
            y = rng.randrange(1 << (count*(width+1)+1))
            def source(word):
                windows = [(word >> (i*(width+1)+1)) & ((1<<width)-1) for i in range(count)]
                return tuple((windows[(i+1)%count].bit_count() + (word >> (count*(width+1))))%2 for i in range(count))
            need(composed(u,t,y,source,*args) == (u,t,ideal(y,source(y),width)),
                 'cross-window dirty endpoint')
            # Direct guarded saturated terminal test, at exact active control width.
            ug = u % base**count
            for i in range(count-1):
                d = (ug // base**i)%base
                ug -= (d == base-1)*base**i
            tg = sum(rng.randrange(base-1)*base**i for i in range(count))
            yg = sum((rng.randrange(2)+2*rng.randrange((1<<width) if i == count-1 else (1<<width)-base+2)) << (i*(width+1)) for i in range(count))
            ones = lambda word: (1,)*count
            need(raw(ug,tg,yg,ones,*args,high=0) == (ug,tg,ideal(yg,(1,)*count,width)),
                 'terminal carry wraps harmlessly')
            saturated += 1
            wrapped += 1
            sampled += 1
    # Explicit weakened-hypothesis controls from the literal new interpreter.
    controls = {}
    controls['nonterminal_window_spill'] = raw(1,2,12,lambda y:(0,0),4,3,2)
    need(controls['nonterminal_window_spill'] != (1,2,12), 'nonterminal spill detected')
    need(raw(3,2,31,lambda y:(1,),4,3,1,high=0) == (3,2,30),
         'simultaneous full data/control wrap')
    controls['interior_source_saturation'] = raw(3,0,0,lambda y:(1,0),4,3,2)
    need(controls['interior_source_saturation'] != (3,0,1), 'interior carry detected')
    controls['temporary_saturation'] = raw(1,3,0,lambda y:(0,),4,3,1)
    need(controls['temporary_saturation'] != (1,3,0), 't saturation detected')
    controls['target_read'] = raw(1,0,0,lambda y:(y&1,),4,3,1)
    need(controls['target_read'] != (1,0,0), 'target source detected')
    # Search a fixed finite domain for a source-transport mutation witness.
    witness = None
    source = lambda y: ((y >> 2)&1, (y >> 3)&1)
    for case in range(4096):
        u,t,y = rng.randrange(512),rng.randrange(512),rng.randrange(32768)
        if composed(u,t,y,source,8,6,2,transport=False) != (u,t,ideal(y,source(y),6)):
            witness = [u,t,y]
            break
    need(witness is not None, 'source transport mutation')
    controls['missing_source_transport'] = witness
    return dict(status='PASS_TERMINAL_CARRY_GUARD_COVER', geometries=hist,
                arbitrary_menu_adversaries=adversaries, all_boolean_endpoint_cases=exhaustive, sampled_endpoint_cases=sampled,
                guarded_terminal_saturation_cases=saturated, full_control_wrap_cases=wrapped,
                controls=controls)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        args.write.write_text(encoded)
    else:
        need(encoded == Path(__file__).with_name('RESULT.json').read_text(), 'receipt mismatch')
    print(encoded,end='')


if __name__ == '__main__':
    main()
