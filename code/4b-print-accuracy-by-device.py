#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import pickle

from sklearn.metrics import accuracy_score


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path')

    return parser


def main(args):
    with open(args.experiment_path, 'rb') as stream:
        all_labels, run_symbols, classifiers, y_true, y_pred = \
                pickle.load(stream)

    device_ids = list(sorted(classifiers.keys()))

    results = []

    for device_id in device_ids:
        results.append((device_id,
            accuracy_score(y_true[device_id], y_pred[device_id])))

    results.sort(key=lambda x: x[1])

    for device_id, acc in results:
        print("{:3s}: {:0.2f}".format(device_id, acc))


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
