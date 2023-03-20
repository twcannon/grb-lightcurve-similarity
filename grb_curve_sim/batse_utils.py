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
    return background


def calc_64ms_background(file_path, duration):
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

    t90 = float(duration['t90'])
    t90_start = float(duration['t90_start'])
    t90_end = float(t90_start+t90)
    t90e = float(duration['t90e'])
    min_data_time = burst_data['trig_time'].min()
    max_data_time = burst_data['trig_time'].max()
    min_window = (((t90_start - t90e) - min_data_time) / 2) + min_data_time
    max_window = ((max_data_time - (t90_end + t90e)) / 2) + (t90_end + t90e)

    print(burst_data)
    print(burst_meta_data)
    print(duration)
    print(min_window)
    print(max_window)

    trimmed_data = burst_data.copy().loc[(burst_data['trig_time'] < min_window) |
                                         (burst_data['trig_time'] > max_window)]
    print(trimmed_data)

    burst_data['background'] = fit_background(data=trimmed_data, time=burst_data['trig_time'])

    plt.plot(burst_data['trig_time'], burst_data['sum_chan'], c='b')
    plt.scatter(trimmed_data['trig_time'], trimmed_data['sum_chan'], c='r', marker='.')
    plt.plot(burst_data['trig_time'], burst_data['background'], c='k')
    plt.axvline(x=t90_start, color='g')
    plt.axvline(x=t90_end, color='g')
    plt.show()

#
# def fix_background(burst_data, time, time_start, time_end, add_time):
#     try:
#         burst_data = burst_data[((time > (time_start - add_time * 2)) & (time < time_start)) | (
#                     (time > time_end) & (time < (time_end + add_time * 2)))]
#     except:
#         burst_data = burst_data[((time > min(time)) & (time < time_start)) | ((time > time_end) & (time < max(time)))]
#     try:
#         time = time[((time > (time_start - add_time * 2)) & (time < time_start)) | (
#                     (time > time_end) & (time < (time_end + add_time * 2)))]
#     except:
#         time = time[((time > min(time)) & (time < time_start)) | ((time > time_end) & (time < max(time)))]
#     time_fixed = time
#     burst_fixed = burst_data
#     return burst_fixed, time_fixed
#
#
# add_time_mult = 1
#
# data_path = os.path.join('..', 'batse_data')
#
# burst_dict = {}
# with open(os.path.join('data', 'burst_info.csv'), newline='') as f:
#     for row in csv.DictReader(f, delimiter=','):
#         burst_dict[str(row['burst_num'])] = row
#
# dur_dict = {}
# with open(os.path.join('data', 'duration_table.csv'), newline='') as f:
#     for row in csv.DictReader(f, delimiter=','):
#         dur_dict[str(row['trig'])] = row
#
# background_file = open(os.path.join('data', 'background_table.csv'), 'w', newline='')
# with background_file:
#     header = ['burst_num', 'slope', 'intercept', 'r_value', 'p_value', 'std_err', 'min_time', 'max_time',
#               'signal_to_noise']
#     writer = csv.DictWriter(background_file, fieldnames=header)
#     writer.writeheader()
#
#     for burst_num in dur_dict:
#
#         if burst_num in burst_dict:
#
#             # remove short bursts
#             if (float(dur_dict[burst_num]['t90']) < 2) or (int(burst_dict[burst_num]['single_emission']) == 0):
#                 next
#             else:
#
#                 try:
#                     burst_info = burst_dict[burst_num]
#                     # burst_num,burst_path,single_emission
#
#                     file_path = os.path.join(data_path, burst_info['burst_file'])
#
#                     grb = BATSEBurst(file_path)
#                     grb.parse_batse_file()
#
#                     burst_data = grb.sum_chan_data
#                     header_names = grb.header_names.split()
#                     header_data = grb.header_data.split()
#
#                     meta_dict = {}
#                     for i in range(len(header_data)):
#                         meta_dict[header_names[i]] = int(header_data[i])
#
#                     time = (np.arange(meta_dict['npts']) - meta_dict['nlasc']) * 0.064
#
#                     if float(dur_dict[burst_num]['t90']) < 4:
#                         add_time = 8
#                     else:
#                         add_time = float(dur_dict[burst_num]['t90']) * add_time_mult
#
#                     try:
#                         time_start = (float(dur_dict[burst_num]['t90_start']) - float(
#                             dur_dict[burst_num]['t90_err']) - add_time)
#                     except:
#                         time_start = min(time) + ((dur_dict[burst_num]['t90_start'] - min(time)) / 2)
#
#                     try:
#                         time_end = (float(dur_dict[burst_num]['t90_start']) + float(
#                             dur_dict[burst_num]['t90']) + add_time + float(dur_dict[burst_num]['t90_err']))
#                     except:
#                         time_start = max(time) - ((max(time) - dur_dict[burst_num]['t90_end']) / 2)
#
#                     trimmed_background, trimmed_time = fix_background(burst_data, time, time_start, time_end, add_time)
#
#                     background_mean = np.mean(trimmed_background)
#                     peak_flux = np.max(burst_data)
#
#                     signal_to_noise = (peak_flux - background_mean) / np.sqrt(peak_flux)
#
#                     # remove bursts with missing data
#                     if min(trimmed_background) == 0:
#                         next
#                     else:
#
#                         slope, intercept, r_value, p_value, std_err = stats.linregress(trimmed_time, trimmed_background)
#
#                         if len(trimmed_time > 5):
#
#                             if str(slope) == 'nan':
#                                 print(burst_num, 'slope = nan')
#                             else:
#                                 writer.writerow({
#                                     'burst_num': burst_num,
#                                     'slope': slope,
#                                     'intercept': intercept,
#                                     'r_value': r_value,
#                                     'p_value': p_value,
#                                     'std_err': std_err,
#                                     'min_time': min(trimmed_time),
#                                     'max_time': max(trimmed_time),
#                                     'signal_to_noise': signal_to_noise
#                                 })
#                                 print(burst_num, 'success')
#                         else:
#                             print(burst_num, 'NOT enough points')
#
#                         # plt.plot(time,burst_data)
#                         # plt.plot(trimmed_time,trimmed_background)
#                         # plt.plot(time,burst_data-intercept-(time*slope))
#                         # plt.show()
#
#                 except Exception as err:
#                     print(burst_num, 'FAILURE - burst:', err)
#                     next