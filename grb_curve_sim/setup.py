#!/usr/bin/env python3
"""
Usage: ETL_example.py (--experiment=<string>) (--data_dir=<string>) (--background_file)

Options:
  --experiment <string>         # experiment name. ex. batse
  --data_dir <string>           # data directory. ex. filepath/for/your/data
  --background_file             # boolean to produce background file.

# Sample Call from repo root:
# BATSE:        python3 grb-lightcurve-similarity/setup.py --experiment=batse --data_dir='<<filepath/for/your/data>>'
"""

import urllib.request
import tarfile
import os, sys
import configparser
from grbpy.batse import BATSEDurations
from batse_utils import calc_64ms_background

config = configparser.ConfigParser()


def run_setup(experiment, data_dir, background_file):

    # config['data'] = {'data_dir': '/home/thomas/git/Research/data/GRB'}
    #
    # with open('grb_curve_sim.conf', 'w') as configfile:
    #     config.write(configfile)
    #
    # if not os.path.exists(data_dir):
    #     print(f'Setting up data directory: {data_dir}')
    #     os.makedirs(data_dir)
    #
    # if experiment.lower() == 'batse':
    #     batse_remote_64ms_dir = 'https://heasarc.gsfc.nasa.gov/FTP/compton/data/batse/ascii_data/64ms/compressed/'
    #
    #     batse_local_dir = os.path.join(data_dir, 'batse')
    #
    #     if not os.path.exists(batse_local_dir):
    #         print(f'Setting up BATSE directory: {batse_local_dir}')
    #         os.makedirs(batse_local_dir)
    #
    #     # Getting burst basic data
    #     batse_basic_local_file = os.path.join(batse_local_dir, 'basic_table.txt')
    #     batse_basic_remote_file = 'https://gammaray.nsstc.nasa.gov/batse/grb/catalog/current/tables/basic_table.txt'
    #     print(f'Downloading file: {batse_basic_remote_file}')
    #     urllib.request.urlretrieve(f'{batse_basic_remote_file}', batse_basic_local_file)
    #
    #     # Getting burst duration data
    #     batse_duration_local_file = os.path.join(batse_local_dir, 'duration_table.txt')
    #     batse_duration_remote_file = 'https://gammaray.nsstc.nasa.gov/batse/grb/catalog/current/tables/duration_table.txt'
    #     print(f'Downloading file: {batse_duration_remote_file}')
    #     urllib.request.urlretrieve(f'{batse_duration_remote_file}', batse_duration_local_file)
    #
    #     # Getting burst 64ms data
    #     batse_local_64ms_dir = os.path.join(batse_local_dir, '64ms')
    #     if not os.path.exists(batse_local_64ms_dir):
    #         print(f'Setting up BATSE 64ms Data in directory: {batse_local_64ms_dir}')
    #         os.makedirs(batse_local_64ms_dir)
    #     for i in range(0, 9):
    #         batse_64ms_remote_file = f'trig0{i}000.tar.gz'
    #         print(f'Downloading file: {batse_64ms_remote_file}')
    #         local_file = os.path.join(batse_local_64ms_dir, batse_64ms_remote_file)
    #         urllib.request.urlretrieve(f'{batse_remote_64ms_dir}/{batse_64ms_remote_file}', local_file)
    #
    #         print(f'Extracting file: {local_file}')
    #         tar_file = tarfile.open(local_file)
    #         tar_file.extractall(batse_local_64ms_dir)
    #
    #         print(f'Removing file: {local_file}')
    #         os.remove(local_file)
    batse_local_dir = os.path.join(data_dir, 'batse')
    batse_duration_local_file = os.path.join(batse_local_dir, 'duration_table.txt')
    batse_local_64ms_dir = os.path.join(batse_local_dir, '64ms')

    if background_file:
        print(f'Building BATSE background file from {batse_duration_local_file}')
        durations = BATSEDurations(file_path=batse_duration_local_file)
        durations.parse_file()
        for burst in durations.dur_data['trig_num'].unique():
            if int(burst) > 3115:
                calc_64ms_background(file_path=os.path.join(batse_local_64ms_dir, f'cat64ms.{str(burst).zfill(5)}'),
                                     duration=durations.dur_data.loc[durations.dur_data['trig_num'] == burst])
            # sys.exit()

    with open('grb_curve_sim.conf', 'w') as configfile:
        config.write(configfile)


def main():
    """Parse arguments and run"""
    from docopt import docopt
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)

    run_setup(
        experiment=args['--experiment'],
        data_dir=args['--data_dir'],
        background_file=args['--background_file'],
    )


if __name__ == '__main__':
    main()
