# Astrophysics

Topics for single-topic notebooks, built the way a researcher works: get the data, reduce it, measure something yourself, fit a model, compare with the catalogue. How a notebook is built is described in [AGENTS.md](AGENTS.md).

## 0. Splitting the existing notebooks

- galaxies.ipynb
  - photometry and Sérsic profiles (M 51, M 104, M 87, M 101)
  - nebular spectroscopy: Hα flux, BPT diagram, metallicity gradient
  - rotation curves and dark matter: SPARC, NFW against isothermal halos, bulge plus disk
  - the M 87 black hole: EHT visibilities, ring size, CLEAN and sparse recovery
- exoplanets.ipynb
  - transit search: light curves, detrending, BLS, phase folding
  - vetting: centroids, difference imaging, Gaia DR3 neighbours, odd/even depths, secondary eclipse
  - populations: period–radius plane, radius valley, mass–radius diagram
  - atmospheres: scale height and transmission features
  - SPADE superresolution and Fisher information
- stars.ipynb
  - solar flares from GOES X-ray flux and their classes
  - SDO AIA images and HMI magnetograms, flare positions
  - the solar cycle from sunspot numbers
- gravitationalwaves.ipynb
  - data access, raw strain and a first Q-transform so far
  - grows into the series of Section 1

## 1. Gravitational waves

**What researchers do**
- characterize the detector noise
- search the strain data for signals, with matched filters or unmodelled methods
- estimate how significant a candidate is
- infer the source parameters with Bayesian methods
- localize the source on the sky for telescopes
- use many events for populations, tests of general relativity, neutron-star physics and cosmology
- work on the detector noise budget, down to the quantum noise limit

**Data and noise**
- First look at GW150914
  - GWOSC strain of H1 and L1, sampling rates, data segments
  - Q-transform spectrogram, the chirp by eye
- Noise characterization
  - power and amplitude spectral density (Welch)
  - spectral lines: power mains, violin modes, calibration lines
  - non-stationarity; plot the ASD of H1, L1 and Virgo for one event
- Whitening and band-passing
  - why the raw strain shows nothing and the whitened strain shows the chirp
- Glitches
  - blips and scattered light, how they mimic signals, Gravity Spy classes

**Searches**
- Matched filtering
  - noise-weighted inner product, SNR time series, peak SNR in each detector
  - code: PyCBC waveform and filter on GW150914
- Chirp mass from the frequency evolution
  - the Newtonian chirp f(t), chirp mass from the spectrogram track
- Template banks and signal-based vetoes
  - placement in mass space, the χ² veto against glitches
- Coincidence and significance
  - time-of-flight window between detectors, background from time slides
  - false-alarm rate, p_astro
- Unmodelled burst searches
  - excess power, the idea of coherent WaveBurst

**Parameter estimation**
- Bayesian inference for a binary
  - likelihood in the frequency domain, priors
  - posteriors of chirp mass, mass ratio, effective spin, distance and inclination
  - code: Bilby with a fast waveform on a short segment
- Degeneracies
  - distance against inclination, mass ratio against spin, corner plots
- Fisher-matrix estimates against full posteriors
  - see maths.md 4.8 for Fisher information in quantum metrology
- Waveform models
  - post-Newtonian inspiral, phenomenological and effective-one-body models, numerical relativity surrogates

**Localization and multi-messenger astronomy**
- Sky maps
  - HEALPix maps from the GWTC releases, 90 % credible areas, triangulation from arrival times
- GW170817
  - the neutron-star merger, the gamma-ray burst 1.7 s later, the kilonova in NGC 4993, the speed of gravity

**Physics from many events**
- Ringdown and black-hole spectroscopy
  - quasinormal modes of a Kerr black hole, the no-hair test
- Tests of general relativity
  - inspiral–merger–ringdown consistency, residual tests, bounds on the graviton mass
- Neutron-star matter
  - tidal deformability, constraints on the equation of state, mass–radius curves
- Populations
  - the GWTC catalogues, mass distribution (peak near 35 solar masses, pair-instability gap)
  - spin distribution, merger rates, selection effects, hierarchical inference
- Standard sirens
  - the Hubble constant from GW170817 and its host galaxy, dark sirens with galaxy catalogues

**Detectors and other sources**
- Interferometer physics
  - Michelson with Fabry–Perot arms, antenna patterns
  - noise budget: seismic, thermal, quantum
