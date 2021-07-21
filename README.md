# EVA-Code

Implementation tool used in:

```
@article{yang2020efficient,
  title={Efficient video integrity analysis through container characterization},
  author={Yang, Pengpeng and Baracchi, Daniele and Iuliani, Massimo and Shullani, Dasara and Ni, Rongrong and Zhao, Yao and Piva, Alessandro},
  journal={IEEE Journal of Selected Topics in Signal Processing},
  volume={14},
  number={5},
  pages={947--954},
  year={2020},
  doi={10.1109/JSTSP.2020.3008088},
  publisher={IEEE}
}
```


## Authors

- Daniele Baracchi (daniele.baracchi@unifi.it)
- Dasara Shullani (dasara.shullani@unifi.it)

## License

Copyright (C) 2021 Università degli studi di Firenze

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Testing

### Requirements
- tested with Python 3.8.10 and the following packages:

```
bokeh==2.3
scikit-learn==0.24
xmltodict==0.12
```

### Data

- uncompress `./code/Containers.tar.gz`


### Replicate results

- run `./code/run_all.sh`

```
cd code
bash run_all.sh
```

The table results are accessible at the following paths:

- **Table I**: results/tampering-detector/no-os/no-lr/non-SN-acc.txt
- **Table III**: results/tampering-classifier/no-os/no-lr/non-SN-cm.html
- **Table IV**: results/tampering-classifier/os/no-lr/non-SN-cm.html
- **Table VI**: results/blind-classifier/os/no-lr/blind-cm.html
- **Table V**: run the `get_global_accuracy.py` script as in 
    
    ```
    python get_global_accuracy.py results/tampering-detector/no-os/no-lr/Facebook.pkl
    python get_global_accuracy.py results/tampering-detector/no-os/no-lr/Tiktok.pkl 
    python get_global_accuracy.py results/tampering-detector/no-os/no-lr/Weibo.pkl 
    python get_global_accuracy.py results/tampering-detector/no-os/no-lr/Youtube.pkl 
    ```

**NOTE**: Be aware that the overall results will need **4.3 GB** of storage.
