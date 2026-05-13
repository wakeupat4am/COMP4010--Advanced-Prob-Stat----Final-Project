# MATH4010 - Final Project - Group 6

## Overview

This repository contains the work for the final project of `MATH4010 - Advanced Probability & Statistics` (Spring 2026).

## Submission Deliverables

Each group must prepare and submit:

1. One written report in PDF format
2. One program package (`.ipynb` notebook or GitHub repository)
3. One presentation slide deck (PDF or PowerPoint)
4. One poster (1-page A0 portrait PDF)

## Project Structure

- `Data/data.csv`: dataset used in the project
- `Problem & Visualization/Problem 1/Problem_1.ipynb`: work for Question 1
- `Problem & Visualization/Problem 2/Problem_2.ipynb`: work for Question 2
- `Problem & Visualization/Problem 3/Problem_3.ipynb`: work for Question 3

## Assignment Tasks

### Question 1
MATH
Define two families of shapes parameterized by the dimension `n`:

- `A_n = {x in R^n such that ||x - (1/2)1||_2 <= 1/2}`, the largest ball inscribed in the unit box `[0,1]^n`
- `B_n = {x in R^n such that ||x||_2 <= 1}`, the unit ball

In other words:

- `A_n` is the ball centered at `(1/2, ..., 1/2)` with radius `1/2`
- `B_n` is the ball centered at `(0, ..., 0)` with radius `1`

#### 1.a

- Visualize `A_2` and `B_2`
- Compute the exact areas of `A_2` and `B_2` through direct calculation
- Choose and implement algorithm(s) to estimate the areas of `A_2` and `B_2`
- Explain the algorithms and justify the choices
- Report estimates, errors, and any other evaluation metrics used

#### 1.b

- Visualize `A_3` and `B_3`
- Compute the exact volumes of `A_3` and `B_3` through direct calculation
- Use the same algorithm(s) from part `1.a` to estimate the volumes
- Report estimates, errors, and other evaluation metrics
- Compare the results against part `1.a`

#### 1.c

- Compute the exact volumes of `A_n` and `B_n` for any `n >= 1`
- Use the same algorithm(s) from part `1.a` to estimate the volumes of `A_100` and `B_100`
- Record any challenges encountered
- Discuss the performance of the selected algorithm(s) as `n -> infinity`
- Suggest revisions or alternative methods for improvement if needed

### Question 2

Let `S(x) = x^4` and let

`f(x) = e^{-S(x)} / Z`

be the associated probability density function.

Required tasks:

- Estimate the normalization factor `Z` by direct calculation or a numerical algorithm
- Choose at least three different symmetric proposal distributions
- Use the Metropolis algorithm to generate `N = 1000` samples following distribution `f`
- Visualize the generated samples
- Explain the algorithm and report numerical performance
- Compare performance across the different symmetric proposal distributions
- Explain the observed differences and suggest improvements

### Question 3

Use a microphone (laptop, phone, or microcontroller with ADC) to record audio using the same setting for all clips, for example:

- mono
- 16-bit
- fixed sampling rate such as `16 kHz`

#### 3.a Data collection

- Record `10` clips of ambient noise
- Record `10` clips of music
- Each clip must have the same length and be at least `3` seconds long
- Document the recording device and settings

#### 3.b Compute four values per clip

Choose a bin width `Delta` and use the same `Delta` for all `20` clips. For each clip, compute:

- Discrete entropy: `H_Q = -sum_b p_b log_2 p_b`
- Differential entropy estimate: `H = H_Q + log_2 Delta`
- Upper bound: `H_max = log_2 K`, where `K` is the number of bins
- Gaussian reference: `H_Gauss = (1/2) log_2(2 pi e sigma^2)`

#### 3.c Discussion

- Report the mean and standard deviation of each quantity within each class
- Compute the gap `H_Gauss - H` for every clip
- Compare the typical value of that gap between the two classes
- Identify which class is closer to Gaussian
- Explain the result using the maximum-entropy-given-variance result from lecture

## Notes

- The written report must be at most 6 pages, including references and the contribution declaration table
- The code package should reproduce the computations, experiments, and results reported in the written report
- The slide deck should focus on data collection and processing, methodology, and experimental results
- The poster should summarize the dataset, methodology, and key results
