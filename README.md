# evogym-design-tool
Design tool for creating Evolution Gym environments as seen in [Evolution Gym: A Large-Scale Benchmark for Evolving Soft Robots](https://evolutiongym.github.io/) (**NeurIPS 2021**).

![teaser](images/teaser.gif)


## Installation

#### Prerequisites

- **Python Version**: 3.7+
- **OpenGL** : may not be auto-installed on some macOS and Linux systems

#### Install Dependencies via Conda

Create a conda environment called **edt-env** by running 

```
conda env create -f environment.yml
```

#### Install Dependencies via pip

In a virtual environment, run 

```
pip install -r requirements.txt
```


## Run the Code

Run

```
python src/main.py
```

### Controls

- **Left Click**: Add/remove voxels and edges or select objects. Action is dependent on the **Edit Mode** selected in the gui
- **Right Click and Drag**: Pan the camera
-  **Mouse Wheel**: Zoom in/out

### Exporting and Importing

All files are saved and read from 

```
exported/
```