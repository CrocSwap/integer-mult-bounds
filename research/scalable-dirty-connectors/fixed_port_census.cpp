// Fixed-port two-root connector census. Apache-2.0.
#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string_view>
#include <system_error>
#include <vector>

using namespace std;

constexpr int kSources = 5;
constexpr int kBCalls = 2 * kSources;
constexpr int kMaxTransfers = 8;
constexpr int kCanonicalPairings = 945;

struct Event {
  int kind; // 0: B source call; 1: S01; 2: S10
};

struct Boundary {
  int row0;
  int source_mask;
};

int transfers = 0;
int event_count = 0;
long long identity_words = 0;
long long frame_patterns = 0;
long long legal_schedules = 0;
array<unsigned long long, 33> coverage_hist{};
int best_coverage = -1;
uint32_t best_cover = 0;
vector<int> best_directions;
vector<int> best_slots;
array<int, kBCalls> best_word{};
array<int, kSources> best_axes{};
vector<Event> events;
array<int, kBCalls> axes_by_call{};
array<int, kBCalls> pair_word{};

bool identity_word(const vector<int> &directions) {
  int row0 = 1, row1 = 2;
  for (int direction : directions) {
    if (direction == 0)
      row0 ^= row1; // S01: z0 += z1
    else
      row1 ^= row0; // S10: z1 += z0
  }
  return row0 == 1 && row1 == 2;
}

int fixed_port_axis(int row0, int row1) {
  for (int axis = 1; axis <= 3; ++axis) {
    const int first = popcount(static_cast<unsigned>(row0 & axis)) & 1;
    const int second = popcount(static_cast<unsigned>(row1 & axis)) & 1;
    if (first == 1 && second == 0)
      return axis;
  }
  abort(); // The current two-row frame is invertible.
}

int project_mask(int row0, const array<int, kSources> &source_state) {
  int mask = 0;
  for (int source = 0; source < kSources; ++source)
    if (popcount(static_cast<unsigned>(row0 & source_state[source])) & 1)
      mask |= 1 << source;
  return mask;
}

uint32_t xor_translate(uint32_t points, int offset) {
  static constexpr uint32_t zero_masks[5] = {
      0x55555555u, 0x33333333u, 0x0f0f0f0fu, 0x00ff00ffu, 0x0000ffffu};
  for (int bit = 0; bit < kSources; ++bit) {
    if ((offset & (1 << bit)) == 0)
      continue;
    const int distance = 1 << bit;
    const uint32_t low = zero_masks[bit];
    points = ((points & low) << distance) | ((points & ~low) >> distance);
  }
  return points;
}

uint32_t difference_cover(const array<uint32_t, 4> &points) {
  uint32_t cover = 0;
  for (int row0 = 1; row0 <= 3; ++row0) {
    uint32_t offsets = points[row0];
    while (offsets != 0) {
      const int offset = countr_zero(offsets);
      offsets &= offsets - 1;
      cover |= xor_translate(points[row0], offset);
    }
  }
  return cover;
}

void evaluate_pair_word(const vector<int> &directions,
                        const vector<int> &slots) {
  array<int, kSources> source_axes{};
  array<int, kSources> source_state{};
  for (int call = 0; call < kBCalls; ++call) {
    const int label = pair_word[call];
    if (source_axes[label] == 0)
      source_axes[label] = axes_by_call[call];
    else if (source_axes[label] != axes_by_call[call])
      abort(); // Pair generation only joins calls with equal axes.
  }

  int row0 = 1, row1 = 2, source_call = 0;
  array<uint32_t, 4> points{};
  auto record = [&]() {
    points[row0] |= uint32_t{1} << project_mask(row0, source_state);
  };
  record();
  for (const Event &event : events) {
    if (event.kind == 0) {
      const int label = pair_word[source_call];
      source_state[label] ^= source_axes[label];
      ++source_call;
    } else if (event.kind == 1) {
      row0 ^= row1;
    } else {
      row1 ^= row0;
    }
    record();
  }
  if (source_call != kBCalls || row0 != 1 || row1 != 2 ||
      any_of(source_state.begin(), source_state.end(),
             [](int value) { return value != 0; }))
    abort();

  const uint32_t cover = difference_cover(points);
  const int size = popcount(cover);
  ++coverage_hist[size];
  ++legal_schedules;
  if (size > best_coverage) {
    best_coverage = size;
    best_cover = cover;
    best_directions = directions;
    best_slots = slots;
    best_word = pair_word;
    best_axes = source_axes;
  }
}

