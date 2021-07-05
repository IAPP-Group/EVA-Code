#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import collections
import glob
import json
import os
import pickle
import re
import xmltodict

from common_defs import MANIPULATION_CLASSES, SOCIAL_CLASSES


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
    parser.add_argument('--keep-final-number', action='store_true')
    parser.add_argument('containers_path')
    parser.add_argument('output_path')

    return parser


def main(args):
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

                if video_name not in valid_videos_names:
                    continue

                with open(os.path.join(xmls_dir, xml_name), 'rb') as stream:
                    data = xmltodict.parse(stream, xml_attribs=True)

                manip_sequences[device_id].append(
                        list(paths_iterator(data, args.keep_final_number)))

            if manip_class.startswith('ffmpeg'):
                if 'ffmpeg' not in social_sequences:
                    social_sequences['ffmpeg'] = manip_sequences
                else:
                    for k in device_ids:
                        social_sequences['ffmpeg'][k].extend(manip_sequences[k])
            else:
                social_sequences[manip_class] = manip_sequences

        sequences[social_class] = social_sequences

    with open(args.output_path, 'wb') as stream:
        pickle.dump(sequences, stream, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
