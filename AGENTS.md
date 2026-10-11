# AGENTS.md

How the notebooks in this repository are built. The topics come from [maths.md](maths.md) and [astrophysics.md](astrophysics.md).

## General

- One topic per notebook
  - small enough to work through in one afternoon
  - a larger topic becomes a short series of notebooks
- File names in the repository root
  - `math_<topic>.ipynb` for mathematics and quantum topics
  - `astro_<topic>.ipynb` for astrophysics
- Runs in Google Colab
  - the first code cell installs the packages it needs
  - data are downloaded at run time, not committed
  - no API keys or tokens in a notebook; use environment variables or Colab secrets
- Derivations are done by hand
  - each notebook has empty cells for them, placed before the code that uses the result
- Plots
  - every plot answers a question stated in the cell above it
  - axes with units, a title, and a legend when more than one curve is shown

## Template for mathematics and quantum notebooks

- Question
  - what the notebook answers, in one sentence
- Theory
  - definitions and the key formulas, short
- Derive it
  - questions, then empty cells to be filled by hand before any code is run
- Code
  - a simulation small enough to read in one sitting
- Plots
  - each plot answers one question stated above it
- Variations
  - change one parameter and predict the plot before running it
- References
  - textbook chapter or paper, with section numbers

## Template for astrophysics notebooks

- Question
  - what the notebook measures, in one sentence
- Background
  - the physics and the key formulas, short
- Data
  - source, download, first look at the raw data before any processing
- Reduction
  - cleaning, calibration, detrending, whitening
- Own measurement
  - the number or curve this notebook produces
- Model and fit
  - a physical model, fitted with uncertainties
- Own measurement against the catalogue
  - the published value next to the own one, and the reason for any difference
- Next steps
  - what a researcher would do next with this result
