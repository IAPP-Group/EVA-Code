#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

import argparse
import pickle

import numpy as np
from sklearn.metrics import balanced_accuracy_score, confusion_matrix


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('results_path')

    return parser


def main(args):
    with open(args.results_path, 'rb') as stream:
        all_classes, all_symbols, clfs, y_true, y_pred = pickle.load(stream)

    all_yt = []
    all_yp = []

    for k in y_true.keys():
        #print("- {}: {:.02f}".format(k, balanced_accuracy_score(y_true[k], y_pred[k])))
        all_yt.extend(y_true[k])
        all_yp.extend(y_pred[k])

    print("Global {:.02f}".format(balanced_accuracy_score(all_yt, all_yp)))
    cm = confusion_matrix(all_yt, all_yp).astype(np.float32)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[0]):
            cm[i,j] /= cm[i].sum()
    tn = cm[0,0]
    fn = cm[1,0]
    tp = cm[1,1]
    fp = cm[0,1]
    #print("tn={:.02f} fn={:.02f} tp={:.02f} fp={:.02f}".format(tn, fn, tp, fp))
    print("TPR: {:.02f}".format(tp / (tp + fn)))
    print("TNR: {:.02f}".format(tn / (tn + fp)))
    print("FNR: {:.02f}".format(fn / (fn + tp)))
    print("FPR: {:.02f}".format(fp / (fp + tn)))
    print("PPV: {:.02f}".format(tp / (tp + fp)))


if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())
