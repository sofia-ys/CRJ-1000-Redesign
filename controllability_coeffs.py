import numpy as np

# ============================================================
# CALCULATION OF  Cm_ac,  CL_Ah,  CL_h
# for the scissor-plot controllability curve
#
# Paste below the existing aerodynamic_parameters.py so all
# previously computed variables are already in scope:
#   b_f, l_fn, b_n, l_n, S_net,
#   lift_rate_coef(), lift_rate_aircraft_less_tail(),
#   downwash(), ac_fuselage(), nacelle_contribution()
# ============================================================
V_app = 72.022
a_app =  np.sqrt(1.4*287.05*288.15) # speed of sound at approach altitude [-]
M_app = V_app/a_app # Mach equivalent of appraoch speed
beta_app = np.sqrt(1 - M_app**2)  # compressability factor for approach [-]
b_h = 8.54  # total horizontal tail span [m]
S_h = 15.91  # total horizontal tail area [m^2]
A_h = b_h**2 / S_h  # aspect ratio of horizontal tail [-]
b = 26.17  # total horizontal tail span [m]
S = 77.39  # total horizontal tail area [m^2]
A = b**2 / S  # aspect ratio of horizontal tail [-]
MAC = 4.11  # mean aerodynamic chord [m]
Lambda_quarterC = 33.76 * np.pi/180 # quarter chord sweep of wing
taper = 0.238129  # taper ratio
b_f = 2.69  # fuselage external diameter


# ============================================================
# ADDITIONAL INPUTS  (fill in your values)
# ============================================================

# --- Weight / density ---
MTOW    = 38995       # [kg]   maximum take-off weight (conservative for approach sizing)
g       = 9.80665   # [m/s²]
rho_app = 1.225     # [kg/m³] ISA sea-level density at approach altitude

# --- Wing airfoil ---
Cm0_airfoil = ...   # [-]  zero-lift pitching moment of wing airfoil
                    #      from airfoil polar (XFOIL / Janes / airfoiltools.com)
                    #      typical range: −0.02 (symmetric) to −0.12 (high camber)

# --- Flap geometry (from your wing design module) ---
Swf_S       = ...   # [-]  flapped wing area / total wing area  (TE flaps only)
delta_Cl_max = ...  # [-]  2-D airfoil ΔCl_max at full landing flap deflection
c_prime_c   = ...   # [-]  chord ratio with flap extended; = 1.0 for non-Fowler flaps

# μ-factors from Torenbeek Fig G-16 and G-17  (graphical look-up required)
mu1 = ...           # [-]  Fig G-16: f(c'/c, Swf/S)
mu2 = ...           # [-]  Fig G-16: f(flap chord position x_f/c, c'/c)
mu3 = ...           # [-]  Fig G-17: f(aspect ratio A, quarter-chord sweep Λ_c/4)

# --- Tail configuration (choose one) ---
#   'fixed'       → CL_h = −0.35 · A_h^(1/3)   (Lecture 8, slide 17)
#   'adjustable'  → CL_h = −0.8
#   'full_moving' → CL_h = −1.0
tail_type = 'adjustable'

# ============================================================
# APPROACH-SPEED AERODYNAMIC PARAMETERS
# (re-run the functions from aerodynamic_parameters.py at
#  approach speed — needed for Cm_ac and the controllability curve)
# ============================================================
print("\n========== Approach-speed aerodynamic parameters ==========")

C_L_alpha_h_app = lift_rate_coef(A_h, beta_app, eta_h, Lambda_halfC_h)
print(f"CLα tail at approach :         {C_L_alpha_h_app:.4f}  1/rad")

C_L_alpha_A_h_app, C_L_alpha_w_app = lift_rate_aircraft_less_tail(beta_app)
print(f"CLα aircraft-less-tail (app):  {C_L_alpha_A_h_app:.4f}  1/rad")

depsilon_dalpha_app = downwash(beta_app)
print(f"Downwash gradient (app):       {depsilon_dalpha_app:.4f}  [-]")

x_ac_f_app = ac_fuselage(beta_app)
x_ac_n_app = nacelle_contribution(beta_app)
# Wing contribution at approach from graph (update value as needed):
x_ac_w_app = 0.445          # [-] fraction of MAC  (from graph at approach beta*A)
x_ac_app   = x_ac_w_app + x_ac_f_app + x_ac_n_app
print(f"x_ac aircraft-less-tail (app): {x_ac_app:.4f}  (fraction of MAC)")

# ============================================================
# 1.  CL_Ah  —  lift coefficient of aircraft-less-tail
#               at approach speed  (flaps fully extended)
# ============================================================
# Force balance: W = ½ ρ V² S · CL_total
# Tail lift is small compared to wing lift → CL_Ah ≈ CL_total
# (conservative: use MTOW rather than landing weight)

CL_Ah = (2 * MTOW * g) / (rho_app * V_app**2 * S)

print("\n=================== CL_Ah ===================")
print(f"CL_Ah (aircraft-less-tail at approach):  {CL_Ah:.4f}")

# ============================================================
# 2.  CL_h  —  maximum (negative) tail lift coefficient
# ============================================================
# From Lecture 8, slide 17 (Torenbeek):
#   Fixed tail:        CL_h = −0.35 · A_h^(1/3)
#   Adjustable tail:   CL_h = −0.8
#   Full moving tail:  CL_h = −1.0
# Values more negative than −1 are not physically realisable.

if tail_type == 'fixed':
    CL_h = -0.35 * A_h**(1/3)
elif tail_type == 'adjustable':
    CL_h = -0.8
elif tail_type == 'full_moving':
    CL_h = -1.0
else:
    raise ValueError("tail_type must be 'fixed', 'adjustable', or 'full_moving'")

