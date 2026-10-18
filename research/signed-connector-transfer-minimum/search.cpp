// Bounded exact synthesis, prepared for Ross Richardson with OpenAI Codex.
// Apache-2.0. See README for the reduction and predecessor attribution.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
using V = std::array<int,3>;
const V target[3] = {{1,1,1},{1,1,-1},{1,-1,0}};
struct State { int h=0; V z{},w{}; };
struct Event { char kind; int op,sign,root; };
struct Read { int before=-1,after=-1,root=-1,sign=0; };
std::vector<int> transfers;
std::vector<State> history;
std::vector<Event> events;
int counts[3]{}, ports[3]{}, signs[3]{}, levels[3]{};
uint64_t leaves=0, masks[8]{}, rootwords=0;
bool found=false, stop_first=true;

bool equal(const V &a,const V &b) {return a==b;}
int extend(int mask, std::array<Read,3> &reads) {
  const auto &now=history.back(); int last=int(history.size())-1;
  for(int prior=0;prior<last;++prior) {
    const auto &old=history[prior];
    for(int root=0;root<2;++root) {
      if(root==0 && now.h!=old.h) continue;
      const V &a=root?now.w:now.z, &b=root?old.w:old.z;
      V d{}; for(int j=0;j<3;++j)d[j]=a[j]-b[j];
      for(int i=0;i<3;++i) if(!(mask&(1<<i))) {
        int s=0;
        if(equal(d,target[i]))s=1;
        V neg{};for(int j=0;j<3;++j)neg[j]=-target[i][j];
        if(equal(d,neg))s=-1;
        if(s) {mask|=1<<i;reads[i]={prior,last,root,s};}
      }
    }
  }
  return mask;
}

void emit(const std::array<Read,3>& reads) {
  std::cout << "{\"transfers\":"<<transfers.size()<<",\"word\":[";
  bool first=true;
  auto out=[&](char k,int op,int sign,int root) {
    if(!first)std::cout<<',';first=false;
    std::cout<<"[\""<<k<<"\","<<op<<','<<sign<<','<<root<<']';
  };
  for(int t=0;t<int(history.size());++t) {
    for(int i=0;i<3;++i) {
      if(reads[i].before==t)out('A',i,-reads[i].sign,reads[i].root);
      if(reads[i].after==t)out('A',i,reads[i].sign,reads[i].root);
    }
    if(t<int(events.size())) {auto e=events[t];out(e.kind,e.op,e.sign,e.root);}
  }
  std::cout<<"]}"<<std::endl;
}

void walk(int rpos,int bcount,int mask,std::array<Read,3> reads) {
  if(found && stop_first)return;
  if(bcount==6 && rpos==int(transfers.size())) {
    ++leaves;++masks[mask];
    const auto &s=history.back();
    if(s.h!=0 || s.z!=V{} || s.w!=V{}) {std::cerr<<"invalid terminal";std::exit(2);}
    if(mask==7 && !found) {found=true;emit(reads);}
    return;
  }
  auto descend=[&](State s,Event e,int nr,int nb) {
    events.push_back(e);history.push_back(s);
    auto nextreads=reads;int nextmask=extend(mask,nextreads);
    walk(nr,nb,nextmask,nextreads);
    history.pop_back();events.pop_back();
  };
  if(rpos<int(transfers.size())) {
    State s=history.back();int a=transfers[rpos];s.h+=a;
    for(int j=0;j<3;++j)s.z[j]+=a*s.w[j];
    descend(s,{'R',a,1,0},rpos+1,bcount);
  }
  for(int j=0;j<3;++j) {
    if(counts[j]==2)continue;
    if(counts[j]==1) {
      if(ports[j] && levels[j]!=history.back().h)continue;
      State s=history.back();(ports[j]?s.w:s.z)[j]-=signs[j];
      ++counts[j];descend(s,{'B',j,-signs[j],ports[j]},rpos,bcount+1);--counts[j];
    } else {
      for(int port=0;port<2;++port)for(int sign:{-1,1}) {
        State s=history.back();(port?s.w:s.z)[j]+=sign;
        ports[j]=port;signs[j]=sign;levels[j]=s.h;++counts[j];
        descend(s,{'B',j,sign,port},rpos,bcount+1);--counts[j];
      }
    }
  }
}

void roots(int remaining,int sum) {
  if(found && stop_first)return;
  if(remaining==0) {
    if(sum)return;
    ++rootwords;history.assign(1,State{});walk(0,0,0,{});return;
  }
  for(int a:{-2,-1,1,2}) {
    if(std::abs(sum+a)>2*(remaining-1))continue;
    transfers.push_back(a);roots(remaining-1,sum+a);transfers.pop_back();
  }
}
int main(int argc,char**argv) {
  int maximum=argc>1?std::stoi(argv[1]):5;
  if(maximum<0 || maximum>6)return 2;
  stop_first=argc<3 || std::string(argv[2])!="--complete";
  for(int n=0;n<=maximum;++n) {
    leaves=rootwords=0;for(auto &x:masks)x=0;found=false;roots(n,0);
    std::cerr<<"n="<<n<<" rootwords="<<rootwords<<" leaves="<<leaves<<" masks=";
    for(auto x:masks)std::cerr<<x<<',';std::cerr<<" found="<<found<<'\n';
    if(found && stop_first)return 0;
  }
  return 0;
}
