// Terminal predicate extracted from Dylan Crow's pinned legality_h.cpp.
// This probes that predicate, not the full native geometry or scalar replay.
// Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include "json.hpp"
using namespace std;
using nlohmann::json;

int main(int argc, char** argv) {
    if (argc != 3) return 2;
    json baseline, st;
    ifstream(argv[1]) >> baseline;
    ifstream(argv[2]) >> st;
    int n = baseline["n"];
    vector<int> state(n);
    for (int s = 0; s < n; s++) state[s] = baseline["final"][to_string(s)];
    // Exact comparison used by the retained native consumer at return.
    for (int s = 0; s < n; s++) {
        if (state[s] != st["final"][to_string(s)]) {
            cout << "REJECT_FINAL_FRAME role=" << s << '\n';
            return 1;
        }
    }
    cout << "PASS_FINAL_FRAME_PREDICATE roles=" << n << '\n';
}
