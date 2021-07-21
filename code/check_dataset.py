#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import json
import os

from common_defs import MANIPULATION_CLASSES, SOCIAL_CLASSES


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('containers_path')

    return parser


def main(args):
    index_path = os.path.join(args.containers_path, 'index.json')

    with open(index_path, 'r') as stream:
        index = json.load(stream)

    device_ids = set(x[:3] for x in index)
    device_ids = list(sorted(device_ids))

    for social in SOCIAL_CLASSES:
        social_path = os.path.join(args.containers_path, social)

        for manip in MANIPULATION_CLASSES:
            manip_path = os.path.join(social_path, manip)

            this_index = set(index)

            for filename in os.listdir(manip_path):
                video_id = filename[:filename.index('.')]
                if video_id in this_index:
                    this_index.remove(video_id)

            if len(this_index) > 0:
                print("Warning: {}/{} is missing the following videos:".format(
                    social, manip))
                for item in this_index:
                    print("- {}".format(item))



if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())
