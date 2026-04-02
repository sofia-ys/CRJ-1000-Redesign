#gemini generated scissor plot, fixed by claude :)

import numpy as np
import matplotlib.pyplot as plt
import math as m
import controllability_coeffs

# ==========================================
# INPUT VARIABLES (Replace with your data)
# ==========================================


# General Parameters
mac = 4.11  # MAC
l_h = 16.06566495  # distance from tail AC to Wing AC
lh_c = l_h/mac         # Tail moment arm normalized by MAC
Vh_V = 1        # Tail speed ratio (Vh / V)
V_app = 72.022  # approach speed [m/s]
MTOW    = 38995 # [kg]   maximum take-off weight (conservative for approach sizing)
rho_app = 1.225   # [kg/m³] ISA sea-level density at approach altitude
g       = 9.80665   # [m/s²]
S = 77.39 # total wing area [m^2]
b = controllability_coeffs.b

# Stability Parameters (Cruise Condition)
SM     = 0.05          # Required stability margin (fraction of MAC, e.g. 5%)
CL_ah  = 4.6793850598197535           # Lift curve slope of the horizontal tail (1/rad)
CL_aAh = 6.423476455793314           # Lift curve slope of the aircraft-less-tail (1/rad)
 
# Controllability Parameters (Approach/landing — flaps fully extended)
CL_Ah = (2 * MTOW * g) / (rho_app * V_app**2 * S) *1.2 # Lift coefficient of aircraft-less-tail at minimum approach speed
CL_h   = -0.8          # Maximum (negative) lift coefficient the tail can generate
                        # (negative because the tail pushes down to counteract nose-down Cmac)
#cm_.25/Deltaf_Clmax = 0.385  #The moment coeff. around the quarter chord over Clmax and the flap deflection. For double-slotted flap it's around 0.385
quarter_chord_sweep = controllability_coeffs.Lambda_quarterC
halfchordsweep = controllability_coeffs.Lambda_halfC
taper_ratio = controllability_coeffs.taper
A_wing = b**2/S *1.25
b_f = controllability_coeffs.b_f
S_net = S - 14.90 #rough estimate

#nacelle stuff
b_n = 1.56 * 1.2 #1.56 from the aiport manual, not 1.7 (???)
l_n = -10.88 * 1.1
l_fn = 17.09
h_f = 2.695 #estimate for fuselage height

# Operational CG range (from your loading diagram, fraction of MAC)
cg_fwd = 0.22365          # Most forward operational CG
cg_aft = 0.60689          # Most aft operational CG

C_L0 = 0.15


def calculate_x_nacelle(k_n, CL_a_Ah):
    return 2*k_n*b_n**2*l_n/(S*mac*CL_a_Ah)

def calculate_x_fus_control(C_L0, CL_a_Ah):
    return -1.8 * (1 - 2.5 * b_f / l_f) * m.pi * b_f * h_f * l_f / (4 * S * mac) * C_L0 / CL_a_Ah

def calculate_x_fus_stab(CL_a_Ah):
    #l_fn is the distance between fuselage and nacelle
    x_1 = -1.8/CL_a_Ah * b_f*h_f*l_fn/(S*mac)
    x_2 = 0.273/(1 + taper_ratio) * b_f * S/b * (b - b_f)/(mac**2*(b - 2.15*b_f)) * m.tan(quarter_chord_sweep)
    return x_1 + x_2


def calculate_CL_a(A, HalfChordSweep, MachNum):
    #MAKE SURE HALFCHORD IS IN RADIANS!!!
    Beta = m.sqrt(1 - MachNum**2)
    eta_h = 0.95
    return 2*m.pi*A/(2 + m.sqrt(4 + (A*Beta/eta_h)**2 * (1 + m.tan(HalfChordSweep)**2)/Beta**2))

def calculate_CL_a_Ah(CL_a_w, b_f, S_net, b, S):
    return CL_a_w * (1 + 2.15*b_f/b) * S_net/S + m.pi/2 * b_f**2/S


# ==========================================
# SCISSOR PLOT CALCULATIONS
# ==========================================
x_cg_range = np.linspace(0.0, 1, 200)
 
# ------------------------------------------------------------------
# 1. STABILITY CURVE  (cruise, flaps retracted, most-aft CG limit)
#
#    Sh/S = (xcg - xac + SM) / [ (CLah/CLaAh) * (1 - dε/dα) * (lh/c̄) * (Vh/V)² ]
#
#    Uses x_ac at CRUISE speed.
# ------------------------------------------------------------------

