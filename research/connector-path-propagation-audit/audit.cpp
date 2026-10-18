// Nick Petalas. Apache-2.0. Tests conorholds' unchanged native source.
// The only source adapter renames its command-line entry point.
#define main predecessor_main
#include "cycle_search.cpp"
#undef main

using Key = std::tuple<int, int, Counts>;
struct LiteralPath {
  int start = 0, end = 0, size = 0;
  std::array<int, 8> vertices{};
  Counts counts{};
};
struct AuditCounts {
  uint64_t raw_paths = 0, relations = 0, domain_cases = 0, tuples = 0;
  uint64_t feasible = 0, feasible_choices = 0, removed = 0, conditional_removed = 0;
  uint64_t universal_tuples = 0, structural_tuples = 0;
  uint64_t controls = 0, projections = 0, incidence_templates = 0, block_relations = 0;
};
void require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

std::set<Key> literal_paths(AuditCounts& counts) {
  std::set<Key> keys;
  // All 1+3+...+3^7=3280 label strings, not a self-avoiding DFS.
  int power = 1;
  for (int length = 0; length <= 7; ++length) {
    for (int encoded = 0; encoded < power; ++encoded) {
      int digits = encoded, state = 0, mask = 1;
      Counts frequency{};
      bool simple = true;
      for (int i = 0; i < length; ++i) {
        int label = digits % 3; digits /= 3;
        ++frequency[label]; state ^= 1 << label;
        if ((mask >> state) & 1) simple = false;
        mask |= 1 << state;
      }
      if (simple) { ++counts.raw_paths; keys.emplace(mask, state, frequency); }
    }
    power *= 3;
  }
  return keys;
}

std::vector<LiteralPath> check_paths(const Tables& tables, AuditCounts& counts) {
  auto expected = literal_paths(counts);
  std::set<Key> actual;
  for (const auto& p : tables.paths) actual.emplace(p.mask, p.end, p.counts);
  require(actual == expected && actual.size() == tables.paths.size(), "path-table completeness");
  std::vector<LiteralPath> paths;
  paths.reserve(tables.candidates.size());
  for (const auto& c : tables.candidates) {
    LiteralPath p; p.start = c.start; p.end = c.start; p.size = 1;
    p.vertices[0] = c.start;
    int mask = 1 << c.start;
    const auto& representative = tables.paths.at(static_cast<size_t>(c.normal));
    require(representative.word.size() <= 7, "path length bound");
    for (int label : representative.word) {
      require(label >= 0 && label < 3, "path label bound");
      ++p.counts[label]; p.end ^= 1 << label;
      require(((mask >> p.end) & 1) == 0, "representative simplicity");
      mask |= 1 << p.end; p.vertices[p.size++] = p.end;
    }
    require(mask == c.mask && p.end == c.end && p.counts == c.counts
            && p.size == c.length + 1, "candidate literal reconstruction");
    paths.push_back(p);
  }
  std::set<std::tuple<Key, int>> translated;
  for (size_t i = 0; i < paths.size(); ++i) {
    const auto& c = tables.candidates[i];
    translated.emplace(Key{tables.paths[c.normal].mask, tables.paths[c.normal].end, c.counts}, c.start);
  }
  require(translated.size() == expected.size() * 8 && paths.size() == translated.size(),
          "translated path-table completeness");
  return paths;
}

bool literal_relation(const LiteralPath& a, const LiteralPath& b, int tag) {
  if ((tag & 1) && a.end != b.start) return false;
  if ((tag & 2) && a.start != b.end) return false;
  std::array<bool, 8> differences{};
  bool overlap = false;
  for (int i = 0; i < a.size; ++i) for (int j = 0; j < b.size; ++j) {
    differences[a.vertices[i] ^ b.vertices[j]] = true;
    if (a.vertices[i] == b.vertices[j]) overlap = true;
  }
  if ((tag & 8) && overlap) return false;
  if (tag & 4) for (bool present : differences) if (!present) return false;
  return true;
}

