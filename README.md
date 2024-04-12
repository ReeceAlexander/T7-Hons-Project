# T7-Hons-Project

This repository contains code for controlling robots using EEG signals. The code leverages EEG data to interpret user commands and guide the movements of different robots.

## Introduction

The purpose of this project is to demonstrate how EEG signals can be utilized to control robotic systems effectively. Two different methods for interpreting EEG signals and controlling robots are implemented in this repository:

1. **Peak-Value-Hook Control Method**: This method captures the peak EEG power level resulting from user blinking to control the AgileX Hunter 2 Robot.
2. **EEG Interpretation for Webots Simulation**: This method interprets EEG commands to guide the movements of an E-Puck robot within the Webots simulation environment.

## Contents

The repository contains the following files:

- `peak_value_hook_control.py`: Python script implementing the Peak-Value-Hook control method for the AgileX Hunter 2 Robot.
- `webots_simulation_control.py`: Python script interpreting EEG commands to control the movements of an E-Puck robot in Webots simulation.
- `README.md`: This file providing an overview of the repository and its contents.