def calculate_de_da(A, l_h, b):
    r = 2 * l_h / b
    m_tv = 2 * 5.026099606 / b
    K_eps_lambda = (0.1124 + 0.1265*quarter_chord_sweep + 0.1766*quarter_chord_sweep**2)/(r**2) + 0.1024/r + 2
    K_eps_0 = 0.1124/(r**2) + 0.1024/r + 2
    CL_a_w = calculate_CL_a(A, halfchordsweep, mach_num_cruise)
    return (K_eps_lambda/K_eps_0) * (
        (0.4876 * r) / ((r**2 + m_tv**2) * m.sqrt(r**2 + 0.6319 + m_tv**2)) +
        (1 + (r**2 / (r**2 + 0.7915 + 5.0734*m_tv**2))**0.3113) *
        (1 - m.sqrt(m_tv**2/(1 + m_tv**2)))
    ) * CL_a_w / (m.pi * A)

mach_num_cruise = 0.82
de_da = calculate_de_da(A_wing, l_h, b)

CL_a_w_cruise = calculate_CL_a(A_wing, quarter_chord_sweep, mach_num_cruise)
CL_a_Ah_cruise = calculate_CL_a_Ah(CL_a_w_cruise, b_f, S_net, b, S)
x_nacelle_cruise = calculate_x_nacelle(-2.5, CL_a_Ah_cruise)
x_fus_cruise = calculate_x_fus_stab(CL_a_Ah_cruise)

#torenbeek bigass formula 0.43 due to effective aspect ratio change 
x_ac_cruise = 0.43 + x_fus_cruise + x_nacelle_cruise

#Cm_nacelle = calculate_cm_nacelle(-2.5, b_n, l_n, S, mac, CL_a_Ah_cruise) #CHANGE THIS LATERRRRRRRRR!!!!!!!!!!!!
K_stab = (CL_ah / CL_a_Ah_cruise) * (1 - de_da) * lh_c * (Vh_V ** 2)  # used a hardcoded value, changed it to CL_a_Ah_cruise
Sh_S_stability = np.clip((x_cg_range - x_ac_cruise + SM) / K_stab,0.0, None)



# ------------------------------------------------------------------
# 2. CONTROLLABILITY CURVE  (approach, flaps extended, most-fwd CG limit)
#
#    Sh/S = (Cmac + CL_Ah * (xcg - xac)) / [ CL_h * (lh/c̄) * (Vh/V)² ]
#
#    Uses x_ac at APPROACH speed (most aft, i.e. most critical for control).
#    K_cont is negative (CL_h < 0), which correctly inverts the sign so that
#    the curve slopes downward — a larger (less negative) tail lift requirement
#    as CG moves aft.
#    Clip at 0: negative Sh/S is physically meaningless.
# ------------------------------------------------------------------

###NEEDED:


#Estimation for cm_.25 number 1
#cm_ac/Clmax = cm_.25/Deltaf_Clmax*(1 - (1.5*cos(quarter_chord_sweep)/Clmax) #Assuming there are no slats in the wing

#Estimation of cm_.25 number 2

takeoff_angle = 9 #Degrees
takeoff_angle = takeoff_angle * m.pi/180
flap_deflection = 45 #Flap deflection in degrees
flap_deflection = flap_deflection * m.pi/180

###WING
mystery_sweep = quarter_chord_sweep
C_m0_airfoil = controllability_coeffs.Cm0_airfoil
Cm_ac_w = C_m0_airfoil * (A_wing * m.cos(mystery_sweep)**2/(A_wing + 2*m.cos(mystery_sweep)))




###FUSELAGE



CL_a_w_lowspeed = calculate_CL_a(A_wing, halfchordsweep, 72.022/343)
CL_a_Ah_lowspeed = calculate_CL_a_Ah(CL_a_w_lowspeed, b_f, S_net, b, S)

# Calculate fuselage and nacelle shifts using low-speed aerodynamics
x_nacelle_approach = calculate_x_nacelle(-2.5, CL_a_Ah_lowspeed)
x_fus_approach = calculate_x_fus_stab(CL_a_Ah_lowspeed)

# Calculate total x_ac for approach using 0.4 from torenbeek bigass formula
x_ac_approach = 0.4 + x_fus_approach + x_nacelle_approach

l_f = controllability_coeffs.l_fn #fuselage length
Cm_fus = -1.8*(1 - 2.5*b_f/l_f) * m.pi*b_f*h_f*l_f/(4*S*mac) * C_L0 / CL_a_Ah_lowspeed