void check_relations(const Tables& tables, const std::vector<LiteralPath>& paths, AuditCounts& counts) {
  require(paths.size() == 848, "translated Q3 table cardinality");
  for (int tag : {1, 2, 4, 5, 6, 8}) {
    for (size_t i = 0; i < paths.size(); ++i) for (size_t j = 0; j < paths.size(); ++j) {
      Bits singleton; singleton.add(static_cast<int>(j));
      bool actual = tables.support[tag][i].intersects(singleton);
      require(actual == literal_relation(paths[i], paths[j], tag), "binary relation disagreement");
      ++counts.relations;
    }
  }
}

void check_incidence(const Tables& tables, AuditCounts& counts) {
  for (bool distinguished : {false, true}) {
    for (const auto& low : universal_templates(distinguished)) {
      Engine engine(tables, low, Counts{4,4,4}, Clock::now() + std::chrono::seconds(30));
      std::vector<int> points; int state = 0;
      for (int label : low) { points.push_back(state); state ^= 1 << label; }
      require(state == 0 && points.size() == low.size(), "incidence low closure");
      for (int d = 0; d < 16; ++d) {
        std::vector<std::pair<int,int>> expected;
        for (int i = 0; i < engine.blocks; ++i) for (int j = i; j < engine.blocks; ++j)
          if ((points[i] ^ points[j]) == d) expected.emplace_back(i,j);
        require(engine.pairs[d] == expected, "low-difference pair incidence");
      }
      for (int i = 0; i < engine.blocks; ++i) for (int d = 0; d < 16; ++d) {
        std::vector<int> expected;
        for (int j = 0; j < engine.blocks; ++j)
          if (i != j && (points[i] ^ points[j]) == d) expected.push_back(j);
        require(engine.neighbors[i][d] == expected, "conditional neighbor incidence");
      }
      for (int i = 0; i < engine.blocks; ++i) for (int j = 0; j < engine.blocks; ++j) {
        int tag = 0, difference = points[i] ^ points[j];
        if (i != j) {
          if ((i + 1) % engine.blocks == j) tag |= 1;
          if ((j + 1) % engine.blocks == i) tag |= 2;
          if (points[i] == points[j]) tag |= 8;
          if (difference != 0 && engine.pairs[difference].size() == 1) tag |= 4;
        }
        require(engine.tags[i][j] == tag, "binary tag incidence");
        ++counts.block_relations;
      }
      ++counts.incidence_templates;
    }
  }
}

std::vector<int> fixture(bool negative, bool repeated) {
  std::vector<int> word{0,1,0,2,0,1,0,5,2,3,4,3,6,3,4,3,5,3,4,3,6,3,4,3};
  if (repeated) std::swap(word[7], word[8]);
  if (negative) { word.erase(word.begin() + 11); word.erase(word.begin() + 9); }
  return word;
}

std::vector<int> remap(const std::vector<int>& word, const Counts& high) {
  std::array<int, 7> mapping{}; mapping.fill(-1);
  for (int i = 0; i < 3; ++i) mapping[high[i]] = i;
  int next = 3;
  for (int i = 0; i < 7; ++i) if (mapping[i] == -1) mapping[i] = next++;
  std::vector<int> mapped;
  mapped.reserve(word.size());
  for (int label : word) mapped.push_back(mapping[label]);
  return mapped;
}

struct TupleContext {
  int blocks = 0;
  std::array<int, 10> low{};
  Counts target{};
};
TupleContext context(const std::vector<int>& word) {
  TupleContext c;
  int state = 0;
  for (int label : word) {
    if (label < 3) { ++c.target[label]; continue; }
    require(c.blocks < 10, "fixture block bound");
    c.low[c.blocks++] = state; state ^= 1 << (label - 3);
  }
  require(state == 0 && word.back() >= 3, "fixture low closure/cut");
  return c;
}

bool literal_feasible(const TupleContext& c, const std::vector<LiteralPath>& paths,
                      const std::array<int, 10>& ids, bool cover) {
  Counts totals{};
  std::array<bool, 128> points{};
  for (int i = 0; i < c.blocks; ++i) {
    const auto& p = paths[ids[i]];
    if (p.end != paths[ids[(i + 1) % c.blocks]].start) return false;
    for (int j = 0; j < 3; ++j) totals[j] += p.counts[j];
    for (int j = 0; j < p.size; ++j) {
      int point = 8 * c.low[i] + p.vertices[j];
      if (points[point]) return false;
      points[point] = true;
    }
  }
  if (totals != c.target) return false;
  if (!cover) return true;
  std::array<bool, 128> differences{};
  for (int a = 0; a < 128; ++a) if (points[a])
    for (int b = 0; b < 128; ++b) if (points[b]) differences[a ^ b] = true;
  for (bool present : differences) if (!present) return false;
  return true;
}

