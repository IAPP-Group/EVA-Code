#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import math
import os
import pickle

from bokeh import colors
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, save

import numpy as np

from sklearn.metrics import confusion_matrix

from common_defs import get_likelihood_symbols


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('lr_path')
    parser.add_argument('output_path')

    return parser


def main(args):
    devices = [x[:3] for x in os.listdir(args.lr_path)]

    for device_id in devices:
        print("Processing device {}".format(device_id))
        device_path = os.path.join(args.output_path, device_id)
        os.makedirs(device_path, exist_ok=True)

        input_path = os.path.join(args.lr_path, '{}-lr.pkl'.format(device_id))
        all_symbols, all_classes, all_ratios = \
                get_likelihood_symbols(input_path)
        all_symbols = set(all_symbols)

        for (cls_id1, cls_id2), ratios in all_ratios.items():
            cls1, cls2 = all_classes[cls_id1], all_classes[cls_id2]
            cls_name1, cls_name2 = '-'.join(cls1), '-'.join(cls2)
            out_name = '{}_vs_{}.html'.format(cls_name1, cls_name2)
            out_path = os.path.join(device_path, out_name)
            out_name_log = '{}_vs_{}.txt'.format(cls_name1, cls_name2)
            out_path_log = os.path.join(device_path, out_name_log)

            valid_ratios = [(k, v) for k, v in ratios
                    if v <= -math.log10(10) or v >= math.log10(10)]
            valid_ratios.sort(key=lambda x: x[1])

            with open(out_path_log, 'w') as stream:
                for sym, ratio in valid_ratios:
                    stream.write('{:7.4f} {}\n'.format(ratio, sym))

            if len(valid_ratios) == 0:
                print("WARNING: empty symbols set for {} vs {} ({})".format(
                    cls_name1, cls_name2, device_id))
                continue
            else:
                print("{} vs {}: {} symbols over threshold".format(
                    cls_name1, cls_name2, len(valid_ratios)))

            keys = [x[0] for x in valid_ratios]
            values = [x[1] for x in valid_ratios]

            p = figure(title='{} vs {}'.format(cls_name1, cls_name2),
                    tools='save',
                    y_range=keys, x_range=[min(values) - 1, max(values) + 1],
                    tooltips=[
                        ('Ratio', '@values{0.00}'),
                    ])
            p.plot_width = 1024
            p.plot_height = 768
            p.output_backend = 'svg'
            data = ColumnDataSource(data=dict(
                keys=keys,
                values=values,
            ))
            p.segment(0, 'keys', 'values', 'keys', line_width=1, source=data)
            p.circle('values', 'keys', size=10, source=data)
            p.segment(0, [keys[0]], 0, [keys[-1]], line_color='red')
            output_file(out_path, title="Likelihood Ratio")
            save(p)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
