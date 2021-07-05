#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import tempfile
import os
import subprocess
import csv
import datetime
from collections import defaultdict


subset_folders = ["subset_avidemux", "subset_ffmpeg1", "subset_ffmpeg3",
                  "subset_ffmpeg5", "subset_native", "subset_exiftool",
                  "subset_ffmpeg2", "subset_ffmpeg4", "subset_kdenlive",
                  "subset_premiere"]
modes = ["still", "move", "panrot"]
vid_metadata = ["File Name", "File Type", "Major Brand", "Make", "Model",
                "Software", "Com Android Version", "Compressor ID",
                "Video Frame Rate", "Pixel Aspect Ratio", "Media Duration",
                "Audio Format", "Audio Channels", "Audio Sample Rate",
                "Megapixels", "Image Size", "Rotation", "Create Date",
                "Modify Date", "GPS Position"]
extentions = ["MOV", "MP4", "3GP", "JPEG", "JPG", "PNG", "TIF", "TIFF"]
vid_metadata_sum = ["File Name", "File Type", "Major Brand", "Make", "Model",
                    "Software", "Com Android Version", "Compressor ID",
                    "Video Frame Rate", "Pixel Aspect Ratio", "Media Duration",
                    "Audio Format", "Audio Channels", "Audio Sample Rate",
                    "Megapixels", "Image Size", "Rotation",
                    "Create/Modify Date", "GPS Present"]
vid_remove_keys = ["File Name", "Video Frame Rate", "Media Duration",
                   "Create Date", "Modify Date", "GPS Position"]


def call_ffprobe(video_path):
    """ call ffprobe on video to get resolution """
    cmd_ffprobe_width = ["ffprobe", "-v", "error", "-show_entries", "stream=width", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    cmd_ffprobe_height = ["ffprobe", "-v", "error", "-show_entries", "stream=height", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    # video to analyse
    # process = subprocess.Popen(cmd_ffprobe_width, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = process.communicate()
    # sout = stdout.decode("utf-8").strip()
    # serr = stderr.decode("utf-8").strip()
    # print(sout)
    # print(serr)
    output_w = subprocess.check_output(cmd_ffprobe_width)
    ow = output_w.decode("utf-8").strip()
    output_h = subprocess.check_output(cmd_ffprobe_height)
    oh = output_h.decode("utf-8").strip()
    return (ow, oh)


def fromString2Dict(exiftool_data):
    """
    Shutter Speed                   : 1/33
    Create Date                     : 2017:02:27 17:38:23.94
    Date/Time Original              : 2017:02:27 17:38:23.94
    Modify Date                     : 2017:02:27 17:38:23.94
    Thumbnail Image                 : (Binary data 11961 bytes, use -b option to extract)
    Circle Of Confusion             : 0.005 mm
    Field Of View                   : 60.3 deg
    """
    list_data = exiftool_data.split('\n')
    mydict = {}
    for item in list_data:
        idx = item.find(":")
        tmp_key = item[:idx].strip()
        tmp_value = item[idx+1:].strip()
        mydict[tmp_key] = tmp_value
    return mydict


def getImportantMetadata(dict_data):
    result_list = []
    # determine if image or video
    if dict_data["File Type"].lower() != "jpeg":
        # this is a video
        for vid_item in vid_metadata:
            local_value = " - "
            if vid_item in dict_data:
                local_value = dict_data[vid_item]
            result_list.append(local_value)

    return result_list


def extractExifData(media_folder, csv_filename):
    """
    extracts from this device folder exiftool data
    """
    with open(csv_filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(vid_metadata)
        for i_media in os.listdir(media_folder):
            file_ext = i_media.split(".")[-1]
            file_check = [file_ext.lower() == item.lower() for item in extentions]
            if not i_media.startswith('.') and not os.path.isdir(os.path.join(media_folder, i_media)) and sum(file_check)>0:
                # print("Study media: ", i_media)
                # call exiftool
                cmd_exiftool = ["exiftool", os.path.join(media_folder, i_media)]
                ex_output = subprocess.check_output(cmd_exiftool)
                ex_result = ex_output.decode("utf-8").strip()
                # ok proceed
                i_dict = fromString2Dict(ex_result)
                data_list = getImportantMetadata(i_dict)
                # print(data_list)
                writer.writerow(data_list)


def vid_callExtractExifData(root_folder, result_folder):
    for social_media in os.listdir(root_folder):
        # for each social_media
        if not social_media.startswith('.') and os.path.isdir(os.path.join(root_folder, social_media)):
            # create result folder
            sm_result_folder = os.path.join(result_folder, social_media)
            if not os.path.exists(sm_result_folder):
                os.makedirs(sm_result_folder)

            for subset in subset_folders:
                # for each subset
                if os.path.exists(os.path.join(root_folder, social_media, subset)):
                    csv_name = "_".join((social_media, subset)) + ".csv"
                    csv_filename = os.path.join(sm_result_folder, csv_name)
                    extractExifData(os.path.join(root_folder, social_media, subset), csv_filename)
                    if os.path.exists(csv_filename):
                        print("Stored ", csv_filename)


def get_parser():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--video-path')
    parser.add_argument('--folder-path')
    parser.add_argument('--output-stats-path')
    return parser


def main(args):
    vid_callExtractExifData(args.folder_path, args.output_stats_path)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
