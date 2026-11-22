"""Check the complete connected activation of a streamed raw-transport installation."""

from fractions import Fraction


def ceil_log2(n):
    return (n-1).bit_length()


def binary_entries(rank_logs):
    cuts = []
    for h in rank_logs:
        minimum = (250*(h+64)+248)//249
        cuts.append(max(minimum,h+64+cuts[-1] if cuts else 0))
    return cuts


def full_entrance(last_cut, numerical):
    target = last_cut + numerical + 102
    s = max(512,target)
    while s - 7*ceil_log2(s) < target:
        s = target + 7*ceil_log2(s)
    log = ceil_log2(s)
    after = 7*(log+1) + target
    if (1<<log)+1 < after:
        s=after
    assert s-7*ceil_log2(s)>=target
    assert (1<<ceil_log2(s))+1-7*(ceil_log2(s)+1)>=target
    return s-1


def resource_receipt(profile):
    ranks=tuple(profile.rank_logs)
    num=profile.complex_log
    m=len(ranks)
    assert 1<=m<=6
    cuts=binary_entries(ranks)
    A=full_entrance(cuts[-1],num)
    s=A+1
    assert s>=8192
    for h in (num,*ranks):
        assert h>=3000
        assert 66+83*h<92*h
        assert 92*h<105*h and 92*h<448*h
        assert (700*h).bit_length()<=h and (872*(4*h+1)).bit_length()<=h
        assert (30*1024*h+120).bit_length()<=h-1
    for i,h in enumerate(ranks):
        assert 28_726_102+80*h<1024*h
        assert not i or cuts[i-1]+2<h
    assert s-100-7*ceil_log2(s)>=num+cuts[-1]+2
    assert profile.eta<Fraction(1,250)
    # Even the older structural allowance suffices as an upper bound on
    # all input-dependent control. The permanently retained raw data are smaller.
    job_log=1024*max(num,*ranks)+(m+1).bit_length()
    table_log=(1<<21)*(s+1)
    assert 64+8*(job_log+1)+64*s+8*(table_log+1)<(s+1)**8
    assert (12*(128*(s+130)*(s+1)**8+64)).bit_length()<=s-2
    assert (1200*(64*(128*s*s+s)+2*s+128)).bit_length()<=s-2
    assert (2000*(34*s+108)).bit_length()<=s-2
    assert 33**9<2*32**9
    # The local coefficient is independent of the astronomical raw width B.
    # The nonnative prefix has at most 32 levels, each with at most 2^64.
    q=2048
    local=2*q+4096+4*(m+1)+128
    per_head=local+4*(s+128).bit_length()
    slack=s//2-2-per_head
    tail=7*s//16-3-local
    assert 16*(local+1028)<=7*s and slack>1024 and tail>1024
    delta=(-pow(2,A,6))%6
    assert delta in (2,4)
    return {"binary_cuts":cuts,"public_exponent_A":A,"first_public_offset":delta,
            "initial_s":s,"stage_and_outer_fixed_log_overhead":local,
            "retimed_first_stripe_margin":slack,"retimed_all_size_margin_floor":tail,
            "absolute_log2_private_control_envelope":job_log,
            "storage_upper":"6.2 p T < 297.6 n bits"}
