// Price a word histogram with the base package's exact rational interval engine and 47-constraint assembly, unchanged.
// Compile with -DPR254_PRICE_SOURCE naming the base package's code/cohort-price.cpp. A price alone is not a certificate:
// verify.py also runs the base finite invoice.
#define main inherited_pr254_main
#include PR254_PRICE_SOURCE
#undef main

int main(int argc, char** argv) {
    if (argc != 4) return 2;
    auto word = load(argv[1]);
    auto banks = load(argv[2]);
    map<int, long long> H;
    for (auto it = word["histogram"].begin(); it != word["histogram"].end(); ++it)
        H[stoi(it.key())] = 40 * it.value().get<long long>();
    for (int r : {4, 23, 46, 50}) H[r] += 16 * 1760;
    int stock = banks["literal_stock"];
    if (stock % 5) throw runtime_error("nonintegral normalized stock");
    auto result = price(H, stock / 5);
    ofstream(argv[3]) << J{{"status", "PASS_REUSED_PR254_EXACT_PRICE_AND_OUTER47"},
        {"candidate", result}, {"finite_invoice_required", true}}.dump(2) << '\n';
    cout << "kappa " << result["kappa"] << '\n';
}
