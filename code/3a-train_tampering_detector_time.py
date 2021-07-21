#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import collections
import json
import math
import os
import pickle
import re
import time

from sklearn.metrics import accuracy_score, classification_report, \
        confusion_matrix
import xmltodict

from common_defs import find_all_symbols, find_device_ids, get_classifier, \
        get_info_for_device, get_video_data, load_likelihood_data
from common_defs import MANIPULATION_CLASSES, SOCIAL_CLASSES


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


FINAL_NUMBER_RE = re.compile(r"-\d+$")

IGNORED_SYMBOLS = set([
    '@author', '@count', '@creationTime', '@depth', '@duration', '@entryCount',
    '@entryCount', '@flags', '@gpscoords', '@matrix', '@modelName',
    '@modificationTime', '@name', '@sampleCount', '@segmentDuration', '@size',
    '@stuff', '@timescale', '@version', '@width', '@height', '@language'
])


def paths_iterator(xml_dict_data, keep_final_number, current_path=[]):
    for key, value in xml_dict_data.items():
        if isinstance(value, dict):
            if keep_final_number:
                filtered_key = key
            else:
                filtered_key = FINAL_NUMBER_RE.sub('', key)
            for item in paths_iterator(value, keep_final_number,
                    current_path + [filtered_key]):
                yield item
        else:
            yield "/".join(current_path + [f"{key}"])
            if key not in IGNORED_SYMBOLS:
                yield "/".join(current_path + [f"{key}={value}"])

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--likelihood-ratios-path', type=str, default=None)
    parser.add_argument('--use-os-info', action='store_true')
    parser.add_argument('containers_path')

    return parser


def load_dataset(containers_path, only_device=None):
    index_path = os.path.join(args.containers_path, 'index.json')

    with open(index_path, 'r') as stream:
        valid_videos_names = set(json.load(stream))

    print("Total videos in index: {}".format(len(valid_videos_names)))

    videos_by_device = collections.defaultdict(list)

    for video_name in valid_videos_names:
        videos_by_device[video_name[:3]].append(video_name)

    videos_by_device = dict(videos_by_device)
    device_ids = set(videos_by_device.keys())

    for device_id, videos in videos_by_device.items():
        print("- {:3s}: {} videos".format(device_id, len(videos)))

    sequences = {}

    for social_class in SOCIAL_CLASSES:
        social_sequences = {}

        for manip_class in MANIPULATION_CLASSES:
            manip_sequences = {device_id: [] for device_id in device_ids}

            print("Parsing {}/{} containers...".format(social_class, manip_class))

            xmls_dir = os.path.join(args.containers_path, social_class,
                    manip_class)

            for xml_name in os.listdir(xmls_dir):
                video_name = xml_name[:xml_name.index('.')]
                device_id = video_name[:3]
                if only_device is not None and device_id != only_device:
                    continue

                if video_name not in valid_videos_names:
                    continue

                with open(os.path.join(xmls_dir, xml_name), 'rb') as stream:
                    data = xmltodict.parse(stream, xml_attribs=True)

                manip_sequences[device_id].append(
                        list(paths_iterator(data, False)))

            if manip_class.startswith('ffmpeg'):
                if 'ffmpeg' not in social_sequences:
                    social_sequences['ffmpeg'] = manip_sequences
                else:
                    for k in device_ids:
                        social_sequences['ffmpeg'][k].extend(manip_sequences[k])
            else:
                social_sequences[manip_class] = manip_sequences

        sequences[social_class] = social_sequences

    return sequences


def get_chosen_symbols(sequences, device_id):
    all_symbols = find_all_symbols(sequences)

    all_classes = []

    all_ratios = {}

    all_symbols, all_classes, all_ratios = extract_ratios(sequences, device_id)
    chosen_symbols = set()

    assert all(len(c) == 2 for c in all_classes)

    for ratio_key, ratio_values in all_ratios.items():

        for sym, sym_lr in ratio_values:
            if sym_lr <= -math.log10(2) or sym_lr >= math.log10(2):
                chosen_symbols.add(sym)

    return chosen_symbols


def main(args):
    start_time = time.time()

    dataset = load_dataset(args.containers_path)

    device_ids = list(sorted(find_device_ids(dataset)))

    chosen_classes = []

    if args.use_os_info:
        chosen_classes.append('Android-Native')
        chosen_classes.append('iOS-Native')
        chosen_classes.append('Android-Tampered')
        chosen_classes.append('iOS-Tampered')
    else:
        chosen_classes.append('Native')
        chosen_classes.append('Tampered')

    for social_name, social_sequences in dataset.items():
        if social_name != 'non-SN':
            continue

        print("Social network name: {}".format(social_name))

        run_symbols = {}
        classifiers = {}
        y_true = {}
        y_pred = {}

        test_device_id = 'D01'
        print("Testing device {}".format(test_device_id))

        if args.likelihood_ratios_path is not None:
            lr_path = os.path.join(args.likelihood_ratios_path,
                    '{}-lr{}.pkl'.format(test_device_id,
                        '-os' if args.use_os_info else ''))

            chosen_symbols = load_likelihood_data(lr_path, args.use_os_info)
            chosen_symbols = get_chosen_symbols(dataset, 'D01')
        else:
            chosen_symbols = find_all_symbols(dataset,
                    filter_devices=lambda x: x != test_device_id)

        chosen_symbols = list(chosen_symbols)
        chosen_symbols.sort()

        train_xs = []
        train_ys = []
        test_xs = []
        test_ys = []

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

                for device_sequence in device_sequences:
                    video_x = get_video_data(device_sequence, chosen_symbols)
                    video_y = chosen_classes.index(videos_class)

                    if device_id != test_device_id:
                        train_xs.append(video_x)
                        train_ys.append(video_y)

        clf = get_classifier()
        clf.fit(train_xs, train_ys)
        train_time = time.time()

        test_dataset = load_dataset(args.containers_path, 'D01')

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

                for device_sequence in device_sequences:
                    video_x = get_video_data(device_sequence, chosen_symbols)
                    video_y = chosen_classes.index(videos_class)

                    if device_id == test_device_id:
                        test_xs.append(video_x)
                        test_ys.append(video_y)

        run_symbols[test_device_id] = chosen_symbols
        classifiers[test_device_id] = clf
        y_true[test_device_id] = test_ys
        y_pred[test_device_id] = clf.predict(test_xs)
        test_time = time.time()

        print("Training time: {:.02f} - Test time: {:.02f}".format(
            train_time - start_time, test_time - train_time))


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
