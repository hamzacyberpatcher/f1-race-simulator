import fastf1
from fastf1 import plotting
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

race_year = int(input("Enter the race year (e.g., 2024): "))
race_name = input("Enter the race name (e.g., Brazil): ")
lap_limit = int(input("Enter the number of laps to simulate: "))

plotting.setup_mpl(misc_mpl_mods=False)
fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(race_year, race_name, 'R')
session.load()

ref_lap = session.laps.pick_fastest().get_telemetry()

fig, ax = plt.subplots(figsize = (10, 10), facecolor = '#333333')
ax.set_facecolor('#333333')

ax.plot(ref_lap['X'], ref_lap['Y'], color='#444444', linewidth =5, zorder=1)

car_dot, = ax.plot([], [], 'ro', markersize = 10, zorder = 2)

ax.axis('equal')
ax.set_axis_off()

all_telemetry = {}
car_dots = {}
car_numbers = {}

for driver in session.drivers:
    driver_info = session.results.loc[driver]
    driver_laps = session.laps.pick_driver(driver)
    driver_laps = driver_laps[driver_laps['LapNumber'] <= lap_limit]

    num_str = str(driver_info['DriverNumber'])
    full_name = f"{driver_info['FirstName']} {driver_info['LastName']}"

    tel_list = []

    for _, lap in driver_laps.iterlaps():
        try:
            tel = lap.get_telemetry()
            tel_list.append(tel)
        except:
            continue

    if len(tel_list) == 0:
        continue

    tel = pd.concat(tel_list).reset_index(drop=True)
    all_telemetry[driver] = tel

    try:
        team_color = plotting.get_team_color(driver_info['TeamName'], session=session)
    except:
        team_color = '#FFFFFF'

    dot, = ax.plot([], [], 'o',
                   color=team_color,
                   markersize=12,
                   label=f"{num_str} - {full_name}",
                   zorder=3)

    car_dots[driver] = dot

    txt = ax.text(0, 0, num_str,
                  color='black',
                  fontsize=8,
                  weight='bold',
                  ha='center',
                  va='center',
                  zorder=4)

    car_numbers[driver] = {'obj': txt, 'num': num_str}

leg = ax.legend(loc='center left',
                bbox_to_anchor=(1, 0.5),
                facecolor='#111111',
                edgecolor='#444444',
                labelcolor='white',
                fontsize=9,
                ncol=2,
                title="Driver Grid")

leg.get_title().set_color('white')

def init():
    for drv in all_telemetry:
        car_numbers[drv]['obj'].set_text('')
    return list(car_dots.values()) + [cn['obj'] for cn in car_numbers.values()]

def update(frame):
    artists = []
    for drv in all_telemetry:
        tel = all_telemetry[drv]
        if frame < len(tel):
            x = tel['X'].iloc[frame]
            y = tel['Y'].iloc[frame]
            car_dots[drv].set_data([x], [y])
            artists.append(car_dots[drv])
            text_element = car_numbers[drv]['obj']
            text_element.set_position((x, y))
            text_element.set_text(car_numbers[drv]['num'])
            artists.append(text_element)
        else:
            car_numbers[drv]['obj'].set_text('')
    return artists

max_frames = max(len(t) for t in all_telemetry.values())

ani = FuncAnimation(
    fig,
    update,
    frames=max_frames,
    init_func=init,
    blit=True,
    interval=20
)

ani.event_source.stop()

def start_animation(event):
    ani.event_source.start()
    fig.canvas.mpl_disconnect(cid)

cid = fig.canvas.mpl_connect('key_press_event', start_animation)

fig.suptitle(f"{race_name} {race_year} - First {lap_limit} Laps", color='white', fontsize=16)
plt.tight_layout()
plt.show()
