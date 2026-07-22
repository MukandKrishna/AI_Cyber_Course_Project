# Updated Grooming Detection Project Plan

## 1. Executive Summary

After checking:

- the assignment brief in `researchProjectReport-03RDL.docx`
- the marking criteria in `researchReport-MarkingCriteria.docx`
- the PASYDA dataset itself
- the current planning documents:
  - `Team_Structure_and_Project_Split.docx`
  - `Grooming_Detection_Project_Plan.docx`

the **core methodology does not need a major change**.

The main ideas that still stand are:

1. use **pair-level samples**, not raw message rows
2. use **grouped evaluation by dataset folder**
3. train at least **3 model families**:
   - Random Forest
   - SVM
   - one deep learning model
4. use **feature engineering + fair comparison + critical analysis**

What does need to be refined is:

1. **how experiments are defined for reporting**
2. **how the team work is sequenced**
3. **what exactly gets submitted**
4. **how to connect the data reality with the wording of the assignment**

This file is the final updated plan from start to finish.

---

## 2. What the Assignment Requires

From the assessment brief and marking criteria, your project must show:

- multiple, meaningfully different models
- proper feature engineering
- handling of class imbalance
- proper train/validation/test methodology
- reproducibility and no data leakage
- fair comparison across models
- evaluation using suitable metrics
- critical analysis of results
- discussion of dataset limitations, model limitations, and real-world application

The required submission is:

1. a **cover page**
2. an **index of all experiments**
3. a **portfolio of experiment reports**
4. a **4-page summary report**

The brief does **not explicitly state** that code must be submitted, but because implementation and reproducibility are assessed, the team should prepare the code cleanly and submit it if Moodle allows.

---

## 3. What the Data Actually Looks Like

This plan is based mainly on the data, not just the README.

### 3.1 Dataset structure

There are:

- **5 dataset folders**
- **2 scenarios per folder**
- **10 scenarios total**

Each scenario contains:

- `*_data.csv` -> full scenario traffic
- `*_vic_data.csv` -> smaller focused subnetwork
- `*_solutions.csv` -> the true grooming-related interaction

All useful files share the same columns:

- `ID`
- `Source`
- `Destination`
- `Date`
- `Length`

### 3.2 Important observed data behavior

From direct inspection of the CSV files:

- each `vic_data` file has **12 nodes**
- each `solutions` file has **2 nodes**
- in each `vic_data`, **one node appears in every interaction**
- `solutions` is always a subset of `vic_data`
- `vic_data` is always a subset of `data`

### 3.3 Real modeling implication

This means the correct supervised sample is **not a single message row**.

The correct sample is:

- one **central-node to contact pair**

For each scenario:

- one central node interacts with 11 contacts
- exactly **one of those 11 contact pairs is the true grooming pair**

So the true supervised task is:

> For each scenario, rank the 11 candidate pairs and identify the true grooming-related pair.

### 3.4 Important nuance for the report

The brief says "detect online grooming from the victim's perspective", but the structure of `vic_data` behaves more like an **ego-network around one central account**.

You should handle this carefully in the report:

- do **not** claim something false about the file structure
- say that your methodology was chosen based on **direct inspection of the data**
- explicitly note the mismatch between the broad wording of the task and the observed dataset behavior

That will make the report stronger, not weaker.

---

## 4. Final Methodology Decision

## Keep the main plan

The best methodology remains:

- **pair-level modeling**
- **5-fold grouped evaluation by dataset folder**
- models:
  - Random Forest
  - SVM
  - small MLP

## Important refinement

The **5 folds are part of the evaluation procedure**, not separate "experiments" for reporting.

That means:

- yes, each model is trained 5 times internally
- but in the report portfolio, one experiment report should describe one **model configuration**
- the fold-level results should be aggregated inside that report

This is the cleanest academic interpretation.

---

## 5. Recommended Deep Learning Model

## Final recommendation: small MLP

Use a **small Multi-Layer Perceptron (MLP)** as the deep learning model.

### Why MLP is the best choice here

1. the real labeled dataset is very small at pair level
2. the strongest representation is **engineered tabular features**
3. LSTM/GRU would need stronger sequential structure and more data
4. MLP is still a valid deep model, but it matches the dataset much better

### Suggested MLP setup

- input: engineered pair-level features
- hidden layers: `64 -> 32`
- activation: `ReLU`
- dropout: `0.2` to `0.3`
- output: `1 sigmoid node`
- optimizer: `Adam`
- loss: weighted binary cross-entropy
- regularization: early stopping

### What to say in the report

Explain that:

- sequence models were considered
- but the dataset is small and primarily tabular after feature engineering
- therefore a lightweight MLP is the most appropriate deep learning baseline

---

## 6. Full End-to-End Workflow

## Phase 0: Project Setup

### Goals

- create a shared team structure
- fix naming conventions
- create a reproducible repository layout

### Tasks

1. create a shared project folder structure
2. decide the experiment naming scheme
3. assign responsibilities
4. create a common feature specification document
5. create a result logging template

