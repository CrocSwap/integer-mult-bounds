// Adapt the PR468 integer relation engine to three active targets and one dirty helper.
// Read ordered words; use exact primitive integer rows for all rational relations.
#include <algorithm>
#include <array>
#include <cstdint>
#include <chrono>
#include <limits>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using V = std::array<int64_t, 8>;

// Use a primitive integer row with a positive leading entry.
void normalize(V& v) {
    int64_t divisor = 0;
    for (int64_t x : v) divisor = std::gcd(divisor, std::abs(x));
    if (!divisor) return;
    int leading = 0;
    while (!v[leading]) ++leading;
    if (v[leading] < 0) divisor = -divisor;
    for (int64_t& x : v) x /= divisor;
}

int pivot(const V& v) {
    for (int i = 0; i < 8; ++i) {
        if (v[i]) return i;
    }
    return 8;
}

struct Rows {
    std::array<V, 3> rows{};
    int size = 0;
    bool operator==(const Rows& other) const { return rows == other.rows; }
};

struct HashRows {
    size_t operator()(const Rows& basis) const {
        size_t hash = 0;
        for (const auto& row : basis.rows) {
            for (int64_t x : row) hash = (hash ^ size_t(x + 97)) * 1099511628211ull;
        }
        return hash;
    }
};

V reduce(V v, const Rows& basis) {
    for (int a = 0; a < basis.size; ++a) {
        const V& row = basis.rows[a];
        int p = pivot(row);
        int64_t coefficient = v[p];
        if (coefficient) {
            for (int i = 0; i < 8; ++i) {
                v[i] = row[p] * v[i] - coefficient * row[i];
            }
            normalize(v);
        }
    }
    return v;
}

Rows append(Rows basis, V v) {
    v = reduce(v, basis);
    if (pivot(v) == 8) return basis;
    normalize(v);
    int p = pivot(v);
    for (int a = 0; a < basis.size; ++a) {
        int64_t coefficient = basis.rows[a][p];
        if (coefficient) {
            for (int i = 0; i < 8; ++i) {
                basis.rows[a][i] = v[p] * basis.rows[a][i] - coefficient * v[i];
            }
            normalize(basis.rows[a]);
        }
    }
    basis.rows[basis.size++] = v;
    std::sort(basis.rows.begin(), basis.rows.begin() + basis.size,
              [](const V& a, const V& b) { return pivot(a) < pivot(b); });
    return basis;
}

V vec(int mask) {
    V v{};
    for (int i = 0; i < 8; ++i) v[i] = (mask >> i) & 1;
    return v;
}

int binaryrank(std::vector<int> rows) {
    int basis[8]{}, rank = 0;
    for (int v : rows) {
        for (int i = 7; i >= 0; --i) {
            if (!(v >> i & 1)) continue;
            if (basis[i]) {
                v ^= basis[i];
            } else {
                basis[i] = v;
                ++rank;
                break;
            }
        }
    }
    return rank;
}

// Binary 4 by 4 matrices use row-major bit order.
constexpr int ID = 0x8421;
constexpr int OFF = 0xffff ^ ID;
constexpr int OFFBITS[12] = {1,2,3,4,6,7,8,9,11,12,13,14};

int outer(int x, int y) {
    int m = 0;
    for (int i = 0; i < 4; ++i) if (x >> i & 1) m |= y << (4*i);
    return m;
}

std::pair<int,int> decode(int m) {
    int x = 0, y = 0;
    for (int i = 0; i < 4; ++i) {
        int row = (m >> (4*i)) & 15;
        if (row) {
            if (y && y != row) throw std::runtime_error("Projector rank is not one");
            y = row;
            x |= 1 << i;
        }
    }
    if (!x || !y || !(__builtin_parity(x & y))) {
        throw std::runtime_error("Invalid rank-one projector");
    }
    return {x,y};
}

int times_projection(int m, int x, int y) {
    int mx = 0;
    for (int i = 0; i < 4; ++i) mx |= __builtin_parity(((m >> (4*i)) & 15) & x) << i;
    return outer(mx,y);
}

struct KeyHash {
    size_t operator()(const V& v) const {
        size_t hash = 0;
        for (int64_t x : v) hash = (hash ^ size_t(x + 4097)) * 1099511628211ull;
        return hash;
    }
};

struct Group {
    V key;
    int mask, matrix;
};

struct Solver {
    std::array<int, 8> ns;
    int ancilla_mask = 0;
    std::vector<std::pair<int, int>> terms;
    std::vector<int> offrows;
    std::unordered_set<Rows, HashRows> seen;
    uint64_t states[4]{}, parityprune = 0, zeroprune = 0, terminal = 0, robust = 0;
    std::ofstream* cert = nullptr;
    int wordidx = 0;

