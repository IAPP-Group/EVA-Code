#!/usr/bin/env python3
# @Author: Daniele Baracchi
# @Date:   2021-07-05
# @Email:  daniele.baracchi@unifi.it
# @Last modified by:   Daniele Baracchi
# @Last modified time: 2021-07-05
# @License: GPL-3.0-or-later
# @Copyright: Copyright (C) 2021  Università degli studi di Firenze

python3 1-create_dataset.py Containers dataset.pkl

mkdir likelihood_ratios
python3 2-eval_likelihood_ratios.py dataset.pkl likelihood_ratios/

mkdir likelihood_ratios_os
python3 2-eval_likelihood_ratios.py --use-os-info dataset.pkl likelihood_ratios_os/

python3 -u 3a-decision-trees-before-youtube.py dataset.pkl experiment-3a.pkl | tee experiment-3a.log
python3 -u 3a-decision-trees-before-youtube.py --use-os-info dataset.pkl experiment-3a-os.pkl | tee experiment-3a-os.log
python3 -u 3a-decision-trees-before-youtube.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3a-lr.pkl | tee experiment-3a-lr.log
python3 -u 3a-decision-trees-before-youtube.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3a-lr-os.pkl | tee experiment-3a-lr-os.log

python3 -u 3b-decision-trees-after-youtube.py dataset.pkl experiment-3b.pkl | tee experiment-3b.log
python3 -u 3b-decision-trees-after-youtube.py --use-os-info dataset.pkl experiment-3b-os.pkl | tee experiment-3b-os.log
python3 -u 3b-decision-trees-after-youtube.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3b-lr.pkl | tee experiment-3b-lr.log
python3 -u 3b-decision-trees-after-youtube.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3b-lr-os.pkl | tee experiment-3b-lr-os.log

python3 -u 3c-decision-trees-with-everything.py dataset.pkl experiment-3c.pkl | tee experiment-3c.log
python3 -u 3c-decision-trees-with-everything.py --use-os-info dataset.pkl experiment-3c-os.pkl | tee experiment-3c-os.log
python3 -u 3c-decision-trees-with-everything.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3c-lr.pkl | tee experiment-3c-lr.log
python3 -u 3c-decision-trees-with-everything.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3c-lr-os.pkl | tee experiment-3c-lr-os.log

python3 -u 3d-decision-trees-before-youtube-binary.py dataset.pkl experiment-3d.pkl | tee experiment-3d.log
python3 -u 3d-decision-trees-before-youtube-binary.py --use-os-info dataset.pkl experiment-3d-os.pkl | tee experiment-3d-os.log
python3 -u 3d-decision-trees-before-youtube-binary.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3d-lr.pkl | tee experiment-3d-lr.log
python3 -u 3d-decision-trees-before-youtube-binary.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3d-lr-os.pkl | tee experiment-3d-lr-os.log

python3 -u 3e-decision-trees-after-youtube-binary.py dataset.pkl experiment-3e.pkl | tee experiment-3e.log
python3 -u 3e-decision-trees-after-youtube-binary.py --use-os-info dataset.pkl experiment-3e-os.pkl | tee experiment-3e-os.log
python3 -u 3e-decision-trees-after-youtube-binary.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3e-lr.pkl | tee experiment-3e-lr.log
python3 -u 3e-decision-trees-after-youtube-binary.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3e-lr-os.pkl | tee experiment-3e-lr-os.log

python3 -u 3f-decision-trees-with-everything-binary.py dataset.pkl experiment-3f.pkl | tee experiment-3f.log
python3 -u 3f-decision-trees-with-everything-binary.py --use-os-info dataset.pkl experiment-3f-os.pkl | tee experiment-3f-os.log
python3 -u 3f-decision-trees-with-everything-binary.py --likelihood-ratios-path likelihood_ratios dataset.pkl experiment-3f-lr.pkl | tee experiment-3f-lr.log
python3 -u 3f-decision-trees-with-everything-binary.py --likelihood-ratios-path likelihood_ratios_os --use-os-info dataset.pkl experiment-3f-lr-os.pkl | tee experiment-3f-lr-os.log

mkdir plots

python3 4a-plot-confusion-matrix.py experiment-3a.pkl plots/cm-experiment-3a.html
python3 4a-plot-confusion-matrix.py experiment-3a-os.pkl plots/cm-experiment-3a-os.html
python3 4a-plot-confusion-matrix.py experiment-3a-lr.pkl plots/cm-experiment-3a-lr.html
python3 4a-plot-confusion-matrix.py experiment-3a-lr-os.pkl plots/cm-experiment-3a-lr-os.html

python3 4a-plot-confusion-matrix.py experiment-3b.pkl plots/cm-experiment-3b.html
python3 4a-plot-confusion-matrix.py experiment-3b-os.pkl plots/cm-experiment-3b-os.html
python3 4a-plot-confusion-matrix.py experiment-3b-lr.pkl plots/cm-experiment-3b-lr.html
python3 4a-plot-confusion-matrix.py experiment-3b-lr-os.pkl plots/cm-experiment-3b-lr-os.html

python3 4a-plot-confusion-matrix.py experiment-3c.pkl plots/cm-experiment-3c.html
python3 4a-plot-confusion-matrix.py experiment-3c-os.pkl plots/cm-experiment-3c-os.html
python3 4a-plot-confusion-matrix.py experiment-3c-lr.pkl plots/cm-experiment-3c-lr.html
python3 4a-plot-confusion-matrix.py experiment-3c-lr-os.pkl plots/cm-experiment-3c-lr-os.html

python3 4a-plot-confusion-matrix.py experiment-3d.pkl plots/cm-experiment-3d.html
python3 4a-plot-confusion-matrix.py experiment-3d-os.pkl plots/cm-experiment-3d-os.html
python3 4a-plot-confusion-matrix.py experiment-3d-lr.pkl plots/cm-experiment-3d-lr.html
python3 4a-plot-confusion-matrix.py experiment-3d-lr-os.pkl plots/cm-experiment-3d-lr-os.html

python3 4a-plot-confusion-matrix.py experiment-3e.pkl plots/cm-experiment-3e.html
python3 4a-plot-confusion-matrix.py experiment-3e-os.pkl plots/cm-experiment-3e-os.html
python3 4a-plot-confusion-matrix.py experiment-3e-lr.pkl plots/cm-experiment-3e-lr.html
python3 4a-plot-confusion-matrix.py experiment-3e-lr-os.pkl plots/cm-experiment-3e-lr-os.html

python3 4a-plot-confusion-matrix.py experiment-3f.pkl plots/cm-experiment-3f.html
python3 4a-plot-confusion-matrix.py experiment-3f-os.pkl plots/cm-experiment-3f-os.html
python3 4a-plot-confusion-matrix.py experiment-3f-lr.pkl plots/cm-experiment-3f-lr.html
python3 4a-plot-confusion-matrix.py experiment-3f-lr-os.pkl plots/cm-experiment-3f-lr-os.html

python3 4c-plot-lr.py likelihood_ratios plots/likelihood_ratios
python3 4c-plot-lr.py likelihood_ratios_os plots/likelihood_ratios_os
