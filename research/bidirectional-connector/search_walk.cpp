// Heuristic proposal search only, never an exclusion or optimality certificate.
// Fixed three-color classes; exact acceptance is in verify_walk.py.
// Cross-platform shuffle/library differences may change the proposed word.
// Apache-2.0. conorholds with substantial OpenAI Codex assistance.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
struct Eval {int score,paired,three;};
Eval evaluate(const std::vector<int>& word,int n,int first,int second) {
 std::array<std::vector<int>,3> values; std::array<std::array<bool,4096>,3> seen{};
 int p=0,q=0;
 auto cut=[&](){std::array<int,3> v{p,q,p^q};for(int d=0;d<3;d++)if(!seen[d][v[d]]){seen[d][v[d]]=true;values[d].push_back(v[d]);}};
 cut();for(int j:word){int color=j<first?0:(j<first+second?1:2);if(color!=1)p^=1<<j;if(color!=0)q^=1<<j;cut();}
 std::array<uint8_t,4096> cover{};
 for(auto& v:values)for(int a:v)for(int b:v)cover[a^b]=2;
 for(int a:values[0])for(int b:values[1])for(int c:values[2])if(!cover[a^b^c])cover[a^b^c]=1;
 int paired=0,three=0;for(int i=1;i<(1<<n);i++){paired+=cover[i]==2;three+=cover[i]!=0;}
 return {paired+three,paired,three};
}
int main(int argc,char** argv) {
 int n=argc>1?std::stoi(argv[1]):12;int trials=argc>2?std::stoi(argv[2]):200000;
 int first=argc>3?std::stoi(argv[3]):n/3;int second=argc>4?std::stoi(argv[4]):n/3;
 if((n!=9&&n!=12)||trials<=0||trials>2000000||first<=0||second<=0||first+second>=n)return 2;std::mt19937 rng(4097+n);
 std::vector<int> w,best;for(int j=0;j<n;j++){w.push_back(j);w.push_back(j);}int bestscore=-1;Eval be{};
 for(int k=0;k<trials;k++){
  if(k%10000==0)std::shuffle(w.begin(),w.end(),rng);
  auto old=evaluate(w,n,first,second);int a=rng()%w.size(),b=rng()%w.size();std::swap(w[a],w[b]);auto now=evaluate(w,n,first,second);
  double temperature=0.25+8.0*(1.0-double(k%10000)/10000);
  if(now.score<old.score&&std::generate_canonical<double,53>(rng)>std::exp((now.score-old.score)/temperature))std::swap(w[a],w[b]);else old=now;
  if(old.score>bestscore){bestscore=old.score;best=w;be=old;}
 }
 std::cout<<"{\"n\":"<<n<<",\"trials\":"<<trials<<",\"class_sizes\":["<<first<<','<<second<<','<<n-first-second<<"],\"paired_nonzero\":"<<be.paired<<",\"three_nonzero\":"<<be.three<<",\"optimistic_A_if_four_reads_suffice\":"<<4*((1<<n)-1)-be.score<<",\"word\":[";
 for(size_t i=0;i<best.size();i++){if(i)std::cout<<',';std::cout<<best[i];}std::cout<<"]}\n";
}
