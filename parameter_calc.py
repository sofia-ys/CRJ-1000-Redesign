import numpy as np

# speed parameters
M_c = 0.82  # mach number at cruise speed, value from Janes [-]
beta_cr = np.sqrt(1 - M_c**2)  # compressability factor [-]
V_app = 72.022  # approach speed [m/s]
# a_app =  # speed of sound at approach altitude [-]
M_app = V_app/a_app # Mach equivalent of appraoch speed
beta_app = np.sqrt(1 - M_app**2)  # compressability factor for approach [-]

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
MAC = 4.11  # mean aerodynamic chord [m]
taper = 0.238129  # taper ratio
Lambda_quarterC = 33.76 * np.pi/180 # quarter chord sweep of wing
sweep = 30 * np.pi/180  # wing LE sweep

# fuselage parameters 
b_f = 2.69  # fuselage external diameter
S_net = S - 14.90  # S - projection of central wing part inside fuselage, value from technical drawing [m^2]
l_h = 16.06566  # wing ac to tail ac length
r = 2 * l_h / b  # tail length to wingspan ratio [-]
m_tv = 2 * 5.026099606 / b # distance between root chord of wing and horizontal tail plane, value from technical drawing [m]
# l_fn = 0  # length from nose to wing root tip

# nacelle parameters
# b_n =  #
# l_n =  #


# lift rate coefficient calcs (short for calculation btw)
print("\n-------------Lift Rate Coefficient-------------")

def lift_rate_coef(A, beta, eta, Lambda_halfC):  # A, eta, Lambda_halfC are geometry dependent, beta is speed dependent
    C_L_alpha = 2 * np.pi * A / (2 + np.sqrt( 4 + (A * beta / eta)**2 * (1 + (np.tan(Lambda_halfC)/beta)**2)))
    return C_L_alpha

# lift rate coefficient of the horizontal tail at cruise [-]
C_L_alpha_h = lift_rate_coef(A_h, beta_cr, eta_h, Lambda_halfC_h)
print(f"Lift rate coefficient of the horizontal tail: {C_L_alpha_h}")

# lift rate coefficient of the aircraft less tail [-]

def lift_rate_aircraft_less_tail(beta):  # beta is a speed dependent parameter
    C_L_alpha_w = lift_rate_coef(A, beta, eta, Lambda_halfC)  # wing contribution
    C_L_alpha_A_h = C_L_alpha_w * (1 + 2.15 * (b_f/b))*(S_net/S) + (np.pi * b_f**2)/(2 * S)
    return C_L_alpha_A_h, C_L_alpha_w

C_L_alpha_A_h_cr, C_L_alpha_w_cr = lift_rate_aircraft_less_tail(beta_cr)  # cruise values
print(f"Lift rate coefficient of the aircraft less tail: {C_L_alpha_A_h_cr}")
print(f"Wing contribution: {C_L_alpha_w_cr}")
print(f"Fuselage contribution: {C_L_alpha_A_h_cr - C_L_alpha_w_cr}")

print("\n------------Wing Downwash Gradient-------------")
# wing downwash gradient

def downwash(beta):  # beta is a speed dependent parameter
    K_epsilon_Lambda = (0.1124 + 0.1265*Lambda_quarterC + 0.1766 * Lambda_quarterC**2)/(r**2) + 0.1024/r + 2 
    K_epsilon_Lambda0 = 0.1124/(r**2) + 0.1024/r + 2 
    _, C_L_alpha_w = lift_rate_aircraft_less_tail(beta)
    depsilon_dalpha = (K_epsilon_Lambda/K_epsilon_Lambda0) * ( (0.4876 * r)/((r**2 + m_tv**2) * np.sqrt(r**2 + 0.6319 + m_tv**2)) + (1 + (r**2 / (r**2 + 0.7915 + 5.0734 * m_tv**2))**0.3113) * (1 - np.sqrt(m_tv**2/(1 + m_tv**2)))) * (C_L_alpha_w/(np.pi * A))
    return depsilon_dalpha

depsilon_dalpha = downwash(beta_cr)  # downwash while at cruise condition
print(f"Wing downwash gradient: {depsilon_dalpha}")

print("\n---------Aerodynamic Centre at Cruise----------")
# ac of aircraft less tail

def ac_fuselage(beta):
    C_L_alpha_A_h, _ = lift_rate_aircraft_less_tail(beta)  # only speed dependent variable is C_L_alpha_A_h
    x_ac_f1 = (-1.8 * b_f**2 * l_fn)/(C_L_alpha_A_h * S * MAC)  # fuselage contribution 1
    x_ac_f2 = (0.273 * b_f * (S/b) * (b - b_f) * np.tan(Lambda_quarterC)) / ((1 + taper) * (S/b)**2 * (b + 2.15 * b_f))  # fuselage contribution 2
    x_ac_f = x_ac_f1 + x_ac_f2  # fuselage contribution
    return x_ac_f

x_ac_f_cr = ac_fuselage(beta_cr)
print(f"Fuselage contribution: {x_ac_f_cr}")

# printing the cruise conditions to find wing speed dependent variable (from graph)
print(f"Beta * A: {beta_cr * A}")
print(f"taper: {taper}")
print(f"Lambda_Beta: {(np.atan2(np.tan(sweep), beta_cr)) * (180/np.pi)}")
x_ac_w_cr = 0.37  # wing contribution
print(f"Wing contribution: {x_ac_w_cr}")

def nacelle_contribution(beta):
    C_L_alpha_A_h, _ = lift_rate_aircraft_less_tail(beta)  # only speed dependent variable is C_L_alpha_A_h
    x_ac_n = 2 * (-2.5 * b_n**2 * l_n)/(S * (S/b) * C_L_alpha_A_h) # nacelle contribution for two nacelles
    return x_ac_n

x_ac_n_cr = nacelle_contribution(beta_cr)
print(f"Nacelle contribution: {x_ac_n_cr}")

x_ac_cr = x_ac_w_cr + x_ac_f_cr + x_ac_n_cr
print(f"AC of aircraft less tail: {x_ac_cr}")

print("\n--------Aerodynamic Centre at Approach---------")

x_ac_f_app = ac_fuselage(beta_app)
print(f"Fuselage contribution: {x_ac_f_app}")

# printing the cruise conditions to find wing speed dependent variable (from graph)
print(f"Beta * A: {beta_cr * A}")
print(f"taper: {taper}")
print(f"Lambda_Beta: {(np.atan2(np.tan(sweep), beta_cr)) * (180/np.pi)}")
# x_ac_w_app = 0  # wing contribution
print(f"Wing contribution: {x_ac_w_app}")

x_ac_n_app = nacelle_contribution(beta_app)
print(f"Nacelle contribution: {x_ac_n_app}")

x_ac_app = x_ac_w_app + x_ac_f_app + x_ac_n_app
print(f"AC of aircraft less tail: {x_ac_app}")

'''TO DO:
- GEOMETRIC PARAMETERS: l_fn, b_n, l_n
- SPEED PARAMETERS: V_app, M_app, beta_app
^ for M_app the approach altitude is needed
'''