#!/usr/bin/env python3
"""
Usage: calc_background.py [options]

Options:
  --experiment <string>         # experiment name. ex. batse
  --data_dir <string>           # data directory. ex. filepath/for/your/data
  --time_sig <string>           # time signature for experiment data. ex. 64ms
  --trig_num <string>           # burst id. ex. 512

# Sample Call from repo root:
# BATSE:        python3 grb-lightcurve-similarity/calc_background.py --experiment=batse
#                   --data_dir='<<filepath/for/your/data>>' --time_signature='64ms' --trig_num=512
"""

import os
from grbpy.batse import BATSEDurations
from batse_utils import calc_64ms_background


def calc_background(experiment, time_sig, data_dir, trig_num):
    local_dir = os.path.join(data_dir, experiment)

    if experiment == 'batse':
        if time_sig == '64ms':
            batse_duration_local_file = os.path.join(local_dir, 'duration_table.txt')
            batse_local_64ms_dir = os.path.join(local_dir, '64ms')
            print(f'Building BATSE background file from {batse_duration_local_file}')
            durations = BATSEDurations(file_path=batse_duration_local_file)
            durations.parse_file()
            if trig_num in durations.dur_data['trig_num'].unique():
                calc_64ms_background(file_path=os.path.join(batse_local_64ms_dir, f'cat64ms.{str(trig_num).zfill(5)}'),
                                     duration=durations.dur_data.loc[durations.dur_data['trig_num'] == trig_num],
                                     trig_num=trig_num)
            else:
                print(f'Trigger number {trig_num} not in duration table')


def main():
    """Parse arguments and run"""
    from docopt import docopt
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)

    calc_background(
        experiment=args['--experiment'],
        time_sig=args['--time_sig'],
        data_dir=args['--data_dir'],
        trig_num=int(args['--trig_num']),
    )


if __name__ == '__main__':
    main()
