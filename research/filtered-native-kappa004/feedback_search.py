#!/usr/bin/env python3
"""Exploratory finite feedback with actively written owned mode banks.

This searches a necessary balanced width-two sector, retaining all seven
independent stage signs. Numerical failure proves no impossibility. A hit
must pass rational reconstruction and the full physical all-width program.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse
import itertools
import json
import time
import numpy as np
import torch

HERE = Path(__file__).resolve().parent


def build(packet, scratch):
    source = json.loads((packet/'upstream/research/kappa-rebuild/bit/COMPLEX-CONTROLLER-FACTOR.json').read_text())['selected_p3_keep43']
    events = source['physical_events']
    banks = 6+scratch
    dim = 2*banks
    sectors = list(itertools.product((1., -1.), repeat=7))
    q = np.array([[0., 1.], [1., 0.]])
    eye = np.eye(dim)
    fixed, reference = [], []
    # Controls are placed before every paid macro; constant bridges are
    # absorbed by these general bank changes of basis.
    for event in events:
        kind = event[0]
        batch, standard, internal = [], [], []
        for signs in sectors:
            m, old, correction = eye.copy(), eye.copy(), np.zeros_like(eye)
            if kind == 'LOCAL':
                _, s, pair, backward = event
                x, y = 2*pair, 2*pair+1
                if backward:
                    x, y = y, x
                coupling = q*(-1 if backward else 1)
                changed = coupling.copy()
                if s == 0:
                    code = np.diag([1+14*(signs[0]-1), 1.])
                    changed = code @ coupling
                d = signs[0]*q if s == 0 else signs[s]*np.eye(2)
                for a in (m, old):
                    a[2*x:2*x+2, 2*x:2*x+2] = d
                    a[2*y:2*y+2, 2*y:2*y+2] = d
                m[2*y:2*y+2, 2*x:2*x+2] = d @ changed
                old[2*y:2*y+2, 2*x:2*x+2] = d @ coupling
                if s == 0:
                    correction[2*y:2*y+2, 2*x:2*x+2] = d @ np.diag([1., 0.]) @ d
            elif kind == 'IDLE':
                _, pair, stages = event
                d = np.eye(2)
                for s in stages:
                    d = (signs[0]*q if s == 0 else signs[s]*np.eye(2)) @ d
                for a in (m, old):
                    for b in (2*pair, 2*pair+1):
                        a[2*b:2*b+2, 2*b:2*b+2] = d
            elif kind == 'ADD':
                _, dst, src, *coef = event
                for a in (m, old):
                    a[2*dst:2*dst+2, 2*src:2*src+2] = (coef[0] if coef else 1)*np.eye(2)
            else:
                assert kind in ('SWAP', 'SIGNED_SWAP')
                _, x, y = event
                for a in (m, old):
                    a[2*x:2*x+2, 2*x:2*x+2] = 0
                    a[2*y:2*y+2, 2*y:2*y+2] = 0
                    a[2*x:2*x+2, 2*y:2*y+2] = np.eye(2)
                    a[2*y:2*y+2, 2*x:2*x+2] = -np.eye(2)
            batch.append(m)
            standard.append(old)
            internal.append(correction)
        fixed.append((kind in ('LOCAL', 'IDLE'), torch.tensor(np.array(batch), dtype=torch.float64),
                      torch.tensor(np.array(internal), dtype=torch.float64)))
        reference.append(torch.tensor(np.array(standard), dtype=torch.float64))
    initial = torch.eye(dim, dtype=torch.float64)[:, :12].repeat(128, 1, 1)
    target = initial.clone()
    for m in reference:
        target = m @ target
    return banks, fixed, initial, target[:, :12, :]


def run(packet, scratch, seed, steps, deadline, allow_internal):
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    banks, fixed, initial, target = build(packet, scratch)
    slots = 1+sum(paid for paid, _, _ in fixed)
    x = torch.nn.Parameter(.03*torch.randn(slots, banks, banks, dtype=torch.float64))
    internal = torch.nn.Parameter(torch.tensor(-14. if allow_internal else 0., dtype=torch.float64),
                                  requires_grad=allow_internal)
    variables = [x, internal] if allow_internal else [x]
    eye = torch.eye(banks, dtype=torch.float64)
    scale = max(1., float((target*target).mean()))

    def endpoint():
        a = initial
        slot = 0
        for paid, op, correction in fixed:
            if paid:
                # I+M acts only on the ordinary selected-mode projection.
                # A proposed hit is rejected if a control is singular.
                z = (eye+x[slot]) @ a[:, ::2, :]
                a = torch.stack((z, a[:, 1::2, :]), dim=2).flatten(1, 2)
                slot += 1
            a = (op+internal*correction) @ a
        z = (eye+x[slot]) @ a[:, ::2, :]
        a = torch.stack((z, a[:, 1::2, :]), dim=2).flatten(1, 2)
        return a[:, :12, :]

    opt = torch.optim.Adam(variables, lr=.025)
    best = float('inf')
    best_x = None
    best_internal = None
    iterations = 0
    for step in range(steps):
        if time.monotonic() >= deadline:
            break
        opt.zero_grad()
        residual = endpoint()-target
        loss = (residual*residual).mean()/scale
        # Small regularizer discourages large interpolation coefficients;
        # it is not included in the recorded endpoint residual.
        (loss+1e-8*(x*x).mean()).backward()
        torch.nn.utils.clip_grad_norm_(variables, 10.)
        opt.step()
        iterations += 1
        if float(loss.detach()) < best:
            best = float(loss.detach())
            best_x = x.detach().clone()
            best_internal = internal.detach().clone()
        if step % 100 == 0:
            print('SEARCH', scratch, seed, step, best, flush=True)
        if best < 1e-22:
            break
    x.data.copy_(best_x)
    internal.data.copy_(best_internal)
    if time.monotonic() < deadline:
        opt = torch.optim.LBFGS(variables, max_iter=100, tolerance_grad=1e-12,
                                tolerance_change=1e-15, line_search_fn='strong_wolfe')

        def closure():
            opt.zero_grad()
            r = endpoint()-target
            loss = (r*r).mean()/scale
            loss.backward()
            return loss

        opt.step(closure)
    residual = endpoint()-target
    maximum = float(residual.detach().abs().max())
    mean = float((residual.detach()**2).mean()/scale)
    min_singular = min(float(torch.linalg.svdvals(eye+m).min()) for m in x.detach())
    return {'scratch_banks': scratch, 'seed': seed, 'adam_iterations': iterations,
            'control_slots': slots, 'parameters': x.numel(),
            'normalized_mean_square_residual': mean, 'maximum_entry_residual': maximum,
            'minimum_control_singular_value': min_singular,
            'internal_source_feedback': allow_internal,
            'internal_feedback_coefficient': float(internal.detach()),
            'numerical_hit': maximum < 1e-9 and min_singular > 1e-8,
            'controls': x.detach().tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', type=Path, required=True)
    ap.add_argument('--seconds', type=int, default=240)
    ap.add_argument('--steps', type=int, default=1000)
    ap.add_argument('--scratch', type=int, default=1)
    ap.add_argument('--internal', action='store_true')
    args = ap.parse_args()
    begin = time.monotonic()
    results = []
    for seed in range(3):
        if time.monotonic()-begin >= args.seconds:
            break
        r = run(args.packet, args.scratch, seed, args.steps, begin+args.seconds, args.internal)
        results.append(r)
        print('RESULT', {k: v for k, v in r.items() if k != 'controls'}, flush=True)
        if r['numerical_hit']:
            break
    out = {'status': 'EXPLORATORY_NUMERICAL_FEEDBACK_SEARCH', 'results': results,
           'scope': '128 balanced width-two sectors, all seven stage signs independent; one filtered stage; extra owned mode banks may be actively mixed. Necessary discovery model only; no rational or physical all-width endpoint is certified.',
           'new_kappa_claimed': False, 'elapsed_seconds': time.monotonic()-begin}
    suffix = '-internal' if args.internal else ''
    (HERE/f'evidence/feedback-scratch{args.scratch}{suffix}.json').write_text(json.dumps(out, indent=2)+'\n')


if __name__ == '__main__':
    main()
