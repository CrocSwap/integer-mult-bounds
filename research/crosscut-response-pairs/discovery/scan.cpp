#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include "json.hpp"
using namespace std;using J=nlohmann::json;struct E{int k,a,b,c,f,z;};
J load(string p){ifstream f(p);J j;f>>j;return j;}
int main(int ac,char**av){string dir=av[1],out=av[2];auto st=load(dir+"/249-states.json");int n=st["n"],v=st["v"],zero=st["ZERO"],full=st["FULL"];vector<E> ev;ifstream f(dir+"/249-records.bin",ios::binary);E e;while(f.read((char*)&e,sizeof e))ev.push_back(e);int nr=n-2*v,W=(nr+63)/64;vector<uint64_t>M((size_t)(n+1)*W);auto row=[&](int s){return &M[(size_t)s*W];};for(int j=0;j<nr;j++)row(2*v+j)[j/64]|=1ull<<(j%64);
vector<int>first(n,ev.size()),firstframe(n,-1),lastread(n,-1);vector<bool> valid(n,false);for(int r=2*v;r<n;r++){string k=to_string(r);int a=st["initial"].value(k,zero),b=st["final"].value(k,full);valid[r]=a==zero&&b==full;}
for(int i=0;i<(int)ev.size();i++){auto e=ev[i];if(e.k==1){if(e.a>=2*v&&first[e.a]==(int)ev.size()){first[e.a]=i;firstframe[e.a]=e.f;}if(e.b>=2*v){if(e.z==4&&e.f==zero&&e.a>=v&&e.a<2*v)lastread[e.b]=i;else if(first[e.b]==(int)ev.size()){first[e.b]=i;firstframe[e.b]=e.f;}}}else if(e.k==2||e.k==3){for(int r:{e.a,e.b})if(r>=2*v&&first[r]==(int)ev.size()){first[r]=i;firstframe[r]=(e.k==2&&r==e.a)?e.c:e.f;}}}
set<int>cuts;for(int i=3;i<ac;i++)cuts.insert(stoi(av[i]));J allmeta=J::object();for(int t=0;t<=*cuts.rbegin();t++){auto e=ev[t];if(e.k==1&&(e.c&1))for(int w=0;w<W;w++)row(e.a)[w]^=row(e.b)[w];else if(e.k==2)copy(row(e.a),row(e.a)+W,row(e.b));if(!cuts.count(t))continue;J meta=J::array();ofstream bin(out+"/response-"+to_string(t)+".bin",ios::binary);int cnt=0;for(int r=2*v;r<n;r++){if(!valid[r]||first[r]<=t||lastread[r]>t||firstframe[r]<0)continue;vector<uint64_t>col((v+63)/64);int c=r-2*v;for(int target=0;target<v;target++)if((row(v+target)[c/64]>>(c%64))&1)col[target/64]|=1ull<<(target%64);bool nonzero=false;for(auto x:col)nonzero|=x!=0;if(!nonzero)continue;bin.write((char*)col.data(),col.size()*8);meta.push_back({{"role",r},{"first",first[r]},{"frame",firstframe[r]},{"lastread",lastread[r]}});cnt++;}ofstream(out+"/meta-"+to_string(t)+".json")<<meta.dump();cerr<<"cut "<<t<<" eligible "<<cnt<<"\n";}
}
