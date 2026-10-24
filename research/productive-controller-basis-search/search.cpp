// Exact GF(16) pruning for the finite class in PROOF.md.
// Apache-2.0. Cinna Davis, with substantial OpenAI Codex assistance.
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <vector>

// Four field elements, packed into one row as four nibbles.
using Matrix = std::array<uint16_t, 4>;
struct State { Matrix even{}, odd{}; };
struct Gate { std::array<int, 4> projector, nilpotent; };
uint16_t times[16][65536];
int product[16][16], inverse_element[16];
std::vector<Gate> full, thin;
std::vector<int> program;
uint64_t nodes[6]{}, pruned[6]{}, hits = 0;
int mask = 27;

int rank(Matrix a) {
    int r = 0;
    for (int c = 0; c < 4; ++c) {
        int j = r;
        while (j < 4 && !((a[j] >> (4*c)) & 15)) ++j;
        if (j == 4) continue;
        std::swap(a[j], a[r]);
        a[r] = times[inverse_element[(a[r] >> (4*c)) & 15]][a[r]];
        for (j = r+1; j < 4; ++j) {
            int q = (a[j] >> (4*c)) & 15;
            if (q) a[j] ^= times[q][a[r]];
        }
        if (++r == 4) break;
    }
    return r;
}

Matrix inverse(Matrix a) {
    Matrix b{};
    for (int i = 0; i < 4; ++i) b[i] = 1 << (4*i);
    for (int c = 0; c < 4; ++c) {
        int j = c;
        while (j < 4 && !((a[j] >> (4*c)) & 15)) ++j;
        if (j == 4) return {};
        std::swap(a[j], a[c]);
        std::swap(b[j], b[c]);
        int x = inverse_element[(a[c] >> (4*c)) & 15];
        a[c] = times[x][a[c]];
        b[c] = times[x][b[c]];
        for (j = 0; j < 4; ++j) if (j != c) {
            int q = (a[j] >> (4*c)) & 15;
            a[j] ^= times[q][a[c]];
            b[j] ^= times[q][b[c]];
        }
    }
    return b;
}

std::array<uint16_t, 16> subset_sums(Matrix a) {
    std::array<uint16_t, 16> sums{};
    for (int i = 1; i < 16; ++i)
        sums[i] = sums[i & (i-1)] ^ a[__builtin_ctz(i)];
    return sums;
}

State apply(State state, const Gate &gate, int d) {
    auto even = subset_sums(state.even), odd = subset_sums(state.odd);
    State next;
    for (int i = 0; i < 4; ++i) {
        next.even[i] = state.even[i] ^ times[d ^ 1][even[gate.projector[i]]]
                                      ^ times[d][odd[gate.nilpotent[i]]];
        next.odd[i] = state.odd[i] ^ times[d ^ 1][odd[gate.projector[i]]]
                                    ^ times[d][even[gate.nilpotent[i]]];
    }
    return next;
}

std::array<int, 4> forced_last_nilpotent(State state) {
    auto oi = inverse(state.odd);
    if (oi == Matrix{}) return {};
    std::array<int, 4> n{};
    for (int i = 0; i < 4; ++i) {
        uint16_t row = 0;
        for (int k = 0; k < 4; ++k)
            row ^= times[(state.even[i] >> (4*k)) & 15][oi[k]];
        for (int j = 0; j < 4; ++j) {
            int a = (row >> (4*j)) & 15;
            if (a > 1) return {}; // The actual call must be binary.
            n[i] |= a << j;
        }
    }
    return n;
}

void search(State state, int step) {
    ++nodes[step];
    int remaining = 5-step;
    if (remaining < 4 && rank(state.even) > remaining) {
        ++pruned[step];
        return;
    }
    if (step == 4) {
        auto n = forced_last_nilpotent(state);
        if (n == std::array<int, 4>{}) return;
        const auto &alphabet = (mask >> 4 & 1) ? full : thin;
        for (int i = 0; i < int(alphabet.size()); ++i) {
            if (alphabet[i].nilpotent != n) continue;
            auto next = apply(state, alphabet[i], (mask >> 4 & 1) ? 6 : 1);
            if (next.even != Matrix{}) continue;
            ++hits;
            std::cout << "HIT " << mask;
            for (int g : program) std::cout << " " << g;
            std::cout << " " << i << "\n";
        }
        return;
    }
    const auto &alphabet = (mask >> step & 1) ? full : thin;
    int d = (mask >> step & 1) ? step+2 : 1;
    // Each recursive edge is an exact matrix operation in the finite field.
    for (int i = 0; i < int(alphabet.size()); ++i) {
        program.push_back(i);
        search(apply(state, alphabet[i], d), step+1);
        program.pop_back();
    }
}

