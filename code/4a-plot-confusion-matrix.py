#!/usr/bin/env python3

import argparse
import pickle

from bokeh import colors
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, output_file, save

import numpy as np

from sklearn.metrics import confusion_matrix


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path')
    parser.add_argument('output_path')

    return parser


def main(args):
    with open(args.experiment_path, 'rb') as stream:
        all_labels, run_symbols, classifiers, y_true, y_pred = \
                pickle.load(stream)

    device_ids = list(sorted(classifiers.keys()))

    flat_y_true = []
    flat_y_pred = []
    for device_id in device_ids:
        flat_y_true.extend(y_true[device_id])
        flat_y_pred.extend(y_pred[device_id])

    cm = confusion_matrix(flat_y_true, flat_y_pred)

    p = figure(x_axis_location='above', tools='hover,save',
            x_axis_label='Prediction', y_axis_label='Target',
            x_range=all_labels, y_range=list(reversed(all_labels)),
            tooltips=[('target', '@target'), ('prediction', '@prediction'),
                ('count', '@count')])

    p.plot_width = 1024
    p.plot_height = 768
    p.output_backend = 'svg'
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "10pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = -np.pi/5

    data = {
        'target': [],
        'prediction': [],
        'color': [],
        'count': [],
        'progress': [],
    }

    empty_color = colors.RGB(210, 210, 240)
    full_color = colors.groups.blue['CornflowerBlue']

    for i in range(cm.shape[0]):
        for j in range(cm.shape[0]):
            data['target'].append(all_labels[i])
            data['prediction'].append(all_labels[j])
            data['count'].append(cm[i, j])
            if cm[i, j] == 0:
                data['color'].append(colors.RGB(240, 240, 240))
                data['progress'].append('')
            else:
                progress = cm[i, j] / cm[i].sum()
                data['progress'].append("{:.2f}".format(progress))
                data['color'].append(colors.RGB(
                    int(empty_color.r + (full_color.r - empty_color.r) * progress),
                    int(empty_color.g + (full_color.g - empty_color.g) * progress),
                    int(empty_color.b + (full_color.b - empty_color.b) * progress),
                ))

    data = ColumnDataSource(data=data)

    p.rect('prediction', 'target', 0.9, 0.9, source=data,
            color='color', line_color=None,
            hover_line_color='black', hover_color='color')

    label_set = LabelSet(x='prediction', y='target', text='progress',
            source=data, text_font_size='9pt', text_align='center',
            text_baseline='middle')
    p.add_layout(label_set)

    output_file(args.output_path, title="Decision Tree CM")
    save(p)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args)
