// By conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
// Exact finite simple22 census: A high(6,4,4)/low(2,2,2,2), B
// high(4,4,4)/low(4,2,2,2). An incomplete bounded run is inconclusive.
// Ross Richardson/PR943 supplies the paired-readout model; Douglas
// Colkitt/PR1185 supplies the retained six-source result and Gray upper bound.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Clock = std::chrono::steady_clock;
constexpr int MAX_BLOCKS = 10, MAX_CANDIDATES = 1024, WORDS = MAX_CANDIDATES / 64;
using LowWord = std::vector<int>;
using Counts = std::array<int, 3>;

int parity(int x) { return __builtin_popcount(static_cast<unsigned>(x)) & 1; }
int bit_count(int x) { return __builtin_popcount(static_cast<unsigned>(x)); }

struct Bits {
  std::array<uint64_t, WORDS> words{};
  void add(int x) { words[x / 64] |= uint64_t(1) << (x % 64); }
  void erase(int x) { words[x / 64] &= ~(uint64_t(1) << (x % 64)); }
  int size() const {
    int n = 0;
    for (auto word : words) n += __builtin_popcountll(word);
    return n;
  }
  bool empty() const {
    for (auto word : words) if (word) return false;
    return true;
  }
  bool intersects(const Bits& other) const {
    for (int i = 0; i < WORDS; ++i) if (words[i] & other.words[i]) return true;
    return false;
  }
  template <class F> void each(F f) const {
    for (int i = 0; i < WORDS; ++i) {
      uint64_t word = words[i];
      while (word) {
        int bit = __builtin_ctzll(word);
        f(i * 64 + bit);
        word &= word - 1;
      }
    }
  }
  int first() const {
    for (int i = 0; i < WORDS; ++i)
      if (words[i]) return i * 64 + __builtin_ctzll(words[i]);
    throw std::runtime_error("empty domain has no first member");
  }
};

struct PathType {
  int mask, end;
  Counts counts;
  std::vector<int> word;
};
struct Candidate {
  int normal, start, end, mask, length;
  Counts counts;
};

struct OracleResult {
  bool restored;
  int coverage, distinct;
  std::array<int, 7> counts;
};
OracleResult independent_oracle(const std::vector<int>& word) {
  int state = 0;
  std::set<int> points, differences;
  std::array<int, 7> counts{};
  for (int label : word) {
    if (label < 0 || label >= 7) throw std::runtime_error("oracle label out of range");
    points.insert(state);
    state ^= 1 << label;
    ++counts[label];
  }
  for (int a : points) for (int b : points) differences.insert(a ^ b);
  return {state == 0, static_cast<int>(differences.size()), static_cast<int>(points.size()), counts};
}

LowWord canonical(const LowWord& input, bool distinguished) {
  int length = static_cast<int>(input.size());
  LowWord best(length, 9);
  for (int direction : {-1, 1}) for (int rotation = 0; rotation < length; ++rotation) {
    LowWord candidate(length);
    std::array<int,4> labels{-1,-1,-1,-1}; int next = 0;
    if (distinguished) { labels[0] = 0; next = 1; }
    for (int i = 0; i < length; ++i) {
      int label = input[(rotation + direction * i + length * length) % length];
      if (labels[label] == -1) labels[label] = next++;
      candidate[i] = labels[label];
    }
    best = std::min(best, candidate);
  }
  return best;
}

std::vector<LowWord> universal_templates(bool distinguished) {
  std::vector<LowWord> result;
  std::set<LowWord> orbits;
  int length = distinguished ? 10 : 8;
  LowWord word(length);
  std::array<int, 4> counts{};
  int generated = 0, universal = 0;
  std::function<void(int, int)> generate = [&](int position, int maximum) {
    if (position == length) {
      ++generated;
      std::set<int> points, differences;
      int state = 0;
      for (int label : word) { points.insert(state); state ^= 1 << label; }
      if (state) throw std::runtime_error("unrestored generated low word");
      for (int a : points) for (int b : points) differences.insert(a ^ b);
      if (differences.size() == 16) { ++universal; orbits.insert(canonical(word, distinguished)); }
      return;
    }
    // All interchangeable labels are ordered by first appearance. In B,
    // four-use0 is distinguished and may appear after the first two-use1.
    for (int label = 0; label <= std::min(3, maximum + 1); ++label)
      if (counts[label] < (distinguished && label == 0 ? 4 : 2)) {
      ++counts[label]; word[position] = label;
      generate(position + 1, std::max(maximum, label));
      --counts[label];
    }
  };
  generate(0, distinguished ? 0 : -1);
  if (generated != (distinguished ? 3150 : 105) || universal != (distinguished ? 1310 : 26))
    throw std::runtime_error("rooted low-word census mismatch");
  result.assign(orbits.begin(), orbits.end());
  if (result.size() != (distinguished ? 77 : 5)) throw std::runtime_error("low-dihedral orbit count mismatch");
  return result;
}

