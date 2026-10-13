// Exhaustive rational nonvanishing certificates via a proved finite prime.
// Adapted from Rohan Arun PR39 geometry.cpp, with James Chang PR34's pivots.
// Both factors are now fixed I+J; every one of the 4,073,300 triple pairs is
// checked. A failed residue test gets a charged 47-singleton fallback.
// Zero identities are proved separately by the inherited exact rank cuts.
// Accelerated with OpenMP 32-core parallelization over triple records.
// Apache-2.0. Prepared with OpenAI Codex assistance.
#include <cstdint>
#include <iostream>
#include <vector>
#include <array>
#include <cassert>
#include <omp.h>
using namespace std;
constexpr int prime=1000003,a=23,b=25,d=47;
int mul(int x,int y){return int(int64_t(x)*y%prime);}
int power(int x,int n){int z=1;for(;n;n>>=1,x=mul(x,x))if(n&1)z=mul(z,x);return z;}

struct Triple { int aa, bb, cc; };
struct Result {
    int rowgood = 0;
    int product = 1;
    int count = 0;
    int64_t checked = 0;
    int64_t zeros = 0;
    vector<array<int,7>> rejected;
};

int main(){
 for(int i=2;i*i<=prime;++i)assert(prime%i);
 vector<int> R,C,piv;
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);
 R.push_back(a-1);C.push_back(0);
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);
 piv.push_back(2*a);
 for(int i=1;i<a-1;i++)piv.push_back(i+a+1);
 for(int i=a-1;i<a+5;i++)piv.push_back(2*a-i);
 for(int i=a+5;i<2*a-1;i++)piv.push_back(i-a-3);
 piv.push_back(1);piv.push_back(0);
 assert(piv.size()==d);
 const int xin=mul(3*(a+1),power(2*(3*(a+1)-10),prime-2));
 const int xout=prime-mul(a+1,power(5,prime-2));
 const int yin=mul(3*(b+1),power(2*(3*(b+1)-10),prime-2));
 const int yout=prime-mul(b+1,power(5,prime-2));

 vector<Triple> triples;
 for(int aa=0;aa<a;aa++)
  for(int bb=aa+1;bb<a;bb++)
   for(int cc=bb+1;cc<a;cc++)
    triples.push_back({aa,bb,cc});
 assert(triples.size()==1771);

 vector<Result> results(triples.size());

 #pragma omp parallel for schedule(dynamic, 1)
 for(size_t t=0; t<triples.size(); ++t){
  int aa=triples[t].aa, bb=triples[t].bb, cc=triples[t].cc;
  int xs[a];for(int i=0;i<a;i++)xs[i]=(i==aa||i==bb||i==cc)?xin:xout;
  int rowgood=0,product=1;
  int count=0;
  int64_t checked=0,zeros=0;
  vector<array<int,7>> rejected;

  for(int u=0;u<b;u++)for(int v=u+1;v<b;v++)for(int w=v+1;w<b;w++){
   int ys[b],M[d][d];bool available[d];
   for(int i=0;i<b;i++)ys[i]=(i==u||i==v||i==w)?yin:yout;
   for(int i=0;i<d;i++){available[i]=true;for(int j=0;j<d;j++){
    int z=prime-1;if(R[i]==C[j])z+=xs[R[i]];
    if(i%b==(a*b-d+j)%b)z+=ys[i%b];M[i][j]=z%prime;
   }}
   bool ok=true;int determinant=1;
   for(int i=0;i<d;i++){
    int c=piv[i],value=M[i][c];assert(available[c]);
    if(!value){rejected.push_back({aa,bb,cc,u,v,w,i});ok=false;break;}
    for(int j=c+1;j<d;j++)if(available[j]){assert(!M[i][j]);zeros++;}
    determinant=mul(determinant,value);checked++;available[c]=false;
    int inv=power(value,prime-2);
    for(int r=i+1;r<d;r++)if(M[r][c]){
     int ratio=mul(M[r][c],inv);
     for(int j=0;j<d;j++)if(available[j]&&M[i][j]){
      int z=M[r][j]-mul(ratio,M[i][j]);M[r][j]=z<0?z+prime:z;
     }
     M[r][c]=0;
    }
   }
   count++;
   if(ok){rowgood++;product=mul(product,determinant);}
  }
  assert(product);
  results[t].rowgood = rowgood;
  results[t].product = product;
  results[t].count = count;
  results[t].checked = checked;
  results[t].zeros = zeros;
  results[t].rejected = std::move(rejected);
 }

 int count=0,good=0;int64_t checked=0,zeros=0;
 vector<array<int,7>> rejected;

 cout<<"{\"prime\":"<<prime<<",\"dimensions\":[23,25],\"records\":[\n";
 for(size_t t=0; t<triples.size(); ++t){
  if(t)cout<<",\n";
  cout<<"["<<triples[t].aa<<","<<triples[t].bb<<","<<triples[t].cc<<","<<results[t].rowgood<<","<<results[t].product<<"]";
  count += results[t].count;
  good += results[t].rowgood;
  checked += results[t].checked;
  zeros += results[t].zeros;
  for(auto& r : results[t].rejected) rejected.push_back(r);
 }
 assert(count==4073300);
 cout<<"\n],\"pairs\":"<<count<<",\"good\":"<<good<<",\"fallback\":"<<rejected.size()
     <<",\"nonzero_pivots\":"<<checked<<",\"ordered_zero_checks\":"<<zeros<<",\"fallback_pairs\":[";
 for(size_t i=0;i<rejected.size();i++){
  if(i)cout<<",";cout<<"[";
  for(int j=0;j<7;j++){if(j)cout<<",";cout<<rejected[i][j];}cout<<"]";
 }
 cout<<"]}\n";
 return 0;
}
