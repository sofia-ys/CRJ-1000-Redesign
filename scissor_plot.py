#gemini generated scissor plot

import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# INPUT VARIABLES (Replace with your data)
# ==========================================

# General Parameters
x_ac = 0.26490730691191755 # Aerodynamic center of aircraft-less-tail (fraction of MAC)
mac = 4.11  # MAC
l_h = 16.06566495  # distance from tail AC to Wing AC
lh_c = l_h/mac         # Tail moment arm normalized by MAC
Vh_V = 1        # Tail speed ratio (Vh / V)

# Stability Parameters (Cruise Condition)
SM = 0.05          # Required Stability Margin (fraction of MAC, e.g., 5%)
CL_ah = 4.0        # Lift curve slope of the horizontal tail (1/rad)
CL_aAh = 5.0       # Lift curve slope of the aircraft-less-tail (1/rad)
de_da = 0.35       # Downwash gradient (d_epsilon / d_alpha)

# Controllability Parameters (Approach/Landing with flaps)
Cm_ac = -0.15      # Pitching moment coefficient about a.c. (typically negative due to flaps)
CL_Ah = 2.5        # Lift coefficient of aircraft-less-tail at minimum speed
CL_h = -0.8        # Maximum negative lift coefficient of the tail 

# Operational CG Range (from your loading diagram)
cg_fwd = 0.15      # Most forward operational CG (fraction of MAC)
cg_aft = 0.35      # Most aft operational CG (fraction of MAC)

# ==========================================
# SCISSOR PLOT CALCULATIONS
# ==========================================

# Generate a range of CG positions for the x-axis (from 0 to 60% MAC)
x_cg_range = np.linspace(0.0, 0.6, 100)

# 1. Stability Curve Calculation
# Sh/S = (xcg - x_ac + SM) / [ (CL_ah / CL_aAh) * (1 - de/da) * (lh/c) * (Vh/V)^2 ]
K_stab = (CL_ah / CL_aAh) * (1 - de_da) * lh_c * (Vh_V**2)
Sh_S_stability = (x_cg_range - x_ac + SM) / K_stab

# 2. Controllability Curve Calculation
# Sh/S = [Cm_ac + CL_Ah * (xcg - x_ac)] / [ CL_h * (lh/c) * (Vh/V)^2 ]
K_cont = CL_h * lh_c * (Vh_V**2)
Sh_S_controllability = (Cm_ac + CL_Ah * (x_cg_range - x_ac)) / K_cont

# ==========================================
# PLOTTING
# ==========================================

plt.figure(figsize=(10, 6))

# Plot the boundaries
plt.plot(x_cg_range, Sh_S_stability, 'b-', linewidth=2, label='Stability Limit (Most Aft CG)')
plt.plot(x_cg_range, Sh_S_controllability, 'r-', linewidth=2, label='Controllability Limit (Most Fwd CG)')

# Fill the feasible region
plt.fill_between(x_cg_range, 
                 np.maximum(Sh_S_stability, Sh_S_controllability), 
                 1.0, # arbitrary upper limit for Sh/S
                 color='green', alpha=0.1, label='Feasible Design Space')

# Overlay the Operational CG Range
plt.axvspan(cg_fwd, cg_aft, color='gray', alpha=0.3, label='Operational CG Range')

# Find intersection to determine minimum required Sh/S for the specific CG range
idx_aft = np.abs(x_cg_range - cg_aft).argmin()
idx_fwd = np.abs(x_cg_range - cg_fwd).argmin()
min_Sh_S_stab = Sh_S_stability[idx_aft]
min_Sh_S_cont = Sh_S_controllability[idx_fwd]
required_Sh_S = max(min_Sh_S_stab, min_Sh_S_cont)

plt.axhline(required_Sh_S, color='k', linestyle='--', label=f'Min Req. Sh/S = {required_Sh_S:.3f}')

# Formatting the plot
plt.title('Aircraft Scissor Plot: Tail Sizing & CG Range')
plt.xlabel('Center of Gravity Position ($X_{cg} / MAC$)')
plt.ylabel('Horizontal Tail Volume Ratio ($S_h / S$)')
plt.xlim([0.0, 0.6])
plt.ylim([0.0, max(Sh_S_controllability[0], Sh_S_stability[-1]) * 1.2])
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper right')

plt.show()