### Recommended folder structure

```text
project/
  PASYDA/
  notebooks/
  src/
    data_processing/
    features/
    models/
    evaluation/
  outputs/
    eda/
    features/
    metrics/
    plots/
  reports/
    experiment_reports/
    summary_report/
  docs/
```

---

## Phase 1: Data Audit and Cleaning

### Goals

- verify the structure of every scenario
- make sure labels are constructed correctly

### Tasks

1. load all `data`, `vic_data`, and `solutions` CSV files
2. ignore archive junk such as `__MACOSX`
3. verify:
   - `solutions ⊂ vic_data`
   - `vic_data ⊂ data`
4. for each scenario:
   - identify the central node
   - identify the 11 candidate contacts
   - identify the true pair from `solutions`
5. produce a data audit table with:
   - rows per file
   - unique nodes
   - time range
   - positive/negative sample counts

### Output

- cleaned scenario inventory
- verified labels
- pair construction logic

---

## Phase 2: Exploratory Data Analysis

### Goals

- understand patterns before modeling
- justify feature engineering choices

### EDA to perform

#### Dataset-level EDA

- row counts per file
- number of nodes per scenario
- scenario time ranges
- total positives vs negatives

#### Network-level EDA

- node activity counts in `vic_data`
- central node dominance
- pair-level communication ranks

#### Pair-level EDA

- message count per pair
- message length statistics
- time-of-day activity
- duration of pair interaction
- inter-message gap behavior
- burstiness

### Visuals to include

- histograms of message lengths
- boxplots of pair-level feature distributions
- rankings of candidate pairs by message count
- timelines of true pair vs non-true pairs
- class imbalance visualization

### Important EDA result to test and report

You should explicitly test whether simple heuristics work:

- highest message count
- shortest average message length
- highest night activity

If simple heuristics fail or only partially work, that strongly justifies the ML models.

---

## Phase 3: Pair-Level Dataset Construction

### Goals

- convert each scenario into modeling-ready samples

### Procedure for each scenario

1. detect the central node in `vic_data`
2. list all 11 central-node contacts
3. create one sample per central-contact pair
4. use `solutions` to label:
   - `1` = true grooming pair
   - `0` = non-grooming pair

### Result

Across the whole dataset:

- 10 scenarios
- 11 candidate pairs per scenario
- about 110 pair-level samples total
- 10 positives
- 100 negatives

---

## Phase 4: Feature Engineering

### Goals

- extract strong, explainable features
- support fair comparison across model families

## Feature Set A: `vic_data` only

For each pair, extract:

- total message count
- share of central-node total traffic
- outgoing count
- incoming count
- outgoing/incoming ratio
- average message length
- median message length
- minimum message length
- maximum message length
- standard deviation of message length
- interaction duration
- number of active days
- mean inter-message gap
- std inter-message gap
- burst ratio under 5 minutes
- burst ratio under 30 minutes
- night activity ratio
- evening activity ratio
- first appearance offset
- last appearance offset
- rank by pair message count within scenario
- rank by traffic share within scenario

## Feature Set B: `vic_data` + context from full `data`

Add:

- central node total activity in full scenario
- central node degree in full scenario
- pair count relative to other contacts
- pair-level z-score within scenario
- concentration of central-node communication
- pair share relative to full-scenario behavior

## Ablation feature set

Create a third feature variant:

- all features **except message-length-based features**

This is important because `Length` may be an overly strong synthetic cue.

---

## Phase 5: Experimental Design

## Outer evaluation

Use **5-fold grouped evaluation by dataset folder**:

- Fold 1: train on D2-D5, test on D1
- Fold 2: train on D1,D3,D4,D5, test on D2
- Fold 3: train on D1,D2,D4,D5, test on D3
- Fold 4: train on D1,D2,D3,D5, test on D4
- Fold 5: train on D1-D4, test on D5

## Inner tuning

Inside each outer fold:

- use only the training folds for tuning
- never use the held-out test folder for tuning

### Validation options

Preferred:

- grouped inner split by scenario or folder

Acceptable:

- one held-out training scenario for validation

## Leakage rules

1. scale using training fold only
2. tune hyperparameters using training data only
3. never use test fold statistics in preprocessing
4. keep feature extraction logic fixed across folds

---

## Phase 6: Models

## Baselines

You should include at least these heuristic baselines:

1. highest message count
2. lowest mean message length
3. optional night-activity heuristic

These are useful because they show whether the ML models are truly adding value.

## Model 1: Random Forest

Suggested starting range:

- `n_estimators`: 200 to 300
- `max_depth`: 3 to 6
- `min_samples_leaf`: 2 to 3
- `class_weight = balanced`

## Model 2: SVM

Suggested setup:

- kernel: `RBF`
- scale features first
- tune `C`
- tune `gamma`
- `class_weight = balanced`

## Model 3: MLP

Suggested setup:

