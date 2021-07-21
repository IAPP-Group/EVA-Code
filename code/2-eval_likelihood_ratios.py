#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import math
import os
import pickle

from common_defs import BRANDS_FOR_DEVICES, find_all_symbols, \
        find_device_ids, get_info_for_device


def get_freqs(sequences, all_symbols, excluded_device=None, chosen_os=None):
    total_sequences = 1

    freqs = {sym: 1 for sym in all_symbols}

    for device_id, device_sequences in sequences.items():
        if device_id == excluded_device:
            continue

        if chosen_os is not None:
            dev_brand, dev_os = get_info_for_device(device_id)
            if dev_os != chosen_os:
                continue

        for sequence in device_sequences:
            total_sequences += 1
            for sym in set(sequence):
                freqs[sym] += 1

    for sym in all_symbols:
        freqs[sym] /= total_sequences

    return freqs


def get_ratio(freqs1, freqs2, all_symbols):
    ratios = []
    for k in all_symbols:
        sym_ratio = math.log10(freqs1[k]) - math.log10(freqs2[k])
        ratios.append((k, sym_ratio))
    ratios.sort(key=lambda x: -x[1])
    return ratios


def extract_ratios(sequences, excluded_device=None):
    if excluded_device:
        filter_devices = lambda x: x != excluded_device
    else:
        filter_devices = None

    all_symbols = find_all_symbols(sequences, filter_devices=filter_devices)
    all_classes = []
    all_ratios = {}

    for social_class, social_sequences in sequences.items():
        for manip_class, manip_sequences in social_sequences.items():
            all_classes.append((social_class, manip_class))

    for i, (social1, manip1) in enumerate(all_classes):
        for j, (social2, manip2) in enumerate(all_classes):
            if i >= j:
                continue

            freqs1 = get_freqs(sequences[social1][manip1], all_symbols,
                    excluded_device)
            freqs2 = get_freqs(sequences[social2][manip2], all_symbols,
                    excluded_device)
            ratios = get_ratio(freqs1, freqs2, all_symbols)

            class_idx1 = all_classes.index((social1, manip1))
            class_idx2 = all_classes.index((social2, manip2))
            all_ratios[(class_idx1, class_idx2)] = ratios

    return all_symbols, all_classes, all_ratios


def extract_ratios_os(sequences, excluded_device=None):
    if excluded_device:
        filter_devices = lambda x: x != excluded_device
    else:
        filter_devices = None

    all_symbols = find_all_symbols(sequences, filter_devices=filter_devices)
    all_classes = []
    all_ratios = {}

    for social_class, social_sequences in sequences.items():
        for manip_class, manip_sequences in social_sequences.items():
            all_classes.append(('Android', social_class, manip_class))
            all_classes.append(('iOS', social_class, manip_class))

    for i, (os1, social1, manip1) in enumerate(all_classes):
        for j, (os2, social2, manip2) in enumerate(all_classes):
            if i >= j:
                continue

            freqs1 = get_freqs(sequences[social1][manip1], all_symbols,
                    excluded_device, os1)
            freqs2 = get_freqs(sequences[social2][manip2], all_symbols,
                    excluded_device, os2)
            ratios = get_ratio(freqs1, freqs2, all_symbols)

            class_idx1 = all_classes.index((os1, social1, manip1))
            class_idx2 = all_classes.index((os2, social2, manip2))
            all_ratios[(class_idx1, class_idx2)] = ratios

    return all_symbols, all_classes, all_ratios


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-os-info', action='store_true')
    parser.add_argument('dataset_path')
    parser.add_argument('output_path')

    return parser


def main(args):
    with open(args.dataset_path, 'rb') as stream:
        sequences = pickle.load(stream)

    all_symbols = find_all_symbols(sequences)

    all_classes = []

    all_ratios = {}

    os.makedirs(args.output_path, exist_ok=True)

    if args.use_os_info:
        for device_id in find_device_ids(sequences):
            print("Device ID: {}".format(device_id))
            symbols, classes, ratios = extract_ratios_os(sequences, device_id)
            result = (symbols, classes, ratios)

            result_path = os.path.join(args.output_path,
                    '{}-lr-os.pkl'.format(device_id))

            with open(result_path, 'wb') as stream:
                pickle.dump(result, stream, pickle.HIGHEST_PROTOCOL)

    else:
        for device_id in find_device_ids(sequences):
            print("Device ID: {}".format(device_id))
            symbols, classes, ratios = extract_ratios(sequences, device_id)
            result = (symbols, classes, ratios)

            result_path = os.path.join(args.output_path,
                    '{}-lr.pkl'.format(device_id))

            with open(result_path, 'wb') as stream:
                pickle.dump(result, stream, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
