#gemini generated scissor plot, fixed by claude :)

import numpy as np
import matplotlib.pyplot as plt
import math as m
import controllability_coeffs

# ==========================================
# INPUT VARIABLES (Replace with your data)
# ==========================================


# General Parameters
x_ac_cruise = 0.26384118583091387 # Aerodynamic center of aircraft-less-tail (fraction of MAC)
x_ac_approach = 0.26490730691191755
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
de_da  = 0.33297873068133915          # Downwash gradient (dε/dα)
 
# Controllability Parameters (Approach/landing — flaps fully extended)
Cm_ac  = -0.15         # Pitching moment coefficient of aircraft-less-tail about its a.c.
                        # (typically large negative with flaps extended)
CL_Ah = (2 * MTOW * g) / (rho_app * V_app**2 * S) # Lift coefficient of aircraft-less-tail at minimum approach speed
CL_h   = -0.8          # Maximum (negative) lift coefficient the tail can generate
                        # (negative because the tail pushes down to counteract nose-down Cmac)
#cm_.25/Deltaf_Clmax = 0.385  #The moment coeff. around the quarter chord over Clmax and the flap deflection. For double-slotted flap it's around 0.385
quarter_chord_sweep = 0


# Operational CG range (from your loading diagram, fraction of MAC)
cg_fwd = 0.15          # Most forward operational CG
cg_aft = 0.35          # Most aft operational CG
 
# ==========================================
# SCISSOR PLOT CALCULATIONS
# ==========================================
x_cg_range = np.linspace(0.0, 0.6, 200)
 
# ------------------------------------------------------------------
# 1. STABILITY CURVE  (cruise, flaps retracted, most-aft CG limit)
#
#    Sh/S = (xcg - xac + SM) / [ (CLah/CLaAh) * (1 - dε/dα) * (lh/c̄) * (Vh/V)² ]
#
#    Uses x_ac at CRUISE speed.
# ------------------------------------------------------------------
Cm_nacelle =
K_stab = (CL_ah / CL_aAh) * (1 - de_da) * lh_c * (Vh_V ** 2)
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
A_wing = S
mystery_sweep = quarter_chord_sweep
C_m0_airfoil = controllability_coeffs.Cm0_airfoil
Cm_ac_w = C_m0_airfoil * (A_wing * m.cos(mystery_sweep)**2/(A_wing + 2*m.cos(mystery_sweep)))

###FUSELAGE


def calculate_CL_a(A, HalfChordSweep, MachNum):
    #MAKE SURE HALFCHORD IS IN RADIANS!!!
    Beta = m.sqrt(1 - MachNum^2)
    eta_h = 0.95
    2*m.pi*A/(2 + m.sqrt(4 + (A*Beta/eta_h)**2 * (1 + m.tan(HalfChordSweep)**2)/Beta**2))
    return CL_a

def calculate_CL_a_Ah(CL_a_w, b_f, S_net, b, S):
    return CL_a_w * (1 + 2.15*b_f/b) * S_net/S + m.pi/2 * b_f**2/S


C_L0 = 0 #CHANGE THIS LATER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
b_f = controllability_coeffs.b_f
S_net = S - b_f*mac #rough estimate
halfchordsweep = controllability_coeffs.Lambda_halfC
CL_a_w_lowspeed = calculate_CL_a(A_wing, halfchordsweep, 72.022/343)
CL_a_Ah_lowspeed = calculate_CL_a_Ah(CL_a_w_lowspeed, b_f, S_net, b, S)

h_f = 2.5 #estimate for fuselage height
l_f = controllability_coeffs.l_fn #fuselage length
Cm_fus = -1.8*(1 - 2.5*b_f/l_f) * m.pi*b_f*h_f*l_f/(4*S*mac) * C_L0 / CL_a_Ah_lowspeed

###FLAPS
cdash_mac = 1.35 #The total span of the wings with flaps/the airfoil MAC
mu_1 = 0.157 #Assuming 45 degree flap angles
mu_2 = 0.4
mu_3 = 0.04
deltaClmax = #How much Cl the flaps add
C_L_landing = C_L0 +
Swf_S = #ratio between flapped wing area and ref wing area
b1 = C_L_landing + deltaClmax*(1 - Swf_S)   #Bracket 1 of the eq
b2 = -mu_1*deltaClmax*cdash_mac - b1*1/8*cdash_mac*(cdash_mac - 1)
Cm_flaps = mu_2 * b2 + 0.7*A_wing/(1 + 2/A_wing)*mu_3*deltaClmax*m.tan(quarter_chord_sweep)
Cm_flaps_transformed = Cm_ac + C_L_landing * (0.25 - x_ac_approach/mac) #apply transformation as seen on controllability hidden slide 20

Cm_ac_total = Cm_ac_w + Cm_fus + Cm_flaps_transformed + Cm_nacelle



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
                Sh_S_controllability,
                Sh_S_stability,
                where=(Sh_S_stability >= Sh_S_controllability),
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
 
ax.set_xlim([0.0, 0.6])
ax.set_ylim([0.0, max(Sh_S_controllability[0], Sh_S_stability[-1]) * 1.2])
ax.grid(True, linestyle=':', alpha=0.7)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()
