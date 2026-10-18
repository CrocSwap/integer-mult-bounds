// SPDX-License-Identifier: Apache-2.0
// Search audit by Nick Petalas. Authenticated subject by conorholds.
#define main subject_main
#include "subject.cpp"
#undef main

void check(bool ok, const char* message) {
  if (!ok) throw std::runtime_error(message);
}

const std::vector<int> gray{0,1,0,2,0,1,0,5,2,3,4,3,6,3,4,3,5,3,4,3,6,3,4,3};

std::vector<int> fixture(bool pattern_b) {
  const std::array<int,7> a{1,3,4,0,2,5,6}, b{3,2,4,0,1,5,6};
  std::vector<int> result;
  for (int i = 0; i < 24; ++i) result.push_back((pattern_b ? b : a)[gray[(i+8)%24]]);
  return result;
}

// This oracle does not consult tags, pair tables, support tables, propagate,
// word_from or the subject's ordinary-word oracle.
bool accepts(const Engine& engine, const std::array<int,MAX_BLOCKS>& ids) {
  std::vector<int> points;
  std::array<int,3> counts{};
  int full = 0;
  for (int i = 0; i < engine.blocks; ++i) {
    const auto& c = engine.tables.candidates[ids[i]];
    if ((full & 7) != c.start) return false;
    for (int label : engine.tables.paths[c.normal].word) {
      points.push_back(full); full ^= 1 << label; ++counts[label];
    }
    points.push_back(full); full ^= 1 << (engine.low_word[i]+3);
  }
  if (full || counts != engine.target) return false;
  const std::set<int> unique(points.begin(), points.end());
  if (unique.size() != points.size()) return false;
  if (!engine.require_cover) return true;
  std::set<int> differences;
  for (int x : unique) for (int y : unique) differences.insert(x^y);
  return differences.size() == 128;
}

struct Oracle { uint64_t tuples=0, solutions=0; };
Oracle cartesian(const Engine& engine, const Domains& domains) {
  std::array<std::vector<int>,MAX_BLOCKS> choices;
  uint64_t product = 1;
  for (int i = 0; i < engine.blocks; ++i) {
    domains[i].each([&](int id) { choices[i].push_back(id); });
    check(choices[i].size() <= 3, "oracle domain capacity");
    product *= choices[i].size();
  }
  check(product <= 59049, "oracle Cartesian capacity");
  Oracle result;
  for (uint64_t ordinal = 0; ordinal < product; ++ordinal) {
    uint64_t remainder = ordinal;
    std::array<int,MAX_BLOCKS> ids{};
    for (int i = 0; i < engine.blocks; ++i) {
      ids[i] = choices[i][remainder % choices[i].size()];
      remainder /= choices[i].size();
    }
    ++result.tuples; result.solutions += accepts(engine, ids);
  }
  return result;
}

struct Totals {
  uint64_t roots=0, tuples=0, solutions=0, sat=0, unsat=0;
  uint64_t branch_sat=0, branch_unsat=0, nodes=0, max_nodes=0;
  uint64_t witness_checks=0, unchanged_checks=0, leaves=0;
};

bool same(const Domains& a, const Domains& b) {
  for (int i = 0; i < MAX_BLOCKS; ++i) if (a[i].words != b[i].words) return false;
  return true;
}

void compare(const Tables& tables, const LowWord& low, Counts target,
             const Domains& domains, bool cover, bool conditional, Totals& totals) {
  Engine engine(tables, low, target, Clock::now()+std::chrono::seconds(30), cover, conditional);
  const auto expected = cartesian(engine, domains);
  const Domains original = domains;
  bool found = engine.search(domains, true);
  check(!engine.timed_out, "small search interrupted");
  check(found == (expected.solutions != 0) && engine.found == found, "search existence mismatch");
  check(same(domains, original), "search modified caller domains");
  ++totals.unchanged_checks;
  if (found) {
    std::array<int,MAX_BLOCKS> ids{};
    for (int i = 0; i < engine.blocks; ++i) {
      check(engine.witness[i].size() == 1, "witness is not singleton");
      ids[i] = engine.witness[i].first();
      check((original[i].words[ids[i]/64] >> (ids[i]%64)) & 1, "witness outside root");
    }
    check(accepts(engine, ids), "literal witness rejected"); ++totals.witness_checks;
  }
  ++totals.roots; totals.tuples += expected.tuples; totals.solutions += expected.solutions;
  totals.sat += found; totals.unsat += !found; totals.nodes += engine.stats.nodes;
  totals.max_nodes = std::max(totals.max_nodes, engine.stats.nodes);
  totals.branch_sat += found && engine.stats.nodes > 1;
  totals.branch_unsat += !found && engine.stats.nodes > 1;
  totals.leaves += engine.stats.leaves;
}

Domains unite(const Domains& first, const Domains& second, int blocks) {
  Domains result = first;
  for (int i = 0; i < blocks; ++i)
    second[i].each([&](int id) { result[i].add(id); });
  return result;
}

uint32_t random_step(uint32_t& state) {
  state = state * 1664525u + 1013904223u;
  return state;
}