    void init() {
        terms = {{0, ID}};
        for (int j = 0; j < 8; ++j) {
            auto [x,y] = decode(ns[j]);
            std::vector<std::pair<int, int>> next;
            for (auto [mask, matrix] : terms) {
                int variable = times_projection(matrix, x, y);
                int constant = matrix ^ variable;
                if (constant) next.emplace_back(mask, constant);
                if (variable) next.emplace_back(mask | (1 << j), variable);
            }
            terms = next;
        }
        for (int bit : OFFBITS) {
            int row = 0;
            for (int i = 0; i < 8; ++i) row |= ((ns[i] >> bit) & 1) << i;
            offrows.push_back(row);
        }
    }

    // Check whether a target is a linear combination of at most two physical frames.
    bool target_rank_small(int mask, const Rows& relations) {
        for (int i = 0; i < 8; ++i) {
            for (int j = i + 1; j < 8; ++j) {
                std::vector<V> basis(relations.rows.begin(),
                                     relations.rows.begin() + relations.size);
                auto add = [&](V v) {
                    for (const auto& row : basis) {
                        int p = pivot(row);
        int64_t coefficient = v[p];
                        if (coefficient) {
                            for (int k = 0; k < 8; ++k) {
                                v[k] = row[p] * v[k] - coefficient * row[k];
                            }
                            normalize(v);
                        }
                    }
                    if (pivot(v) < 8) {
                        normalize(v);
                        basis.push_back(v);
                        std::sort(basis.begin(), basis.end(),
                                  [](const V& a, const V& b) { return pivot(a) < pivot(b); });
                    }
                };
                add(vec(1 << i));
                add(vec(1 << j));
                int before = basis.size();
                add(vec(mask));
                if (int(basis.size()) == before) return true;
            }
        }
        return false;
    }

    void go(const Rows& relations) {
        if (!seen.insert(relations).second) return;
        ++states[relations.size];

        auto parity = offrows;
        for (int a = 0; a < relations.size; ++a) {
            int row = 0;
            for (int j = 0; j < 8; ++j) {
                row |= (std::abs(relations.rows[a][j]) & 1) << j;
            }
            parity.push_back(row);
        }
        if (binaryrank(parity) > 3) {
            ++parityprune;
            return;
        }
        for (int i = 0; i < 8; ++i) {
            if (pivot(reduce(vec(1 << i), relations)) == 8) {
                ++zeroprune;
                return;
            }
        }

        // Form exact quotient keys with one common integer denominator.
        int64_t denominator = 1;
        for (int a = 0; a < relations.size; ++a) {
            denominator = std::lcm(denominator, relations.rows[a][pivot(relations.rows[a])]);
        }
        std::unordered_map<V, std::pair<int, int>, KeyHash> groups;
        for (auto [mask, matrix] : terms) {
            V key = vec(mask);
            for (int64_t& x : key) x *= denominator;
            for (int a = 0; a < relations.size; ++a) {
                int p = pivot(relations.rows[a]);
                if (mask >> p & 1) {
                    for (int j = 0; j < 8; ++j) {
                        key[j] -= (denominator / relations.rows[a][p]) * relations.rows[a][j];
                    }
                }
            }
            auto [it, inserted] = groups.emplace(key, std::make_pair(mask, 0));
            it->second.second ^= matrix;
        }
        std::vector<Group> active;
        bool has_offdiagonal = false;
        for (const auto& [key, term] : groups) {
            if (term.second) {
                active.push_back({key, term.first, term.second});
                has_offdiagonal |= (term.second & OFF) != 0;
            }
        }

        if (!has_offdiagonal) {
            int targets[4] = {-1, -1, -1, -1};
            for (const auto& group : active) {
                for (int w = 0; w < 4; ++w) {
                    if (group.matrix >> (5 * w) & 1) {
                        if (targets[w] != -1) throw std::logic_error("A diagonal unit has multiple terms");
                        targets[w] = group.mask;
                    }
                }
            }
            for (int target : targets) {
                if (target < 0) throw std::logic_error("A diagonal unit is zero");
            }
            ++terminal;
            for (int ancilla = 0; ancilla < 4; ++ancilla) {
                if (!(ancilla_mask >> ancilla & 1)) continue;
                Rows constrained = relations;
                if (pivot(reduce(vec(targets[ancilla]), constrained)) != 8) {
                    if (constrained.size == 3) continue;
                    constrained = append(constrained, vec(targets[ancilla]));
                }
                bool zero = false;
                for (int i = 0; i < 8; ++i) zero |= pivot(reduce(vec(1 << i), constrained)) == 8;
                if (zero) continue;
                bool survives = true;
                for (int w = 0; w < 4; ++w) {
                    if (w != ancilla) survives &= !target_rank_small(targets[w], constrained);
                }
                if (!survives) continue;
                ++robust;
                if (cert) {
                    *cert << wordidx << ' ' << ancilla;
                    for (int projector : ns) *cert << ' ' << projector;
                    *cert << " : ";
                    for (int a = 0; a < constrained.size; ++a) {
                        for (int64_t x : constrained.rows[a]) *cert << x << ',';
                        *cert << " ; ";
                    }
                    *cert << " : ";
                    for (int target : targets) *cert << target << ' ';
                    *cert << '\n';
                }
            }
            return;
        }
        if (relations.size == 3) return;

        // A nonzero off-diagonal entry must cancel with a partner group.
        int best = -1, best_bit = -1, best_count = 1000;
        for (int a = 0; a < int(active.size()); ++a) {
            for (int bit : OFFBITS) {
                if (!(active[a].matrix >> bit & 1)) continue;
                int count = 0;
                for (int b = 0; b < int(active.size()); ++b) {
                    if (a != b && (active[b].matrix >> bit & 1)) ++count;
                }
                if (count < best_count) {
                    best = a;
                    best_bit = bit;
                    best_count = count;
                }
            }
        }
        for (int b = 0; b < int(active.size()); ++b) {
            if (b != best && (active[b].matrix >> best_bit & 1)) {
                V difference{};
                for (int i = 0; i < 8; ++i) {
                    difference[i] = ((active[best].mask >> i) & 1) - ((active[b].mask >> i) & 1);
                }
                Rows next = append(relations, difference);
                if (next.size == relations.size) {
                    throw std::logic_error("Partner already in this group");
                }
                go(next);
            }
        }
    }
};