struct Tables {
  std::vector<PathType> paths;
  std::vector<Candidate> candidates;
  std::array<std::array<uint8_t, 256>, 256> sums{};
  // Tags1/2: next/previous endpoint joins; tag4: unique-difference cover.
  std::array<std::vector<Bits>, 9> support;
  Tables() {
    for (int a = 0; a < 256; ++a) for (int b = 0; b < 256; ++b) {
      int covered = 0;
      for (int x = 0; x < 8; ++x) if (a >> x & 1)
        for (int y = 0; y < 8; ++y) if (b >> y & 1) covered |= 1 << (x ^ y);
      sums[a][b] = static_cast<uint8_t>(covered);
    }
    std::map<std::tuple<int, int, Counts>, std::vector<int>> normalized;
    Counts counts{};
    std::vector<int> word;
    std::function<void(int, int)> generate = [&](int state, int mask) {
      normalized.emplace(std::make_tuple(mask, state, counts), word);
      for (int label = 0; label < 3; ++label) {
        int next = state ^ (1 << label);
        if (mask >> next & 1) continue;
        ++counts[label]; word.push_back(label);
        generate(next, mask | (1 << next));
        word.pop_back(); --counts[label];
      }
    };
    generate(0, 1);
    if (normalized.size() != 106) throw std::runtime_error("normalized Q3 path count differs from106");
    for (const auto& [key, representative] : normalized) {
      const auto& [mask, end, frequency] = key;
      paths.push_back({mask, end, frequency, representative});
    }
    for (int normal = 0; normal < static_cast<int>(paths.size()); ++normal) {
      const auto& path = paths[normal];
      for (int start = 0; start < 8; ++start) {
        int mask = 0;
        for (int p = 0; p < 8; ++p) if (path.mask >> p & 1) mask |= 1 << (p ^ start);
        candidates.push_back({normal, start, path.end ^ start, mask,
                              static_cast<int>(path.word.size()), path.counts});
      }
    }
    if (candidates.size() > MAX_CANDIDATES) throw std::runtime_error("candidate bitset is too small");
    for (int tag : {1, 2, 4, 5, 6, 8}) {
      support[tag].resize(candidates.size());
      for (int i = 0; i < static_cast<int>(candidates.size()); ++i)
        for (int j = 0; j < static_cast<int>(candidates.size()); ++j) {
          const auto& a = candidates[i]; const auto& b = candidates[j];
          bool allowed = (!(tag & 1) || a.end == b.start)
                      && (!(tag & 2) || a.start == b.end)
                      && (!(tag & 4) || sums[a.mask][b.mask] == 255)
                      && (!(tag & 8) || (a.mask & b.mask) == 0);
          if (allowed) support[tag][i].add(j);
        }
    }
  }
};

struct Statistics {
  uint64_t nodes = 0, arc_removed = 0, count_removed = 0, cover_removed = 0;
  uint64_t compositions = 0, capacity_survivors = 0, root_consistent = 0, leaves = 0;
};
using Domains = std::array<Bits, MAX_BLOCKS>;

struct Engine {
  const Tables& tables;
  LowWord low_word, low_points{};
  int blocks;
  Counts target;
  std::array<std::vector<std::pair<int, int>>, 16> pairs;
  std::array<std::array<int, MAX_BLOCKS>, MAX_BLOCKS> tags{};
  std::array<std::array<std::vector<int>, 16>, MAX_BLOCKS> neighbors;
  Statistics stats;
  Clock::time_point deadline;
  Clock::time_point began = Clock::now(), next_report = began + std::chrono::seconds(5);
  bool timed_out = false, found = false;
  bool require_cover, conditional_cover;
  Domains witness{};
  explicit Engine(const Tables& t, LowWord low, Counts expected, Clock::time_point end,
                  bool cover = true, bool conditional = true)
      : tables(t), low_word(low), low_points(low.size()), blocks(static_cast<int>(low.size())),
        target(expected), deadline(end), require_cover(cover), conditional_cover(conditional) {
    if (blocks < 1 || blocks > MAX_BLOCKS) throw std::runtime_error("invalid block count");
    int state = 0;
    std::set<int> distinct;
    for (int i = 0; i < blocks; ++i) {
      low_points[i] = state; distinct.insert(state); state ^= 1 << low_word[i];
    }
    if (state) throw std::runtime_error("engine requires a restored low projection");
    for (int i = 0; i < blocks; ++i) for (int j = i; j < blocks; ++j)
      pairs[low_points[i] ^ low_points[j]].emplace_back(i, j);
    for (int difference = 0; difference < 16; ++difference) {
      if (pairs[difference].empty()) throw std::runtime_error("low projection is not universal");
      if (require_cover && difference && pairs[difference].size() == 1) {
        auto [i, j] = pairs[difference][0]; tags[i][j] |= 4; tags[j][i] |= 4;
      }
    }
    for (int i = 0; i < blocks; ++i) for (int j = 0; j < blocks; ++j) if (i != j) {
      if ((i + 1) % blocks == j) tags[i][j] |= 1;
      if ((j + 1) % blocks == i) tags[i][j] |= 2;
      if (low_points[i] == low_points[j]) tags[i][j] |= 8;
      neighbors[i][low_points[i] ^ low_points[j]].push_back(j);
      if (tags[i][j] >= static_cast<int>(tables.support.size()) || (tags[i][j] && tables.support[tags[i][j]].empty()))
        throw std::runtime_error("unsupported binary-relation tag");
    }
  }