###FLAPS

# validate
cdash_mac = 1.35 #The total span of the wings with flaps/the airfoil MAC

#these mu values def are wrong
mu_1 = 0.157 #Assuming 45 degree flap angles 
mu_2 = 0.4
mu_3 = 0.0

#yes revise this
deltaClmax = 1.3 #REVISE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #How much Cl the flaps add
C_L_w_lowspeed = C_L0 + takeoff_angle * CL_a_Ah_lowspeed

#should be a bit higher
Swf_S = 0.45#ratio between flapped wing area and ref wing area

b1 = C_L_w_lowspeed + deltaClmax*(1 - Swf_S)   #Bracket 1 of the eq
b2 = -mu_1*deltaClmax*cdash_mac - b1*1/8*cdash_mac*(cdash_mac - 1)


Cm_flaps = mu_2 * b2 + 0.7*A_wing/(1 + 2/A_wing)*mu_3*deltaClmax*m.tan(quarter_chord_sweep)
Cm_c4_total = Cm_ac_w + Cm_fus + Cm_flaps
Cm_ac_total = Cm_c4_total - CL_Ah * (x_ac_approach - 0.25)

K_cont = CL_h * lh_c * (Vh_V ** 2)          # negative, because CL_h < 0
Sh_S_controllability_raw = (Cm_ac_total + CL_Ah * (x_cg_range - x_ac_approach)) / K_cont
Sh_S_controllability = np.clip(Sh_S_controllability_raw, 0.0, None)

# ------------------------------------------------------------------
# 3. REQUIRED Sh/S FOR THE GIVEN CG RANGE
#    - Stability is critical at the MOST AFT CG position.
#    - Controllability is critical at the MOST FORWARD CG position.
# ------------------------------------------------------------------
idx_aft = np.abs(x_cg_range - cg_aft).argmin()
idx_fwd = np.abs(x_cg_range - cg_fwd).argmin()
 
min_Sh_S_stab = Sh_S_stability[idx_aft]
min_Sh_S_cont = Sh_S_controllability[idx_fwd]
required_Sh_S = max(min_Sh_S_stab, min_Sh_S_cont)
driver = "Controllability" if min_Sh_S_cont >= min_Sh_S_stab else "Stability"
 
print("\n" + "="*60)
print("FULL PARAMETER SUMMARY FOR LATEX REPORT")
print("="*60)

print("\n--- Wing AC base values (from Fig E-10 interpolation) ---")
print(f"Cruise:   beta*A = {m.sqrt(1-mach_num_cruise**2) * A_wing:.3f}, wing AC base = 0.384")
print(f"Approach: beta*A = {72.022/343 * A_wing:.3f}, wing AC base = 0.340")

print("\n--- Fuselage contributions to x_ac ---")
x_fus_1_cruise = -1.8/CL_a_Ah_cruise * b_f*h_f*l_fn/(S*mac)
x_fus_2_cruise = 0.273/(1 + taper_ratio) * b_f * S/b * (b - b_f)/(mac**2*(b - 2.15*b_f)) * m.tan(quarter_chord_sweep)
x_fus_1_app = -1.8/CL_a_Ah_lowspeed * b_f*h_f*l_fn/(S*mac)
x_fus_2_app = 0.273/(1 + taper_ratio) * b_f * S/b * (b - b_f)/(mac**2*(b - 2.15*b_f)) * m.tan(quarter_chord_sweep)
print(f"Cruise:   f1 = {x_fus_1_cruise:.4f}, f2 = {x_fus_2_cruise:.4f}, total = {x_fus_cruise:.4f}")
print(f"Approach: f1 = {x_fus_1_app:.4f}, f2 = {x_fus_2_app:.4f}, total = {x_fus_approach:.4f}")

print("\n--- Nacelle contributions to x_ac ---")
print(f"Cruise:   {x_nacelle_cruise:.4f}  (positive = stabilizing = correct for rear engines)")
print(f"Approach: {x_nacelle_approach:.4f}")
print(f"l_n = {l_n} (negative = nacelle exit aft of wing quarter-chord)")
print(f"k_n = -2.5, b_n = {b_n}")

