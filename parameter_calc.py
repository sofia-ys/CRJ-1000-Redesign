import numpy as np

# speed parameters
M_c = 0.82  # mach number at cruise speed, value from Janes [-]
beta = np.sqrt(1 - M_c**2)  # compressability factor [-]

# horizontal tail parameters
b_h = 8.54  # total horizontal tail span [m]
S_h = 15.91  # total horizontal tail area [m^2]
A_h = b_h**2 / S_h  # aspect ratio of horizontal tail [-]
eta_h = 0.95  # airfoil efficiency, value from sead slides [-]
Lambda_halfC_h = 26.2 * (np.pi/180)  # sweep angle at the half chord of the horizontal tail, value from technical drawings [rad] 

# wing parameters
b = 26.17  # total horizontal tail span [m]
S = 77.39  # total horizontal tail area [m^2]
A = b**2 / S  # aspect ratio of horizontal tail [-]
eta = 0.95  # airfoil efficiency, value from sead slides [-]
Lambda_halfC = 21.1 * (np.pi/180)  # sweep angle at the half chord of the horizontal tail, value from technical drawings [rad] 

def lift_rate_coef(A, beta, eta, Lambda_halfC):
    C_L_alpha = 2 * np.pi * A / (2 + np.sqrt( 4 + (A * beta / eta)**2 * (1 + (np.tan(Lambda_halfC)/beta)**2)))
    return C_L_alpha

# lift rate coefficient of the horizontal tail [-]
C_L_alpha_h = lift_rate_coef(A_h, beta, eta_h, Lambda_halfC_h)
print(f"Lift rate coefficient of the horizontal tail: {C_L_alpha_h}")

# lift rate coefficient of the aircraft less tail [-]
C_L_alpha_w = lift_rate_coef(A, beta, eta, Lambda_halfC)  # wing contribution
b_f = 2.69  # fuselage external diameter
S_net = S - 14.90  # S - projection of central wing part inside fuselage, value from technical drawing [m^2]
C_L_alpha_A_h = C_L_alpha_w * (1 + 2.15 * (b_f/b))*(S_net/S) + (np.pi * b_f**2)/(2 * S)
print(f"Lift rate coefficient of the aircraft less tail: {C_L_alpha_A_h}")
print(f"Wing contribution: {C_L_alpha_w}")
print(f"Fuselage contribution: {C_L_alpha_A_h - C_L_alpha_w}")

# wing downwash gradient
Lambda_quarterC = 33.76 * np.pi/180 # quart chord sweep of wing
l_h = 16.06566  # wing ac to tail ac length
r = 2 * l_h / b  # ratio
m_tv = 0  # 
K_epsilon_Lambda = (0.1124 + 0.1265*Lambda_quarterC + 0.1766 * Lambda_quarterC**2)/(r**2) + 0.1024/r + 2  #
K_epsilon_Lambda0 = 0.1124/(r**2) + 0.1024/r + 2  #

depsilon_dalpha = (K_epsilon_Lambda/K_epsilon_Lambda0) * ( (0.4876 * r)/((r**2 + m_tv**2) * np.sqrt(r**2 + 0.6319 + m_tv**2)) + (1 + (r**2 / (r**2 + 0.7915 + 5.0734 * m_tv**2))**0.3113)(1 - np.sqrt(m_tv**2/(1+m_tv**2)))) * (C_L_alpha_w/(np.pi * A))