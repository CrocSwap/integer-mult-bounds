// Compare the field engine with the separate rational engine on fixed words.
#define main full_catalogue_main
#include "../../clean-ancilla/two_bases.cpp"
#undef main

int main() {
    setup();
    int x, y, index = 0;
    while (std::cin >> x >> y) {
        Search s;
        s.index = index;
        s.word[0] = outer_table[x][y];
        for (int j = 1; j < 8; ++j) {
            if (!(std::cin >> x >> y)) return 2;
            s.word[j] = outer_table[x][y];
        }
        s.start();
        std::cout << "{\"case\":" << index++ << ",\"terminals\":" << s.terminals
                  << ",\"robust\":" << s.robust << ",\"states\":["
                  << s.states[0] << ',' << s.states[1] << ',' << s.states[2]
                  << ',' << s.states[3] << "]}\n";
    }
}
