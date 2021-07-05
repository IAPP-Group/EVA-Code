#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import os
import pickle

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

from common_defs import find_all_symbols, find_device_ids, \
        get_info_for_device, get_video_data, load_likelihood_data


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--likelihood-ratios-path', type=str, default=None)
    parser.add_argument('--use-os-info', action='store_true')
    parser.add_argument('dataset_path')
    parser.add_argument('output_path')

    return parser


def main(args):
    with open(args.dataset_path, 'rb') as stream:
        dataset = pickle.load(stream)

    device_ids = list(sorted(find_device_ids(dataset)))

    chosen_classes = []

    if args.use_os_info:
        chosen_classes.append('Android-Native')
        chosen_classes.append('iOS-Native')
        chosen_classes.append('Android-Tampered')
        chosen_classes.append('iOS-Tampered')
        chosen_classes.append('Android-Native-YouTube')
        chosen_classes.append('iOS-Native-YouTube')
        chosen_classes.append('Android-Tampered-YouTube')
        chosen_classes.append('iOS-Tampered-YouTube')
    else:
        chosen_classes.append('Native')
        chosen_classes.append('Tampered')
        chosen_classes.append('Native-YouTube')
        chosen_classes.append('Tampered-YouTube')

    run_symbols = {}
    classifiers = {}
    y_true = {}
    y_pred = {}

    for test_device_id in device_ids:
        print("Testing device {}".format(test_device_id))

        if args.likelihood_ratios_path is not None:
            lr_path = os.path.join(args.likelihood_ratios_path,
                    '{}-lr.pkl'.format(test_device_id))

            chosen_symbols = load_likelihood_data(lr_path, args.use_os_info)
        else:
            chosen_symbols = find_all_symbols(dataset,
                    filter_devices=lambda x: x != test_device_id)

        chosen_symbols = list(chosen_symbols)
        chosen_symbols.sort()

        train_xs = []
        train_ys = []
        test_xs = []
        test_ys = []

        for social_name, social_sequences in dataset.items():
            for manip_name, manip_sequences in social_sequences.items():
                for device_id, device_sequences in manip_sequences.items():
                    if args.use_os_info:
                        device_brand, device_os = get_info_for_device(device_id)
                        if manip_name == 'native':
                            videos_class = '{}-Native'.format(device_os)
                        else:
                            videos_class = '{}-Tampered'.format(device_os)
                    else:
                        if manip_name == 'native':
                            videos_class = 'Native'
                        else:
                            videos_class = 'Tampered'

                    if social_name == 'After-YouTube':
                        videos_class += '-YouTube'

                    for device_sequence in device_sequences:
                        video_x = get_video_data(device_sequence,
                                chosen_symbols)
                        video_y = chosen_classes.index(videos_class)

                        if device_id == test_device_id:
                            test_xs.append(video_x)
                            test_ys.append(video_y)
                        else:
                            train_xs.append(video_x)
                            train_ys.append(video_y)

        clf = DecisionTreeClassifier(class_weight='balanced')
        clf.fit(train_xs, train_ys)

        run_symbols[test_device_id] = chosen_symbols
        classifiers[test_device_id] = clf
        y_true[test_device_id] = test_ys
        y_pred[test_device_id] = clf.predict(test_xs)

    result = (chosen_classes, run_symbols, classifiers, y_true, y_pred)
    with open(args.output_path, 'wb') as stream:
        pickle.dump(result, stream, pickle.HIGHEST_PROTOCOL)

    flat_y_true = []
    flat_y_pred = []
    for device_id in device_ids:
        flat_y_true.extend(y_true[device_id])
        flat_y_pred.extend(y_pred[device_id])

    print("Confusion matrix")
    print(confusion_matrix(flat_y_true, flat_y_pred))

    print(classification_report(flat_y_true, flat_y_pred,
        target_names=chosen_classes))


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