Domains noisy_domains(const Engine& engine, const Domains& planted, int mode) {
  Domains domains = planted;
  for (int i = 0; i < engine.blocks; ++i) {
    int id = planted[i].first();
    const auto& p = engine.tables.candidates[id];
    // One deterministic alternative per block, selected without propagation.
    for (size_t step = 1; step <= engine.tables.candidates.size(); ++step) {
      size_t j = (static_cast<size_t>(id) + step * 37 + static_cast<size_t>(mode) * 131)
                 % engine.tables.candidates.size();
      const auto& q = engine.tables.candidates[j];
      if (static_cast<int>(j) != id && q.length == p.length
          && parity(q.start) == parity(p.start) && (i != 0 || q.start == 0)) {
        domains[i].add(static_cast<int>(j)); break;
      }
    }
    require(domains[i].size() <= 2, "two-choice domain bound");
  }
  return domains;
}

void compare_domains(const Tables& tables, const std::vector<LiteralPath>& paths,
                     const std::vector<int>& word, int mode, bool cover, AuditCounts& counts) {
  auto c = context(word);
  Engine engine(tables, low_of(word), c.target, Clock::now() + std::chrono::seconds(30), cover);
  auto planted = fixed_domains(engine, word);
  auto original = noisy_domains(engine, planted, mode);
  auto pruned = original;
  bool accepted = engine.propagate(pruned);
  std::array<std::array<int, 2>, 10> choices{};
  std::array<int, 10> sizes{};
  int products = 1;
  for (int i = 0; i < c.blocks; ++i) {
    original[i].each([&](int id) { choices[i][sizes[i]++] = id; });
    products *= sizes[i];
  }
  require(products > 0 && products <= 1024, "Cartesian tuple bound");
  uint64_t feasible = 0;
  for (int encoded = 0; encoded < products; ++encoded) {
    int cursor = encoded; std::array<int, 10> ids{};
    for (int i = 0; i < c.blocks; ++i) { ids[i] = choices[i][cursor % sizes[i]]; cursor /= sizes[i]; }
    ++counts.tuples;
    if (!literal_feasible(c, paths, ids, cover)) continue;
    ++feasible; ++counts.feasible;
    if (cover) ++counts.universal_tuples; else ++counts.structural_tuples;
    require(accepted, "propagation rejected a feasible tuple");
    for (int i = 0; i < c.blocks; ++i) {
      Bits singleton; singleton.add(ids[i]);
      require(pruned[i].intersects(singleton), "propagation removed a feasible choice");
      ++counts.feasible_choices;
    }
  }
  require(feasible > 0, "planted tuple missing from independent oracle");
  counts.removed += engine.stats.arc_removed + engine.stats.count_removed + engine.stats.cover_removed;
  counts.conditional_removed += engine.stats.cover_removed;
  ++counts.domain_cases;
}

void fixed_controls(const Tables& tables, const std::vector<int>& word, AuditCounts& counts) {
  auto c = context(word);
  auto deadline = Clock::now() + std::chrono::seconds(30);
  Engine positive(tables, low_of(word), c.target, deadline);
  auto fixed = fixed_domains(positive, word);
  require(positive.propagate(fixed), "positive fixed tuple rejected"); ++counts.controls;
  Engine wrong_count(tables, low_of(word), Counts{c.target[0] + 1, c.target[1], c.target[2]}, deadline, false);
  fixed = fixed_domains(positive, word);
  require(!wrong_count.propagate(fixed), "incorrect totals accepted"); ++counts.controls;
  Engine wrong_join(tables, low_of(word), c.target, deadline, false);
  fixed = fixed_domains(positive, word);
  const auto first = tables.candidates[fixed[0].first()]; fixed[0] = Bits{};
  for (size_t id = 0; id < tables.candidates.size(); ++id) {
    const auto& p = tables.candidates[id];
    if (p.normal == first.normal && p.start == (first.start ^ 1)) fixed[0].add(static_cast<int>(id));
  }
  require(fixed[0].size() == 1 && !wrong_join.propagate(fixed), "incorrect cyclic join accepted");
  ++counts.controls;
}

