// Philipp / mightyOil, substantial OpenAI Codex assistance. Apache-2.0.
// Fresh ternary-row implementation of the standard radius4 / middle / radius4 test.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using Key = std::uint64_t;
struct Gate { int target, source, sign; };

int main(int argc, char** argv) {
  try {
    if (argc != 5) throw std::runtime_error("usage: ternary N PERM BALL REPORT");
    const int n = std::stoi(argv[1]);
    if (n < 2 || n > 6) throw std::runtime_error("dimension 2..6 required");
    const std::string permutation(argv[2]);
    if (int(permutation.size()) != n) throw std::runtime_error("permutation length");
    // Digits denote +e_j; a..f denote -e_j (used by the distance-nine control).
    std::vector<int> p(n), sign(n, 1), inverse(n, -1);
    for (int i = 0; i < n; ++i) {
      sign[i] = permutation[i] >= 'a' && permutation[i] <= 'f' ? -1 : 1;
      p[i] = permutation[i] - (sign[i] == -1 ? 'a' : '0');
      if (p[i] < 0 || p[i] >= n || inverse[p[i]] != -1) throw std::runtime_error("permutation");
      inverse[p[i]] = i;
    }
    int row_base = 1;
    for (int i = 0; i < n; ++i) row_base *= 3;
    std::vector<Key> place(n, 1);
    for (int i = 1; i < n; ++i) place[i] = place[i-1] * row_base;
    std::vector<int> negative(row_base), right_permuted(row_base);
    std::vector<int> plus(row_base * row_base), minus(row_base * row_base);
    for (int a = 0; a < row_base; ++a) {
      std::vector<int> digits(n);
      int residual = a;
      for (int c = 0; c < n; ++c) { digits[c] = residual % 3; residual /= 3; }
      int digit_place = 1;
      for (int c = 0; c < n; ++c) {
        negative[a] += ((3-digits[c]) % 3) * digit_place;
        right_permuted[a] += ((3 + sign[inverse[c]]*digits[inverse[c]]) % 3) * digit_place;
        digit_place *= 3;
      }
      for (int b = 0; b < row_base; ++b) {
        int other = b, radix = 1;
        for (int c = 0; c < n; ++c) {
          plus[a*row_base+b] += ((digits[c] + other%3) % 3) * radix;
          minus[a*row_base+b] += ((digits[c] - other%3 + 3) % 3) * radix;
          other /= 3; radix *= 3;
        }
      }
    }
    std::vector<Gate> gates;
    for (int t = 0; t < n; ++t) {
      gates.push_back({t, t, 0});
      for (int s = 0; s < n; ++s) if (t != s)
        for (int sign : {1, -1}) gates.push_back({t, s, sign});
    }
    auto change = [&](Key state, Gate gate) {
      const int a = state / place[gate.target] % row_base;
      const int b = state / place[gate.source] % row_base;
      const int replacement = gate.target == gate.source ? negative[a]
        : (gate.sign == 1 ? plus[a*row_base+b] : minus[a*row_base+b]);
      return state - Key(a)*place[gate.target] + Key(replacement)*place[gate.target];
    };
    Key identity = 0;
    int basis = 1;
    for (int i = 0; i < n; ++i) { identity += Key(basis)*place[i]; basis *= 3; }
    std::unordered_map<Key, unsigned char> distance;
    distance.reserve(n == 6 ? 2500000 : 600000);
    distance.emplace(identity, 0);
    std::vector<Key> queue{identity};
    std::array<std::uint64_t, 5> layers{1,0,0,0,0};
    for (std::size_t cursor = 0; cursor < queue.size(); ++cursor) {
      const Key state = queue[cursor];
      const int depth = distance.at(state);
      if (depth == 4) continue;
      for (const Gate gate : gates) {
        const Key next = change(state, gate);
        if (distance.emplace(next, depth+1).second) {
          queue.push_back(next); ++layers[depth+1];
        }
      }
    }
    std::uint64_t transitions = 0, direct_hits = 0, middle_hits = 0;
    int minimum = 99;
    for (Key state : queue) {
      Key transformed = 0;
      for (int r = 0; r < n; ++r)
        transformed += Key(right_permuted[state/place[r]%row_base]) * place[r];
      auto found = distance.find(transformed);
      if (found != distance.end()) {
        ++direct_hits;
        minimum = std::min(minimum, int(distance.at(state)) + int(found->second));
      }
      for (Gate gate : gates) {
        ++transitions;
        found = distance.find(change(transformed, gate));
        if (found != distance.end()) {
          ++middle_hits;
          minimum = std::min(minimum, int(distance.at(state)) + 1 + int(found->second));
        }
      }
    }
    std::vector<std::pair<Key, unsigned char>> ordered(distance.begin(), distance.end());
    std::sort(ordered.begin(), ordered.end());
    std::ofstream ball(argv[3], std::ios::binary);
    if (!ball) throw std::runtime_error("ball open");
    for (auto entry : ordered) {
      for (int i = 0; i < 8; ++i) ball.put(char((entry.first >> (8*i)) & 255));
      ball.put(char(entry.second));
    }
    ball.close(); if (!ball) throw std::runtime_error("ball write");
    std::ofstream out(argv[4]);
    if (!out) throw std::runtime_error("report open");
    out << "{\"n\":" << n << ",\"permutation\":\"" << permutation << "\",\"layers\":[";
    for (int i=0;i<5;++i) out << (i ? "," : "") << layers[i];
    out << "],\"states\":" << queue.size() << ",\"generators\":" << gates.size()
        << ",\"transitions\":" << transitions << ",\"direct_hits\":" << direct_hits
        << ",\"middle_hits\":" << middle_hits << ",\"minimum_through_nine\":";
    if (minimum == 99) out << "null"; else out << minimum;
    out << "}\n"; out.close(); if (!out) throw std::runtime_error("report write");
    std::cout << "PASS_TERNARY n=" << n << " states=" << queue.size() << " transitions=" << transitions << '\n';
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n'; return 1;
  }
}
