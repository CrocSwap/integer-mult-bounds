#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iostream>
#include <random>
#include <vector>
using namespace std;
int coverage(const vector<int>& w){
 unsigned long long seen[4]={1,0,0,0}; int p[32],q=0;
 for(int i=0;i<(int)w.size();i++){p[i]=q;q^=1<<w[i];}
 for(int i=0;i<(int)w.size();i++)for(int j=0;j<i;j++){int x=p[i]^p[j];seen[x>>6]|=1ULL<<(x&63);}
 return __builtin_popcountll(seen[0])+__builtin_popcountll(seen[1])+__builtin_popcountll(seen[2])+__builtin_popcountll(seen[3]);
}
int main(int argc,char**argv){
 int seconds=argc>1?atoi(argv[1]):30; int dim=argc>2?atoi(argv[2]):8; int len=4*dim-4; int pattern=argc>3?atoi(argv[3]):-1; mt19937_64 rng(20261024); vector<int>w;
 for(int i=0;i<dim;i++)for(int j=0;j<(i<dim-2?4:2);j++)w.push_back(i);
 if(pattern>=0){w.clear();for(int i=0;i<8;i++){int c=i<pattern?6:(i<7-pattern?4:2);for(int j=0;j<c;j++)w.push_back(i);}len=w.size();}
 auto start=chrono::steady_clock::now();int best=0;long long n=0; vector<int>bw;
 while(chrono::duration<double>(chrono::steady_clock::now()-start).count()<seconds){
  shuffle(w.begin(),w.end(),rng);int cur=coverage(w);
  for(int t=0;t<20000;t++){
   int a=rng()%len,b=rng()%len;if(w[a]==w[b])continue;
   swap(w[a],w[b]);int c=coverage(w);double temp=0.15+2.5*pow(1-t/20000.0,2);
   if(c>=cur||generate_canonical<double,53>(rng)<exp((c-cur)/temp))cur=c;else swap(w[a],w[b]);n++;
   if(cur>best){best=cur;bw=w;cout<<"best "<<best<<" trials "<<n<<" word ";for(int v:bw)cout<<v;cout<<endl;}
   if(best==(1<<dim))return 0;
  }
 }
 cout<<"INCOMPLETE heuristic only trials "<<n<<" best "<<best<<endl;
 return 0;
}
