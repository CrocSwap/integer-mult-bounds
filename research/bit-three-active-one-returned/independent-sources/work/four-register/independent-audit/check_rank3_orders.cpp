// Replay every multiset permutation and check the finite quotient with ring vectors.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;

struct Gate { int x,y,m; vector<int> steps; };
vector<Gate> gates;
bool commutes[16][16];

int scalar_product(int a,int b) {
    int out=0;
    for(int i=0;i<4;++i)for(int j=0;j<4;++j) {
        int bit=0;
        for(int k=0;k<4;++k)bit^=((a>>(4*i+k))&1)&((b>>(4*k+j))&1);
        out|=bit<<(4*i+j);
    }
    return out;
}

bool normal(const vector<int>& word) {
    for(int j=1;j<8;++j)
        for(int i=j-1;i>=0 && commutes[word[i]][word[j]];--i)
            if(word[i]>word[j])return false;
    return true;
}

vector<int> least_trace(vector<int> word) {
    vector<int> result;
    while(!word.empty()) {
        int chosen=0;
        for(int i=1;i<(int)word.size();++i)if(word[i]<word[chosen]) {
            bool movable=true;
            for(int j=0;j<i;++j)if(!commutes[word[i]][word[j]])movable=false;
            if(movable)chosen=i;
        }
        result.push_back(word[chosen]);word.erase(word.begin()+chosen);
    }
    return result;
}

void extend_span(vector<int>& values,int x) {
    if(find(values.begin(),values.end(),x)!=values.end())return;
    int old=values.size();
    for(int i=0;i<old;++i)values.push_back(values[i]^x);
}

void set_quotient_steps(const vector<int>& sorted_word) {
    vector<int> relations{0};
    for(int i=0;i<4;++i)for(int j=0;j<4;++j)if(i!=j) {
        int row=0;
        for(int k=0;k<8;++k)row|=((gates[sorted_word[k]].m>>(4*i+j))&1)<<k;
        extend_span(relations,row);
    }
    if(relations.size()!=8)throw runtime_error("Expected relation rank three");
    vector<int> full=relations, free;
    for(int i=0;i<8;++i)if(find(full.begin(),full.end(),1<<i)==full.end()) {
        free.push_back(1<<i);extend_span(full,1<<i);
    }
    if(free.size()!=5)throw runtime_error("Expected five quotient coordinates");
    int labels[256];fill(labels,labels+256,-1);
    for(int g=0;g<32;++g) {
        int representative=0;
        for(int i=0;i<5;++i)if((g>>i)&1)representative^=free[i];
        for(int r:relations)labels[r^representative]=g;
    }
    for(auto &gate:gates)gate.steps.clear();
    for(int k=0;k<8;++k)gates[sorted_word[k]].steps.push_back(labels[1<<k]);
}

uint32_t translate(uint32_t v,int step) {
    if(step&1)v=((v&0x55555555u)<<1)|((v&0xaaaaaaaau)>>1);
    if(step&2)v=((v&0x33333333u)<<2)|((v&0xccccccccu)>>2);
    if(step&4)v=((v&0x0f0f0f0fu)<<4)|((v&0xf0f0f0f0u)>>4);
    if(step&8)v=((v&0x00ff00ffu)<<8)|((v&0xff00ff00u)>>8);
    if(step&16)v=(v<<16)|(v>>16);
    return v;
}

int finite_roles(const vector<int>& word,int possible) {
    uint32_t matrix[4][4]{};int occurrence[16]{};
    for(int i=0;i<4;++i)matrix[i][i]=1;
    for(int letter:word) {
        auto &gate=gates[letter];
        int step=gate.steps[occurrence[letter]++];
        for(int row=0;row<4;++row) {
            uint32_t inner=0;
            for(int col=0;col<4;++col)if((gate.x>>col)&1)inner^=matrix[row][col];
            uint32_t delta=inner^translate(inner,step);
            for(int col=0;col<4;++col)if((gate.y>>col)&1)matrix[row][col]^=delta;
        }
    }
    int roles=0;
    for(int i=0;i<4;++i) {
        for(int j=0;j<4;++j)if(i!=j && matrix[i][j])return 0;
        if(__builtin_popcount(matrix[i][i])!=1)return 0;
        if(((possible>>i)&1) && matrix[i][i]==1)roles|=1<<i;
    }
    return roles;
}

int main(int argc,char**argv) {
    try {
        if(argc!=3)throw runtime_error("Need word input and expected binary records");
        ifstream input(argv[1]);ifstream binary(argv[2],ios::binary);
        if(!input || !binary)throw runtime_error("Cannot open input");
        int families;input>>families;
        uint64_t raw=0, traces=0, reversed=0, survivors=0;
        for(int family=0;family<families;++family) {
            int n,possible;input>>n>>possible;gates.resize(n);
            vector<int> word;
            for(int j=0;j<n;++j) {
                int count;input>>gates[j].x>>gates[j].y>>count;gates[j].m=0;
                for(int i=0;i<4;++i)if((gates[j].x>>i)&1)gates[j].m|=gates[j].y<<(4*i);
                for(int k=0;k<count;++k)word.push_back(j);
            }
            if(!input || word.size()!=8)throw runtime_error("Invalid family");
            for(int i=0;i<n;++i)for(int j=0;j<n;++j)
                commutes[i][j]=scalar_product(gates[i].m,gates[j].m)==scalar_product(gates[j].m,gates[i].m);
            set_quotient_steps(word);
            do {
                ++raw;if(!normal(word))continue;++traces;
                vector<int> backwards(word.rbegin(),word.rend());
                if(word>least_trace(backwards))continue;++reversed;
                int roles=finite_roles(word,possible);if(!roles)continue;
                unsigned char record[18];binary.read(reinterpret_cast<char*>(record),18);
                if(!binary)throw runtime_error("Binary records ended early");
                for(int j=0;j<8;++j)
                    if(record[2*j]+256*record[2*j+1]!=gates[word[j]].m)
                        throw runtime_error("The independently retained word differs");
                if(record[16]+256*record[17]!=roles)throw runtime_error("The ancilla mask differs");
                ++survivors;
            } while(next_permutation(word.begin(),word.end()));
        }
        if(binary.peek()!=char_traits<char>::eof())throw runtime_error("Unused binary records");
        int extra;if(input>>extra)throw runtime_error("Unused family input");
        cout<<"{\"status\":\"PASS_INDEPENDENT_RANK3_ORDER_AND_QUOTIENT_REPLAY\",\"families\":"<<families
            <<",\"raw_orders\":"<<raw<<",\"commutation_orders\":"<<traces<<",\"reversal_orders\":"<<reversed
            <<",\"quotient_survivors\":"<<survivors<<",\"binary_word_and_role_stream_identical\":true}\n";
    } catch(const exception& error) { cerr<<error.what()<<'\n';return 1; }
}