void cases(const Tables& tables, Totals& totals) {
  uint32_t seed = 0x9433261u;
  for (bool pattern_b : {false,true}) {
    auto word = fixture(pattern_b);
    const auto low = low_of(word);
    const Counts target = pattern_b ? Counts{8,4,2} : Counts{8,4,4};
    Engine base(tables, low, target, Clock::now()+std::chrono::seconds(30));
    const Domains fixed = fixed_domains(base, word);
    for (int permutation = 0; permutation < 6; ++permutation) {
      std::array<int,3> perm{0,1,2};
      for (int j = 0; j < permutation; ++j)
        check(std::next_permutation(perm.begin(),perm.end()), "permutation ordinal");
      auto changed = word;
      for (int& label : changed) if (label < 3) label = perm[label];
      Domains unioned = unite(fixed, fixed_domains(base,changed), base.blocks);
      for (bool cover : {false,true}) for (bool conditional : {false,true}) {
        compare(tables,low,target,unioned,cover,conditional,totals);
        Counts other{};
        for (int j=0;j<3;++j) other[perm[j]]=target[j];
        compare(tables,low,other,unioned,cover,conditional,totals);
        Counts middle{};
        for (int j=0;j<3;++j) middle[j]=(target[j]+other[j])/2;
        compare(tables,low,middle,unioned,cover,conditional,totals);
      }
    }
    for (int sample = 0; sample < 192; ++sample) {
      Domains domains = fixed;
      for (int block = 0; block < base.blocks; ++block) {
        const auto& original = tables.candidates[fixed[block].first()];
        std::vector<int> alternatives;
        for (int id = 0; id < static_cast<int>(tables.candidates.size()); ++id) {
          const auto& c = tables.candidates[id];
          if (c.length == original.length && parity(c.start) == parity(original.start)
              && (block || c.start == 0)) alternatives.push_back(id);
        }
        for (int extra=0;extra<2 && !alternatives.empty();++extra)
          domains[block].add(alternatives[random_step(seed)%alternatives.size()]);
        if ((sample%3)==0) domains[block].erase(fixed[block].first());
      }
      for (bool cover : {false,true})
        compare(tables,low,target,domains,cover,(sample%2)!=0,totals);
    }
    Domains empty = fixed; empty[base.blocks-1]=Bits{};
    compare(tables,low,target,empty,true,true,totals);
  }
}

void timeout_controls(const Tables& tables) {
  auto word=fixture(false); const auto low=low_of(word); Counts target{8,4,4};
  Engine base(tables,low,target,Clock::now()+std::chrono::seconds(30));
  auto fixed=fixed_domains(base,word);
  auto swapped=word;
  for (int& label:swapped) if(label<3) label=(label==1?2:label==2?1:0);
  auto domains=unite(fixed,fixed_domains(base,swapped),base.blocks);
  for (uint64_t initial : {1022,1023}) {
    Engine stopped(tables,low,target,Clock::now()-std::chrono::seconds(1));
    stopped.stats.nodes=initial;
    check(!stopped.search(domains,true),"interrupted search returned success");
    check(stopped.timed_out && !stopped.found && stopped.stats.nodes==1024,
          "interrupted search lost its timeout flag");
    check(stopped.stats.leaves==0,"interrupted search reached a leaf");
  }
  Engine stopped(tables,low,target,Clock::now()-std::chrono::seconds(1));
  stopped.stats.compositions=255;
  check(!stopped.enumerate() && stopped.timed_out && !stopped.found,
        "interrupted enumeration reported exhaustion");
  Engine exhausted(tables,low,Counts{0,0,0},Clock::now()+std::chrono::seconds(30));
  check(exhausted.enumerate() && !exhausted.found && !exhausted.timed_out,
        "trivial impossible target not exhausted");
  Engine found(tables,low,target,Clock::now()+std::chrono::seconds(30));
  check(!found.enumerate() && found.found && !found.timed_out,
        "successful enumeration reported exhaustion");
  std::array<int,MAX_BLOCKS> ids{};
  for (int i=0;i<found.blocks;++i) ids[i]=found.witness[i].first();
  check(accepts(found,ids),"enumeration witness failed literal oracle");
}

int main() {
  try {
    Tables tables; Totals totals;
    cases(tables,totals); timeout_controls(tables);
    check(totals.sat && totals.unsat && totals.branch_sat && totals.branch_unsat,
          "missing satisfiable/unsatisfiable branching controls");
    std::cout << "{\"roots\":" << totals.roots << ",\"tuples\":" << totals.tuples
      << ",\"solutions\":" << totals.solutions << ",\"sat\":" << totals.sat
      << ",\"unsat\":" << totals.unsat << ",\"branch_sat\":" << totals.branch_sat
      << ",\"branch_unsat\":" << totals.branch_unsat << ",\"nodes\":" << totals.nodes
      << ",\"max_nodes\":" << totals.max_nodes << ",\"witness_checks\":" << totals.witness_checks
      << ",\"unchanged_checks\":" << totals.unchanged_checks << ",\"leaves\":" << totals.leaves
      << ",\"timeout_controls\":3,\"enumeration_controls\":2}\n";
    return 0;
  } catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
