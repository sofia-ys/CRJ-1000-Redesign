import math as m

r = 1.2278
mtv = 0.3841
Lambda = 33.76 * m.pi/180  # radians
A_orig = 8.8496
A_new  = 11.062
CL_a_w_orig = 4.1551
CL_a_w_new  = 4.3042

K_lam = (0.1124 + 0.1265*Lambda + 0.1766*Lambda**2)/(r**2) + 0.1024/r + 2
K_0   = 0.1124/(r**2) + 0.1024/r + 2

term1 = (0.4876 * r) / ((r**2 + mtv**2) * m.sqrt(r**2 + 0.6319 + mtv**2))
term2 = (1 + (r**2/(r**2 + 0.7915 + 5.0734*mtv**2))**0.3113) * (1 - m.sqrt(mtv**2/(1+mtv**2)))

bracket = term1 + term2

de_da_orig = (K_lam/K_0) * bracket * CL_a_w_orig / (m.pi * A_orig)
de_da_new  = (K_lam/K_0) * bracket * CL_a_w_new  / (m.pi * A_new)

print(f"K_lam={K_lam:.4f}, K_0={K_0:.4f}, ratio={K_lam/K_0:.4f}")
print(f"term1={term1:.4f}")
print(f"term2={term2:.4f}")
print(f"bracket={bracket:.4f}")
print(f"de_da Part 1: {de_da_orig:.4f}")
print(f"de_da Part 2: {de_da_new:.4f}")