  bool time_limit() {
    auto now = Clock::now();
    if (now >= next_report) {
      std::cerr << "PROGRESS seconds=" << std::chrono::duration<double>(now - began).count()
                << " compositions=" << stats.compositions << " capacity_survivors=" << stats.capacity_survivors
                << " nodes=" << stats.nodes << " root_consistent=" << stats.root_consistent << '\n';
      next_report = now + std::chrono::seconds(5);
    }
    if (now < deadline) return false;
    timed_out = true;
    return true;
  }

  bool capacity(const LowWord& gaps) const {
    std::array<int, 16> evens{}, odds{}, sizes{};
    int high_parity = 0;
    for (int i = 0; i < blocks; ++i) {
      int size = gaps[i] + 1;
      if (size > 8) return false;
      int point = low_points[i];
      int even = (size + (high_parity == 0)) / 2;
      evens[point] += even; odds[point] += size - even; sizes[point] += size;
      high_parity ^= gaps[i] & 1;
    }
    if (high_parity) return false;
    int even_zero = 0, odd_zero = 0;
    for (int point = 0; point < 16; ++point) {
      if (sizes[point] > 8) return false;
      even_zero += evens[point] * (evens[point] - 1) / 2 + odds[point] * (odds[point] - 1) / 2;
      odd_zero += evens[point] * odds[point];
    }
    if (even_zero < 3 || odd_zero < 4) return false;
    for (int d = 1; d < 16; ++d) {
      int even = 0, odd = 0;
      for (int a = 0; a < 16; ++a) {
        int b = a ^ d;
        if (a >= b) continue;
        even += evens[a] * evens[b] + odds[a] * odds[b];
        odd += evens[a] * odds[b] + odds[a] * evens[b];
      }
      if (even < 4 || odd < 4) return false;
    }
    return true;
  }

  Domains domains_for(const LowWord& gaps) const {
    Domains domains;
    int start_parity = 0;
    for (int i = 0; i < blocks; ++i) {
      for (int id = 0; id < static_cast<int>(tables.candidates.size()); ++id) {
        const auto& c = tables.candidates[id];
        if (c.length == gaps[i] && parity(c.start) == start_parity && (i || c.start == 0))
          domains[i].add(id);
      }
      start_parity ^= gaps[i] & 1;
    }
    return domains;
  }