void pair_calls_by_axis(int first_unpaired, int next_label,
                        const vector<int> &directions,
                        const vector<int> &slots) {
  int first = first_unpaired;
  while (first < kBCalls && pair_word[first] != -1)
    ++first;
  if (first == kBCalls) {
    evaluate_pair_word(directions, slots);
    return;
  }

  pair_word[first] = next_label;
  for (int partner = first + 1; partner < kBCalls; ++partner) {
    if (pair_word[partner] != -1 ||
        axes_by_call[first] != axes_by_call[partner])
      continue;
    pair_word[partner] = next_label;
    pair_calls_by_axis(first + 1, next_label + 1, directions, slots);
    pair_word[partner] = -1;
  }
  pair_word[first] = -1;
}

void visit_frame(const vector<int> &directions, const vector<int> &slots) {
  ++frame_patterns;
  events.clear();
  events.reserve(event_count);
  int row0 = 1, row1 = 2, slot_index = 0, source_call = 0;
  for (int time = 0; time < event_count; ++time) {
    if (slot_index < transfers && slots[slot_index] == time) {
      const int direction = directions[slot_index++];
      events.push_back({direction + 1});
      if (direction == 0)
        row0 ^= row1;
      else
        row1 ^= row0;
    } else {
      axes_by_call[source_call++] = fixed_port_axis(row0, row1);
      events.push_back({0});
    }
  }
  if (slot_index != transfers || source_call != kBCalls || row0 != 1 ||
      row1 != 2)
    abort();

  pair_word.fill(-1);
  pair_calls_by_axis(0, 0, directions, slots);
}

void choose_slots(int next, vector<int> &slots, const vector<int> &directions) {
  if (static_cast<int>(slots.size()) == transfers) {
    visit_frame(directions, slots);
    return;
  }
  const int have = static_cast<int>(slots.size());
  for (int time = next; time <= event_count - (transfers - have); ++time) {
    slots.push_back(time);
    choose_slots(time + 1, slots, directions);
    slots.pop_back();
  }
}

void run_exact_census() {
  event_count = kBCalls + transfers;
  const int direction_words = 1 << transfers;
  for (int code = 0; code < direction_words; ++code) {
    vector<int> directions(static_cast<size_t>(transfers));
    for (int index = 0; index < transfers; ++index)
      directions[index] = (code >> index) & 1;
    if (!identity_word(directions))
      continue;
    ++identity_words;
    vector<int> slots;
    slots.reserve(static_cast<size_t>(transfers));
    choose_slots(0, slots, directions);
  }

  const unsigned long long full_schedules =
      static_cast<unsigned long long>(frame_patterns) * kCanonicalPairings;
  cout << "PASS_FIXED_PORT_CENSUS\n";
  cout << "transfers=" << transfers
       << " identity_direction_words=" << identity_words
       << " frame_patterns=" << frame_patterns
       << " canonical_pairings_per_frame=" << kCanonicalPairings
       << " full_schedules=" << full_schedules
       << " legal_schedules=" << legal_schedules
       << " max_coverage=" << best_coverage
       << " universal=" << (best_coverage == 32) << "\n";
  cout << "coverage_hist";
  for (int size = 0; size <= 32; ++size)
    if (coverage_hist[size] != 0)
      cout << ' ' << size << ':' << coverage_hist[size];
  cout << "\n";
  cout << "best_directions";
  for (int direction : best_directions)
    cout << ' ' << direction;
  cout << " best_slots";
  for (int slot : best_slots)
    cout << ' ' << slot;
  cout << " best_word";
  for (int label : best_word)
    cout << ' ' << label;
  cout << " best_axes";
  for (int axis : best_axes)
    cout << ' ' << axis;
  cout << " best_cover=0x" << hex << best_cover << dec << "\n";
}

