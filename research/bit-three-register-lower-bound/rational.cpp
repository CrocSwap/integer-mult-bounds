// Enumerate the required rational subset-collision spaces of rank at most three.
#include <algorithm>
#include <array>
#include <cstdint>
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

using V = std::array<int, 8>;

// Use a primitive integer row with a positive leading entry.
void normalize(V& v) {
    int divisor = 0;
    for (int x : v) divisor = std::gcd(divisor, std::abs(x));
    if (!divisor) return;
    int leading = 0;
    while (!v[leading]) ++leading;
    if (v[leading] < 0) divisor = -divisor;
    for (int& x : v) x /= divisor;
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
            for (int x : row) hash = (hash ^ size_t(x + 97)) * 1099511628211ull;
        }
        return hash;
    }
};

V reduce(V v, const Rows& basis) {
    for (int a = 0; a < basis.size; ++a) {
        const V& row = basis.rows[a];
        int p = pivot(row), coefficient = v[p];
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
        int coefficient = basis.rows[a][p];
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

// Binary 3 by 3 matrices use row-major bit order. The identity is 273.
int mul(int a, int b) {
    int result = 0;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            int entry = 0;
            for (int k = 0; k < 3; ++k) {
                entry ^= ((a >> (3 * i + k)) & 1) * ((b >> (3 * k + j)) & 1);
            }
            result |= entry << (3 * i + j);
        }
    }
    return result;
}

struct KeyHash {
    size_t operator()(const V& v) const {
        size_t hash = 0;
        for (int x : v) hash = (hash ^ size_t(x + 4097)) * 1099511628211ull;
        return hash;
    }
};

struct Group {
    V key;
    int mask, matrix;
};

struct Solver {
    std::array<int, 8> ns;
    std::vector<std::pair<int, int>> terms;
    std::vector<int> offrows;
    std::unordered_set<Rows, HashRows> seen;
    uint64_t states[4]{}, parityprune = 0, zeroprune = 0, terminal = 0, robust = 0;
    std::ofstream* cert = nullptr;
    int wordidx = 0;

    void init() {
        terms = {{0, 273}};
        for (int j = 0; j < 8; ++j) {
            std::vector<std::pair<int, int>> next;
            for (auto [mask, matrix] : terms) {
                int constant = mul(matrix, 273 ^ ns[j]);
                int variable = mul(matrix, ns[j]);
                if (constant) next.emplace_back(mask, constant);
                if (variable) next.emplace_back(mask | (1 << j), variable);
            }
            terms = next;
        }
        for (int bit : {1, 2, 3, 5, 6, 7}) {
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
                        int p = pivot(row), coefficient = v[p];
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
        int denominator = 1;
        for (int a = 0; a < relations.size; ++a) {
            denominator = std::lcm(denominator, relations.rows[a][pivot(relations.rows[a])]);
        }
        std::unordered_map<V, std::pair<int, int>, KeyHash> groups;
        for (auto [mask, matrix] : terms) {
            V key = vec(mask);
            for (int& x : key) x *= denominator;
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
                has_offdiagonal |= (term.second & ~273) != 0;
            }
        }

        if (!has_offdiagonal) {
            int targets[3] = {-1, -1, -1};
            for (const auto& group : active) {
                for (int w = 0; w < 3; ++w) {
                    if (group.matrix >> (4 * w) & 1) {
                        if (targets[w] != -1) return;
                        targets[w] = group.mask;
                    }
                }
            }
            for (int target : targets) {
                if (target < 0) return;
            }
            ++terminal;
            bool survives = true;
            for (int target : targets) survives &= !target_rank_small(target, relations);
            if (survives) {
                ++robust;
                if (cert) {
                    *cert << wordidx;
                    for (int projector : ns) *cert << ' ' << projector;
                    *cert << " : ";
                    for (int a = 0; a < relations.size; ++a) {
                        for (int x : relations.rows[a]) *cert << x << ',';
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
            for (int bit : {1, 2, 3, 5, 6, 7}) {
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
        if (argc != 5 || std::string(argv[1]) != "--batch") {
            throw std::runtime_error("Usage: rational --batch INPUT RESULTS CANDIDATES");
        }
        std::ifstream input(argv[2]);
        if (!input) throw std::runtime_error("Cannot open batch input");
        int case_count;
        if (!(input >> case_count) || case_count <= 0) {
            throw std::runtime_error("Invalid batch case count");
        }
        std::ofstream results(argv[3]), candidates(argv[4]);
        if (!results || !candidates) throw std::runtime_error("Cannot open result paths");

        std::set<int> case_ids;
        uint64_t total_words = 0, total_robust = 0;
        for (int index = 0; index < case_count; ++index) {
            int case_id;
            std::array<int, 8> projectors;
            if (!(input >> case_id) || !case_ids.insert(case_id).second) {
                throw std::runtime_error("Invalid or duplicate case id");
            }
            for (int& projector : projectors) {
                if (!(input >> projector)) throw std::runtime_error("Incomplete projector row");
            }
            for (int projector : projectors) {
                if (projector <= 0 || projector >= 512 || mul(projector, projector) != projector) {
                    throw std::runtime_error("Invalid projector");
                }
                int nonzero_row = 0;
                for (int i = 0; i < 3; ++i) {
                    int row = (projector >> (3 * i)) & 7;
                    if (row) {
                        if (nonzero_row && nonzero_row != row) {
                            throw std::runtime_error("Projector rank is not one");
                        }
                        nonzero_row = row;
                    }
                }
            }

            std::sort(projectors.begin(), projectors.end());
            uint64_t states[4]{}, terminals = 0, robust = 0, parity = 0, zero = 0;
            int words = 0;
            do {
                Solver solver;
                solver.ns = projectors;
                solver.wordidx = words;
                solver.cert = &candidates;
                solver.init();
                solver.go(Rows{});
                for (int i = 0; i < 4; ++i) states[i] += solver.states[i];
                terminals += solver.terminal;
                robust += solver.robust;
                parity += solver.parityprune;
                zero += solver.zeroprune;
                ++words;
            } while (std::next_permutation(projectors.begin(), projectors.end()));

            results << "{\"case\":" << case_id << ",\"words\":" << words
                    << ",\"states\":[" << states[0] << ',' << states[1] << ','
                    << states[2] << ',' << states[3] << "],\"terminals\":" << terminals
                    << ",\"robust\":" << robust << ",\"parity_prunes\":" << parity
                    << ",\"zero_frame_prunes\":" << zero << "}\n";
            results.flush();
            if (!results || !candidates) throw std::runtime_error("Cannot write result");
            total_words += words;
            total_robust += robust;
            if ((index + 1) % 10 == 0) {
                std::cerr << index + 1 << " / " << case_count << " cases; "
                          << total_words << " words; robust " << total_robust << '\n';
            }
        }
        std::string extra;
        if (input >> extra) throw std::runtime_error("Trailing batch data");
        candidates.close();
        if (!candidates) throw std::runtime_error("Cannot close candidate file");
        results.close();
        if (!results) throw std::runtime_error("Cannot close result file");
        std::cout << "{\"completed_cases\":" << case_count << ",\"words\":" << total_words
                  << ",\"robust\":" << total_robust << "}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
