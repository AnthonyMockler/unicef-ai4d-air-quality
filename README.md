<div align="center">

# UNICEF AI4D Air Quality Research

</div>

<br/>
<br/>


# 📜 Description

Repository for UNICEF AI4D air quality research. Goal is to train models that can predict ground-level PM2.5 for areas with no ground-monitoring stations using satellite-derived data (e.g. Aerosol Optical Depth, Meteorological Variables, NDVI, etc) and other datasets (e.g. population).


<br/>
<br/>


# ⚙️ Local Setup for Development

Though you are free to use any python environment manager you wish, this guide will assume the usage of [miniconda](https://docs.conda.io/en/latest/miniconda.html#:~:text=Miniconda%20is%20a%20free%20minimal,zlib%20and%20a%20few%20others.).


## Requirements

1. Python 3.7+
2. make


## 🐍 One-time Set-up
Run this the very first time you are setting-up the project on a machine to set-up a local Python environment for this project.

1. Install miniconda for your environment if you don't have it yet. Either:
* Manually download and install the appropriate version from [here](https://docs.conda.io/en/latest/miniconda.html); or
* For VMs with no GUI, this is an example of how to install from your terminal:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```


2. Create a local python environment and activate it.
* Note:
    * You can change the name if you want; in this example, the env name is `ai4d-air-quality`.
```bash
conda create -n ai4d-air-quality python=3.7
conda activate ai4d-air-quality
```

3. Clone this repo and navigate into the folder. For example:
```bash
git clone git@github.com:thinkingmachines/unicef-ai4d-air-quality.git
cd unicef-ai4d-air-quality
```

4. Install the project dependencies by running:
    * Note:
        * This make command installs `poetry` (the python dependency manager),  `pre-commit` hooks (which enforce the automated formatters), and `jupyter`/`jupyter lab`.
        * If you don't have `make` available in your system, you can refer to the commands under `Makefile` > `dev` recipe. That is, copy-paste those commands into your terminal.
```bash
make dev
```


## 📦 Dependencies

Over the course of development, you might introduce new library dependencies. When you do so, please add it in `poetry` along with your commits so that other devs can get the updated list of project requirements.

For example, to add `pandas` as a dependency, run:
```bash
poetry add pandas
```

To update your local conda env and sync it with the dependencies listed in the poetry files (e.g. after you pull changes from GitHub), run:
```bash
poetry install
```

<br/>
<br/>

# 🧠 Training the Model
To-do: This will be updated once we've created code for training the PM2.5 regression model.