// Reuse one nonpivot delivery wire across nested source frames.
// A left vertex is a binary gate; a right vertex is one input delivery.
// If b=a+x and c=a+y, x an ancestor of y, then source_frame(b)<=source_frame(c).
// Matching at most one outgoing delivery per b leaves a last-used input at
// every gate, which can be overwritten by its sum. Each link saves one role.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <unordered_map>
#include <vector>
using U=uint32_t;using W=uint64_t;
U word(std::ifstream&f){U x;f.read(reinterpret_cast<char*>(&x),4);if(!f)throw std::runtime_error("Short file");return x;}
template<class T>std::vector<T>read(std::ifstream&f,size_t n){std::vector<T>x(n);f.read(reinterpret_cast<char*>(x.data()),sizeof(T)*n);if(!f)throw std::runtime_error("Short vector");return x;}
W pair_key(U a,U b){return(W(std::min(a,b))<<32)|std::max(a,b);}
struct Hash{size_t operator()(W x)const{x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);}};
int main(int argc,char**argv){
  if(argc!=5&&argc!=6)return 2;auto start=std::chrono::steady_clock::now();U depth=std::stoul(argv[3]);
  bool mixed=argc==6&&std::string(argv[5])=="mixed";
  if(depth>12)throw std::runtime_error("Depth bound too large");
  std::ifstream f(argv[1],std::ios::binary),t(argv[2],std::ios::binary);
  U h=word(f),v=word(f),n=word(f),q=word(f);auto parents=read<std::pair<U,U>>(f,n);
  auto roots=read<U>(f,q);auto active=read<uint8_t>(f,n);auto core=read<U>(f,n);
  U th=word(t),tn=word(t),nz=word(t);if(th!=h||tn!=n)throw std::runtime_error("Mismatched target export");
  t.seekg(20*W(nz)+4*W(n),std::ios::cur);auto delayed=read<uint8_t>(t,n);
  std::vector<uint8_t>source(n);std::vector<U>size(n);uint64_t additions=0,source_gates=0;
  for(U i=1;i<n;i++)if(active[i]){
    source[i]=__builtin_popcount(core[i])>=2||delayed[i];
    if(i<=v)size[i]=1;
    else{auto[a,b]=parents[i];if(!a||!b||a>=i||b>=i)throw std::runtime_error("Invalid topological DAG");size[i]=size[a]+size[b];additions++;source_gates+=source[i];}
  }
  std::unordered_map<W,U,Hash>lookup;lookup.reserve(source_gates*4/3);
  for(U i=v+1;i<n;i++)if(active[i]&&source[i]){
    auto[a,b]=parents[i];if(!source[a]||!source[b])throw std::runtime_error("Source cut not ancestor closed");
    if(!lookup.emplace(pair_key(a,b),i).second)throw std::runtime_error("Duplicate addition pair");
  }
  std::vector<W>edges;uint64_t probes=0;
  for(U c=v+1;c<n;c++)if(active[c]&&(source[c]||mixed)){
    for(U side=0;side<2;side++){
      U a=side?parents[c].second:parents[c].first;
      U y=side?parents[c].first:parents[c].second;
      std::vector<std::pair<U,U>>stack{{y,0}};
      while(!stack.empty()){
        auto[at,level]=stack.back();stack.pop_back();if(level==depth||at<=v)continue;
        for(U x:{parents[at].first,parents[at].second}){
          probes++;auto found=lookup.find(pair_key(a,x));
          if(found!=lookup.end()){
            U b=found->second;if(size[b]>=size[c])throw std::runtime_error("Nonmonotone stream link");
            edges.push_back((W(b)<<32)|(2*c+side));
          }
          stack.emplace_back(x,level+1);
        }
      }
    }
  }
  std::unordered_map<W,U,Hash>().swap(lookup);
  std::sort(edges.begin(),edges.end());edges.erase(std::unique(edges.begin(),edges.end()),edges.end());
  std::cerr<<"candidate links "<<edges.size()<<" after "<<probes<<" ancestor probes\n";
  std::vector<U>offset(n+1),right(edges.size()),left_vertices;
  for(W e:edges)offset[(e>>32)+1]++;
  for(U i=1;i<=n;i++)offset[i]+=offset[i-1];
  for(U i=1;i<n;i++)if(offset[i]<offset[i+1])left_vertices.push_back(i);
  for(size_t j=0;j<edges.size();j++)right[j]=U(edges[j]);std::vector<W>().swap(edges);
  std::vector<U>match_left(n),match_right(2*size_t(n)),distance(n);
  constexpr U INF=std::numeric_limits<U>::max();U matched=0,phases=0;
  while(true){
    std::vector<U>queue;queue.reserve(left_vertices.size());bool path=false;
    for(U b:left_vertices){distance[b]=match_left[b]?INF:0;if(!match_left[b])queue.push_back(b);}
    for(size_t j=0;j<queue.size();j++){
      U b=queue[j];for(U at=offset[b];at<offset[b+1];at++){
        U next=match_right[right[at]];if(!next)path=true;
        else if(distance[next]==INF){distance[next]=distance[b]+1;queue.push_back(next);}
      }
    }
    if(!path)break;phases++;
    std::function<bool(U)>augment=[&](U b){
      for(U at=offset[b];at<offset[b+1];at++){
        U r=right[at],next=match_right[r];
        if(!next||(distance[next]==distance[b]+1&&augment(next))){match_left[b]=r;match_right[r]=b;return true;}
      }
      distance[b]=INF;return false;
    };
    U delta=0;for(U b:left_vertices)if(!match_left[b]&&augment(b)){matched++;delta++;}
    if(!delta)throw std::runtime_error("Matching failed to progress");
    std::cerr<<"phase "<<phases<<" added "<<delta<<" links; total "<<matched<<'\n';
  }
  // Every chosen outgoing continuation leaves the other input at its last use.
  // Each destination delivery has at most one predecessor, and support size
  // strictly increases along every continuation, so the value channels are paths.
  for(U b:left_vertices)if(U r=match_left[b]){
    U c=r/2,side=r%2,a=side?parents[c].second:parents[c].first;
    if(match_right[r]!=b||(parents[b].first!=a&&parents[b].second!=a)||size[b]>=size[c])
      throw std::runtime_error("Invalid matched channel");
  }
  uint64_t candidates=right.size(),mixed_links=0;
  for(U b:left_vertices)if(match_left[b]&&!source[match_left[b]/2])mixed_links++;
  std::vector<U>().swap(offset);std::vector<U>().swap(right);std::vector<U>().swap(distance);std::vector<U>().swap(left_vertices);
  // Materialize the entire physical register schedule, independently of the
  // R=oldR-matched accounting identity. Last-frame witnesses are either an
  // original producer edge or the selected nested-frame continuation.
  std::vector<U>use_offset(n+1),use_cursor;
  for(U i=v+1;i<n;i++)if(active[i])for(U a:{parents[i].first,parents[i].second})use_offset[a+1]++;
  for(U a:roots)use_offset[a+1]++;
  for(U i=1;i<=n;i++)use_offset[i]+=use_offset[i-1];
  use_cursor=use_offset;std::vector<U>uses(use_offset[n]);
  for(U i=v+1;i<n;i++)if(active[i]){
    uses[use_cursor[parents[i].first]++]=2*i;
    uses[use_cursor[parents[i].second]++]=2*i+1;
  }
  for(U j=0;j<q;j++)uses[use_cursor[roots[j]]++]=2*n+j;
  std::vector<U>().swap(use_cursor);
  std::vector<U>order;order.reserve(source_gates+v);
  for(U i=1;i<n;i++)if(active[i]&&source[i])order.push_back(i);
  std::sort(order.begin(),order.end(),[&](U a,U b){return size[a]==size[b]?a<b:size[a]<size[b];});
  for(U i=1;i<n;i++)if(active[i]&&!source[i])order.push_back(i);
  std::vector<U>delivery(2*size_t(n),INF),output_slots(q,INF),last_frame;
  last_frame.reserve(additions+q);uint64_t normal_visits=0,reused_visits=0,producer_incidences=0;
  auto continuation=[&](U d)->U{
    U b=d/2,r=match_left[b];if(!r)return 0;
    U a=(r&1)?parents[r/2].second:parents[r/2].first;
    return ((d&1)?parents[b].second:parents[b].first)==a?r:0;
  };
  for(U at:order){
    U base=INF;
    if(at<=v){base=last_frame.size();last_frame.push_back(at);producer_incidences++;}
    else{
      U ins[2]={delivery[2*at],delivery[2*at+1]};
      if(ins[0]==INF||ins[1]==INF||ins[0]==ins[1])throw std::runtime_error("Missing or aliased producer inputs");
      for(U side=0;side<2;side++){
        U slot=ins[side],previous=last_frame[slot],a=side?parents[at].second:parents[at].first;
        if(previous==a)normal_visits++;
        else if(match_left[previous]==2*at+side&&source[previous])reused_visits++;
        else throw std::runtime_error("Uncertified physical frame transition");
        last_frame[slot]=at;
        if(base==INF&&!continuation(2*at+side))base=slot;
      }
      if(base==INF)throw std::runtime_error("Neither input can be overwritten");
      producer_incidences+=2;
    }
    U channels=0;
    for(U j=use_offset[at];j<use_offset[at+1];j++){
      U d=uses[j];if(d<2*n&&match_right[d])continue;
      U slot=base;if(channels++){slot=last_frame.size();last_frame.push_back(at);producer_incidences++;}
      if(d>=2*n){output_slots[d-2*n]=slot;continue;}
      while(true){
        if(delivery[d]!=INF)throw std::runtime_error("Duplicate physical delivery assignment");
        delivery[d]=slot;U next=continuation(d);if(!next)break;d=next;
      }
    }
    if(!channels)throw std::runtime_error("Value has no initial channel");
  }
  for(U j=0;j<q;j++)if(output_slots[j]==INF||last_frame[output_slots[j]]!=roots[j])
    throw std::runtime_error("A protected designated output was reused");
  if(last_frame.size()!=additions+q-matched||reused_visits!=matched)
    throw std::runtime_error("Physical allocation disagrees with matching count");
  std::ofstream out(argv[4],std::ios::binary);for(U x:{h,v,n,q,matched})out.write(reinterpret_cast<char*>(&x),4);
  out.write(reinterpret_cast<char*>(match_left.data()),4*W(n));
  uint64_t roles=additions+q;
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  uint64_t center_loss=W(h)*(h-1)/2*(h-2),rank_sum=(2*W(v)+last_frame.size())*h-2*W(v)+2*center_loss;
  std::cout<<"{\"status\":\"EXACT NESTED DELIVERY MATCHING AND FULL PHYSICAL ROLE SCHEDULE\",\"h\":"<<h
    <<",\"inputs\":"<<v<<",\"source_gates\":"<<source_gates<<",\"ancestor_depth\":"<<depth
    <<",\"ancestor_probes\":"<<probes<<",\"candidate_links\":"<<candidates<<",\"matched_links\":"<<matched
    <<",\"matching_phases\":"<<phases<<",\"original_roles\":"<<roles<<",\"new_roles\":"<<roles-matched
    <<",\"source_to_dual_enabled\":"<<(mixed?"true":"false")<<",\"source_to_dual_links\":"<<mixed_links
    <<",\"physical_roles_allocated\":"<<last_frame.size()<<",\"ordinary_frame_transitions\":"<<normal_visits
    <<",\"reused_frame_transitions\":"<<reused_visits<<",\"producer_wire_incidences\":"<<producer_incidences
    <<",\"every_physical_producer_transition_certified\":true,\"every_designated_output_protected\":true"
    <<",\"center_loss\":"<<center_loss<<",\"physical_rank_sum_each_orientation\":"<<rank_sum
    <<",\"extra_frame_loss\":0,\"seconds\":"<<seconds<<"}\n";
}
