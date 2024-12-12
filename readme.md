# IoT Controller

This repository contains the software to control the Wacom IoT Paper acquisition graphics tablet.

The repository also includes all the example `.inkml` files for acquisitions of various ductus for the Greek letter alpha.

## Environment Setup

The virtual environment management can be handled using the [Conda](https://anaconda.org/anaconda/conda) environment manager.

To get started, create a new environment with the command:

```command
conda env create -f environment.yml
```

Once all the necessary dependencies are installed, you can activate the environment with the command:

```command
conda activate iot_experiment_cntrl
```

## Running the Software

To run the software, simply use the command:

```command
python GUI.py
```