  // Every deletion has a necessary-condition justification: lack of binary
  // support, incompatible remaining coordinate totals, or a missing mask even
  // after independently unioning all remaining domain choices.
  bool propagate(Domains& domains) {
    bool changed = true;
    while (changed) {
      changed = false;
      for (int i = 0; i < blocks; ++i) {
        if (domains[i].empty()) return false;
        for (int j = 0; j < blocks; ++j) if (tags[i][j]) {
          Bits remove;
          domains[i].each([&](int id) {
            if (!tables.support[tags[i][j]][id].intersects(domains[j])) remove.add(id);
          });
          remove.each([&](int id) { domains[i].erase(id); ++stats.arc_removed; changed = true; });
          if (domains[i].empty()) return false;
        }
      }
      std::array<Counts, MAX_BLOCKS> minima{}, maxima{};
      Counts sum_min{}, sum_max{};
      for (int i = 0; i < blocks; ++i) {
        minima[i].fill(8);
        domains[i].each([&](int id) {
          for (int label = 0; label < 3; ++label) {
            int value = tables.candidates[id].counts[label];
            minima[i][label] = std::min(minima[i][label], value);
            maxima[i][label] = std::max(maxima[i][label], value);
          }
        });
        for (int label = 0; label < 3; ++label) {
          sum_min[label] += minima[i][label]; sum_max[label] += maxima[i][label];
        }
      }
      for (int label = 0; label < 3; ++label)
        if (sum_min[label] > target[label] || sum_max[label] < target[label]) return false;
      for (int i = 0; i < blocks; ++i) {
        Bits remove;
        domains[i].each([&](int id) {
          for (int label = 0; label < 3; ++label) {
            int value = tables.candidates[id].counts[label];
            if (sum_min[label] - minima[i][label] + value > target[label]
                || sum_max[label] - maxima[i][label] + value < target[label]) remove.add(id);
          }
        });
        remove.each([&](int id) { domains[i].erase(id); ++stats.count_removed; changed = true; });
        if (domains[i].empty()) return false;
      }
      if (!require_cover) continue;
      std::array<int, MAX_BLOCKS> union_masks{}, self_sums{};
      for (int i = 0; i < blocks; ++i) domains[i].each([&](int id) {
        int mask = tables.candidates[id].mask;
        union_masks[i] |= mask; self_sums[i] |= tables.sums[mask][mask];
      });
      std::array<std::array<int, 16>, MAX_BLOCKS> excluding{};
      for (int difference = 0; difference < 16; ++difference) {
        int possible = 0;
        for (auto [a, b] : pairs[difference]) {
          int contribution = a == b ? self_sums[a] : tables.sums[union_masks[a]][union_masks[b]];
          possible |= contribution;
          for (int i = 0; i < blocks; ++i) if (i != a && i != b) excluding[i][difference] |= contribution;
        }
        if (possible != 255) return false;
      }
      if (!conditional_cover) continue;
      for (int i = 0; i < blocks; ++i) {
        Bits remove;
        domains[i].each([&](int id) {
          int mask = tables.candidates[id].mask;
          for (int difference = 0; difference < 16; ++difference) {
            int possible = excluding[i][difference];
            if (difference == 0) possible |= tables.sums[mask][mask];
            for (int j : neighbors[i][difference]) possible |= tables.sums[mask][union_masks[j]];
            if (possible != 255) {
              remove.add(id); return;
            }
          }
        });
        remove.each([&](int id) { domains[i].erase(id); ++stats.cover_removed; changed = true; });
        if (domains[i].empty()) return false;
      }
    }
    return true;
  }

  bool search(Domains domains, bool root = false) {
    ++stats.nodes;
    if ((stats.nodes & 1023) == 0 && time_limit()) return false;
    if (!propagate(domains)) return false;
    if (root) ++stats.root_consistent;
    int chosen = -1, smallest = MAX_CANDIDATES + 1, best_degree = -1;
    for (int i = 0; i < blocks; ++i) {
      int size = domains[i].size(), degree = 0;
      for (int j = 0; j < blocks; ++j) degree += tags[i][j] != 0;
      if (size > 1 && (size < smallest || (size == smallest && degree > best_degree))) {
        chosen = i; smallest = size; best_degree = degree;
      }
    }
    if (chosen == -1) {
      ++stats.leaves;
      auto word = word_from(domains); auto replay = independent_oracle(word);
      if (!replay.restored || replay.distinct != static_cast<int>(word.size())
          || (require_cover && replay.coverage != 128))
        throw std::runtime_error("singleton leaf failed ordinary-word replay");
      for (int label = 0; label < 3; ++label)
        if (replay.counts[label] != target[label]) throw std::runtime_error("singleton leaf has wrong counts");
      witness = domains; found = true; return true;
    }
    bool success = false;
    domains[chosen].each([&](int id) {
      if (success || timed_out) return;
      Domains child = domains; child[chosen] = Bits{}; child[chosen].add(id);
      if (search(child)) success = true;
    });
    return success;
  }

  std::vector<int> word_from(const Domains& domains) const {
    std::vector<int> word;
    int high_state = 0;
    for (int i = 0; i < blocks; ++i) {
      if (domains[i].size() != 1) throw std::runtime_error("word reconstruction requires singleton domains");
      const auto& c = tables.candidates[domains[i].first()];
      if (c.start != high_state) throw std::runtime_error("reconstruction endpoint mismatch");
      for (int label : tables.paths[c.normal].word) { word.push_back(label); high_state ^= 1 << label; }
      if (high_state != c.end) throw std::runtime_error("reconstruction endpoint failed");
      word.push_back(low_word[i] + 3);
    }
    if (high_state) throw std::runtime_error("reconstruction did not restore");
    return word;
  }

  bool enumerate() {
    LowWord gaps(blocks);
    int total = std::accumulate(target.begin(), target.end(), 0);
    std::function<void(int, int)> visit = [&](int position, int remaining) {
      if (found || timed_out) return;
      if (position == blocks) {
        if (remaining) return;
        ++stats.compositions;
        if ((stats.compositions & 255) == 0 && time_limit()) return;
        if (!capacity(gaps)) return;
        ++stats.capacity_survivors;
        search(domains_for(gaps), true);
        return;
      }
      for (int length = 0; length <= std::min(7, remaining); ++length) {
        gaps[position] = length; visit(position + 1, remaining - length);
        if (found || timed_out) return;
      }
    };
    visit(0, total);
    return !timed_out && !found;
  }
};