bool run_eight_transfer_positive_control() {
  constexpr array<int, 8> directions{1, 1, 0, 0, 1, 1, 0, 0};
  constexpr array<int, 8> slots{0, 2, 3, 5, 8, 10, 11, 13};
  constexpr array<int, kBCalls> word{0, 1, 2, 3, 0, 4, 3, 1, 4, 2};
  constexpr array<int, kSources> expected_axes{3, 1, 1, 1, 1};

  array<int, kSources> source_axes{};
  array<int, kSources> source_state{};
  vector<Event> witness_events;
  witness_events.reserve(kBCalls + 8);
  int row0 = 1, row1 = 2, slot_index = 0, source_call = 0;
  for (int time = 0; time < kBCalls + 8; ++time) {
    if (slot_index < 8 && slots[slot_index] == time) {
      const int direction = directions[slot_index++];
      witness_events.push_back({direction + 1});
      if (direction == 0)
        row0 ^= row1;
      else
        row1 ^= row0;
    } else {
      const int axis = fixed_port_axis(row0, row1);
      const int label = word[source_call++];
      if (source_axes[label] == 0)
        source_axes[label] = axis;
      else if (source_axes[label] != axis)
        return false;
      witness_events.push_back({0});
    }
  }
  if (slot_index != 8 || source_call != kBCalls || row0 != 1 || row1 != 2 ||
      source_axes != expected_axes)
    return false;

  vector<Boundary> boundaries;
  boundaries.reserve(kBCalls + 9);
  row0 = 1;
  row1 = 2;
  auto record = [&]() {
    boundaries.push_back({row0, project_mask(row0, source_state)});
  };
  record();
  source_call = 0;
  for (const Event &event : witness_events) {
    if (event.kind == 0) {
      const int label = word[source_call];
      source_state[label] ^= source_axes[label];
      ++source_call;
    } else if (event.kind == 1) {
      row0 ^= row1;
    } else {
      row1 ^= row0;
    }
    record();
  }
  if (row0 != 1 || row1 != 2 ||
      any_of(source_state.begin(), source_state.end(),
             [](int value) { return value != 0; }))
    return false;

  array<bool, 32> covered{};
  int readout_pairs = 0;
  for (int target = 1; target < 32; ++target) {
    bool found = false;
    for (size_t first = 0; first < boundaries.size() && !found; ++first) {
      for (size_t second = first + 1; second < boundaries.size(); ++second) {
        if (boundaries[first].row0 == boundaries[second].row0 &&
            (boundaries[first].source_mask ^ boundaries[second].source_mask) ==
                target) {
          covered[static_cast<size_t>(target)] = true;
          ++readout_pairs;
          found = true;
          break;
        }
      }
    }
    if (!found)
      return false;
  }

  // Exercise the actual census path, including compatible-pair generation
  // and difference_cover, on this restoring eight-transfer frame. This is
  // bounded to one frame, not an exhaustive eight-transfer census.
  transfers = 8;
  event_count = kBCalls + transfers;
  visit_frame(vector<int>(directions.begin(), directions.end()),
              vector<int>(slots.begin(), slots.end()));
  if (frame_patterns != 1 || coverage_hist[32] == 0)
    return false;
  cout << "PASS_FIXED_PORT_EIGHT_TRANSFER_POSITIVE_CONTROL\n";
  cout << "engine_frame_patterns=" << frame_patterns
       << " engine_legal_pairings=" << legal_schedules
       << " engine_universal_pairings=" << coverage_hist[32] << "\n";
  cout << "transfers=8 source_calls=10 readout_pairs=" << readout_pairs
       << " readout_calls=" << 2 * readout_pairs << " covered_nonzero_masks="
       << count(covered.begin() + 1, covered.end(), true)
       << " roots_restored=1 sources_restored=1\n";
  cout << "directions";
  for (int direction : directions)
    cout << ' ' << direction;
  cout << " slots";
  for (int slot : slots)
    cout << ' ' << slot;
  cout << " source_word";
  for (int label : word)
    cout << ' ' << label;
  cout << " source_axes";
  for (int axis : source_axes)
    cout << ' ' << axis;
  cout << "\n";
  return true;
}

int main(int argc, char **argv) {
  if (argc != 2) {
    cerr << "usage: fixed_port_census <transfers: 0..8>\n";
    return 2;
  }
  int requested = -1;
  const string_view argument(argv[1]);
  const auto [end, error] =
      from_chars(argument.data(), argument.data() + argument.size(), requested);
  if (error != errc{} || end != argument.data() + argument.size() ||
      requested < 0 || requested > kMaxTransfers) {
    cerr << "usage: fixed_port_census <transfers: 0..8>\n";
    return 2;
  }

  if (requested == 8)
    return run_eight_transfer_positive_control() ? 0 : 1;
  transfers = requested;
  run_exact_census();
  return 0;
}
