from scipy.integrate import odeint
import matplotlib.pyplot as plt
from scipy.constants import g
import os, time, glob
import numpy as np

#====================================================================

def bungee(y,t,k,l,m,c_1, c_2):
    """
    ============
    bungee
    ============
        A simple bungee jump ODE for bungee jumps in the glasgow python IT lab
    ============
    Parameters
    ============
    first:
        array [h,v]: how high does the jump start in m and how fast are they going in ms^-1
    second:
        float t: length of timestep in seconds
    third:
        float k: the k value of the bungee rope
    fourth:
        float l: how high above the ground does the rope start stretching!
    fifth:
        float m: how heavy is the jumper in kg
    sixth:
        float c_1: air resistance parameter 1
    seventh:
        float c_2: air resistance parameter 2
    """
    h, v = y
    air_param_1 = c_1/m*v
    air_param_2 = c_2/m*abs(v)*v
    if h > l:
        E = 0
    else:
        E = k*(l-h)
    if h < 0 and v < 0:
        dydt = [0, -g+(E/m)-air_param_1-air_param_2] # [0,0] breaks solver, write exception in main file 
    else:
        dydt = [v, -g+(E/m)-air_param_1-air_param_2]
    return dydt

#====================================================================

def any_bungee_solver(y0,tmax,argz):
    """
    ============
    any_bungee_solver
    ============
        a messy function for solving the bungee problem! requires the bungee ODE to be already defined separately
    ============
    Parameters
    ============
    first:
        array [h,v]: how high does the jump start in m and how fast are they going in ms^-1
    second:
        float tmax: how many seconds to calculate over, timestep set to tmax/101
    third:
        array (k, l, m, c_1, c_2): All the arguments needed for modeling the jump, see bungee() for details!
    """
    warnings = []
    if y0[0] < 0:
        warnings.append("WARNING: Negative jump height, setting to 80m")
        y0[0] = 80
    if tmax < 0:
        warnings.append("WARNING: Time must be positive, setting to 20s")
        tmax = 20
    arg_list = list(argz)
    arg_list[1] = y0[0]-arg_list[1]
    if arg_list[1] > y0[0]:
        warnings.append("WARNING: Negative bungee length, setting to 20m")
        arg_list[1] = 20
    if arg_list[0] < 0:
        warnings.append("WARNING: Negative k value, setting to 100N\m")
        arg_list[0] = 100
    if arg_list[2] < 0:
        warnings.append("WARNING: Negative mass, setting to 100kg")
        arg_list[2] = 100
    argz = tuple(arg_list
                )
    t = np.linspace(0, tmax, 1001)
    sol = odeint(bungee, y0, t, args=argz)
    if any(i <= 0 for i in sol[:,0]):
        y_ground = [0,0]
        impact_index = np.argmax(sol[:,0]<0)
        sol_crash =  odeint(bungee, y_ground, t, args=argz)
        if all(i <= 0 for i in sol_crash[:,1]):
            warnings.append(f'OUTCOME: The jumper hit the ground after {impact_index*t[1]:.2f} seconds')
            sol_crash[:,1] = 0
            warnings.append(f'WARNING: Velocity is set to 0 beyond {impact_index*t[1]:.2f} seconds')
            warnings.append('REASON: l value was set too high')
        else:
            warnings.append(f'OUTCOME: The jumper hit the ground after {impact_index*t[1]:.2f} seconds')
            warnings.append('REASON: k value was set too low')
        final_sol = np.concatenate((sol[:impact_index,:],sol_crash[:-impact_index,:]))
    else:
        warnings.append("OUTCOME: A safe bungee jump happened")
        final_sol = sol

    fig, ax1 = plt.subplots( figsize = (10,6))

    color = 'tab:green'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('heigh(m)')
    ax1.plot(t, final_sol[:, 0] , label='heigh(m)', color=color)
    ax1.hlines(argz[1], 0,  max(t), colors='orange', linestyles='dashed', label='bungee length')
    ax1.set_ylim(0,80)
    ax1.set_xlim(0,max(t))

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('velocity($ms^{-1}$)')  # we already handled the x-label with ax1
    ax2.plot(t, final_sol[:, 1], label='velocity($ms^{-1}$)', color=color)
    ax2.hlines(0, 0,  max(t), colors='r', linestyles='dashed', label='zero velocity')
    vel_min = abs(min(final_sol[:, 1]))*1.1
    ax2.set_ylim(-vel_min,vel_min)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.legend(loc='upper right',framealpha=1)
    ax1.grid() #ax2 grid doesn't have vertical lines for some reason
   
    #server bookeeping

    if not os.path.isdir('static'):
        os.mkdir('static')
    else:
        for filename in glob.glob(os.path.join('static','*png')):
            os.remove(filename)

    #save figure for display

    fig = os.path.join('static', str(time.time())+'.png')
    plt.savefig(fig)
    plt.close()
    fig = f'../{fig}'
    return fig, warnings    
