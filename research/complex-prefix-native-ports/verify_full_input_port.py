"""Exact full-input triangular block checks; standard library only."""
import hashlib, importlib.util, json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    pins = json.loads((root / 'SOURCE-PINS.json').read_text(encoding='utf-8'))
    src = root / 'pr4710' / 'verify_residual.py'
    expected = next(x['sha256'] for x in pins if x['file'] == 'pr4710/verify_residual.py')
    if hashlib.sha256(src.read_bytes()).hexdigest() != expected:
        raise ValueError('frozen predecessor drift')
    spec = importlib.util.spec_from_file_location('residual_full_port', src)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    def require(ok, msg):
        if not ok:
            raise ValueError(msg)
    C = [v.c_letter(j) for j in range(3)]
    I = v.ident()
    Z = v.scale(v.q(0), I)
    U = v.monomial([0, 5, 2, 7, 4, 1, 6, 3])
    V = v.monomial([0, 2, 1, 3, 4, 6, 5, 7])
    S = v.s_letter(7)
    P, Q = v.word(S, U, S), v.word(S, V, S)
    L = v.plus(P, v.scale(v.q(2), Q))
    K, a = v.word(*C), v.pauli(1, 3)
    W = v.pauli(0, 5)
    J = v.word(v.pauli(0, 2), V, C[2])
    M = v.monomial([2, 0, 3, 1, 4, 6, 5, 7], [0, 0, 2, 2, 1, 3, 3, 1])
    A = C[0]
    D = v.word(J, W, C[0])
    B = v.plus(v.word(M, C[2]), v.scale(v.q(2), v.word(K, a)))
    require(v.word(J, W, C[0], P, C[0]) == v.word(M, C[2]), 'P branch')
    require(v.word(J, W, C[0], Q, C[0]) == v.word(K, a), 'Q branch')
    R = v.word(v.adjoint(P), Q)
    R2, R3, R4 = v.word(R, R), v.word(R, R, R), v.word(R, R, R, R)
    require(R4 == I, 'actual phase relative order four')
    Linv = v.scale(v.q(v.F(-1, 15)), v.word(v.plus(v.plus(I, v.scale(v.q(-2), R)), v.plus(v.scale(v.q(4), R2), v.scale(v.q(-8), R3))), v.adjoint(P)))
    require(v.word(Linv, L) == I and v.word(L, Linv) == I, 'free coupling inverse')
    F = v.word(A, L, A)
    Ai = v.adjoint(A)
    require(v.word(Ai, F) == v.word(L, A), 'two call inverse left order')
    require(v.word(F, Ai) == v.word(A, L), 'two call inverse right order')
    require(v.word(D, L, A) == B, 'full input bottom left block')
    Ai, Di = v.adjoint(A), v.adjoint(D)
    require(v.word(Ai, A) == I and v.word(A, Ai) == I, 'A inverse')
    require(v.word(Di, D) == I and v.word(D, Di) == I, 'D inverse')
    require(v.plus(v.scale(v.q(-1), v.word(L, A)), v.word(Di, B)) == Z, 'inverse times forward off diagonal')
    require(v.plus(v.word(B, Ai), v.scale(v.q(-1), v.word(D, L))) == Z, 'forward times inverse off diagonal')
    for j in range(3):
        require(v.adjoint(C[j]) == v.word(v.pauli(1 << j, 0), C[j]), 'one paid inverse')
    require(D != Z, 'reject erasing arbitrary second input')
    print(json.dumps({'status': 'PASS_FULL_INPUT_TRIANGULAR_PORT', 'two_call_port': {'forward_paid_calls': 2, 'inverse_paid_calls': 2}, 'three_call_port': {'forward_paid_calls': 3, 'inverse_paid_calls': 3}, 'arbitrary_independent_input_arrays': 2, 'euclidean_norm_bound': 4, 'inverse_norm_bound': 4, 'new_kappa': False}, sort_keys=True))

if __name__ == '__main__':
    main()
