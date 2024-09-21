### LaKey2 Threshold PRF
#
# Set enviroment variables.
#   PRIME=57896044618658097711785492504343953926634992332820282019728792003956566065153
#   PROG=lakey2
#
# Compile and run.
#   ./MP-SPDZ/Scripts/compile-run.py -O -E mal-shamir -P $PRIME $PROG
#
# Compile and run with separate preprecossing.
#   PROG=$PROG PRIME=$PRIME ./Scripts/compile-run-pre.sh
# 
# Adjust parameters.
#   PROG=lakey2 LOG2Q=12 LOG2P=8 ./Scripts/compile-run-pre.sh
#   PROG=lakey2 LOG2Q=32 LOG2P=24 ./Scripts/compile-run-pre.sh
#   PROG=lakey2 LOG2Q=64 LOG2P=56 ./Scripts/compile-run-pre.sh
#
# Measure communication more precisely.
#   ./MP-SPDZ/Scripts/compile-run.py -O -E mal-shamir -P $PRIME $PROG -- --batch-size 100

import math, os
from random import randint

from Compiler.types import *
from Compiler.library import if_, print_ln, for_range_parallel
from Compiler.comparison import PRandM, BitLTL as BitLT

def parse_bool(s: str) -> bool:
    return bool(int(s))

KEYGEN = parse_bool(os.environ.get("KEYGEN", False)) # Run key generation.
REVEAL = parse_bool(os.environ.get("REVEAL", False)) # Reval output.
LOG2Q = int(os.environ.get("LOG2Q", 12)) # Lattice modulus bitlength.
LOG2P = int(os.environ.get("LOG2P", 8)) # Rounding modulus bitlength.
DIM = int(os.environ.get("DIM", 512)) # Lattice dimension.
DOUBLE = parse_bool(os.environ.get("DOUBLE", False)) # Run evaluation twice.
CHECK = parse_bool(os.environ.get("CHECK", False)) # Check result against cleartext computation.
OUTPUT = parse_bool(os.environ.get("OUTPUT", False)) # Write result to file.

log2q = LOG2Q # Lattice modulus.
log2p = LOG2P # Rounding modulus.
m = DIM # Lattice dimension
int_size = ((2**log2q - 1)**2 * m).bit_length() # Maximum integer size.
kappa = program.security # Statistical security level.

def stat_dist(m: int, n: int):
    """Computes the statistical distance between U(Z_m) mod n and U(Z_n)."""
    r = m % n
    return math.log2(r * n - r**2) - math.log2(m * n)

def derive_l():
    base_prime = program.prime
    # Attempt to use tight `l` and check whether the statistical distance
    # between the generated range and the target raneg is sufficiently small.
    l = round(math.log(base_prime, 2**log2p))
    d = stat_dist(2**(l*log2p), base_prime)
    if d > -kappa:
        # If statistical distance with tight `l` is not sufficient, widen range
        # to ensure negligible statistical distance.
        return math.ceil(math.log(program.prime + 2**kappa, 2**log2p))
    return l

l = derive_l() # Number of p-bit elements required to fill up the target range.

if DOUBLE:
    l *= 2

print(f"q=2^{log2q}, p=2^{log2p}, m={m}, l={l}")
print(f"KEYGEN={KEYGEN}, REVEAL={REVEAL}, DOUBLE={DOUBLE}, CHECK={CHECK}, OUTPUT={OUTPUT}")

def crand():
    r = randint(0, 2**log2q-1)
    return cint(r)

def srand():
    return sint.get_random_int(log2q)

def trunc(a: sint, k: int, m1: int, m2: int) -> sint:
    """
    Truncate the top and bottom bits of the `k`-bit integer `a`. Returns the
    integer corresponding to the bits in the range `[m1:m2]`.
    """
    r_dprime, r_prime, r = sint(), sint(), [sint() for i in range(m2)]
    PRandM(r_dprime, r_prime, r, k, m2, kappa)
    c = (two_power(k-1) + a + two_power(m2) * r_dprime + r_prime).reveal()
    m_list = [m1, m2]
    a_list = [sint(), sint()]
    @for_range_parallel(2, 2)
    def _(i):
        m = m_list[i]
        c_prime = c % two_power(m)
        r_bits = r[:m]
        u = sint()
        BitLT(u, c_prime, r_bits, kappa)
        a_list[i] = c_prime - sint.bit_compose(r_bits) + two_power(m) * u
    return (a_list[1] - a_list[0]).field_div(two_power(m1))

def compose(a: Array) -> sint:
    l = len(a)
    log2_p1 = log2q - log2p
    log2_p2 = 2 * log2p - log2q
    def shift(i):
        p1_shift = (i - 1) * log2_p1
        p2_shift = i * log2_p2
        return max(0, p1_shift + p2_shift)
    return sum(a[i] << shift(i) for i in range(l))

def key_gen(m: int):
    a = Matrix(l, m, cint)
    for i in range(l):
        for j in range(m):
            a[i][j] = crand()
            
    k = Array(m, sint)
    for i in range(m):
        k[i] = srand() if KEYGEN else sint(crand())
    
    return a, k

def eval(a: Matrix, k: Array):
    r = a * k
    
    # Modulo q and round p.
    for i in range(l):
        r[i] = trunc(r[i], int_size, log2q-log2p, log2q)
    
    if DOUBLE:
        l_half = l//2
        
        # Compose.
        r = [
            compose(r[:l_half]),
            compose(r[l_half:]),
        ]
    else:        
        # Compose.
        r = compose(r)
    
    return r

def eval_clear(a: Matrix, k: Array):
    k: Array = k.reveal()
    
    r = a * k
    
    def trunc(a: cint, k: int, m1: int, m2: int):
        a_bits = a.bit_decompose()
        return cint.bit_compose(a_bits[m1:m2])
    
    # Modulo q and round p.
    for i in range(l):
        r[i] = trunc(r[i], int_size, log2q-log2p, log2q)
    
    if DOUBLE:
        l_half = l//2
        
        # Compose.
        r = [
            compose(r[:l_half]),
            compose(r[l_half:]),
        ]
    else:        
        # Compose.
        r = compose(r)
    
    return r

def main():    
    a, k = key_gen(m)
    r = eval(a, k)
    if OUTPUT:
        sint.write_to_file(r)
    if REVEAL:
        print_ln("output = %s", r.reveal())
    if CHECK:
        r_clear = eval_clear(a, k)
        r_revealed = r.reveal()
        @if_(r_clear != r_revealed)
        def _():
            print_ln("r_clear    = %s", r_clear)
            print_ln("r_revealed = %s", r_revealed)
            print_ln("check failed")

main()
