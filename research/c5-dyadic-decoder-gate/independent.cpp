// Tekalign (tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
// Separately written exact search; input file supplies the ten physical labels.
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
using namespace std;
using Mask=__uint128_t;
array<array<int,8>,120> roots;
array<unsigned,120> support;
array<Mask,120> ortho;
array<int,32> costs;
array<unsigned,10> neighbors;
array<int,10> chosen;
uint64_t nodes=0,leaves=0,prunes=0;
int cap=19;
int indexbit(Mask m){uint64_t lo=(uint64_t)m;return lo?countr_zero(lo):64+countr_zero((uint64_t)(m>>64));}
int pop(Mask m){return popcount((uint64_t)m)+popcount((uint64_t)(m>>64));}
int rankbin(vector<unsigned> rows){array<unsigned,10>b={};int r=0;for(unsigned x:rows){while(x){int k=31-countl_zero(x);if(b[k])x^=b[k];else{b[k]=x;r++;break;}}}return r;}
int price(const array<unsigned,8>& masks){int s=0;for(auto m:masks)s+=costs[m];return s;}
bool dfs(array<Mask,10> domains,array<unsigned,8> masks,unsigned todo){
 nodes++; if(!todo){leaves++;cout<<"WITNESS cost="<<price(masks);for(int x:chosen)cout<<" "<<x;cout<<"\n";return true;}
 // Exact monotonic-cost filtering and minimum remaining values.
 int slot=-1,best=121;
 for(int i=0;i<10;i++)if(todo>>i&1){
  Mask keep=0,d=domains[i];
  while(d){int r=indexbit(d);d&=d-1;auto nm=masks;for(int k=0;k<8;k++)if(support[r]>>k&1)nm[k]|=1u<<(i/2);
   if(price(nm)<=cap)keep|=Mask(1)<<r;
  }
  domains[i]=keep;int n=pop(keep);if(!n){prunes++;return false;}if(n<best){slot=i;best=n;}
 }
 Mask d=domains[slot];
 while(d){int r=indexbit(d);d&=d-1;auto ds=domains;auto ms=masks;
  for(int k=0;k<8;k++)if(support[r]>>k&1)ms[k]|=1u<<(slot/2);
  bool ok=true;unsigned rem=todo&~(1u<<slot);
  for(int j=0;j<10;j++)if(rem>>j&1){
   if(neighbors[slot]>>j&1)ds[j]&=ortho[r];
   // Within-plane port interchange leaves this mask and tariff unchanged.
   if(j== (slot^1)){
    if(slot%2==0) ds[j]&=~((Mask(1)<<(r+1))-1);
    else ds[j]&=(Mask(1)<<r)-1;
   }
   if(!ds[j]){ok=false;break;}
  }
  if(ok){chosen[slot]=r;if(dfs(ds,ms,rem))return true;}
 }
 return false;
}
int main(int argc,char**argv){
 int anchor=argc>1?stoi(argv[1]):0;
 if(argc>2)cap=stoi(argv[2]);
 int n=0;for(int i=0;i<8;i++){roots[n][i]=2;support[n++]=1u<<i;}
 vector<array<int,4>> quads;
 for(int a=1;a<8;a++)for(int b=0;b<2;b++){array<int,4> q={};int j=0;for(int x=0;x<8;x++)if((popcount((unsigned)(a&x))%2)==b)q[j++]=x;quads.push_back(q);}
 sort(quads.begin(),quads.end());
 for(auto q:quads)for(int s=0;s<8;s++){roots[n][q[0]]=1;for(int j=1;j<4;j++)roots[n][q[j]]=(s>>(3-j)&1)?1:-1;for(int j:q)support[n]|=1u<<j;n++;}
 if(n!=120)return 2;
 for(int i=0;i<120;i++)for(int j=0;j<120;j++){int v=0;for(int k=0;k<8;k++)v+=roots[i][k]*roots[j][k];if(!v)ortho[i]|=Mask(1)<<j;}
 array<array<unsigned,2>,5> planes={{{289,49},{194,134},{304,56},{50,193},{200,196}}};
 if(argc>3){ifstream f(argv[3]);int row=stoi(argv[4]);for(int z=0;z<=row;z++)for(auto &p:planes)for(auto &v:p)if(!(f>>v))return 3;}
 for(int m=0;m<32;m++){vector<unsigned> vec;for(int i=0;i<5;i++)if(m>>i&1)for(auto x:planes[i])vec.push_back(x);vector<unsigned> rows;for(auto x:vec){unsigned r=0;for(int j=0;j<(int)vec.size();j++)r|=(popcount(x&vec[j])%2)<<j;rows.push_back(r);}costs[m]=rankbin(rows);}
 for(int i=0;i<10;i++)for(int j=0;j<10;j++)if(i!=j){bool bad=false;for(auto a:planes[i/2])for(auto b:planes[j/2])bad|=popcount(a&b)%2;if(bad)neighbors[i]|=1u<<j;}
 array<Mask,10> ds;ds.fill((Mask(1)<<120)-1);ds[0]=Mask(1)<<anchor;array<unsigned,8> ms={};chosen.fill(-1);
 auto begin=chrono::steady_clock::now();bool found=dfs(ds,ms,1023);
 cout<<"RESULT anchor="<<anchor<<" cap="<<cap<<" found="<<found<<" nodes="<<nodes<<" leaves="<<leaves<<" prunes="<<prunes<<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-begin).count()<<"\n";
}