Domains fixed_domains(const Engine& engine, const std::vector<int>& word) {
  Domains domains;
  int cursor = 0, high_state = 0;
  for (int i = 0; i < engine.blocks; ++i) {
    int start = high_state, mask = 1 << high_state;
    Counts counts{};
    while (cursor < static_cast<int>(word.size()) && word[cursor] < 3) {
      int label = word[cursor++]; ++counts[label]; high_state ^= 1 << label; mask |= 1 << high_state;
    }
    if (cursor >= static_cast<int>(word.size()) || word[cursor++] != engine.low_word[i] + 3)
      throw std::runtime_error("fixed control low-projection mismatch");
    for (int id = 0; id < static_cast<int>(engine.tables.candidates.size()); ++id) {
      const auto& c = engine.tables.candidates[id];
      if (c.start == start && c.end == high_state && c.mask == mask && c.counts == counts) domains[i].add(id);
    }
    if (domains[i].size() != 1) throw std::runtime_error("fixed control is absent/ambiguous in path table");
  }
  if (cursor != static_cast<int>(word.size()) || high_state) throw std::runtime_error("fixed control did not close");
  return domains;
}

LowWord low_of(const std::vector<int>& word) {
  LowWord low;
  for (int label : word) if (label >= 3) low.push_back(label - 3);
  return low;
}

std::vector<int> canonical_full_word(const std::vector<int>& input, bool distinguished) {
  LowWord best(low_of(input).size(), 9);
  std::vector<int> result;
  int length = static_cast<int>(input.size());
  for (int direction : {-1, 1}) for (int rotation = 0; rotation < length; ++rotation) {
    std::vector<int> candidate;
    std::array<int, 7> labels{0,1,2,-1,-1,-1,-1}; int next = 3;
    if (distinguished) { labels[3] = 3; next = 4; }
    for (int i = 0; i < length; ++i) {
      int label = input[(rotation + direction * i + length * length) % length];
      if (labels[label] == -1) labels[label] = next++;
      candidate.push_back(labels[label]);
    }
    // A low-step boundary ends the last block. Rotating the word translates
    // its entire prefix set; reversing it also preserves differences.
    if (candidate.back() < 3) continue;
    LowWord low = low_of(candidate);
    if (low < best) { best = low; result = candidate; }
  }
  if (result.empty() || low_of(result) != canonical(low_of(input), distinguished))
    throw std::runtime_error("full-word canonicalization disagrees with low dihedral action");
  return result;
}

