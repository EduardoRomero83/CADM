# CADM

## Thank you for accessing this repository.
## How to use

1. Clone the repo and navigate inside it.
```
git clone https://github.com/EduardoRomero83/CADM.git
cd CADM
```
2. Get the dataset [here](https://osu.app.box.com/v/traffic-events-june20) and decompress it. (See more information about the dataset [here](https://smoosavi.org/datasets/lstw))

3. Move the dataset to `trainOgForest/`
```
mv path/to/TrafficEvents_Aug16_Dec19_Publish.csv trainOgForest/
```

4. Create and activate an virtual environment, and install dependencies.
```
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
```

5. Run `experiment.py` using Python 3
```
python3 experiment.py
```

6. When done, deactivate virtual environment and check `ResearchData/combined.csv` for results (for example using `cat`)
```
deactivate
cat ResearchData/combined.csv | column -t -s, | less -S
```

## Acknowledgement
Moosavi, Sobhan, Mohammad Hossein Samavatian, Arnab Nandi, Srinivasan Parthasarathy, and Rajiv Ramnath. “Short and Long-term Pattern Discovery Over Large-Scale Geo-Spatiotemporal Data.” In proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, ACM, 2019.