void initialize() {
    for (int a = 0; a < 16; ++a) for (int b = 0; b < 16; ++b) {
        int value = 0;
        for (int x = a, y = b; y; y >>= 1) {
            if (y & 1) value ^= x;
            x <<= 1;
            if (x & 16) x ^= 19; // x^4+x+1
        }
        product[a][b] = value;
    }
    for (int a = 1; a < 16; ++a) for (int b = 1; b < 16; ++b)
        if (product[a][b] == 1) inverse_element[a] = b;
    for (int d = 0; d < 16; ++d) for (int x = 0; x < 65536; ++x) {
        int value = 0;
        for (int k = 0; k < 4; ++k)
            value |= product[d][(x >> (4*k)) & 15] << (4*k);
        times[d][x] = value;
    }
    for (int u = 1; u < 16; ++u) for (int v = 1; v < 16; ++v) {
        if (__builtin_popcount(u & v) & 1) continue;
        Gate gate{};
        for (int i = 0; i < 4; ++i) if (u >> i & 1) gate.nilpotent[i] = v;
        thin.push_back(gate);
        std::map<std::array<int, 4>, bool> seen;
        for (int a = 1; a < 16; ++a) if (__builtin_popcount(v & a) & 1)
            for (int b = 1; b < 16; ++b) {
                if (!(__builtin_popcount(u & b) & 1) ||
                    (__builtin_popcount(a & b) & 1)) continue;
                for (int i = 0; i < 4; ++i)
                    gate.projector[i] = ((u >> i & 1) ? b : 0) ^
                                        ((a >> i & 1) ? v : 0);
                if (!seen[gate.projector]) {
                    seen[gate.projector] = true;
                    full.push_back(gate);
                }
            }
    }
}

void traces() {
    // No pruning: separately check transitions on 128 deterministic words.
    for (int trial = 0; trial < 128; ++trial) {
        int word_mask = (trial*13+7) & 31;
        State state;
        for (int i = 0; i < 4; ++i) state.even[i] = 1 << (4*i);
        std::cout << "TRACE " << word_mask;
        for (int stage = 0; stage < 5; ++stage) {
            const auto &alphabet = (word_mask >> stage & 1) ? full : thin;
            int g = (137*trial+37*stage) % alphabet.size();
            std::cout << " " << g;
            state = apply(state, alphabet[g], (word_mask >> stage & 1) ? stage+2 : 1);
        }
        for (auto row : state.even) std::cout << " " << row;
        for (auto row : state.odd) std::cout << " " << row;
        std::cout << "\n";
    }
}

int main(int argc, char **argv) {
    initialize();
    if (argc > 1 && std::string(argv[1]) == "trace") { traces(); return 0; }
    if (argc > 1) mask = std::stoi(argv[1]);
    std::cerr << "full=" << full.size() << " thin=" << thin.size() << "\n";
    State state;
    for (int i = 0; i < 4; ++i) state.even[i] = 1 << (4*i);
    const auto &alphabet = (mask & 1) ? full : thin;
    for (int i = 0; i < int(alphabet.size()); ++i) {
        if (alphabet[i].nilpotent != std::array<int, 4>{0, 1, 0, 0}) continue;
        if ((mask & 1) && alphabet[i].projector != std::array<int, 4>{1, 2, 0, 0})
            continue;
        program.push_back(i);
        search(apply(state, alphabet[i], (mask & 1) ? 2 : 1), 1);
        break;
    }
    std::cerr << "mask=" << mask << " hits=" << hits;
    for (int i = 0; i < 5; ++i)
        std::cerr << " s" << i << "=" << nodes[i] << "/" << pruned[i];
    std::cerr << "\n";
}