void controls(const Tables& tables, const std::vector<LowWord>& templates, bool distinguished,
              Clock::time_point deadline) {
  // Independently compare all2520/18900 raw permutations with the105/3150
  // first-occurrence representatives used by the production census.
  std::set<LowWord> raw_orbits;
  LowWord raw = distinguished ? LowWord{0,0,0,0,1,1,2,2,3,3} : LowWord{0,0,1,1,2,2,3,3};
  int raw_count = 0;
  do {
    ++raw_count;
    std::set<int> points, differences; int state = 0;
    for (int label : raw) { points.insert(state); state ^= 1 << label; }
    for (int a : points) for (int b : points) differences.insert(a ^ b);
    if (differences.size() == 16) raw_orbits.insert(canonical(raw, distinguished));
  } while (std::next_permutation(raw.begin(), raw.end()));
  if (raw_count != (distinguished ? 18900 : 2520)
      || std::vector<LowWord>(raw_orbits.begin(), raw_orbits.end()) != templates)
    throw std::runtime_error("raw low-word census disagrees with first-occurrence quotient");

  // Authentic universal simple24 fixture from the swapped Gray junction.
  // Low counts are2222/4222, and high counts844/842 exercise the entire
  // model without requiring an unknown length22 universal word.
  std::vector<int> original{0,1,0,2,0,1,0,5,2,3,4,3,6,3,4,3,5,3,4,3,6,3,4,3};
  const std::array<int,7> positive_mapping = distinguished ? std::array<int,7>{3,2,4,0,1,5,6}
                                                        : std::array<int,7>{1,3,4,0,2,5,6};
  std::vector<int> positive;
  for (int label : original) positive.push_back(positive_mapping[label]);
  positive = canonical_full_word(positive, distinguished);
  std::vector<int> negative_original{3,4,2,5,0,1,6,1,0,3,5,4,0,3,1,4,3,2,0,4,6,1};
  const std::array<int,7> negative_mapping{3,0,4,1,2,5,6};
  std::vector<int> negative;
  if (distinguished) for (int label : negative_original) negative.push_back(negative_mapping[label]);
  else for (int i = 0; i < 24; ++i) if (i != 9 && i != 11) negative.push_back(positive_mapping[original[i]]);
  negative = canonical_full_word(negative, distinguished);
  auto pos = independent_oracle(positive), neg = independent_oracle(negative);
  if (!pos.restored || pos.distinct != 24 || pos.coverage != 128
      || pos.counts != (distinguished ? std::array<int,7>{8,4,2,4,2,2,2} : std::array<int,7>{8,4,4,2,2,2,2}))
    throw std::runtime_error("simple24 universal positive fixture failed independent oracle");
  if (!neg.restored || neg.distinct != 22 || neg.coverage != (distinguished ? 126 : 116)
      || neg.counts != (distinguished ? std::array<int,7>{4,4,4,4,2,2,2} : std::array<int,7>{6,4,4,2,2,2,2}))
    throw std::runtime_error("simple22 noncover fixture failed independent oracle");
  if (!std::binary_search(templates.begin(), templates.end(), low_of(positive))
      || !std::binary_search(templates.begin(), templates.end(), low_of(negative)))
    throw std::runtime_error("fixed control low orbit is absent from generated list");
  Counts positive_counts = distinguished ? Counts{8,4,2} : Counts{8,4,4};
  Counts negative_counts = distinguished ? Counts{4,4,4} : Counts{6,4,4};
  Engine positive_engine(tables, low_of(positive), positive_counts, deadline);
  if (!positive_engine.search(fixed_domains(positive_engine, positive)) || positive_engine.timed_out)
    throw std::runtime_error("full CSP rejected fixed simple24 universal positive");
  auto reconstructed = independent_oracle(positive_engine.word_from(positive_engine.witness));
  if (reconstructed.coverage != 128 || reconstructed.distinct != 24) throw std::runtime_error("positive reconstruction failed");
  Engine negative_no_cover(tables, low_of(negative), negative_counts, deadline, false);
  if (!negative_no_cover.search(fixed_domains(negative_no_cover, negative)) || negative_no_cover.timed_out)
    throw std::runtime_error("known negative fixture failed endpoint/count/simplicity-only CSP");
  Engine negative_engine(tables, low_of(negative), negative_counts, deadline);
  if (negative_engine.search(fixed_domains(negative_engine, negative)) || negative_engine.timed_out)
    throw std::runtime_error("full CSP accepted fixed simple22 noncover negative");
  // Undo the junction swap: the full24-word remains universal, but visits
  // its origin twice. With cover checks disabled, only simplicity excludes
  // its otherwise valid paths, joins and multiplicities.
  auto unswapped = original; std::swap(unswapped[7], unswapped[8]);
  for (int& label : unswapped) label = positive_mapping[label];
  unswapped = canonical_full_word(unswapped, distinguished);
  auto repeated = independent_oracle(unswapped);
  if (!repeated.restored || repeated.coverage != 128 || repeated.distinct != 23)
    throw std::runtime_error("repeated-origin universal fixture failed ordinary-word oracle");
  Engine repeated_engine(tables, low_of(unswapped), positive_counts, deadline, false);
  if (repeated_engine.search(fixed_domains(repeated_engine, unswapped)) || repeated_engine.timed_out
      || repeated_engine.stats.arc_removed == 0)
    throw std::runtime_error("same-low disjointness accepted repeated-origin universal word");
  auto wrong_counts = positive_counts; --wrong_counts[0];
  Engine count_engine(tables, low_of(positive), wrong_counts, deadline, false);
  if (count_engine.search(fixed_domains(count_engine, positive)) || count_engine.timed_out)
    throw std::runtime_error("fixed word accepted an incorrect multiplicity target");
  Engine join_engine(tables, low_of(positive), positive_counts, deadline, false);
  auto wrong_join = fixed_domains(join_engine, positive);
  const auto first = tables.candidates[wrong_join[0].first()];
  wrong_join[0] = Bits{};
  for (int id = 0; id < static_cast<int>(tables.candidates.size()); ++id) {
    const auto& c = tables.candidates[id];
    if (c.normal == first.normal && c.start == (first.start ^ 1)) wrong_join[0].add(id);
  }
  if (wrong_join[0].size() != 1 || join_engine.search(wrong_join) || join_engine.timed_out)
    throw std::runtime_error("fixed paths accepted an incorrect joining endpoint");
  // Full search-path control: from the fixture's low orbit and true high
  // counts alone, gap enumeration, capacity, start domains, propagation and
  // branching must rediscover a universal simple24 word.
  Engine full_engine(tables, low_of(positive), positive_counts, deadline);
  bool full_exhausted = full_engine.enumerate();
  if (!full_engine.found || full_engine.timed_out || full_exhausted)
    throw std::runtime_error("full enumeration failed to rediscover a simple24 universal word");
  // Each capacity survivor calls search once at the root; additional nodes
  // therefore certify that the positive control also exercised branching.
  if (full_engine.stats.nodes <= full_engine.stats.capacity_survivors)
    throw std::runtime_error("full enumeration positive control did not exercise recursive branching");
  auto rediscovered = independent_oracle(full_engine.word_from(full_engine.witness));
  if (!rediscovered.restored || rediscovered.distinct != 24 || rediscovered.coverage != 128)
    throw std::runtime_error("rediscovered simple24 word failed the independent oracle");
  // Independently audit every normalized table representative.
  for (const auto& path : tables.paths) {
    int state = 0, mask = 1; Counts counts{};
    for (int label : path.word) {
      ++counts[label]; state ^= 1 << label;
      if (mask >> state & 1) throw std::runtime_error("path-table representative repeats a vertex");
      mask |= 1 << state;
    }
    if (mask != path.mask || state != path.end || counts != path.counts)
      throw std::runtime_error("path-table representative audit failed");
  }
  std::cout << "{\"controls\":\"PASS\",\"pattern\":\"" << (distinguished ? "B" : "A")
            << "\",\"normalized_paths\":" << tables.paths.size()
            << ",\"translated_candidates\":" << tables.candidates.size()
            << ",\"low_raw_words\":" << raw_count << ",\"universal_low_dihedral_orbits\":" << templates.size()
            << ",\"positive_simple24_coverage\":" << pos.coverage
            << ",\"negative_simple22_coverage\":" << neg.coverage
            << ",\"repeated_origin_rejected\":true,\"wrong_count_rejected\":true,\"wrong_join_rejected\":true"
            << ",\"full_enumeration_rediscovered\":true,\"full_enumeration_compositions\":" << full_engine.stats.compositions
            << ",\"full_enumeration_capacity_survivors\":" << full_engine.stats.capacity_survivors
            << ",\"full_enumeration_nodes\":" << full_engine.stats.nodes << "}\n";
}