print("\n--- Total x_ac ---")
print(f"Cruise:   {x_ac_cruise:.4f}  (wing 0.430 + fus {x_fus_cruise:.4f} + nac {x_nacelle_cruise:.4f})")
print(f"Approach: {x_ac_approach:.4f}  (wing 0.400 + fus {x_fus_approach:.4f} + nac {x_nacelle_approach:.4f})")
print("\n--- Lift rate coefficients ---")
print(f"CL_ah (cruise):       {CL_ah:.4f} rad^-1")
print(f"CL_a_Ah (cruise):     {CL_a_Ah_cruise:.4f} rad^-1")
print(f"  wing contribution:  {CL_a_w_cruise:.4f} rad^-1")
print(f"  fus correction:     {CL_a_Ah_cruise - CL_a_w_cruise:.4f} rad^-1")
print(f"CL_a_Ah (approach):   {CL_a_Ah_lowspeed:.4f} rad^-1")
print(f"  wing contribution:  {CL_a_w_lowspeed:.4f} rad^-1")
print(f"  fus correction:     {CL_a_Ah_lowspeed - CL_a_w_lowspeed:.4f} rad^-1")

print("\n--- Downwash gradient ---")
print(f"de/da (cruise): {de_da:.4f}")

print("\n--- Stability curve parameters ---")
print(f"SM: {SM}")
print(f"Vh/V: {Vh_V}")
print(f"lh/c: {lh_c:.4f}")
print(f"K_stab: {K_stab:.4f}")

print("\n--- Controllability parameters ---")
print(f"V_app: {V_app} m/s")
print(f"CL_Ah: {CL_Ah:.4f}")
print(f"CL_h:  {CL_h}")
print(f"K_cont: {CL_h * lh_c * Vh_V**2:.4f}")

print("\n--- Cm_ac contributions ---")
print(f"Clean wing Cm_ac_w:     {Cm_ac_w:.4f}")
print(f"Fuselage Cm_fus:        {Cm_fus:.4f}")
print(f"Flaps Cm_flaps (c/4):   {Cm_flaps:.4f}")
print(f"Conversion to AC:       {-(CL_Ah * (x_ac_approach - 0.25)):.4f}  = -CL_Ah*(x_ac-0.25)")
print(f"Total Cm_ac:            {Cm_ac_total:.4f}")

print("\n--- CG range ---")
print(f"Most forward CG: {cg_fwd:.5f} (fraction of MAC)")
print(f"Most aft CG:     {cg_aft:.5f} (fraction of MAC)")

print("\n--- Required tail size ---")
print(f"Sh/S from stability at cg_aft:      {min_Sh_S_stab:.4f}")
print(f"Sh/S from controllability at cg_fwd: {min_Sh_S_cont:.4f}")
print(f"Required Sh/S (max of above):        {required_Sh_S:.4f}")
print(f"Driven by: {driver}")
print(f"Actual CRJ-1000 Sh/S: {15.91/77.39:.4f}  (Sh=15.91 m², S=77.39 m²)")
print("="*60)

# ==========================================
# PLOTTING
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6))
 
# --- Curves ---
ax.plot(x_cg_range, Sh_S_stability,
        'b-', linewidth=2, label='Stability limit (most aft CG)')
ax.plot(x_cg_range, Sh_S_controllability,
        'r-', linewidth=2, label='Controllability limit (most fwd CG)')
 
# --- FIX 3: Feasible region = BETWEEN the two curves (the "scissors opening") ---
#     For a chosen Sh/S, the admissible CG window lies where:
#       controllability curve  ≤  Sh/S  ≤  stability curve  (i.e. stab ≥ cont)
ax.fill_between(x_cg_range,
                np.maximum(Sh_S_stability, Sh_S_controllability),
                1.0, # Arbitrary upper boundary for shading
                color='green', alpha=0.15,
                label='Feasible design space')
 
# --- Operational CG range overlay ---
ax.axvspan(cg_fwd, cg_aft,
           color='gray', alpha=0.25, label='Operational CG range')
 
# --- Required Sh/S line ---
ax.axhline(required_Sh_S, color='k', linestyle='--',
           label=f'Min required $S_h/S$ = {required_Sh_S:.3f} (driven by {driver})')
 
# --- Formatting ---
ax.set_title('Aircraft Scissor Plot: Tail Sizing & CG Range')
ax.set_xlabel(r'Center of gravity position  ($\bar{x}_{cg}$ / MAC)')
 
# FIX 1: Sh/S is a tail AREA ratio, not a volume ratio
ax.set_ylabel(r'Horizontal tail area ratio  ($S_h / S$)')
 
ax.set_xlim([0.0, 1])
ax.set_ylim([0.0, max(Sh_S_controllability[0], Sh_S_stability[-1]) * 1.2])
ax.grid(True, linestyle=':', alpha=0.7)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()