int main(int argc, char** argv) {
    try {
        if (argc < 4 || argc > 6) {
            throw std::runtime_error("Usage: integer_engine INPUT OUTPUT_PREFIX [START [COUNT]]");
        }
        uint64_t start = argc >= 5 ? std::stoull(argv[4]) : 0;
        uint64_t limit = argc >= 6 ? std::stoull(argv[5]) : std::numeric_limits<uint64_t>::max();
        // The third argument identifies the result schema. It must be 'dirty'.
        if (std::string(argv[3]) != "dirty") throw std::runtime_error("Expected dirty mode");
        std::ifstream input(argv[1], std::ios::binary);
        if (!input) throw std::runtime_error("Cannot open input");
        input.seekg(0,std::ios::end);
        auto bytes = input.tellg();
        if (bytes < 0 || bytes % 18 != 0) throw std::runtime_error("Invalid input length");
        uint64_t available = uint64_t(bytes) / 18;
        if (start > available) throw std::runtime_error("Start exceeds input count");
        uint64_t stop = start + std::min(limit, available-start);
        input.seekg(start*18);
        std::string prefix = argv[2];
        std::ofstream results(prefix+".chunks.jsonl"), candidates(prefix+".candidates.txt"), terminals(prefix+".terminals.jsonl");
        if (!results || !candidates || !terminals) throw std::runtime_error("Cannot open result paths");
        uint64_t states[4]{}, total_terminal = 0, total_robust = 0, parity = 0, zero = 0;
        auto begin = std::chrono::steady_clock::now();
        for (uint64_t index = start; index < stop; ++index) {
            unsigned char data[18];
            if (!input.read(reinterpret_cast<char*>(data),18)) throw std::runtime_error("Incomplete record");
            Solver solver;
            for (int i=0;i<8;++i) solver.ns[i] = data[2*i] | (int(data[2*i+1])<<8);
            solver.ancilla_mask = data[16] | (int(data[17])<<8);
            if (solver.ancilla_mask < 1 || solver.ancilla_mask > 15) throw std::runtime_error("Invalid helper mask");
            solver.wordidx = index;
            solver.cert = &candidates;
            solver.init();
            solver.go(Rows{});
            for (int i=0;i<4;++i) states[i] += solver.states[i];
            total_terminal += solver.terminal;
            total_robust += solver.robust;
            parity += solver.parityprune;
            zero += solver.zeroprune;
            if (solver.terminal || solver.robust) {
                terminals << "{\"word\":" << index << ",\"terminals\":" << solver.terminal << ",\"robust\":" << solver.robust << "}\n";
            }
            if ((index+1-start)%1000 == 0 || index+1 == stop) {
                results << "{\"start\":" << start << ",\"end\":" << index+1 << ",\"states\":[" << states[0] << ',' << states[1] << ',' << states[2] << ',' << states[3] << "],\"terminals\":" << total_terminal << ",\"robust\":" << total_robust << ",\"parity_prunes\":" << parity << ",\"zero_prunes\":" << zero << "}\n";
                results.flush();
                if (!results || !candidates || !terminals) throw std::runtime_error("Cannot write result");
            }
            if ((index+1-start)%10000 == 0) {
                double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
                std::cerr << index+1 << " / " << stop << "; terminals " << total_terminal << "; robust " << total_robust << "; seconds " << seconds << '\n';
            }
        }
        std::cout << "{\"start\":" << start << ",\"end\":" << stop << ",\"words\":" << stop-start << ",\"terminals\":" << total_terminal << ",\"robust\":" << total_robust << "}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
