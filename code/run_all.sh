#! /bin/bash
# @Author: Daniele Baracchi
# @Date:   2021-07-21
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-21
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

mkdir logs

./1-create_dataset.py Containers dataset.pkl

./2-eval_likelihood_ratios.py dataset.pkl likelihood_ratios
./2-eval_likelihood_ratios.py --use-os-info dataset.pkl likelihood_ratios

./3-train_tampering_detector.py --likelihood-ratios-path likelihood_ratios/ dataset.pkl results/tampering-detector/no-os/lr/ | tee logs/tampering-detector-lr.log
./3-train_tampering_detector.py --likelihood-ratios-path likelihood_ratios/ --use-os-info dataset.pkl results/tampering-detector/os/lr/ | tee logs/tampering-detector-os-lr.log
./3-train_tampering_detector.py dataset.pkl results/tampering-detector/no-os/no-lr/ | tee logs/tampering-detector.log
./3-train_tampering_detector.py --use-os-info dataset.pkl results/tampering-detector/os/no-lr/ | tee logs/tampering-detector-os.log

./4-train_tampering_classifier.py --likelihood-ratios-path likelihood_ratios/ dataset.pkl results/tampering-classifier/no-os/lr/ | tee logs/tampering-classifier-lr.log
./4-train_tampering_classifier.py --likelihood-ratios-path likelihood_ratios/ --use-os-info dataset.pkl results/tampering-classifier/os/lr/ | tee logs/tampering-classifier-os-lr.log
./4-train_tampering_classifier.py dataset.pkl results/tampering-classifier/no-os/no-lr/ | tee logs/tampering-classifier.log
./4-train_tampering_classifier.py --use-os-info dataset.pkl results/tampering-classifier/os/no-lr/ | tee logs/tampering-classifier-os.log

./5-train_blind_classifier.py --likelihood-ratios-path likelihood_ratios/ dataset.pkl results/blind-classifier/no-os/lr/ | tee logs/blind-classifier-lr.log
./5-train_blind_classifier.py --likelihood-ratios-path likelihood_ratios/ --use-os-info dataset.pkl results/blind-classifier/os/lr/ | tee logs/blind-classifier-os-lr.log
./5-train_blind_classifier.py dataset.pkl results/blind-classifier/no-os/no-lr/ | tee logs/blind-classifier.log
./5-train_blind_classifier.py --use-os-info dataset.pkl results/blind-classifier/os/no-lr/ | tee logs/blind-classifier-os.log

for osvariant in no-os os; do
    for lrvariant in no-lr lr; do
        for item in Facebook Tiktok Weibo Youtube non-SN; do
            ./6a-plot-confusion-matrix.py results/tampering-detector/$osvariant/$lrvariant/$item.pkl results/tampering-detector/$osvariant/$lrvariant/$item-cm.html
            ./6a-plot-confusion-matrix.py results/tampering-classifier/$osvariant/$lrvariant/$item.pkl results/tampering-classifier/$osvariant/$lrvariant/$item-cm.html
            ./6b-print-accuracy-by-device.py results/tampering-detector/$osvariant/$lrvariant/$item.pkl > results/tampering-detector/$osvariant/$lrvariant/$item-acc.txt
            ./6b-print-accuracy-by-device.py results/tampering-classifier/$osvariant/$lrvariant/$item.pkl > results/tampering-classifier/$osvariant/$lrvariant/$item-acc.txt
            ./6c-plot-trees.py results/tampering-detector/$osvariant/$lrvariant/$item.pkl results/tampering-detector/$osvariant/$lrvariant/trees/$item/
            ./6c-plot-trees.py results/tampering-classifier/$osvariant/$lrvariant/$item.pkl results/tampering-classifier/$osvariant/$lrvariant/trees/$item/
        done
        ./6a-plot-confusion-matrix.py results/blind-classifier/$osvariant/$lrvariant/blind.pkl results/blind-classifier/$osvariant/$lrvariant/blind-cm.html
        ./6b-print-accuracy-by-device.py results/blind-classifier/$osvariant/$lrvariant/blind.pkl > results/blind-classifier/$osvariant/$lrvariant/blind-acc.txt
        ./6c-plot-trees.py results/blind-classifier/$osvariant/$lrvariant/blind.pkl results/blind-classifier/$osvariant/$lrvariant/trees/blind/
    done
done

./6d-plot-lr.py likelihood_ratios likelihood_ratios/plots
