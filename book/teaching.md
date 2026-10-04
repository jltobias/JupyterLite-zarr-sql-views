# Instructor guide

Designed for introductory GIS, environmental data science, climate literacy, and browser-computing instruction. Students need a current browser and basic familiarity with variables and tables. No prior Zarr or SQL knowledge is assumed. More advanced students can inspect the upstream code and replace teaching extracts with reviewed real datasets.

## Three teaching formats

| Format | Suggested sequence | Deliverable |
|---|---|---|
| 90-minute demonstration | 01 → 02 highlights → 03 → 04 lab | One map, one SQL predicate, and an evidence statement |
| Three-session workshop | Session 1: 01–04; session 2: 05 plus selected thematic labs; session 3: 11–12 | Reproducible notebook and GeoJSON handoff |
| Four-week module | Week 1: 01–04; week 2: 05–07; week 3: 08–11; week 4: capstone | Peer-reviewed climate-data narrative |

The full twelve lessons total roughly eight hours before extensions and discussion. Select thematic labs according to the class; do not rush the data-origin and uncertainty discussions.

## Teaching routine

1. **Predict:** Ask students to sketch the expected result before executing.
2. **Run:** Execute a short Python cell or one SQL predicate.
3. **Inspect:** Read units, support, denominator, time labels, missingness, and origin.
4. **Perturb:** Change a threshold, mask, slice, or viewpoint.
5. **Explain:** State what changed and which claims remain justified.

Use pair work with a driver and an evidence reviewer. Switch roles halfway through. Give students the [data catalog](data.md) before asking them to interpret maps.

## Discussion prompts

Lake Ngami: Why does water frequency differ from flood extent? What happens when cloud cover changes the observation sample?

C3S Atlas: What is the difference between a global warming level and a regional anomaly? How do missing model-member windows affect comparison?

Heat: Which meteorological inputs and social conditions are missing from a temperature-only map? How would a global comparison keep definitions consistent?

Coasts: Why can a smooth 3D terrain picture create false confidence? How do datums, connectivity, and coastal defenses affect interpretation?

Air and water quality: Which physical quantity was measured, and which quantity is the public concerned about? What validation connects them?

Food and water insecurity: Which social and institutional conditions are absent from an environmental raster? How can local researchers and communities guide a useful question?

## Assessment and answer guidance

Each notebook ends with a task, reasoning guidance, and a four-sentence evidence journal. The capstone rubric awards 4 points each for question/scope, reproducibility, provenance, visual reasoning, and interpretation. Require the executed notebook, evidence record, a static figure with text alternative, and a two-minute explanation of limitations.

A good answer can conclude that the supplied data cannot support a proposed claim. Do not reward elaborate graphics over transparent methods. Avoid ranking communities with unsupported synthetic indicators.

## Preparation and classroom resilience

Open JupyterLite and import NumPy and Matplotlib on each device before class so the first runtime download does not surprise students. Test the lab’s WebGL support on classroom hardware. Keep the rendered Jupyter Book and a native Python environment as alternatives. A blank iframe can often be bypassed using its new-tab link. Students should download their work: browser storage is not a submission system.

For limited bandwidth, prioritize the rendered book and its static maps, then run the small Python exercises. The 3D lab and Pyodide require initial runtime downloads. Synthetic experiments remain labeled, even if used in an offline lesson.
