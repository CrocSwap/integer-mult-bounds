#include <array>
#include <fstream>
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

struct Projector { int x,y,m; };
vector<Projector> p;
vector<int> counts, word;
bool commutes[16][16];
int family_index, possible_ancilla;
long long prefixes=0, normal_orders=0, reversed_orders=0, parity_survivors=0;
const int ID=0x8421, OFF=0x7bde;

int outer(int x,int y) {
    int result=0;
    for(int i=0;i<4;++i) if((x>>i)&1) result|=y<<(4*i);
    return result;
}

vector<int> normalize(vector<int> w) {
    vector<int> result;
    unsigned remaining=255;
    while(remaining) {
        int choice=-1;
        for(int i=0;i<8;++i) if((remaining>>i)&1) {
            bool available=true;
            for(int j=0;j<i;++j) if(((remaining>>j)&1) && !commutes[w[i]][w[j]]) available=false;
            if(available && (choice<0 || w[i]<w[choice])) choice=i;
        }
        result.push_back(w[choice]);remaining^=1u<<choice;
    }
    return result;
}

int parity_check() {
    int pivots[8]={}, rank=0;
    for(int bit=0;bit<16;++bit) if((OFF>>bit)&1) {
        int row=0;
        for(int j=0;j<8;++j) row|=((p[word[j]].m>>bit)&1)<<j;
        while(row) {
            int k=31-__builtin_clz((unsigned)row);
            if(pivots[k]) row^=pivots[k];
            else { pivots[k]=row; ++rank; break; }
        }
    }
    if(rank!=3) abort();
    int steps[8];
    for(int j=0;j<8;++j) {
        int row=1<<j, compact=0, target=0;
        for(int k=7;k>=0;--k) if(pivots[k] && ((row>>k)&1)) row^=pivots[k];
        for(int k=0;k<8;++k) if(!pivots[k]) compact|=((row>>k)&1)<<target++;
        steps[j]=compact;
    }
    array<unsigned short,32> polynomial{};
    polynomial[0]=ID;
    for(int j=0;j<8;++j) {
        array<unsigned short,32> next{};
        auto &gate=p[word[j]];
        for(int g=0;g<32;++g) if(polynomial[g]) {
            int m=polynomial[g], mx=0;
            for(int i=0;i<4;++i) mx|=__builtin_parity((unsigned)(((m>>(4*i))&15)&gate.x))<<i;
            int b=outer(mx,gate.y);
            next[g]^=m^b;next[g^steps[j]]^=b;
        }
        polynomial=next;
    }
    int diagonal_count[4]={}, exponent[4]={};
    for(int g=0;g<32;++g) {
        if(polynomial[g]&OFF) return 0;
        for(int i=0;i<4;++i) if((polynomial[g]>>(5*i))&1) { ++diagonal_count[i];exponent[i]=g; }
    }
    int valid=0;
    for(int i=0;i<4;++i) if(diagonal_count[i]!=1) return 0;
    for(int a=0;a<4;++a) if(((possible_ancilla>>a)&1) && exponent[a]==0) valid|=1<<a;
    return valid;
}

void enumerate() {
    ++prefixes;
    if(word.size()==8) {
        ++normal_orders;
        auto reversed=word;
        reverse(reversed.begin(),reversed.end());
        if(word>normalize(reversed)) return;
        ++reversed_orders;
        int valid=parity_check();
        if(!valid) return;
        ++parity_survivors;
        cout<<"{\"family\":"<<family_index<<",\"ancilla_mask\":"<<valid<<",\"order\":[";
        for(int j=0;j<8;++j) cout<<(j?",":"")<<word[j];
        cout<<"]}\n";
        return;
    }
    for(int j=0;j<(int)p.size();++j) if(counts[j]) {
        bool normal=true;
        for(int k=(int)word.size()-1;k>=0 && commutes[j][word[k]];--k) if(word[k]>j) { normal=false;break; }
        if(!normal) continue;
        --counts[j];word.push_back(j);enumerate();word.pop_back();++counts[j];
    }
}

int main(int argc,char**argv) {
    if(argc!=2) return 2;
    ifstream input(argv[1]);int families;input>>families;
    for(family_index=0;family_index<families;++family_index) {
        int n;input>>n>>possible_ancilla;
        p.resize(n);counts.resize(n);
        for(int j=0;j<n;++j) { input>>p[j].x>>p[j].y>>counts[j];p[j].m=outer(p[j].x,p[j].y); }
        for(int i=0;i<n;++i) for(int j=0;j<n;++j) commutes[i][j]=(i==j)||(!__builtin_parity((unsigned)(p[i].x&p[j].y))&&!__builtin_parity((unsigned)(p[j].x&p[i].y)));
        enumerate();
        if(family_index%200==0) cerr<<"progress "<<family_index<<" orders "<<reversed_orders<<" survivors "<<parity_survivors<<"\n";
    }
    cerr<<"{\"families\":"<<families<<",\"prefixes\":"<<prefixes<<",\"commutation_orders\":"<<normal_orders<<",\"reversal_orders\":"<<reversed_orders<<",\"parity_survivors\":"<<parity_survivors<<"}\n";
}
