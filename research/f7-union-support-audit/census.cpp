// Independent singleton-prefix census. Nick Petalas. Apache-2.0.
#include <array>
#include <bit>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string_view>

namespace {
constexpr int max_length = 20;
constexpr int max_side = max_length / 2;

struct Bits {
    std::array<std::uint64_t, 2> words{};
    bool contains(int x) const {
        return (words[static_cast<unsigned>(x) / 64U] >> (x % 64)) & 1U;
    }
    void insert(int x) { words[static_cast<unsigned>(x) / 64U] |= std::uint64_t{1} << (x % 64); }
    int size() const { return std::popcount(words[0]) + std::popcount(words[1]); }
};

struct Node {
    Bits visited, same, cross;
    std::array<std::array<int, max_side>, 2> points{};
    std::array<int, 2> sizes{1, 0};
    int position = 0;
    int used = 0;
};

struct Config {
    int n, length;
    std::array<int, 2> goal;
    bool prune;
    std::uint64_t cap;
};

struct Totals {
    std::uint64_t attempts = 0, entered = 1, leaves = 0, hits = 0;
    std::uint64_t restoration = 0, size = 0, same = 0, cross = 0;
    bool complete = false;
};

std::uint64_t number(std::string_view text) {
    std::uint64_t value = 0;
    auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        throw std::invalid_argument("expected an unsigned decimal integer");
    }
    return value;
}

Config parse(char** argv) {
    std::array<std::uint64_t, 6> v{};
    for (unsigned i = 0; i < v.size(); ++i) v[i] = number(argv[i + 1]);
    if (v[0] < 2 || v[0] > 7 || v[1] < 2 * v[0] || v[1] > max_length || v[1] % 2 != 0 ||
        v[2] < 1 || v[3] < 1 || v[2] > v[1] / 2 || v[3] > v[1] / 2 || v[4] > 1) {
        throw std::invalid_argument("require 2<=n<=7, even 2n<=L<=20, 1<=s,t<=L/2, mode=0 or 1");
    }
    return {static_cast<int>(v[0]), static_cast<int>(v[1]),
            {static_cast<int>(v[2]), static_cast<int>(v[3])}, v[4] == 1, v[5]};
}

int pairs(int size) { return size * (size - 1) / 2; }

bool extend(Node& next, int label, int depth, const Config& c) {
    next.position ^= 1 << label;
    if (label == next.used) ++next.used;
    const int remaining = c.length - depth;
    if (std::popcount(static_cast<unsigned>(next.position)) + 2 * (c.n - next.used) > remaining) {
        return false;
    }
    if (next.visited.contains(next.position)) return true;
    const unsigned side = static_cast<unsigned>(depth % 2);
    if (next.sizes[side] >= c.goal[side]) throw std::logic_error("point capacity exceeded");
    for (int j = 0; j < next.sizes[side]; ++j) {
        next.same.insert(next.position ^ next.points[side][static_cast<unsigned>(j)]);
    }
    for (int j = 0; j < next.sizes[1U - side]; ++j) {
        next.cross.insert(next.position ^ next.points[1U - side][static_cast<unsigned>(j)]);
    }
    next.points[side][static_cast<unsigned>(next.sizes[side]++)] = next.position;
    next.visited.insert(next.position);
    return true;
}

bool viable(const Node& node, int depth, const Config& c, Totals& totals) {
    // Only nonclosing positions can add distinct points in a restored word.
    if (depth < c.length &&
        (node.sizes[0] + c.length / 2 - 1 - depth / 2 < c.goal[0] ||
         node.sizes[1] + c.length / 2 - (depth + 1) / 2 < c.goal[1])) {
        ++totals.size;
        return false;
    }
    if (!c.prune) return true;
    const int half = 1 << (c.n - 1);
    const int future_same = pairs(c.goal[0]) + pairs(c.goal[1]) - pairs(node.sizes[0]) - pairs(node.sizes[1]);
    if (node.same.size() + future_same < half - 1) {
        ++totals.same;
        return false;
    }
    const int future_cross = c.goal[0] * c.goal[1] - node.sizes[0] * node.sizes[1];
    if (node.cross.size() + future_cross < half) {
        ++totals.cross;
        return false;
    }
    return true;
}