// These independent small word censuses reproduce the finite f5/f6 premises
// credited to PR943/PR1185. Positive even multiplicities leave only the three
// cases below; at six-source length14 the four-use coordinate is designated0.
void multiplicity_premises() {
  auto five = independent_oracle({0,1,0,1,2,3,2,4,2,3,2,4});
  auto six = independent_oracle({0,1,0,2,0,1,0,2,3,4,3,5,3,4,3,5});
  if (!five.restored || five.coverage != 32 || !six.restored || six.coverage != 64)
    throw std::runtime_error("f5/f6 Gray positive controls failed");
  struct Case { int dimension, length; bool heavy; uint64_t leaves; int maximum; };
  for (const Case spec : {Case{5,10,false,945,31}, Case{6,12,false,10395,49}, Case{6,14,true,945945,59}}) {
    std::array<int,6> counts{};
    std::array<int,15> prefixes{};
    uint64_t leaves = 0; int maximum = 0;
    std::function<void(int,int)> visit = [&](int position, int used) {
      if (position == spec.length) {
        if (prefixes[position]) throw std::runtime_error("premise word is not restored");
        uint64_t differences = 1;
        for (int i = 0; i < position; ++i) for (int j = i + 1; j < position; ++j)
          differences |= uint64_t(1) << (prefixes[i] ^ prefixes[j]);
        ++leaves; maximum = std::max(maximum, __builtin_popcountll(differences));
        return;
      }
      auto append = [&](int label, int next_used) {
        ++counts[label]; prefixes[position + 1] = prefixes[position] ^ (1 << label);
        visit(position + 1, next_used); --counts[label];
      };
      if (spec.heavy && counts[0] < 4) append(0, used);
      int offset = spec.heavy ? 1 : 0;
      for (int ordinal = 0; ordinal < spec.dimension - offset && ordinal <= used; ++ordinal)
        if (counts[ordinal + offset] < 2) append(ordinal + offset, used + (ordinal == used));
    };
    visit(0, 0);
    if (leaves != spec.leaves || maximum != spec.maximum) throw std::runtime_error("multiplicity premise census mismatch");
    std::cout << "{\"premise\":\"PASS\",\"dimension\":" << spec.dimension << ",\"length\":" << spec.length
              << ",\"canonical_words\":" << leaves << ",\"maximum_coverage\":" << maximum << "}\n";
  }
}

