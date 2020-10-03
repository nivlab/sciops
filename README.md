# silver-screen

## Project Organization

    ├── data                         <- Raw task and self-report behavior data.
    │   
    ├── figures                      <- Figures for presentations & manuscript.
    │   
    ├── laverna                     <- Source code used in notebooks (installation instructions below).
    │   
    ├── manuscripts                  <- Manuscripts.
    │   
    ├── notebooks                    <- Analysis notebooks for the projects.

## Installation

This repository hosts the `laverna` package, which is used in some of this project's simulations. 

To install the code through Github, open a terminal and run:

```bash

    pip install git+https://github.com/nivlab/silver-screen.git

```

Alternately, you can clone the repository and install locally:

```bash 

    git clone https://github.com/nivlab/silver-screen
    cd laverna
    pip install -e .

```

Once installed, the simulations (found in the notebooks folder) should be reproducible on any computer.

## Notes

Pull updates from Overleaf

> git pull overleaf master

Push updates to Overleaf

> git push overleaf master
