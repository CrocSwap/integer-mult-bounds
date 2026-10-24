// Exact finite Dic_3 six-call diagonal join. Nick Petalas, Apache-2.0.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

using Mask = std::uint16_t;
using Mat = std::array<Mask, 9>;
constexpr std::size_t CAPACITY = 178809; // sum of 56^j, j=0..3
struct Gate { unsigned x, y, g; };
struct Node { Mat value, inverse; std::array<unsigned, 3> word{}; unsigned length; };
struct Hash {
    std::size_t operator()(const Mat& a) const noexcept {
        std::uint64_t h = 1469598103934665603ULL;
        for (Mask v : a) { h ^= v; h *= 1099511628211ULL; }
        return static_cast<std::size_t>(h);
    }
};
void need(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
unsigned mul(unsigned a, unsigned b) {
    const int sign = a / 6 == 0 ? 1 : -1;
    const int exponent = (static_cast<int>(a % 6) + sign * static_cast<int>(b % 6)
                          + (a / 6 && b / 6 ? 3 : 0) + 6) % 6;
    return static_cast<unsigned>(exponent) + 6 * ((a / 6 + b / 6) % 2);
}
unsigned inverse(unsigned a) {
    for (unsigned b = 0; b < 12; ++b)
        if (mul(a,b) == 0 && mul(b,a) == 0) return b;
    throw std::runtime_error("missing group inverse");
}
Mat identity() { return Mat{1,0,0,0,1,0,0,0,1}; }
Mask ring(Mask a, Mask b) {
    Mask out = 0;
    for (unsigned i = 0; i < 12; ++i)
        if ((a >> i) & 1U)
            for (unsigned j = 0; j < 12; ++j)
                if ((b >> j) & 1U) out ^= static_cast<Mask>(1U << mul(i,j));
    return out;
}
Mat literal(const Mat& a, const Mat& b) {
    Mat out{};
    for (unsigned i = 0; i < 3; ++i)
        for (unsigned j = 0; j < 3; ++j)
            for (unsigned k = 0; k < 3; ++k) out[3*i+j] ^= ring(a[3*i+k],b[3*k+j]);
    return out;
}
unsigned parity(unsigned a) { return ((a >> 2) ^ (a >> 1) ^ a) & 1U; }
std::vector<Gate> gates() {
    std::vector<Gate> out;
    out.reserve(56);
    for (unsigned g : {1U,6U})
        for (unsigned x = 1; x < 8; ++x)
            for (unsigned y = 1; y < 8; ++y)
                if (parity(x & y)) out.push_back({x,y,g});
    need(out.size() == 56,"alphabet size");
    return out;
}
Mat factor(Gate t) {
    Mat out = identity();
    for (unsigned i = 0; i < 3; ++i)
        for (unsigned j = 0; j < 3; ++j)
            if (((t.x >> i) & 1U) && ((t.y >> j) & 1U))
                out[3*i+j] ^= static_cast<Mask>((1U << t.g) ^ 1U);
    return out;
}
using Shifts = std::array<std::array<Mask,4096>,12>;
Shifts right_shifts() {
    Shifts out{};
    for (unsigned g = 0; g < 12; ++g)
        for (unsigned a = 0; a < 4096; ++a)
            for (unsigned i = 0; i < 12; ++i)
                if ((a >> i) & 1U) out[g][a] ^= static_cast<Mask>(1U << mul(i,g));
    return out;
}
Mat append(const Mat& a, Gate t, const Shifts& shifts) {
    Mat out = a;
    for (unsigned i = 0; i < 3; ++i) {
        Mask total = 0;
        for (unsigned k = 0; k < 3; ++k)
            if ((t.x >> k) & 1U) total ^= a[3*i+k];
        const Mask delta = total ^ shifts[t.g][total];
        for (unsigned j = 0; j < 3; ++j)
            if ((t.y >> j) & 1U) out[3*i+j] ^= delta;
    }
    return out;
}
// Left multiplication by D(g)^-1, needed for (A D)^-1.
Mat prepend_inverse(const Mat& a, Gate t) {
    t.g = inverse(t.g);
    Mat out = a;
    for (unsigned j = 0; j < 3; ++j) {
        Mask total = 0;
        for (unsigned k = 0; k < 3; ++k)
            if ((t.y >> k) & 1U) total ^= a[3*k+j];
        const Mask delta = total ^ ring(static_cast<Mask>(1U << t.g),total);
        for (unsigned i = 0; i < 3; ++i)
            if ((t.x >> i) & 1U) out[3*i+j] ^= delta;
    }
    return out;
}
std::array<unsigned,12> distances() {
    std::array<unsigned,12> d{};
    d.fill(99); d[0] = 0;
    for (unsigned step = 0; step < 11; ++step)
        for (unsigned a = 0; a < 12; ++a)
            for (unsigned g : {1U,6U})
                if (d[a]+1 < d[mul(a,g)]) d[mul(a,g)] = d[a]+1;
    for (unsigned a : d) need(a < 12,"unreachable positive group element");
    return d;
}
void self_checks(const std::vector<Gate>& ops, const Shifts& shifts) {
    for (unsigned a = 0; a < 12; ++a)
        for (unsigned b = 0; b < 12; ++b)
            for (unsigned c = 0; c < 12; ++c)
                need(mul(mul(a,b),c) == mul(a,mul(b,c)),"associativity");
    for (Gate t : ops) {
        need(literal(factor(t),prepend_inverse(identity(),t)) == identity(),"factor inverse");
        for (Gate s : ops) {
            const Mat a = factor(s);
            need(append(a,t,shifts) == literal(a,factor(t)),"append control");
            need(prepend_inverse(a,t) == literal(prepend_inverse(identity(),t),a),"inverse control");
        }
    }
    need(mul(1,6) != mul(6,1),"noncommuting order");
}
std::vector<Node> inventory(const std::vector<Gate>& ops, const Shifts& shifts,
                            std::array<std::size_t,4>& counts) {
    std::vector<Node> nodes;
    nodes.reserve(CAPACITY);
    std::unordered_map<Mat,std::size_t,Hash> seen;
    seen.reserve(CAPACITY);
    nodes.push_back({identity(),identity(),{},0});
    need(seen.emplace(identity(),0).second,"initial inventory insertion");
    counts[0] = 1;
    std::size_t begin = 0, end = 1;
    for (unsigned depth = 1; depth <= 3; ++depth) {
        const std::size_t next_begin = nodes.size();
        for (std::size_t k = begin; k < end; ++k)
            for (unsigned op = 0; op < ops.size(); ++op) {
                const Mat value = append(nodes[k].value,ops[op],shifts);
                if (seen.find(value) != seen.end()) continue;
                need(nodes.size() < CAPACITY,"state capacity");
                Node n{value,prepend_inverse(nodes[k].inverse,ops[op]),nodes[k].word,depth};
                n.word[depth-1] = op;
                need(literal(n.value,n.inverse) == identity(),"state inverse");
                const auto inserted = seen.emplace(value,nodes.size());
                need(inserted.second,"duplicate insertion"); nodes.push_back(n);
            }
        begin = next_begin; end = nodes.size(); counts[depth] = end-begin;
    }
    return nodes;
}
Mat target(std::array<unsigned,3> w) {
    Mat out{};
    for (unsigned j = 0; j < 3; ++j) out[4*j] = static_cast<Mask>(1U << w[j]);
    return out;
}
void emit_word(const Node& p, const Node& q) {
    std::cout << '[';
    unsigned count = 0;
    for (const Node* n : {&p,&q})
        for (unsigned i = 0; i < n->length; ++i) {
            if (count++) std::cout << ',';
            std::cout << n->word[i];
        }
    std::cout << ']';
}
void raw_coverage(const std::vector<Node>& nodes, const std::vector<Gate>& ops) {
    std::unordered_map<Mat,unsigned,Hash> seen;
    seen.reserve(CAPACITY);
    for (const Node& n : nodes) need(seen.emplace(n.value,n.length).second,"raw uniqueness");
    std::size_t words = 0;
    for (unsigned a = 0; a < 56; ++a) {
        const Mat first = literal(identity(),factor(ops[a]));
        need(seen.find(first) != seen.end(),"raw first missing");
        for (unsigned b = 0; b < 56; ++b) {
            const Mat pair = literal(first,factor(ops[b]));
            need(seen.find(pair) != seen.end(),"raw pair missing");
            for (unsigned c = 0; c < 56; ++c) {
                const Mat triple = literal(pair,factor(ops[c]));
                need(seen.find(triple) != seen.end(),"raw triple missing");
                ++words;
            }
        }
    }
    need(words == 175616,"raw word coverage");
}
void join_controls(const std::vector<Node>& nodes,
                   const std::unordered_map<Mat,std::size_t,Hash>& table,
                   const Shifts& shifts) {
    // Every target below has a coordinate word of length at most six.
    const std::array<std::array<unsigned,3>,8> fixtures{{
        {0,0,0},{1,0,0},{2,0,0},{2,1,0},
        {2,2,0},{2,2,1},{2,2,2},{6,1,2}}};
    for (const auto& w : fixtures) {
        bool hit = false;
        for (const Node& p : nodes) {
            Mat needed{};
            for (unsigned i = 0; i < 3; ++i)
                for (unsigned j = 0; j < 3; ++j)
                    needed[3*i+j] = shifts[w[j]][p.inverse[3*i+j]];
            const auto found = table.find(needed);
            if (found == table.end()) continue;
            need(literal(p.value,nodes[found->second].value) == target(w),"positive endpoint");
            hit = true; break;
        }
        need(hit,"positive join missing");
    }
}
void run() {
    const auto ops = gates(); const auto shifts = right_shifts();
    self_checks(ops,shifts);
    std::array<std::size_t,4> counts{};
    const auto nodes = inventory(ops,shifts,counts);
    std::unordered_map<Mat,std::size_t,Hash> table;
    table.reserve(CAPACITY);
    for (std::size_t i = 0; i < nodes.size(); ++i)
        need(table.emplace(nodes[i].value,i).second,"inventory uniqueness");
    raw_coverage(nodes,ops);
    join_controls(nodes,table,shifts);
    const auto dist = distances();
    std::size_t endpoints = 0, lookups = 0, hits = 0;
    std::cout << "{\"new_states\":[" << counts[0] << ',' << counts[1] << ','
              << counts[2] << ',' << counts[3] << "],\"distances\":[";
    for (unsigned i = 0; i < 12; ++i) { if (i) std::cout << ','; std::cout << dist[i]; }
    std::cout << "],\"multiplication\":[";
    for (unsigned a = 0; a < 12; ++a) {
        if (a) std::cout << ',';
        std::cout << '[';
        for (unsigned b = 0; b < 12; ++b) {
            if (b) std::cout << ',';
            std::cout << mul(a,b);
        }
        std::cout << ']';
    }
    std::cout << "],\"hits\":[";
    for (unsigned a = 0; a < 12; ++a)
        for (unsigned b = 0; b < 12; ++b)
            for (unsigned c = 0; c < 12; ++c) {
                const std::array<unsigned,3> w{a,b,c};
                if (dist[a]+dist[b]+dist[c] < 7) continue;
                ++endpoints;
                for (const Node& p : nodes) {
                    Mat needed{};
                    for (unsigned i = 0; i < 3; ++i)
                        for (unsigned j = 0; j < 3; ++j)
                            needed[3*i+j] = shifts[w[j]][p.inverse[3*i+j]];
                    ++lookups;
                    const auto found = table.find(needed);
                    if (found == table.end()) continue;
                    const Node& q = nodes[found->second];
                    need(literal(p.value,q.value) == target(w),"join endpoint");
                    if (hits++) std::cout << ',';
                    std::cout << "{\"target\":[" << a << ',' << b << ',' << c << "],\"word\":";
                    emit_word(p,q); std::cout << '}';
                    break;
                }
            }
    std::cout << "],\"endpoint_count\":" << endpoints << ",\"lookups\":" << lookups
              << ",\"total_states\":" << nodes.size() << "}\n";
    need(std::cout.good(),"output write");
}
int main() {
    try { run(); return 0; }
    catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
