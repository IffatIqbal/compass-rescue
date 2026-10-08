# Actual-connectivity run — 2026-09-26

Source: Janelia hemibrain v1.2.1, SEISMIC committed extract. 106 neurons, 1,932 directed pairs, 46,842 synapses. See data/provenance.json for the immutable commit and SHA-256.

Functional weights are fitted to an idealized task. Real anatomical wiring does not make these simulated rates or perturbations empirical measurements.

| Condition | Mean error (degrees) | Off-window error | Hold drift | Command cost |
|---|---:|---:|---:|---:|
| intact | 2.71 | 0.68 | 0.29 | 0.000 |
| damaged | 69.59 | 77.77 | 4.98 | 0.000 |
| constant | 83.93 | 95.87 | 13.93 | 0.108 |
| random | 57.60 | 69.25 | 9.99 | 0.142 |
| rescue | 37.77 | 49.15 | 41.53 | 0.259 |

## Interpretation

The three selected phase-sector groups (C0,C2,C7; 39 individual neurons) give partial feedback compensation, not intact-level accuracy. The selected gain is 2.0, the highest candidate tested. Average error falls about 46% versus the damaged condition across eight test configurations.

The 12 sampled random target sets average 44.3–69.8 degrees; the selected set averages 37.8 degrees. This is a limited comparison, with unequal stimulated-cell counts and unequal energy. It does not prove superiority to a well-tuned, dose-matched baseline.

Continuous feedback averages 35.5 degrees. During the stimulation-free hold, net heading drift averages **41.5 degrees** with the selected policy, compared with 0.3 degrees for the intact model and 5.0 degrees for the damaged model. The stimulated circuit is not permanently repaired; even the smaller drift of the damaged condition can reflect fixation at an incorrect heading.

## Verification

Eight tests pass: raw-source checksum/counts; adjacency support and pre/post orientation; deterministic replay, stimulation bounds and blackout; zero-damage/zero-controller equivalence; timestep refinement; fixed nominal controller under plant changes; intact hold stability; train/test seed separation. Offline UI logic tests cover replay, trial selection, scrubbing, SVG generation and neuron filtering. Full browser layout was not verified because the browser download failed. Figure generated with Matplotlib.

## Scope that remains experimental

No wet-lab rescue, genetic driver access, measured neuron dynamics, second connectome specimen, or permanently restored heading computation has been established. Missing inhibitory connectivity is represented by an explicit mean-population mechanism. The runnable pipeline is complete for this declared model; the biological research program is not.