print("\n=================== CL_h ====================")
print(f"Tail type: {tail_type}")
print(f"A_h = {A_h:.4f}")
print(f"CL_h (max negative tail lift):  {CL_h:.4f}")

# ============================================================
# 3.  Cm_ac  —  pitching moment of aircraft-less-tail
#               about its a.c., at approach (flaps fully out)
# ============================================================
# Method (Lecture 8, slides 19-21 + Torenbeek Appendix G):
#   Step A: compute each contribution about the quarter-chord (Cm_c/4)
#   Step B: convert to Cm about the aerodynamic centre using x_ac_app
#
#   Cm_ac = Cm_c/4_total − CL_Ah · (x̄_ac_app − 0.25)
#
# Contributions to Cm_c/4:
#   (i)   Wing airfoil (clean)         → dominant clean-config term
#   (ii)  Fuselage and nacelles        → small; re-uses x_ac shift formulae
#   (iii) Flaps                        → dominant term at landing (large negative)

print("\n=================== Cm_ac ===================")

# --- (i) Clean wing contribution  (Torenbeek Eq. 8-14 / Lecture 8 slide 19) ---
# About the quarter-chord of the MAC.
# Note: use low-speed (approach) aerodynamics  ("recompute for low speed" — slide 19)
Cm_c4_wing = Cm0_airfoil * (A * np.cos(Lambda_quarterC)**2) / (A + 2 * np.cos(Lambda_quarterC))
print(f"(i)  Clean wing  Cm_c/4:              {Cm_c4_wing:.4f}")

# --- (ii) Fuselage and nacelle contributions  (Lecture 8 slide 19: "see previous lecture") ---
# The fuselage/nacelle contribution to Cm at the quarter-chord equals
# the a.c. shift they induce multiplied by CL_Ah:
#   ΔCm_c/4_fus = -x_ac_f1_app · CL_Ah
#   ΔCm_c/4_nac = -x_ac_n_app  · CL_Ah
#
# x_ac_f_app contains two Torenbeek terms:
#   f1: destabilising body-upwash term  (-1.8 b_f² l_fn / (CLαAh S MAC))
#   f2: stabilising trailing-vortex term
# Only f1 enters Cm (f2 is a vortex-lift correction, no direct Cm counterpart).
x_ac_f1_app = (-1.8 * b_f**2 * l_fn) / (C_L_alpha_A_h_app * S * MAC)

Cm_c4_fus = -x_ac_f1_app * CL_Ah
Cm_c4_nac = -x_ac_n_app  * CL_Ah
print(f"(ii) Fuselage   ΔCm_c/4:              {Cm_c4_fus:.4f}")
print(f"     Nacelles   ΔCm_c/4:              {Cm_c4_nac:.4f}")

# --- (iii) Flap contribution  (Torenbeek Appendix G, Fig G-15/16/17) ---
# About the quarter-chord of the MAC:
#
#   ΔCm_c/4_flap = μ1 · (−μ2 · ΔCl_max  +  μ3 · CL_Ah · tan(Λ_c/4))
#
# Sign convention:
#   • −μ2 · ΔCl_max  : always negative (flap lift acts aft of c/4 → nose-down)
#   • +μ3 · CL_Ah · tan(Λ_c/4) : sweep-induced correction (usually small positive)
#
# Graph look-up guidance:
#   μ1  (Fig G-16): abscissa = c'/c,  parameter = Swf/S
#   μ2  (Fig G-16): abscissa = c'/c,  parameter = flap chord-to-wing-chord ratio
#   μ3  (Fig G-17): abscissa = A · tan(Λ_c/4),  read off correction factor

DCm_c4_flap = mu1 * (-mu2 * delta_Cl_max + mu3 * CL_Ah * np.tan(Lambda_quarterC))
print(f"(iii) Flaps     ΔCm_c/4:              {DCm_c4_flap:.4f}")

# --- Cm_c/4 total ---
Cm_c4_total = Cm_c4_wing + Cm_c4_fus + Cm_c4_nac + DCm_c4_flap
print(f"\nTotal Cm_c/4 (all contributions):     {Cm_c4_total:.4f}")

# --- Convert from quarter-chord to aerodynamic centre  (Lecture 8 slide 20) ---
# Cm_ac = Cm_c/4 − CL_Ah · (x̄_ac_app − 0.25)
# If x_ac_app > 0.25 and CL_Ah > 0: Cm_ac is more negative than Cm_c/4
conversion = -CL_Ah * (x_ac_app - 0.25)
Cm_ac = Cm_c4_total + conversion
print(f"Conversion  −CL_Ah·(x_ac−0.25):      {conversion:.4f}")
print(f"Cm_ac (aircraft-less-tail at app):    {Cm_ac:.4f}")

# ============================================================
# SUMMARY — scissor plot controllability inputs
# ============================================================
print("\n" + "="*52)
print("  SCISSOR PLOT — CONTROLLABILITY CURVE INPUTS")
print("="*52)
print(f"  x_ac_approach  = {x_ac_app:.4f}   (fraction of MAC)")
print(f"  CL_Ah          = {CL_Ah:.4f}   (lift at approach)")
print(f"  CL_h           = {CL_h:.4f}   (max tail lift, {tail_type})")
print(f"  Cm_ac          = {Cm_ac:.4f}   (pitching moment at a.c.)")
print(f"  CLα tail (app) = {C_L_alpha_h_app:.4f}   (1/rad)")
print(f"  CLα A-h  (app) = {C_L_alpha_A_h_app:.4f}   (1/rad)")
print(f"  dε/dα   (app)  = {depsilon_dalpha_app:.4f}   [-]")
print("="*52)