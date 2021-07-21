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

from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, classification_report

from common_defs import BRANDS_FOR_DEVICES

parser = argparse.ArgumentParser()
parser.add_argument('exp_path')

args = parser.parse_args()

with open(args.exp_path, 'rb') as stream:
    chosen_classes, run_symbols, classifiers, y_true, y_pred = pickle.load(stream)

device_ids = list(sorted(y_true.keys()))

print("Accuracy by device")
for device_id in device_ids:
    print("{} & {:.2f} \\\\".format(device_id, accuracy_score(y_true[device_id], y_pred[device_id])))


print("Accuracy by device with brand")
for device_id in device_ids:
    print("{} ({}) & {:.2f} \\\\".format(device_id, BRANDS_FOR_DEVICES[device_id], accuracy_score(y_true[device_id], y_pred[device_id])))

print("Balanced Accuracy by device")
for device_id in device_ids:
    print("{} & {:.2f} \\\\".format(device_id, balanced_accuracy_score(y_true[device_id], y_pred[device_id])))


print("Balanced Accuracy by device with brand")
for device_id in device_ids:
    print("{} ({}) & {:.2f} \\\\".format(device_id, BRANDS_FOR_DEVICES[device_id], balanced_accuracy_score(y_true[device_id], y_pred[device_id])))

all_y_pred = []
all_y_true = []

for device_id in device_ids:
    all_y_pred.extend(y_pred[device_id])
    all_y_true.extend(y_true[device_id])

print("Global accuracy: {:.1f}".format(100 * accuracy_score(all_y_pred, all_y_true)))
print("Global balanced accuracy: {:.1f}".format(100 * balanced_accuracy_score(all_y_pred, all_y_true)))

print("Confusion matrix")
cm = confusion_matrix(all_y_true, all_y_pred)

print(" & {} \\\\".format(" & ".join(chosen_classes)))
for i, c1 in enumerate(chosen_classes):
    print(c1, end=' ')
    for j, c2 in enumerate(chosen_classes):
        print("& {:.2f} ".format(cm[i, j]), end='')
    print('\\\\')

print("Normalized confusion matrix")
print(" & {} \\\\".format(" & ".join(chosen_classes)))
for i, c1 in enumerate(chosen_classes):
    print(c1, end=' ')
    for j, c2 in enumerate(chosen_classes):
        print("& {:.2f} ".format(cm[i, j] / cm[i].sum()), end='')
    print('\\\\')

print(classification_report(all_y_true, all_y_pred, 
    target_names=chosen_classes))