- architecture: `64 -> 32`
- dropout: `0.2` to `0.3`
- learning rate: around `1e-3`
- batch size: `8` or `16`
- early stopping patience: about `10`
- weighted loss

---

## Phase 7: Evaluation

## Primary metric

Use:

- **Top-1 Accuracy per scenario**

This best matches the real task:

> did the model rank the true pair highest among the 11 candidates?

## Secondary metrics

Also report:

- Mean Reciprocal Rank (MRR)
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC

## Critical analysis to include

- compare false positives vs false negatives
- identify which negative pairs are hard to separate
- discuss which features drive each model
- explain whether the model is learning realistic behavior or synthetic shortcuts

---

## Phase 8: Final Experiment Portfolio

## Important reporting rule

Do **not** treat each fold as a separate experiment report.

Each experiment report should describe one **model configuration**, with the 5-fold grouped evaluation results summarized inside it.

## Recommended experiment portfolio

### Baselines

1. Baseline 1: highest message count
2. Baseline 2: lowest mean message length

### Random Forest

3. RF with `vic_data` features
4. RF with `vic_data + context` features
5. RF ablation without message-length features

### SVM

6. SVM with `vic_data` features
7. SVM with `vic_data + context` features
8. SVM ablation without message-length features

### MLP

9. MLP with `vic_data` features
10. MLP with `vic_data + context` features
11. MLP ablation without message-length features

### Optional extension experiments

12. RF hyperparameter refinement experiment
13. SVM kernel/tuning comparison
14. MLP architecture sensitivity experiment
15. final best-model rerun with fixed settings

## Recommended minimum portfolio

If time is limited, the safest minimum is:

- Experiments 1 to 11

That gives a strong portfolio while staying manageable.

---

## Phase 9: Team Structure

## Member 1: Data, EDA, and Feature Engineering Lead

### Owns

- dataset audit
- pair construction
- EDA
- feature extraction
- final shared feature tables

### Main outputs

- cleaned data pipeline
- feature dictionary
- EDA plots
- modeling-ready CSV/dataframes

## Member 2: Classical ML Lead

### Owns

- heuristic baselines
- Random Forest
- SVM
- grouped evaluation engine for classical models

### Main outputs

- baseline reports
- RF reports
- SVM reports
- metric tables and comparison charts

## Member 3: Deep Learning and Integration Lead

### Owns

- MLP model
- DL tuning
- final comparison tables
- final integration of results into the summary report and presentation

### Main outputs

- MLP reports
- final comparison discussion
- final summary write-up support

## Shared team rules

Everyone must use:

- the same sample definition
- the same feature versions
- the same fold structure
- the same metric definitions
- the same experiment naming convention

---

## Phase 10: Report and Submission Plan

## Required submission package

1. **Cover page**
   - module code
   - module name
   - assessment title
   - group members' names
   - group members' logins

2. **Experiment index**
   - experiment ID
   - objective
   - data used
   - model used
   - feature set used
   - evaluation setup
   - main findings

3. **Separate experiment reports**
   - one report per experiment
   - use the provided experiment template

4. **4-page summary report**
   - summarize all work
   - justify methodology
   - present and analyze final results
   - discuss limitations
   - explain what extra metadata should have been included
   - explain how the work could be improved

5. **Code archive**
   - not explicitly required in the brief
   - strongly recommended if the submission system allows it

## Suggested experiment report format

Use the supplied structure:

- Experiment No
- Date
- Name
- Objective
- Tools used
- Data used
- Procedure
- Results
- Analysis

## Suggested 4-page summary report structure

### Page 1

- problem statement
- dataset understanding
- pair-level task definition

### Page 2

- feature engineering
- experimental setup
- grouped evaluation strategy

### Page 3

- model comparison
- main results
- best model discussion

### Page 4

- limitations
- synthetic data concerns
- false positive/false negative implications
- extra metadata needed
- future improvements

---

## Phase 11: Final Quality Checks

Before submission, verify:

1. labels are correct
2. no fold leakage exists
3. all reported metrics are computed consistently
4. all experiment reports follow the same template
5. the 4-page summary stays within the page limit
6. the cover page and experiment index are included
7. all Generative AI use is disclosed if used

---

## 12. Final Recommendation

## Does the plan need to change?

### Short answer

**No major change is needed.**

The current plan is already strong and aligned with the real structure of the dataset.

### What has been updated

This updated version improves the existing plan by:

1. clarifying that the task is **pair-level ranking/classification**
2. clarifying that **folds are evaluation, not separate report experiments**
3. aligning the workflow with the actual assignment deliverables
4. tightening the submission structure
5. making the deep learning choice explicit and defensible

## Final recommended core workflow

Use:

- pair-level samples
- grouped 5-fold evaluation by dataset folder
- models:
  - Random Forest
  - SVM
  - MLP
- feature sets:
  - `vic_data` only
  - `vic_data + context`
  - no-length ablation
- separate experiment reports with aggregated fold results
- one final 4-page summary report

That is the most rigorous, realistic, and full-marks-oriented plan for this project.
