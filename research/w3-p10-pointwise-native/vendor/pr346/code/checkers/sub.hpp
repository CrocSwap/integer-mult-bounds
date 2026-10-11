// Subspace store over F_p (p = 2^31-1) for subspaces of F_p^24 in canonical RREF.
#pragma once
#include <bits/stdc++.h>
using namespace std;
typedef uint64_t u64; typedef int64_t i64;
static const u64 P = 2147483647ULL;
#ifndef HDIM
#define HDIM 24
#endif
static const int H = HDIM;
static inline u64 mulm(u64 a, u64 b) { return (a * b) % P; }
static inline u64 addm(u64 a, u64 b) { u64 c = a + b; return c >= P ? c - P : c; }
static inline u64 subm(u64 a, u64 b) { return a >= b ? a - b : a + P - b; }
static u64 powm(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = mulm(r, a); a = mulm(a, a); e >>= 1; } return r; }
static inline u64 invm(u64 a) { return powm(a, P - 2); }
typedef array<u64, H> Row;

// in-place RREF; returns rank, rows resized to rank
static int rref(vector<Row>& M) {
    int r = 0, n = M.size();
    for (int c = 0; c < H && r < n; c++) {
        int k = -1;
        for (int i = r; i < n; i++) if (M[i][c]) { k = i; break; }
        if (k < 0) continue;
        swap(M[r], M[k]);
        u64 iv = invm(M[r][c]);
        for (int j = 0; j < H; j++) M[r][j] = mulm(M[r][j], iv);
        for (int i = 0; i < n; i++) if (i != r && M[i][c]) {
            u64 f = M[i][c];
            for (int j = 0; j < H; j++) if (M[r][j]) M[i][j] = subm(M[i][j], mulm(f, M[r][j]));
        }
        r++;
    }
    M.resize(r);
    return r;
}

struct Store {
    vector<vector<Row>> S;      // canonical RREF rows
    unordered_map<u64, vector<int>> byhash;
    unordered_map<u64, int> joinm, meetm;
    vector<int> annm;           // -1 unknown
    vector<signed char> ndm;    // -1 unknown, 0 degenerate, 1 nondegenerate
    u64 hashrows(const vector<Row>& R) {
        u64 h = 1469598103934665603ULL ^ R.size();
        for (auto& r : R) for (int j = 0; j < H; j++) { h ^= r[j] + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2); }
        return h;
    }
    int intern_rref(const vector<Row>& R) {  // R must be canonical rref
        u64 h = hashrows(R);
        auto& L = byhash[h];
        for (int id : L) if (S[id] == R) return id;
        S.push_back(R); annm.push_back(-1); ndm.push_back(-1);
        L.push_back(S.size() - 1);
        return S.size() - 1;
    }
    int intern(vector<Row> R) { rref(R); return intern_rref(R); }
    int dim(int a) const { return S[a].size(); }
    int join(int a, int b) {
        if (a == b) return a;
        if (a > b) swap(a, b);
        u64 key = (u64)a << 32 | (u64)b;
        auto it = joinm.find(key); if (it != joinm.end()) return it->second;
        vector<Row> M = S[a]; M.insert(M.end(), S[b].begin(), S[b].end());
        int r = intern(M);
        joinm[key] = r; return r;
    }
    int ann(int a) {
        if (annm[a] >= 0) return annm[a];
        const vector<Row>& R = S[a];
        vector<int> piv; vector<char> isp(H, 0);
        for (auto& r : R) { int c = 0; while (!r[c]) c++; piv.push_back(c); isp[c] = 1; }
        vector<Row> N;
        for (int f = 0; f < H; f++) if (!isp[f]) {
            Row x{}; x[f] = 1;
            for (size_t i = 0; i < R.size(); i++) x[piv[i]] = subm(0, R[i][f]);
            N.push_back(x);
        }
        int r = intern(N);
        annm[a] = r; annm[r] = a;
        return r;
    }
    int meet(int a, int b) {
        if (a == b) return a;
        if (a > b) swap(a, b);
        u64 key = (u64)a << 32 | (u64)b;
        auto it = meetm.find(key); if (it != meetm.end()) return it->second;
        int r = ann(join(ann(a), ann(b)));
        meetm[key] = r; return r;
    }
    bool contains(int big, int small) { return join(big, small) == big; }
    bool nondeg(int a) {  // Gram under G = I - J/9
        if (ndm[a] >= 0) return ndm[a];
        const vector<Row>& R = S[a]; int d = R.size();
        if (d == 0) { ndm[a] = 1; return true; }
        u64 i9 = invm(9);
        vector<u64> s(d, 0);
        for (int i = 0; i < d; i++) { u64 t = 0; for (int j = 0; j < H; j++) t = addm(t, R[i][j]); s[i] = t; }
        vector<Row> M(d);
        // use Row type with first d columns as matrix (d<=24)
        for (int i = 0; i < d; i++) for (int k = 0; k < d; k++) {
            u64 t = 0; for (int j = 0; j < H; j++) t = addm(t, mulm(R[i][j], R[k][j]));
            t = subm(t, mulm(i9, mulm(s[i], s[k])));
            M[i][k] = t;
        }
        for (int i = 0; i < d; i++) for (int k = d; k < H; k++) M[i][k] = 0;
        int rk = rref(M);
        ndm[a] = (rk == d);
        return ndm[a];
    }
};

static Row rowmod(const vector<long long>& v) {
    Row r{};
    for (int j = 0; j < H; j++) { long long x = v[j] % (long long)P; if (x < 0) x += P; r[j] = x; }
    return r;
}

struct Rec { int k, a, b, c, f, z; };

struct Snapshot {
    int n, v, ZERO, FULL;
    vector<int> init, fin;          // catalog ids
    vector<vector<long long>> cov;  // v covectors
    unordered_map<int, int> cat2id; // catalog frame id -> store id
    vector<Rec> rec;
    void load(Store& st, const string& dir, const string& recfile) {
        {
            ifstream f(dir + "/frames.txt"); int nf; f >> nf;
            for (int i = 0; i < nf; i++) {
                int id, d; f >> id >> d; vector<Row> R;
                for (int k = 0; k < d; k++) { vector<long long> v(H); for (int j = 0; j < H; j++) f >> v[j]; R.push_back(rowmod(v)); }
                cat2id[id] = st.intern(R);
            }
        }
        {
            ifstream f(dir + "/states.txt"); f >> n >> v >> ZERO >> FULL;
            init.resize(n); fin.resize(n);
            for (int r = 0; r < n; r++) f >> init[r] >> fin[r];
            cov.assign(v, vector<long long>(H));
            for (int t = 0; t < v; t++) for (int j = 0; j < H; j++) f >> cov[t][j];
        }
        {
            ifstream f(recfile, ios::binary); Rec e;
            while (f.read((char*)&e, sizeof e)) rec.push_back(e);
        }
    }
};
