// Nick Petalas. Apache-2.0.
// Audit-only leaf/search substitutions; never a scientific word census.
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

struct Engine;
void audit_gap(const std::vector<int>& gaps, int blocks);
bool audit_capacity(const std::vector<int>& gaps);
void audit_search(Engine& engine);
#define main predecessor_main
#include "subject.cpp"
#undef main

namespace {
std::array<std::array<uint64_t, 81>, 11> completions{};
uint64_t ordinal = 0, expected_count = 0, roots = 0, stop_at = 0;
int expected_total = 0, stop_mode = 0;

void need(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

void initialize(int blocks, int total) {
  need(blocks >= 1 && blocks <= 10 && total >= 0 && total <= 80,
       "invalid audit domain");
  completions = {};
  completions[0][0] = 1;
  for (int slots = 1; slots <= blocks; ++slots)
    for (int sum = 0; sum <= total; ++sum)
      for (int digit = 0; digit <= 7 && digit <= sum; ++digit)
        completions[slots][sum] += completions[slots - 1][sum - digit];
  expected_count = completions[blocks][total];
  expected_total = total;
  ordinal = roots = 0;
  stop_at = 0;
  stop_mode = 0;
}
}  // namespace

void audit_gap(const std::vector<int>& gaps, int blocks) {
  need(static_cast<int>(gaps.size()) == blocks, "gap width");
  int remaining = expected_total;
  uint64_t rank = 0;
  for (int position = 0; position < blocks; ++position) {
    int digit = gaps[position];
    need(digit >= 0 && digit <= 7 && digit <= remaining, "gap digit");
    for (int smaller = 0; smaller < digit; ++smaller)
      rank += completions[blocks - position - 1][remaining - smaller];
    remaining -= digit;
  }
  need(remaining == 0 && rank == ordinal, "gap rank is not next lexicographic rank");
  ++ordinal;
}

bool audit_capacity(const std::vector<int>&) {
  // Deterministic sparse acceptance; the actual capacity proof is a predecessor.
  return stop_mode ? true : ordinal % 257 == 1;
}

void audit_search(Engine& engine) {
  ++roots;
  if (roots != stop_at) return;
  if (stop_mode == 1) engine.found = true;
  if (stop_mode == 2) engine.timed_out = true;
}

struct AuditTotals {
  uint64_t gaps = 0, handoffs = 0;
  int runs = 0, small = 0, stops = 0;
};

void complete_runs(const Tables& tables, const std::vector<LowWord>& templates,
                   Counts target, int total, AuditTotals& result) {
  const auto future = Clock::now() + std::chrono::minutes(10);
  for (bool conditional : {false, true}) for (const auto& low : templates) {
    initialize(static_cast<int>(low.size()), total);
    Engine engine(tables, low, target, future, true, conditional);
    need(engine.enumerate(), "complete audit enumeration must exhaust");
    need(!engine.found && !engine.timed_out, "complete flags");
    need(ordinal == expected_count && engine.stats.compositions == ordinal,
         "gap count does not equal independent coefficient count");
    need(roots == (expected_count + 256) / 257 && engine.stats.capacity_survivors == roots,
         "capacity/search handoff count");
    result.gaps += ordinal;
    result.handoffs += roots;
    ++result.runs;
  }
  for (int total_small = 0; total_small <= 8; ++total_small) {
    initialize(static_cast<int>(templates[0].size()), total_small);
    Engine engine(tables, templates[0], Counts{total_small, 0, 0}, future);
    need(engine.enumerate() && ordinal == expected_count, "small gap domain");
    ++result.small;
  }
}

int early_stops(const Tables& tables, const LowWord& low, Counts target, int total) {
  const auto future = Clock::now() + std::chrono::minutes(10);
  int stops = 0;
  // Both flags must stop enclosing loops, even when search's return is unused.
  for (int mode : {1, 2}) for (uint64_t limit : {uint64_t(1), uint64_t(137)}) {
    initialize(static_cast<int>(low.size()), total);
    stop_mode = mode;
    stop_at = limit;
    Engine engine(tables, low, target, future);
    need(!engine.enumerate() && roots == limit && ordinal == limit,
         "found/timeout did not stop the entire traversal");
    need(engine.found == (mode == 1) && engine.timed_out == (mode == 2),
         "early-stop result flags");
    ++stops;
  }
  initialize(static_cast<int>(low.size()), total);
  stop_mode = 2;
  Engine expired(tables, low, target, Clock::now() - std::chrono::seconds(1));
  need(!expired.enumerate() && expired.timed_out && !expired.found,
       "real deadline must not report exhaustion");
  need(ordinal == 256 && roots == 255 && expired.stats.compositions == 256,
       "real deadline checkpoint placement");
  return stops + 1;
}

int main() {
  try {
    Tables tables;
    AuditTotals result;
    for (bool distinguished : {false, true}) {
      const auto templates = universal_templates(distinguished);
      const Counts target = distinguished ? Counts{4, 4, 4} : Counts{6, 4, 4};
      const int total = distinguished ? 12 : 14;
      need(templates.size() == (distinguished ? 77 : 5), "template inventory");
      complete_runs(tables, templates, target, total, result);
      result.stops += early_stops(tables, templates[0], target, total);
    }
    need(result.runs == 164 && result.gaps == 45189640 && result.small == 18 && result.stops == 10,
         "declared audit coverage");
    std::cout << "{\"template_mode_runs\":" << result.runs
              << ",\"rank_checked_gaps\":" << result.gaps
              << ",\"search_handoffs\":" << result.handoffs
              << ",\"small_domains\":" << result.small
              << ",\"early_stop_controls\":" << result.stops << "}\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL " << error.what() << '\n';
    return 1;
  }
}
