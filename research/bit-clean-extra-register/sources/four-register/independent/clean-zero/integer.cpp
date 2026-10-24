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
constexpr int OFF = 0x356;
constexpr int OFFBITS[6] = {1,2,4,6,8,9};

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
        std::sort(terms.begin(), terms.end());
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


        std::sort(active.begin(), active.end(), [](const Group& a, const Group& b) { return a.mask < b.mask; });
        if (!has_offdiagonal) {
            int targets[3] = {-1,-1,-1};
            std::vector<Group> needed;
            for (int w=0;w<3;++w) {
                std::vector<Group> present;
                for (const auto& group:active) if(group.matrix>>(5*w)&1)present.push_back(group);
                if(present.empty())throw std::logic_error("An active diagonal has zero augmentation");
                if(present.size()==1)targets[w]=present[0].mask;
                else if(needed.empty() || present.size()<needed.size())needed=present;
            }
            if(!needed.empty()) {
                if(relations.size==3)return;
                for(int i=0;i<2;++i)for(int j=i+1;j<int(needed.size());++j) {
                    V difference{};
                    for(int k=0;k<8;++k)difference[k]=((needed[i].mask>>k)&1)-((needed[j].mask>>k)&1);
                    Rows next=append(relations,difference);
                    if(next.size!=relations.size+1)throw std::logic_error("A diagonal partner is in the same group");
                    go(next);
                }
                return;
            }
            ++terminal;
            for(int w=0;w<3;++w)if(target_rank_small(targets[w],relations))return;
            ++robust;
            if(cert) {
                *cert<<wordidx;
                for(int n:ns)*cert<<' '<<n;
                *cert<<" : ";
                for(int a=0;a<relations.size;++a) {
                    for(int64_t x:relations.rows[a])*cert<<x<<',';
                    *cert<<" ; ";
                }
                *cert<<" : ";
                for(int t:targets)*cert<<t<<' ';
                *cert<<'\n';
            }
            return;
        }
        if (relations.size == 3) return;

        // A nonzero off-diagonal entry must cancel with a partner group.
        int best = -1, best_bit = -1, best_count = 1000;
        for (int bit : OFFBITS) {
            int count = 0;
            for (const auto& group : active) count += (group.matrix >> bit) & 1;
            if (count && count < best_count) { best_bit = bit; best_count = count; }
        }
        for (int a = 0; a < int(active.size()); ++a) {
            if (active[a].matrix >> best_bit & 1) { best = a; break; }
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


int main(int argc,char**argv) {
    try {
        if(argc!=3)throw std::runtime_error("Usage: clean_integer INPUT OUTPUT");
        std::ifstream input(argv[1],std::ios::binary);
        if(!input)throw std::runtime_error("Cannot open input");
        input.seekg(0,std::ios::end);auto bytes=input.tellg();
        if(bytes<0 || bytes%16)throw std::runtime_error("Invalid input length");
        input.seekg(0);
        uint64_t count=uint64_t(bytes)/16,states[4]{},terminals=0,robust=0,parity=0,zero=0;
        std::ofstream out(argv[2]), terminal_output(std::string(argv[2])+".terminals.jsonl"), candidates(std::string(argv[2])+".candidates.txt");
        if(!out || !terminal_output || !candidates)throw std::runtime_error("Cannot open output");
        for(uint64_t index=0;index<count;++index) {
            unsigned char data[16];
            if(!input.read(reinterpret_cast<char*>(data),16))throw std::runtime_error("Incomplete record");
            Solver solver;solver.wordidx=index;solver.cert=&candidates;
            for(int j=0;j<8;++j)solver.ns[j]=data[2*j]+256*data[2*j+1];
            solver.init();solver.go(Rows{});
            for(int k=0;k<4;++k)states[k]+=solver.states[k];
            terminals+=solver.terminal;robust+=solver.robust;parity+=solver.parityprune;zero+=solver.zeroprune;
            if(solver.terminal || solver.robust)terminal_output<<"{\"word\":"<<index<<",\"terminals\":"<<solver.terminal<<",\"robust\":"<<solver.robust<<"}\n";
            if((index+1)%1000==0 || index+1==count) {
                out<<"{\"words\":"<<index+1<<",\"states\":["<<states[0]<<','<<states[1]<<','<<states[2]<<','<<states[3]<<"],\"terminals\":"<<terminals<<",\"robust\":"<<robust<<",\"parity_prunes\":"<<parity<<",\"zero_frame_prunes\":"<<zero<<"}\n";
                out.flush();
                if(!out || !terminal_output || !candidates)throw std::runtime_error("Cannot write output");
            }
        }
        return 0;
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
