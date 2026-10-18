// Prepared for commdata2338, with substantial OpenAI Codex assistance.
// Apache-2.0. The included predecessor retains conorholds' attribution.
// Execute its actual predicate; do not copy or patch its implementation.
#define main predecessor_main
#include "../connector-covering-code/cycle_search.cpp"
#undef main

namespace audit {
using Profile = std::array<std::array<int, 2>, 16>;
struct Slot { int low, side, block; };
struct Result {
  bool accepted;
  int reason;
  Profile profile{};
};

void require(bool condition, const std::string& message) {
  if (!condition) throw std::runtime_error(message);
}

// Definition-level oracle: list positions, then enumerate unordered pairs.
// No source parity routine, source low_points, or aggregated product formula.
Result oracle(const LowWord& low, const LowWord& gaps, int mutant = 0) {
  require(low.size() == gaps.size(), "oracle length mismatch");
  std::vector<Slot> slots;
  std::array<int, 16> occupied{};
  int point = 0, side = 0;
  bool oversized_block = false;
  for (size_t block = 0; block < low.size(); ++block) {
    require(gaps[block] >= 0 && gaps[block] <= 8, "oracle gap outside audit domain");
    oversized_block |= gaps[block] > 7;
    if (mutant == 1) side = 0; // Wrong: reset at every low step.
    for (int step = 0; step <= gaps[block]; ++step) {
      slots.push_back({point, side, static_cast<int>(block)});
      ++occupied[point];
      if (step < gaps[block]) side = 1 - side;
    }
    point ^= 1 << low[block];
  }
  require(point == 0, "oracle low projection not restored");
  Result result{false, 0, {}};
  for (size_t i = 0; i < slots.size(); ++i)
    for (size_t j = i + 1; j < slots.size(); ++j) {
      const auto& a = slots[i]; const auto& b = slots[j];
      if (mutant == 2 && a.low == b.low && a.block != b.block) continue;
      ++result.profile[a.low ^ b.low][a.side ^ b.side];
    }
  if (oversized_block) { result.reason = 1; return result; }
  // Restore testing uses the actual total high-step count, even for mutants.
  if (std::accumulate(gaps.begin(), gaps.end(), 0) % 2) { result.reason = 2; return result; }
  for (int count : occupied) if (count > 8) { result.reason = 3; return result; }
  for (int difference = 0; difference < 16; ++difference)
    for (int bit = 0; bit < 2; ++bit) {
      int needed = difference == 0 && bit == 0 ? 3 : 4;
      if (result.profile[difference][bit] < needed) {
        result.reason = 4 + 2 * difference + bit;
        return result;
      }
    }
  result.accepted = true;
  return result;
}

std::string digits(const LowWord& value) {
  std::string out;
  for (int x : value) out += static_cast<char>('0' + x);
  return out;
}

struct CountsAudit {
  uint64_t cases = 0, accepted = 0, repeated_low = 0;
  std::array<uint64_t, 36> reasons{};
  std::array<uint64_t, 2> mutant_disagreements{};
  std::array<std::string, 2> mutant_examples{};
  void check(const Engine& engine, const LowWord& gaps) {
    auto expected = oracle(engine.low_word, gaps);
    bool actual = engine.capacity(gaps);
    require(actual == expected.accepted,
            "capacity mismatch low=" + digits(engine.low_word) + " gaps=" + digits(gaps));
    ++cases; accepted += actual; ++reasons[expected.reason];
    std::set<int> low_points; int point = 0;
    for (int label : engine.low_word) { low_points.insert(point); point ^= 1 << label; }
    repeated_low += low_points.size() < engine.low_word.size();
    for (int mutant = 1; mutant <= 2; ++mutant) {
      auto changed = oracle(engine.low_word, gaps, mutant);
      if (changed.accepted == actual) continue;
      ++mutant_disagreements[mutant - 1];
      if (mutant_examples[mutant - 1].empty())
        mutant_examples[mutant - 1] = digits(engine.low_word) + "/" + digits(gaps)
            + "/correct=" + std::to_string(actual) + "/mutant=" + std::to_string(changed.accepted);
    }
  }
  void print(const std::string& name) const {
    std::cout << "{\"domain\":\"" << name << "\",\"cases\":" << cases
              << ",\"accepted\":" << accepted << ",\"repeated_low_cases\":" << repeated_low
              << ",\"reasons\":[";
    for (size_t i = 0; i < reasons.size(); ++i) std::cout << (i ? "," : "") << reasons[i];
    std::cout << "],\"mutant_disagreements\":[" << mutant_disagreements[0]
              << ',' << mutant_disagreements[1] << "],\"mutant_examples\":[\""
              << mutant_examples[0] << "\",\"" << mutant_examples[1] << "\"]}\n";
  }
};

// Complete bounded composition domain. This enumerates gap vectors only;
// no high paths, source words, or CSP search are generated.
void compositions(const Engine& engine, int cap, int total, CountsAudit& count) {
  LowWord gaps(engine.blocks);
  std::function<void(int, int)> visit = [&](int position, int remaining) {
    if (position == engine.blocks) {
      if (remaining == 0) count.check(engine, gaps);
      return;
    }
    for (int next = 0; next <= cap; ++next) {
      int left = remaining - next;
      if (left < 0 || left > cap * (engine.blocks - position - 1)) continue;
      gaps[position] = next; visit(position + 1, left);
    }
  };
  visit(0, total);
}

void bounded_domains(const Tables& tables) {
  for (bool b : {false, true}) {
    CountsAudit core, boundary;
    auto low_words = universal_templates(b);
    for (const auto& low : low_words) {
      Engine engine(tables, low, b ? Counts{4,4,4} : Counts{6,4,4}, Clock::time_point::max());
      compositions(engine, b ? 2 : 3, b ? 12 : 14, core);
      // Exactly zero, one, or two nonzero gaps, each 1..8. This reaches
      // both sides of the eight-state capacity and odd-restoration guards.
      LowWord gaps(low.size()); boundary.check(engine, gaps);
      for (int i = 0; i < engine.blocks; ++i) for (int x = 1; x <= 8; ++x) {
        gaps[i] = x; boundary.check(engine, gaps);
        for (int j = i + 1; j < engine.blocks; ++j) for (int y = 1; y <= 8; ++y) {
          gaps[j] = y; boundary.check(engine, gaps); gaps[j] = 0;
        }
        gaps[i] = 0;
      }
    }
    core.print(b ? "B-core" : "A-core");
    boundary.print(b ? "B-boundary" : "A-boundary");
  }
}

// Query mode lets a separately written Python oracle check the compiled
// source without importing any algorithm above. Bounded, nonnegative inputs.
void query(const Tables& tables) {
  std::string low_text, gap_text;
  size_t count = 0;
  while (std::cin >> low_text) {
    require(static_cast<bool>(std::cin >> gap_text), "missing gap vector");
    require(++count <= 10000, "query cap exceeded");
    require(low_text.size() == gap_text.size() && low_text.size() <= 10, "invalid query length");
    LowWord low, gaps;
    for (char c : low_text) { require(c >= '0' && c <= '3', "invalid low label"); low.push_back(c - '0'); }
    for (char c : gap_text) { require(c >= '0' && c <= '8', "invalid gap"); gaps.push_back(c - '0'); }
    Engine engine(tables, low, Counts{0,0,0}, Clock::time_point::max());
    std::cout << engine.capacity(gaps) << '\n';
  }
  require(std::cin.eof(), "query input failure");
}
} // namespace audit

int main(int argc, char** argv) {
  try {
    const Tables tables;
    if (argc == 2 && std::string(argv[1]) == "--query") audit::query(tables);
    else if (argc == 1) audit::bounded_domains(tables);
    else throw std::runtime_error("usage: audit [--query]");
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL_CAPACITY_AUDIT " << error.what() << '\n';
    return 1;
  }
}