void check_fixture(const Tables& tables, const std::vector<LiteralPath>& paths,
                   const std::vector<int>& word, AuditCounts& counts) {
  auto result = independent_oracle(word);
  require(result.restored && result.distinct == 24 && result.coverage == 128, "positive fixture");
  fixed_controls(tables, word, counts);
  for (int mode = 0; mode < 3; ++mode)
    for (bool cover : {false, true}) compare_domains(tables, paths, word, mode, cover, counts);
  ++counts.projections;
}

void check_word_fixtures(const Tables& tables, const std::vector<LiteralPath>& paths, AuditCounts& counts) {
  auto positive = fixture(false, false);
  for (int a = 0; a < 7; ++a) for (int b = a + 1; b < 7; ++b) for (int c = b + 1; c < 7; ++c) {
    Counts high{a,b,c};
    auto mapped = remap(positive, high);
    if (low_of(mapped).size() > 10) continue;
    for (int permutation = 0; permutation < 6; ++permutation) {
      auto word = remap(positive, high);
      // A low step closes the last block. Every such rotation is included.
      for (size_t cut = 0; cut < word.size(); ++cut) if (word[cut] >= 3) {
        auto rotated = word; std::rotate(rotated.begin(), rotated.begin() + static_cast<long>(cut + 1), rotated.end());
        check_fixture(tables, paths, rotated, counts);
        std::reverse(rotated.begin(), rotated.end());
        std::rotate(rotated.begin(), rotated.begin() + 1, rotated.end());
        check_fixture(tables, paths, rotated, counts);
      }
      bool next = std::next_permutation(high.begin(), high.end());
      require(next == (permutation < 5), "high permutation exhaustion");
    }
  }
}

void negative_word_controls(const Tables& tables, AuditCounts& counts) {
  for (bool repeated : {false, true}) {
    auto word = remap(fixture(!repeated, repeated), Counts{0,3,4});
    size_t cut = 0;
    for (size_t i = 0; i < word.size(); ++i) if (word[i] >= 3) { cut = i + 1; break; }
    std::rotate(word.begin(), word.begin() + static_cast<long>(cut), word.end());
    auto c = context(word);
    auto result = independent_oracle(word);
    require(result.restored && result.distinct == (repeated ? 23 : 22)
            && result.coverage == (repeated ? 128 : 116), "negative ordinary-word fixture");
    for (bool cover : {false, true}) {
      Engine rotated(tables, low_of(word), c.target, Clock::now() + std::chrono::seconds(30), cover);
      auto domains = fixed_domains(rotated, word);
      require(rotated.propagate(domains) == (!repeated && !cover), "fixed negative propagation");
      ++counts.controls;
    }
  }
}

int main() {
  try {
    AuditCounts counts;
    Tables tables;
    auto paths = check_paths(tables, counts);
    check_relations(tables, paths, counts);
    check_incidence(tables, counts);
    check_word_fixtures(tables, paths, counts);
    negative_word_controls(tables, counts);
    require(counts.conditional_removed > 0, "conditional-coverage deletion unexercised");
    std::cout << "{\"raw_paths\":" << counts.raw_paths << ",\"normalized_paths\":" << tables.paths.size()
      << ",\"candidates\":" << paths.size() << ",\"relations\":" << counts.relations
      << ",\"incidence_templates\":" << counts.incidence_templates
      << ",\"block_relations\":" << counts.block_relations
      << ",\"projections\":" << counts.projections << ",\"domain_cases\":" << counts.domain_cases
      << ",\"tuples\":" << counts.tuples << ",\"feasible_tuples\":" << counts.feasible
      << ",\"universal_tuples\":" << counts.universal_tuples
      << ",\"structural_tuples\":" << counts.structural_tuples
      << ",\"feasible_choices\":" << counts.feasible_choices << ",\"removed\":" << counts.removed
      << ",\"conditional_removed\":" << counts.conditional_removed << ",\"controls\":" << counts.controls
      << ",\"lost_feasible_choices\":0,\"full_census\":false}\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "AUDIT_ERROR " << error.what() << '\n'; return 1;
  }
}
