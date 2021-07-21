#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import os
import pickle

from matplotlib.pyplot import savefig
from sklearn.tree import export_graphviz

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('exp_path')
    parser.add_argument('output_path')

    return parser

def main(args):
    with open(args.exp_path, 'rb') as stream:
        chosen_classes, run_symbols, classifiers, y_true, y_pred = pickle.load(stream)

    device_ids = list(sorted(classifiers.keys()))

    os.makedirs(args.output_path, exist_ok=True)

    for device_id in device_ids:
        clf = classifiers[device_id]
        fig_path = os.path.join(args.output_path, device_id + '.dot')
        export_graphviz(clf, out_file=fig_path,
                feature_names=run_symbols[device_id],
                class_names=chosen_classes)

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
