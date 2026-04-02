#gemini generated scissor plot, fixed by claude :)

import numpy as np
import matplotlib.pyplot as plt
import math as m
from controllability_coeffs import *

# ==========================================
# INPUT VARIABLES (Replace with your data)
# ==========================================


# General Parameters
mac = 4.11  # MAC
l_h = 16.40  # distance from tail AC to Wing AC, value changed, from technical drawing
lh_c = l_h/mac         # Tail moment arm normalized by MAC
Vh_V = 1        # Tail speed ratio (Vh / V)
V_app = 72.022  # approach speed [m/s]
MTOW    = 38995 # [kg]   maximum take-off weight (conservative for approach sizing)
rho_app = 1.225   # [kg/m³] ISA sea-level density at approach altitude
g       = 9.80665   # [m/s²]
S = 77.39 # total wing area [m^2]

# Stability Parameters (Cruise Condition)
SM     = 0.05          # Required stability margin (fraction of MAC, e.g. 5%)
CL_ah  = lift_rate_coef(A_h, beta_app, eta_h, Lambda_halfC_h)           # Lift curve slope of the horizontal tail (1/rad)
CL_aAh, _ = lift_rate_aircraft_less_tail(beta_cr)           # Lift curve slope of the aircraft-less-tail (1/rad)
de_da  = downwash(beta_cr)          # Downwash gradient (dε/dα)
 
# Controllability Parameters (Approach/landing — flaps fully extended)
CL_Ah = (2 * MTOW * g) / (rho_app * V_app**2 * S) # Lift coefficient of aircraft-less-tail at minimum approach speed
CL_h   = -0.8          # Maximum (negative) lift coefficient the tail can generate
                        # (negative because the tail pushes down to counteract nose-down Cmac)
#cm_.25/Deltaf_Clmax = 0.385  #The moment coeff. around the quarter chord over Clmax and the flap deflection. For double-slotted flap it's around 0.385
quarter_chord_sweep = Lambda_quarterC
halfchordsweep = Lambda_halfC
taper_ratio = taper
A_wing = b**2/S
b_f = b_f
S_net = S - 14.90 #rough estimate

#nacelle stuff
b_n = 1.56 #1.56 from the aiport manual, not 1.7 (???)
l_n = -10.88
l_fn = 17.09
h_f = 2.695 #estimate for fuselage height

'''TODO: verify these values, not hardcoded'''
# Operational CG range (from your loading diagram, fraction of MAC)
cg_fwd = 0.13419          # Most forward operational CG
cg_aft = 0.52525          # Most aft operational CG

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

mach_num_cruise = 0.82

'''TODO: where does -2.5 come from'''
CL_a_w_cruise = calculate_CL_a(A_wing, quarter_chord_sweep, mach_num_cruise)
CL_a_Ah_cruise = calculate_CL_a_Ah(CL_a_w_cruise, b_f, S_net, b, S)
x_nacelle_cruise = calculate_x_nacelle(-2.5, CL_a_Ah_cruise)
x_fus_cruise = calculate_x_fus_stab(CL_a_Ah_cruise)
x_ac_cruise = 0.36 + x_fus_cruise + x_nacelle_cruise

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
C_m0_airfoil = Cm0_airfoil
Cm_ac_w = C_m0_airfoil * (A_wing * m.cos(mystery_sweep)**2/(A_wing + 2*m.cos(mystery_sweep)))




###FUSELAGE



CL_a_w_lowspeed = calculate_CL_a(A_wing, halfchordsweep, 72.022/343)
CL_a_Ah_lowspeed = calculate_CL_a_Ah(CL_a_w_lowspeed, b_f, S_net, b, S)

# Calculate fuselage and nacelle shifts using low-speed aerodynamics
x_nacelle_approach = calculate_x_nacelle(-2.5, CL_a_Ah_lowspeed)
x_fus_approach = calculate_x_fus_stab(CL_a_Ah_lowspeed)

