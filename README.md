# Compass Rescue

**How much heading information can targeted feedback recover after a neural circuit is damaged?**

Compass Rescue investigates this question using a 106-neuron subcircuit from the Drosophila hemibrain connectome. It fits a rate model to the recorded wiring, weakens part of the circuit, and searches for a small set of stimulation groups that compensates for the resulting heading error.

The current experiment achieves partial compensation: mean error decreases from **69.6° to 37.8°** across eight held-out simulations. The intact model averages **2.7°**. Recovery does not persist when stimulation is removed.

![Heading trajectories and held-out results](results/benchmark.png)

## What the project includes

- **Real anatomical connectivity:** 106 identified neurons, 1,932 directed connections, and 46,842 synapses from hemibrain v1.2.1.
- **A constrained dynamical model:** excitatory edges follow the measured graph; functional strengths are fitted to an idealized heading task.
- **Sparse intervention search:** all 56 three-group combinations, evaluated at four feedback gains on six training trials.
- **Separate evaluation:** eight held-out configurations, 12 random target sets, stimulation-free holds, and a damage/parameter sweep.
- **An offline viewer:** replay trials, inspect the measured matrix, and search individual neuron IDs.

## Results

| Condition | Mean heading error | Drift during stimulation-free hold |
|---|---:|---:|
| Intact | 2.7° | 0.3° |
| Damaged | 69.6° | 5.0° |
| Constant stimulation | 83.9° | 13.9° |
| One random target set | 57.6° | 10.0° |
| Selected feedback | **37.8°** | **41.5°** |

These are results from the model, not measurements from living flies. The selected three groups contain **39 neurons**. Baselines are not matched for stimulation cost or number of stimulated cells. The large drift after feedback stops is a limitation of the controller, not evidence of lasting repair.

See [the full results](RESULTS.md) for baseline distributions, stimulation costs, and interpretation.

## Try it

Download or clone the repository and open **`Compass-Rescue.html`** in a browser. The viewer runs offline and includes the completed experiment. It replays recorded trajectories; it does not run the numerical optimization in the browser.

To reproduce the pipeline with Python 3.10 or later:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prepare.py
python experiment.py
python -m unittest test_pipeline.py
python plot_results.py
```

On Windows, use `.venv\Scripts\activate` to activate the environment. The raw extract is included, so no neuPrint account or API token is needed.

## How it works

1. **Load the anatomy.** Preserve the measured neuron IDs and sum EB/PB synapse counts into a directed matrix.
2. **Fit the intact model.** Learn nonnegative functional weights on observed edges using idealized heading profiles and a count-based regularization term.
3. **Apply damage.** Weaken outgoing PENa connections within an angular sector.
4. **Estimate and compensate.** Reconstruct activity from eight delayed, noisy EPG measurements and estimate lost recurrent input using a fixed nominal model.
5. **Test generalization.** Freeze targets and feedback gain before evaluating unseen initial headings and circuit parameters.

The controller has no access to true heading, angular velocity, or a parallel intact circuit. The simulated circuit receives angular velocity as its sensory input. [Methods](docs/METHODS.md) gives the equations, parameter choices, and train/test split.

## Scope

The wiring is anatomical; the dynamics are task-fitted. Preferred phases, sensory encoding, time constants, and a supplemental population-inhibition term are model assumptions. The source extract excludes inhibitory cells, and optical access to the proposed reporter and stimulation groups has not been verified.

This project does not establish biological rescue, permanent recovery, or novelty relative to all prior work. Its purpose is to make an intervention hypothesis reproducible and expose where that hypothesis fails.

## Data and attribution

Connectivity comes from the public [SEISMIC repository](https://github.com/aplbrain/seismic), using Janelia hemibrain **v1.2.1**. The bundled file is pinned to commit `1a789eefc2ca03c1f79e283069e41d20d12ed91f`; its checksum and processing details are recorded in [data/provenance.json](data/provenance.json).

The original SEISMIC license is retained in [data/SEISMIC-LICENSE.txt](data/SEISMIC-LICENSE.txt). This project does not claim to have reconstructed the source connectome. Related resources: [Virtual Fly Brain](https://www.virtualflybrain.org/) and [neuPrint](https://neuprint.janelia.org/).

## Repository layout

| File | Purpose |
|---|---|
| `prepare.py` | Validate the source and fit the model |
| `model.py` | Circuit dynamics and feedback law |
| `experiment.py` | Target search and held-out experiments |
| `test_pipeline.py` | Data integrity, numerical behavior, and split checks |
| `data/` | Raw extract, annotations, provenance, and fitted parameters |
| `results/` | Trial-level results, full trajectories, and figure |
| `Compass-Rescue.html` | Self-contained experiment viewer |

## Next experiments

- Replace effective inhibition with reconstructed inhibitory circuitry.
- Compare interventions with matched stimulation dose and cell counts.
- Fit and test dynamics against physiological recordings.
- Evaluate access through documented driver lines and a second specimen.

Code is available under the [MIT license](LICENSE). Upstream material retains its accompanying attribution.