int main(int argc, char** argv) {
  try {
    double seconds = 300;
    std::string pattern = "both";
    std::vector<int> requested;
    bool controls_only = false, list_only = false, premises_only = false, conditional_cover = true;
    for (int i = 1; i < argc; ++i) {
      std::string arg = argv[i];
      if (arg == "--controls-only") { controls_only = true; continue; }
      if (arg == "--list-only") { list_only = true; continue; }
      if (arg == "--premises-only") { premises_only = true; continue; }
      if (arg == "--no-conditional-cover") { conditional_cover = false; continue; }
      if (i + 1 >= argc) throw std::runtime_error("option needs value");
      std::string value = argv[++i];
      if (arg == "--seconds") seconds = std::stod(value);
      else if (arg == "--pattern") pattern = value;
      else if (arg == "--templates") {
        requested.clear(); std::istringstream stream(value); std::string item;
        while (std::getline(stream, item, ',')) requested.push_back(std::stoi(item));
      } else throw std::runtime_error("unknown option: " + arg);
    }
    if (!(seconds > 0) || seconds > 86400) throw std::runtime_error("invalid budget");
    if (pattern != "A" && pattern != "B" && pattern != "both") throw std::runtime_error("pattern must be A, B or both");
    if (premises_only) { multiplicity_premises(); return 0; }
    auto control_deadline = Clock::now() + std::chrono::seconds(60);
    Tables tables;
    auto templates_A = universal_templates(false), templates_B = universal_templates(true);
    controls(tables, templates_A, false, control_deadline);
    controls(tables, templates_B, true, control_deadline);
    if (Clock::now() >= control_deadline) throw std::runtime_error("control budget exhausted");
    if (controls_only) return 0;
    auto begin = Clock::now();
    auto deadline = begin + std::chrono::duration_cast<Clock::duration>(std::chrono::duration<double>(seconds));
    bool all_exhausted = true;
    int completed = 0;
    for (bool distinguished : {false, true}) {
      std::string name = distinguished ? "B" : "A";
      if (pattern != "both" && pattern != name) continue;
      const auto& templates = distinguished ? templates_B : templates_A;
      auto ids = requested;
      if (ids.empty()) for (int id = 1; id <= static_cast<int>(templates.size()); ++id) ids.push_back(id);
      for (int id : ids) {
        if (id < 1 || id > static_cast<int>(templates.size())) throw std::runtime_error("template ID out of range");
        if (list_only) {
          std::cout << "{\"pattern\":\"" << name << "\",\"template\":" << id << ",\"low_word\":[";
          for (int i = 0; i < static_cast<int>(templates[id-1].size()); ++i) std::cout << (i ? "," : "") << templates[id-1][i];
          std::cout << "]}\n"; continue;
        }
        if (Clock::now() >= deadline) { all_exhausted = false; break; }
        auto started = Clock::now();
        Engine engine(tables, templates[id - 1], distinguished ? Counts{4,4,4} : Counts{6,4,4},
                      deadline, true, conditional_cover);
        bool exhausted = engine.enumerate();
        all_exhausted &= exhausted;
        const auto& s = engine.stats;
        if (exhausted) ++completed;
        std::cout << "{\"pattern\":\"" << name << "\",\"template\":" << id
                  << ",\"conditional_cover\":" << (conditional_cover ? "true" : "false")
                  << ",\"exhausted\":" << (exhausted ? "true" : "false")
                  << ",\"found\":" << (engine.found ? "true" : "false")
                  << ",\"compositions\":" << s.compositions << ",\"capacity_survivors\":" << s.capacity_survivors
                  << ",\"root_consistent\":" << s.root_consistent << ",\"nodes\":" << s.nodes
                  << ",\"arc_removed\":" << s.arc_removed << ",\"count_removed\":" << s.count_removed
                  << ",\"cover_removed\":" << s.cover_removed << ",\"leaves\":" << s.leaves
                  << ",\"seconds\":" << std::chrono::duration<double>(Clock::now() - started).count() << "}\n" << std::flush;
        if (engine.found) {
          auto word = engine.word_from(engine.witness); auto result = independent_oracle(word);
          if (!result.restored || result.distinct != 22 || result.coverage != 128
              || result.counts != (distinguished ? std::array<int,7>{4,4,4,4,2,2,2} : std::array<int,7>{6,4,4,2,2,2,2}))
            throw std::runtime_error("discovered candidate failed independent ordinary-word oracle");
          std::cout << "{\"word\":[";
          for (int i = 0; i < static_cast<int>(word.size()); ++i) std::cout << (i ? "," : "") << word[i];
          std::cout << "],\"independent_verification\":\"PASS\"}\n";
          return 2;
        }
        if (engine.timed_out) break;
      }
      if (!all_exhausted) break;
    }
    if (list_only) return 0;
    std::cout << "{\"all_requested_exhausted\":" << (all_exhausted ? "true" : "false")
              << ",\"completed_orbits\":" << completed
              << ",\"seconds\":" << std::chrono::duration<double>(Clock::now() - begin).count() << "}\n";
    return all_exhausted ? 0 : 3;
  } catch (const std::exception& error) {
    std::cerr << "ERROR " << error.what() << '\n'; return 1;
  }
}
