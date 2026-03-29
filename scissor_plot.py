#gemini generated scissor plot, fixed by claude :)

import numpy as np
import matplotlib.pyplot as plt

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

# Stability Parameters (Cruise Condition)
SM     = 0.05          # Required stability margin (fraction of MAC, e.g. 5%)
CL_ah  = 4.6793850598197535           # Lift curve slope of the horizontal tail (1/rad)
CL_aAh = 6.423476455793314           # Lift curve slope of the aircraft-less-tail (1/rad)
de_da  = 0.33297873068133915          # Downwash gradient (dε/dα)
 
# Controllability Parameters (Approach/landing — flaps fully extended)
Cm_ac  = -0.15         # Pitching moment coefficient of aircraft-less-tail about its a.c.
                        # (typically large negative with flaps extended)
CL_Ah  = 1.5553   # Lift coefficient of aircraft-less-tail at minimum approach speed
CL_Ah = (2 * MTOW * g) / (rho_app * V_app**2 * S)
CL_h   = -0.8          # Maximum (negative) lift coefficient the tail can generate
                        # (negative because the tail pushes down to counteract nose-down Cmac)
 
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
K_cont = CL_h * lh_c * (Vh_V ** 2)           # negative, because CL_h < 0
Sh_S_controllability_raw = (Cm_ac + CL_Ah * (x_cg_range - x_ac_approach)) / K_cont
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