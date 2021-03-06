#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Universit√† degli studi di Firenze

import argparse
import os
import pickle

from sklearn.metrics import accuracy_score, classification_report, \
        confusion_matrix

from common_defs import find_all_symbols, find_device_ids, get_classifier, \
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

    for manip_name in dataset['non-SN'].keys():
        if args.use_os_info:
            chosen_classes.append('Android-{}'.format(manip_name))
            chosen_classes.append('iOS-{}'.format(manip_name))
        else:
            chosen_classes.append(manip_name)

    sn_classes = set()

    for key in dataset.keys():
        if key == 'non-SN':
            continue
        chosen_classes.append(key)
        sn_classes.add(key)

    run_symbols = {}
    classifiers = {}
    y_true = {}
    y_pred = {}

    for test_device_id in device_ids:
        print("Testing device {}".format(test_device_id))

        if args.likelihood_ratios_path is not None:
            lr_path = os.path.join(args.likelihood_ratios_path,
                    '{}-lr{}.pkl'.format(test_device_id,
                        '-os' if args.use_os_info else ''))

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
                    if social_name in sn_classes:
                        videos_class = social_name
                    elif args.use_os_info:
                        device_brand, device_os = \
                                get_info_for_device(device_id)
                        videos_class = '{}-{}'.format(device_os, manip_name)
                    else:
                        videos_class = manip_name

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

        clf = get_classifier()
        clf.fit(train_xs, train_ys)

        run_symbols[test_device_id] = chosen_symbols
        classifiers[test_device_id] = clf
        y_true[test_device_id] = test_ys
        y_pred[test_device_id] = clf.predict(test_xs)

    os.makedirs(args.output_path, exist_ok=True)
    output_path = os.path.join(args.output_path, 'blind.pkl')

    result = (chosen_classes, run_symbols, classifiers, y_true, y_pred)
    with open(output_path, 'wb') as stream:
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
