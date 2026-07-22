I’ve read the project files and outputs. The project is in a good position, but it is not finished yet.

**Project Understanding**

This is a COMP7029 AI + Cyber Security project on detecting online grooming using the PASYDA synthetic metadata dataset.

The most important methodological decision is already correct:

Use **pair-level samples**, not individual message rows.

Each scenario has:

- 1 central node
- 11 candidate contact pairs
- exactly 1 true grooming-related pair
- 10 scenarios total
- therefore 110 pair-level samples: 10 positive, 100 negative

Your current EDA has already validated the dataset structure and produced useful feature outputs in:

`outputs/eda/pair_level_features.csv`

The EDA also found that single-feature heuristics are not enough. For example, the true pair is never top-1 by message count, and duration only gets top-1 in 3 of 10 scenarios. That strongly supports using multi-feature models.

**What Is Already Done**

You already have:

- assignment brief and marking criteria understood
- project methodology planned
- team structure planned
- pair-level EDA notebook completed
- dataset audit completed
- feature table created
- EDA plots created
- report-ready EDA summary written

The strongest existing files are:

- `Updated_Grooming_Project_Plan.md`
- `PASYDA_EDA_Final.ipynb`
- `PASYDA_EDA_Report_Summary.md`
- `outputs/eda/pair_level_features.csv`

**What Is Missing**

The main missing work is the actual modelling and report portfolio.

I did not see a proper `src/` modelling pipeline, metrics output, experiment reports, or final summary report yet.

So the next major task is:

Build the grouped evaluation pipeline and run the experiments.

**Recommended Next Steps**

1. **Freeze the current feature table**

Use:

`outputs/eda/pair_level_features.csv`

as the modelling input.

2. **Add stronger contextual features**

Add features such as:

- rank of message count within scenario
- rank of duration within scenario
- scenario-level z-scores
- short-message ratio
- late-night ratio
- first-day / last-day intensity
- direction-switch frequency

These will improve model quality and help your feature-engineering mark.

3. **Create the modelling pipeline**

Use grouped 5-fold evaluation by dataset folder:

- train on 4 dataset folders
- test on 1 held-out folder
- repeat for all 5 folders

This avoids leakage and matches the marking criteria.

4. **Run baseline experiments**

Start with simple baselines:

- highest message count
- longest duration
- lowest mean message length
- possibly a weighted heuristic

These are needed so your ML models have something fair to beat.

5. **Train the required model families**

Minimum recommended models:

- Random Forest
- SVM
- small MLP

Use the same folds, same feature sets, and same metrics for all models.

6. **Use the right metrics**

The most important metrics should be:

- Top-1 accuracy per scenario
- Mean Reciprocal Rank
- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC

Top-1 accuracy and MRR are especially important because the real task is ranking 11 candidate pairs and identifying the correct one.

7. **Prepare the experiment portfolio**

The brief says every experiment needs a separate report. Do not treat each fold as a separate experiment report.

A strong minimum portfolio would be:

- 2 heuristic baselines
- RF with base features
- RF with contextual features
- RF without message-length features
- SVM with base features
- SVM with contextual features
- SVM without message-length features
- MLP with base features
- MLP with contextual features
- MLP without message-length features

That gives 11 experiment reports.

8. **Write the 4-page summary report**

Suggested structure:

- Page 1: problem, dataset, pair-level task definition
- Page 2: feature engineering and grouped evaluation
- Page 3: model comparison and best results
- Page 4: limitations, false positives/negatives, missing metadata, improvements

**Most Urgent Recommendation**

Because the brief deadline in the document is **Friday, 12 June 2026**, and today is **Tuesday, 9 June 2026**, the best next step is not more planning. It is to implement the modelling pipeline immediately.

I would do this next:

Create a clean `src/` pipeline that loads `pair_level_features.csv`, adds contextual features, runs baselines/RF/SVM/MLP with grouped evaluation, and saves metrics tables ready for the experiment reports.