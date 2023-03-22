from scipy import stats
from grbpy.batse import BATSEBurst
import matplotlib.pyplot as plt
import csv
import os
import numpy as np
import sys


def fit_background(data, time):
    poly_coefs = list(np.polyfit(x=data['trig_time'], y=data['sum_chan'], deg=2))[::-1]
    background = 0
    messed_up_bg_list = [512, 526, 547, 878, 927, 1025, 1076, 1384, 1419, 1439, 1452, 1461, 1661, 1680, 1687, 1953,
                         2114, 2143, 2197, 2213, 2311, 2412, 2482, 2500, 2515, 2634, 2663, 2681, 2695, 2770, 2774,
                         2815, 2823, 2825, 2834, 2843, 2863, 2877, 2893, 2922, 2984, 2986, 3039, 3078, 3084, 3115,
                         3141, 3284, 3307, 3333, 3441, 3458, 3580, 3593, 3728, 3864, 3895, 3911, 3930, 4388, 4745,
                         5423, 5463, 5508, 5572, 5573, 5590, 5612, 5626, 6105, 6125, 6188, 6271, 6283, 6284, 6305,
                         6320, 6344, 6351, 6358, 6440, 6583, 6613, 6621, 6630, 6649, 6659, 6774, 6891, 6987, 7087,
                         7130, 7148, 7207, 7219, 7247, 7287, 7294, 7440, 7449, 7460, 7493, 7566, 7569, 7575, 7595,
                         7642, 7645, 7654, 7703, 7705, 7789, 7798, 7802, 7845, 7885, 7924, 7952, 7963, 7965, 8001,
                         8004, 8008, 8039, 8079, 8086, 8105, 8116, 8121]
    for i in range(len(poly_coefs)):
        background += poly_coefs[i] * time ** i
    return background, poly_coefs[0], poly_coefs[1], poly_coefs[2]


def calc_64ms_background(file_path, trig_num, duration=None, init_params=None, auto_save=False):
    if init_params is None and duration is None:
        print(f'must either specify init_params or duration')
        return None

    if '64ms' not in file_path:
        print(f'file {file_path} is not a 64 ms file')
        return None

    grb = BATSEBurst(file_path, time_signature='64ms')

    if not grb.parse_file():
        print(f'file {file_path} does not exist')
        return None

    burst_data = grb.chan_data
    burst_meta_data = grb.meta_data
    burst_data = burst_data[(burst_data.sum_chan != 0) | (burst_data.chan1 != 0) | (burst_data.chan2 != 0) |
                            (burst_data.chan3 != 0) | (burst_data.chan4 != 0)]

    if init_params is None:
        t90 = float(duration['t90'])
        t90_start = float(duration['t90_start'])
        t90_end = float(t90_start+t90)
        t90e = float(duration['t90e'])
        window_params = {
            'start_min_win': burst_data['trig_time'].min(),
            'start_max_win': (((t90_start - t90e) - burst_data['trig_time'].min()) / 2) + burst_data['trig_time'].min(),
            'end_min_win': ((burst_data['trig_time'].max() - (t90_end + t90e)) / 2) + (t90_end + t90e),
            'end_max_win': burst_data['trig_time'].max(),
        }
    else:
        window_params = init_params

    while True:
        print(f'burst_data {burst_data}')
        print(f'burst_meta_data {burst_meta_data}')
        print(f'duration {duration}')
        print(f'start_max_window {window_params["start_max_win"]}')
        print(f'end_min_window {window_params["end_min_win"]}')

        trimmed_data = burst_data.copy().loc[((burst_data['trig_time'] < window_params['start_max_win']) &
                                              (burst_data['trig_time'] > window_params['start_min_win'])) |
                                             ((burst_data['trig_time'] > window_params['end_min_win']) &
                                              (burst_data['trig_time'] < window_params['end_max_win']))]

        background_mean = np.mean(trimmed_data)
        peak_flux = np.max(burst_data)
        signal_to_noise = (peak_flux - background_mean) / np.sqrt(peak_flux)

        print(f' {background_mean}')
        print(f'peak_flux {peak_flux}')
        print(f'signal_to_noise {signal_to_noise}')
        print(f'trimmed_data {trimmed_data}')

        burst_data['background'], c, x, x2 = fit_background(data=trimmed_data, time=burst_data['trig_time'])

        plt.plot(burst_data['trig_time'], burst_data['sum_chan'], c='b')
        plt.scatter(trimmed_data['trig_time'], trimmed_data['sum_chan'], c='r', marker='.')
        plt.plot(burst_data['trig_time'], burst_data['background'], c='k')
        if duration is not None:
            plt.axvline(x=t90_start, color='g')
            plt.axvline(x=t90_end, color='g')
        plt.show()

        return_data = {
            'trig_num': trig_num,
            'start_min_win': window_params['start_min_win'],
            'start_max_win': window_params['start_max_win'],
            'end_min_win': window_params['end_min_win'],
            'end_max_win': window_params['end_max_win'],
            'c': c,
            'x': x,
            'x2': x2,
        }

        if auto_save is True:
            return return_data

        save_input = input('save background calculations? (y/n): ')
        if save_input.lower() == 'y':
            return return_data
        else:
            for key, value in window_params.items():
                raw_input = input(f'enter new {key} value (press Enter to leave the same): ')
                if raw_input != '':
                    window_params[key] = float(raw_input)