void leaf(const Node& node, const Config& c, const std::array<int, max_length>& word,
          Totals& totals, std::ofstream& hits) {
    if (node.position != 0 || node.used != c.n || node.sizes != c.goal) return;
    if (node.visited.size() != node.sizes[0] + node.sizes[1]) throw std::logic_error("distinct-point invariant");
    if (node.same.contains(0) || node.cross.contains(0)) throw std::logic_error("nonzero-pair invariant");
    ++totals.leaves;
    if (node.same.size() + node.cross.size() != (1 << c.n) - 1) return;
    ++totals.hits;
    for (int i = 0; i < c.length; ++i) hits << word[static_cast<unsigned>(i)];
    hits << '\n';
}

std::uint64_t iteration_bound(const Config& c) {
    // At most n^d nodes at depth d. One descent and one return per edge.
    std::uint64_t level = 1, nodes = 1;
    for (int d = 1; d <= c.length; ++d) {
        level *= static_cast<unsigned>(c.n);
        nodes += level;
    }
    return 2 * nodes;
}

Totals enumerate(const Config& c, std::ofstream& hits) {
    std::array<Node, max_length + 1> stack{};
    std::array<int, max_length + 1> next_label{};
    std::array<int, max_length> word{};
    stack[0].visited.insert(0);
    Totals totals;
    int depth = 0;
    const auto bound = iteration_bound(c);
    for (std::uint64_t iteration = 0; iteration < bound; ++iteration) {
        const auto index = static_cast<unsigned>(depth);
        if (depth == c.length || next_label[index] >= c.n || next_label[index] > stack[index].used) {
            if (depth == c.length) leaf(stack[index], c, word, totals, hits);
            if (depth == 0) { totals.complete = true; return totals; }
            --depth;
            continue;
        }
        if (c.cap != 0 && totals.attempts == c.cap) return totals;
        ++totals.attempts;
        const int label = next_label[index]++;
        Node candidate = stack[index];
        const int position = candidate.position ^ (1 << label);
        const auto side = static_cast<unsigned>((depth + 1) % 2);
        if (!candidate.visited.contains(position) && candidate.sizes[side] == c.goal[side]) {
            ++totals.size;
            continue;
        }
        if (!extend(candidate, label, depth + 1, c)) { ++totals.restoration; continue; }
        if (!viable(candidate, depth + 1, c, totals)) continue;
        word[index] = label;
        ++depth;
        stack[index + 1] = candidate;
        next_label[index + 1] = 0;
        ++totals.entered;
    }
    throw std::logic_error("finite tree bound exhausted");
}

void report(const Config& c, const Totals& t) {
    if (t.attempts + 1 != t.entered + t.restoration + t.size + t.same + t.cross) {
        throw std::logic_error("extension accounting invariant");
    }
    std::cout << "{\"n\":" << c.n << ",\"length\":" << c.length
              << ",\"split\":[" << c.goal[0] << ',' << c.goal[1] << "]"
              << ",\"prune\":" << (c.prune ? "true" : "false")
              << ",\"cap\":" << c.cap << ",\"complete\":" << (t.complete ? "true" : "false")
              << ",\"attempts\":" << t.attempts << ",\"entered\":" << t.entered
              << ",\"candidate_leaves\":" << t.leaves << ",\"hits\":" << t.hits
              << ",\"restoration_prunes\":" << t.restoration << ",\"size_prunes\":" << t.size
              << ",\"same_prunes\":" << t.same << ",\"cross_prunes\":" << t.cross << "}\n";
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 8) throw std::invalid_argument("usage: census n L s t mode cap hits-file");
        const Config c = parse(argv);
        std::ofstream hits(argv[7]);
        hits.exceptions(std::ios::failbit | std::ios::badbit);
        const Totals totals = enumerate(c, hits);
        hits.close();
        report(c, totals);
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("failed to write summary");
        return totals.complete ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
