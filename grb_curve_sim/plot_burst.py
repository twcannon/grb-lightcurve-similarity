#!/usr/bin/env python3
from grbpy.batse import BATSEBurst
import matplotlib.pyplot as plt
import csv
import os
import sys
import numpy as np
from file_utils import grb_config
import sys
'''this is just a quick script to show plots of GRBs
with the option to add buffers

to run:
python3 -m grb_curve_sim.plot_burst.py
python3 grb_curve_sim/plot_burst.py'''

DATA_DIR = grb_config.get('data', 'data_dir')
BATSE64MS_DIR = os.path.join(DATA_DIR, 'batse', '64ms')

print(BATSE64MS_DIR)

# dur_dict = {}
# with open(os.path.join(DATA_DIR, 'duration_table.txt'), newline='') as f:
#     for row in csv.DictReader(f, delimiter=','):
#         dur_dict[str(row['trig'])] = row
#
# background_dict = {}
# with open(os.path.join(DATA_DIR, 'background_table.txt'), newline='') as f:
#     for row in csv.DictReader(f, delimiter=','):
#         background_dict[str(row['burst_num'])] = row
#
# burst_dict = {}
# with open(os.path.join(DATA_DIR, 'burst_info.csv'), newline='') as f:
#     for row in csv.DictReader(f, delimiter=','):
#         burst_dict[str(row['burst_num'])] = row


def remove_background(background_dict, burst_data, time):
    return burst_data - float(background_dict['intercept']) - (time * float(background_dict['slope']))


def norm_time(time):
    return (time - min(time)) / (max(time) - min(time))


def norm_data(data):
    return data / max(data)


def get_burst_data(burst_num):
    file_path = os.path.join(BATSE64MS_DIR, f'cat64ms.{str(burst_num).zfill(5)}')
    grb = BATSEBurst(file_path=file_path, time_signature='64ms')
    grb.parse_file()

    burst_data = grb.chan_data
    header_names = grb.header_names.split()
    header_data = grb.header_data.split()

    meta_dict = {}
    for i in range(len(header_data)):
        meta_dict[header_names[i]] = int(header_data[i])

    time = (np.arange(meta_dict['npts']) - meta_dict['nlasc']) * 0.064
    # t90 = float(dur_dict[burst_num]['t90'])
    # t90_start = float(dur_dict[burst_num]['t90_start'])
    # t90_end = float(dur_dict[burst_num]['t90_start']) + t90

    return time, burst_data#, t90_start, t90_end, t90


# burst_dict = {}

# with open(os.path.join('data','burst_info.csv'), newline='') as burstfile:
#     base_path = os.path.join('..','batse_data')
#     # burst_num,burst_path,single_emission

#     for row in csv.DictReader(burstfile, delimiter=','):
#         burst_dict[int(row['burst_num'])] = row['burst_path']

# EUCLIDEAN
# euclid no buffer
# euclid
# generally euclidean does not perform well. because it was not normalized,
# it clusters together bursts that fit together well and also have large vectors
# burst_list = [2824,7924,2061,3248] # ????
# burst_list = [7548,5895,3056] # not bad
# burst_list = [6313,1467,7711] # Single
# burst_list = [3003,1085,1956] # single plus ???
# burst_list = [3212,841,7250,3048] # kind of...
# burst_list = [5563,6814,3345] # ok
# burst_list = [3131,3649,676,1982] # single but wrong


# ZNCC
# corr
# corr no buffer
# THIS IS NONSENSE
# burst_list = [6662,845,6219,6598] # single
# burst_list = [3779,2484,3908] # single
# burst_list = [7798,7984,5704] # ??????
# burst_list = [6300,5716,7741] # ?????
# burst_list = [6615,7674,2961] # ?????
# burst_list = [7576,1714,2812] # ?????
# burst_list = [8062,6303,3336] # ?????


# DTW
# dtw
# burst_list = [8105,2405] #
# burst_list = [6745,5572,5539] #
# burst_list = [3028,1042,6582] #
# burst_list = [3256,3886,1204] #
# burst_list = [105,5711,3138] # ????
# burst_list = [5530,4569,1114] # ????
# burst_list = [2728,1443] #

# burst_list = [1953,108,3160,2844,6412,2283] #
# burst_list = [559,1196,7608,5723] #
# burst_list = [1625,2897,1652,3905,3253] #
# burst_list = [4556,5567,3491,1085,6100] #
burst_list = [3936, 2728, 1443, 711]  #

# MANHATTAN
# norm
# burst_list = [7028,7781,7172,5470,2367] #
# burst_list = [5517,6708,1733,5545] #
# burst_list = [5719,3870,7374,3906] #
# burst_list = [2533,7932,2329,6763] #


# burst_list = [7581,5716,3523,7028] # for example bursts plot in paper

# TITLE
# plt.suptitle('DTW Cluster Examples - Normalized Emissions')

# plot type :: 'horizontal', 'stacked', 'single'
plot_type = 'stacked'

i = 0
for burst_num in burst_list:
    # for burst_num in burst_dict:

    i += 1
    # time, burst_data, t90_start, t90_end, t90 = get_burst_data(str(burst_num))
    time, burst_data = get_burst_data(str(burst_num))

    # # plt.title('Raw Burst Data')
    # t90_buffer = (2.5 * t90)
    # burst_data = remove_background(background_dict[str(burst_num)], burst_data, time)
    # burst_data = norm_data(burst_data[(time > float(t90_start) - t90_buffer) & (time < float(t90_end) + t90_buffer)])
    # time = norm_time(time[(time > float(t90_start) - t90_buffer) & (time < float(t90_end) + t90_buffer)])
    # plt.title('Normalized Emissions')

    if plot_type == 'horizontal':
        grid = plt.GridSpec(1, len(burst_list))
        if i == 1:
            plt.subplot(grid[0, i - 1])
        else:
            plt.subplot(grid[0, i - 1]).axes.get_yaxis().set_visible(False)

    elif plot_type == 'stacked':
        if len(burst_list) == 1:
            continue
        elif len(burst_list) == 2:
            plt.subplot(210 + i)
        elif len(burst_list) == 3:
            grid = plt.GridSpec(2, 2)
            if i != 3:
                plt.subplot(grid[0, i - 1])
            else:
                plt.subplot(grid[1, :2])
        elif len(burst_list) == 4:
            plt.subplot(220 + i)
        elif len(burst_list) == 5:
            grid = plt.GridSpec(3, 2)
            if i in [1, 2]:
                plt.subplot(grid[0, i - 1])
            elif i in [3, 4]:
                plt.subplot(grid[1, i - 3])
            else:
                plt.subplot(grid[2, :2])
        elif len(burst_list) == 6:
            plt.subplot(230 + i)
        else:
            print('too many bursts')
            break

    elif plot_type == 'single':
        next

    else:
        print('unsupported plot type')

    # plt.plot(time,burst_data, label='Burst '+str(burst_num))
    # plt.legend()
    # plt.ylim(-0.1, 1.1)
    plt.title('Burst - ' + str(burst_num))
    print(time)
    print(burst_data)
    plt.plot(time, burst_data)

plt.show()