# Calculate total x_ac for approach using the 0.325 wing contribution, corrected value
x_ac_approach = 0.325 + x_fus_approach + x_nacelle_approach

l_f = l_fn #fuselage length
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
print("TABLE VALUES FOR ASSIGNMENT DELIVERABLE 3.3e)")
print("="*60)

print("\n--- Velocity Parameters ---")
print(f"V_C (cruise):     230      m/s  (from Janes/specs)")
print(f"V_app (approach): {V_app:.2f}  m/s")
print(f"Vh/V:             {Vh_V:.4f}   [-]")
print(f"de/da:            {de_da:.4f}   [-]")

print("\n--- Lift Rate Coefficients (at cruise) ---")
print(f"CL_ah (tail):              {CL_ah:.4f}  rad^-1")
print(f"CL_a_Ah (aircraft-less-tail): {CL_a_Ah_cruise:.4f}  rad^-1")
print(f"  Wing CL_a_w:             {CL_a_w_cruise:.4f}  rad^-1")
print(f"  Fuselage correction:     {CL_a_Ah_cruise - CL_a_w_cruise:.4f}  rad^-1")

print("\n--- Aerodynamic Centre at Cruise ---")
print(f"Total x_ac_Ah:    {x_ac_cruise:.4f}  [-]")
print(f"  Wing:           {x_ac_cruise - x_fus_cruise - x_nacelle_cruise:.4f}  [-]  (base from Fig E-10)")
print(f"  Fuselage f1:    {x_fus_1_cruise:.4f}  [-]")
print(f"  Fuselage f2:    {x_fus_2_cruise:.4f}  [-]")
print(f"  Fuselage total: {x_fus_cruise:.4f}  [-]")
print(f"  Nacelle:        {x_nacelle_cruise:.4f}  [-]")

print("\n--- Aerodynamic Centre at Approach ---")
print(f"Total x_ac_Ah:    {x_ac_approach:.4f}  [-]")
print(f"  Wing:           {x_ac_approach - x_fus_approach - x_nacelle_approach:.4f}  [-]  (base from Fig E-10)")
print(f"  Fuselage f1:    {x_fus_1_app:.4f}  [-]")
print(f"  Fuselage f2:    {x_fus_2_app:.4f}  [-]")
print(f"  Fuselage total: {x_fus_approach:.4f}  [-]")
print(f"  Nacelle:        {x_nacelle_approach:.4f}  [-]")

print("\n--- Aircraft-less-tail Lift Coefficient ---")
print(f"CL_Ah at approach: {CL_Ah:.4f}  [-]")

print("\n--- Horizontal Tail Lift Coefficient ---")
print(f"Tail type:  Adjustable")
print(f"A_h:        4.5840  [-]")
print(f"CL_h:       {CL_h:.4f}  [-]")

print("\n--- Zero-Lift Pitching Moment Coefficient ---")
print(f"Clean wing Cm_ac_w:     {Cm_ac_w:.4f}  [-]")
print(f"Fuselage Cm_fus:        {Cm_fus:.4f}  [-]")
print(f"Flaps Cm_flaps:         {Cm_flaps:.4f}  [-]")
print(f"Conversion -CL_Ah*(x_ac-0.25): {-(CL_Ah*(x_ac_approach-0.25)):.4f}  [-]")
print(f"Total Cm_ac:            {Cm_ac_total:.4f}  [-]")

print("\n--- Required Tail Size ---")
print(f"Sh/S from stability:      {min_Sh_S_stab:.4f}  [-]  (at cg_aft = {cg_aft:.4f})")
print(f"Sh/S from controllability:{min_Sh_S_cont:.4f}  [-]  (at cg_fwd = {cg_fwd:.4f})")
print(f"Required Sh/S:            {required_Sh_S:.4f}  [-]  (driven by {driver})")
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