- Quantum noise and squeezed light
  - shot noise, radiation-pressure noise, the standard quantum limit, frequency-dependent squeezing
  - see maths.md 4.8
- Continuous waves from rotating neutron stars
  - the idea of the F-statistic, Doppler modulation by Earth's motion
- Stochastic background and pulsar timing arrays
  - cross-correlation of detectors, the Hellings–Downs curve, the NANOGrav 15-year evidence
- Space-based detection with LISA
  - massive black-hole binaries, extreme mass ratio inspirals, galactic binaries as foreground
- Machine learning in gravitational-wave analysis
  - glitch classification, denoising, fast inference with normalizing flows (DINGO)

## 2. Exoplanets

**What researchers do**
- find planets: transits, radial velocities, astrometry, direct imaging, microlensing
- rule out false positives
- measure radius, mass and orbit
- study the population as a whole
- characterize atmospheres with spectroscopy

**Detection and vetting**
- Transit search
  - TESS and Kepler light curves, detrending, BLS against TLS, phase folding
  - see also exoplanets.ipynb
- Vetting and false positives
  - eclipsing binaries, blends, odd/even depths, secondary eclipses, centroid motion, difference images
  - see also exoplanets.ipynb
- Completeness
  - injection and recovery of synthetic transits, recovery rate in the period–radius plane
- Statistical validation
  - false-positive probability from priors on blends and binaries

**Characterizing planets**
- Transit modelling
  - limb darkening, impact parameter, stellar density from the transit shape, MCMC fit with uncertainties
- Radial velocities
  - Keplerian orbits, periodograms, stellar activity as noise (Gaussian processes), minimum mass
- Bulk composition
  - density from radius and mass, mass–radius curves of rock, water and gas
- Transit-timing variations and resonances
  - dynamical stability with N-body integrations

**Populations**
- Occurrence rates
  - correcting detections for completeness and transit probability
- The radius valley
  - photoevaporation against core-powered mass loss, dependence on stellar mass
- Hot Jupiters, the Neptune desert, period distributions

**Atmospheres and habitability**
- Transmission spectroscopy
  - scale height, expected feature sizes, JWST spectra
- Emission spectra, secondary eclipses and phase curves
  - day–night contrast, heat redistribution
- Atmospheric retrieval
  - forward models, Bayesian retrieval of temperature and composition
- Habitable zone and equilibrium temperature
  - dependence on stellar type and albedo

**Imaging**
- Direct imaging
  - coronagraphy, PSF subtraction (ADI, KLIP), contrast curves
- Superresolution of close sources
  - SPADE against direct imaging, Fisher information per photon
  - see maths.md 2.3 and 4.8
- Astrometric planets with Gaia
  - the wobble of the host star

## 3. Stars and the Sun

### 3.1 The Sun

**What researchers do**
- monitor flares and coronal mass ejections
- map magnetic fields
- follow the activity cycle
- probe the interior with oscillations
- forecast space weather

**Topics**
- Solar flares
  - GOES X-ray flux, flare classes, flare positions
  - see also stars.ipynb
- EUV imaging and magnetograms
  - SDO AIA channels and temperatures, HMI line-of-sight magnetic field
- The solar cycle
  - sunspot number, cycle length, butterfly diagram
- Flare statistics
  - power-law frequency distribution of flare energies
- Differential rotation
  - from tracking sunspots or magnetic features
- Coronal mass ejections
  - SOHO LASCO coronagraph images, speeds, arrival at Earth
- Solar wind and space weather
  - ACE and DSCOVR data, geomagnetic indices
- Helioseismology
  - p-modes, the five-minute oscillation, the interior structure

### 3.2 Stellar physics

**What researchers do**
- measure stellar parameters: temperature, radius, mass, age, composition
- test stellar evolution models
- study variability, binaries and the end states of stars

**Topics**
- The Hertzsprung–Russell diagram from Gaia
  - parallaxes, absolute magnitudes, colours, main sequence, giants, white dwarfs
- Isochrones and ages
  - cluster HR diagrams fitted with stellar evolution tracks
- Asteroseismology
  - power spectra of TESS or Kepler light curves, ν_max and Δν, scaling relations for mass and radius
- Stellar rotation and gyrochronology
  - rotation periods from starspots, age from spin-down
- Flares on M dwarfs
  - rates and energies in TESS data, comparison with the Sun
