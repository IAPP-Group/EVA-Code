# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import math
import pickle

from sklearn.tree import DecisionTreeClassifier


SOCIAL_CLASSES = ["Facebook", "Tiktok", "Weibo", "Youtube", "non-SN"]

MANIPULATION_CLASSES = ['avidemux', 'exiftool', 'ffmpeg1', 'ffmpeg2',
        'ffmpeg3', 'ffmpeg4', 'ffmpeg5', 'kdenlive', 'native', 'premiere']

BRANDS_FOR_DEVICES = {
    'D01': 'Samsung',
    'D02': 'Apple',
    'D03': 'Huawei',
    'D04': 'LG',
    'D05': 'Apple',
    'D06': 'Apple',
    'D07': 'Lenovo',
    'D08': 'Samsung',
    'D09': 'Apple',
    'D10': 'Apple',
    'D11': 'Samsung',
    'D12': 'Sony',
    'D13': 'Apple',
    'D14': 'Apple',
    'D15': 'Apple',
    'D16': 'Huawei',
    'D17': 'Microsoft',
    'D18': 'Apple',
    'D19': 'Apple',
    'D20': 'Apple',
    'D21': 'Wiko',
    'D22': 'Samsung',
    'D23': 'Asus',
    'D24': 'Xiaomi',
    'D25': 'Oneplus',
    'D26': 'Samsung',
    'D27': 'Samsung',
    'D28': 'Huawei',
    'D29': 'Apple',
    'D30': 'Huawei',
    'D31': 'Samsung',
    'D32': 'Oneplus',
    'D33': 'Huawei',
    'D34': 'Apple',
    'D35': 'Samsung',
}


def find_all_symbols(dataset, filter_socials=None, filter_manipulations=None,
        filter_devices=None):
    all_symbols = set()

    for social_class, social_sequences in dataset.items():
        if filter_socials is not None and not filter_socials(social_class):
            continue

        for manip_class, manip_sequences in social_sequences.items():
            if filter_manipulations is not None and \
                    not filter_manipulations(manip_class):
                continue

            for device_id, device_sequences in manip_sequences.items():
                if filter_devices is not None and \
                        not filter_devices(device_id):
                    continue

                for sequence in device_sequences:
                    all_symbols.update(sequence)

    all_symbols = list(all_symbols)
    all_symbols.sort()

    return all_symbols


def find_device_ids(dataset):
    device_ids = set()

    for social_class, social_sequences in dataset.items():
        for manip_class, manip_sequences in social_sequences.items():
            for device_id, device_sequences in manip_sequences.items():
                device_ids.add(device_id)

    return device_ids


def get_info_for_device(device_id):
    brand = BRANDS_FOR_DEVICES[device_id]

    if brand == 'Apple':
        return brand, 'iOS'
    elif brand == 'Microsoft':
        return brand, 'WindowsMobile'
    else:
        return brand, 'Android'


def get_likelihood_symbols(lr_path):
    with open(lr_path, 'rb') as stream:
        all_symbols, all_classes, all_ratios = pickle.load(stream)

    return all_symbols, all_classes, all_ratios


def load_likelihood_data(lr_path, use_os_info):
    with open(lr_path, 'rb') as stream:
        all_symbols, all_classes, all_ratios = pickle.load(stream)

    chosen_symbols = set()

    if use_os_info:
        assert all(len(c) == 3 for c in all_classes)
    else:
        assert all(len(c) == 2 for c in all_classes)

    for ratio_key, ratio_values in all_ratios.items():

        for sym, sym_lr in ratio_values:
            if sym_lr <= -math.log10(2) or sym_lr >= math.log10(2):
                chosen_symbols.add(sym)

    return chosen_symbols


def get_video_data(sequence, chosen_symbols):
    result = [0] * len(chosen_symbols)

    symbols_set = set(sequence)

    for i, sym in enumerate(chosen_symbols):
        if sym in symbols_set:
            result[i] = 1

    return result


def get_classifier():
    return DecisionTreeClassifier(class_weight='balanced', min_samples_leaf=12)