- Variable stars
  - Cepheids and the period–luminosity relation, RR Lyrae, the distance ladder
- Eclipsing binaries
  - masses and radii from light and velocity curves
- Stellar spectra
  - spectral classification, effective temperature and surface gravity from lines
- White dwarfs
  - cooling sequence in Gaia, the Chandrasekhar limit from Fermi degeneracy
- Neutron stars and pulsars
  - spin-down, magnetic field estimates, the P–Ṗ diagram

## 4. Galaxies and nebulae

**What researchers do**
- measure the light distribution: morphology and structure
- measure spectra: redshift, star formation, chemistry, ionizing sources
- measure motions: rotation curves, velocity dispersion, dark matter
- study central black holes
- place galaxies in the large-scale structure

**Structure and morphology**
- Surface photometry
  - isophotes, Sérsic profiles, bulge–disk decomposition
  - see also galaxies.ipynb
- Morphology
  - concentration, asymmetry, Gini–M20, machine-learned morphology (Galaxy Zoo)

**Spectra**
- Redshifts and emission lines
  - line fitting, Hα flux, star formation rate
- Ionizing sources
  - BPT diagram, star-forming regions against AGN
  - see also galaxies.ipynb
- Chemistry
  - metallicity calibrations and gradients across a disk
- Stellar populations
  - SED fitting, ages and stellar masses
- Integral-field spectroscopy
  - maps of velocity and line ratios (MaNGA)

**Dynamics and dark matter**
- Rotation curves
  - SPARC, NFW against cored halos, bulge plus disk plus gas
  - see also galaxies.ipynb
- Scaling relations
  - baryonic Tully–Fisher, Faber–Jackson, fundamental plane

**Black holes and imaging**
- The M 87 shadow
  - interferometric visibilities, uv coverage, ring size, CLEAN against sparse recovery
  - see also galaxies.ipynb
- Black-hole masses
  - the M–σ relation, reverberation mapping

**Nebulae**
- H II regions
  - electron temperature and density from line ratios
- Planetary nebulae and supernova remnants
  - morphology, expansion, abundances

**Large-scale structure**
- Redshift surveys
  - the cosmic web in SDSS, two-point correlation function, baryon acoustic oscillations
- Gravitational lensing
  - strong lensing arcs, weak lensing shear, cluster masses

## 5. Adjacent areas for later

- Cosmology
  - CMB power spectrum from Planck maps, supernova Hubble diagram (Pantheon+), the Hubble tension
- Transients
  - supernova light curves, ZTF alerts, the Rubin Observatory stream
- Radio transients
  - fast radio bursts, dispersion measures
- High-energy astrophysics
  - X-ray spectra, gamma-ray bursts, Fermi LAT

## 6. Bridges between astrophysics and quantum topics

- Quantum limits of gravitational-wave detectors
  - squeezed light and the standard quantum limit (Section 1, maths.md 4.8)
- Superresolution by mode sorting
  - SPADE (Section 2, maths.md 2.3 and 4.8)
- Intensity interferometry
  - Hanbury Brown–Twiss, photon bunching, stellar diameters (maths.md 2.7)
- Degenerate matter
  - the Chandrasekhar limit from Fermi statistics (Section 3.2)
- Sparse recovery
  - CLEAN in radio imaging and top-k search for sparse spectra (Section 4, maths.md 4.4)
- Black holes and information
  - Hawking radiation, Page curve, scrambling (maths.md 3.4)

## Data sources and tools

- Gravitational waves
  - data: GWOSC (strain, event catalogues, sky maps)
  - tools: gwosc, gwpy, pycbc, bilby, ligo.skymap
- Exoplanets
  - data: MAST (TESS, Kepler), NASA Exoplanet Archive, Gaia
  - tools: lightkurve, astroquery, transitleastsquares, batman, emcee
- Sun
  - data: VSO and JSOC (SDO), NOAA SWPC (GOES), SILSO (sunspots)
  - tools: sunpy, astropy
- Stars
  - data: Gaia archive, TESS and Kepler, VizieR
  - tools: astroquery, lightkurve, isochrones
- Galaxies
  - data: SDSS, NED, SIMBAD, SPARC, EHT public data, MaNGA
  - tools: astroquery, photutils, astropy
- Cosmology
  - data: Planck Legacy Archive, Pantheon+
  - tools: healpy, camb
