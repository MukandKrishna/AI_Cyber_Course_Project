# PASYDA EDA Report Summary

This file explains what the notebook did, what the outputs show, and what the team should do next.

Notebook used:
- [PASYDA_EDA_Final.ipynb](</D:/Kent Files/AI_Cyber/project/PASYDA_EDA_Final.ipynb>)

Main output folder:
- [outputs/eda](</D:/Kent Files/AI_Cyber/project/outputs/eda>)

## 1. What This EDA Did

The notebook was written to match the real PASYDA task more closely than the first short version.

Instead of treating each message row as one machine learning sample, it used the better unit:

- one central node
- one contact node
- one pair-level sample

For each scenario, the notebook:

- loaded `data`, `vic_data`, and `solutions`
- checked that `solutions` is inside `vic_data`
- checked that `vic_data` is inside `data`
- found the central node
- created the 11 candidate pairs
- labelled the true pair as positive
- extracted pair-level features
- compared positive vs negative pairs
- checked whether simple heuristics were enough

This means the EDA now matches the project methodology much better.

## 2. Files Produced

Main audit and feature files:

- [scenario_index.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/scenario_index.csv>)
- [scenario_audit.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/scenario_audit.csv>)
- [pair_level_features.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/pair_level_features.csv>)
- [pair_level_label_check.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/pair_level_label_check.csv>)
- [feature_comparison_by_label.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/feature_comparison_by_label.csv>)
- [feature_gaps_ranked.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/feature_gaps_ranked.csv>)
- [positive_pair_ranks.csv](</D:/Kent Files/AI_Cyber/project/outputs/eda/positive_pair_ranks.csv>)

Plots:

- [01_dataset_overview.png](</D:/Kent Files/AI_Cyber/project/outputs/eda/01_dataset_overview.png>)
- [02_positive_vs_negative_boxplots.png](</D:/Kent Files/AI_Cyber/project/outputs/eda/02_positive_vs_negative_boxplots.png>)
- [03_positive_pair_ranks.png](</D:/Kent Files/AI_Cyber/project/outputs/eda/03_positive_pair_ranks.png>)

## 3. What Happened in the Data

### Structure checks

The audit results are strong and clean:

- 10 scenarios were found
- 5 dataset folders were found
- every scenario passed the subset checks
- every `vic_data` file had 12 unique nodes
- every scenario produced 11 candidate pairs
- every scenario produced exactly 1 positive pair

This is important because it confirms that the pair-level setup is valid.

### Class balance

At pair level:

- total pairs = 110
- positive pairs = 10
- negative pairs = 100
- positive rate = 9.09%

This is a clear imbalance, but it is the correct imbalance for the actual task.

### Scenario size variation

The scenario sizes vary a lot:

- smallest `vic_data` scenario = 2,427 rows
- largest `vic_data` scenario = 11,654 rows

This means some scenarios are much denser than others, so raw counts alone may not generalize well.

## 4. Main EDA Findings

The feature comparison output gives some strong early signals.

### Positive pairs tend to have:

- more messages than negative pairs
- longer total conversation duration
- much shorter average message lengths
- more evening activity
- more night-time activity
- slightly shorter average gaps between messages
- a larger share of the whole scenario traffic

### Positive pairs tend to have less:

- reciprocity balance
- weekend activity

## 5. Most Useful Findings

These were the strongest differences in the output:

1. `duration_hours`
   Positive mean: 817.55
   Negative mean: 696.84

2. `message_count`
   Positive mean: 568.40
   Negative mean: 498.96

3. `mean_length`
   Positive mean: 20.90
   Negative mean: 52.65

4. `median_length`
   Positive mean: 16.50
   Negative mean: 44.58

5. `evening_ratio`
   Positive mean: 0.586
   Negative mean: 0.284

These are useful because they suggest the grooming-related pair is not just “bigger” in one simple way. It looks different across multiple dimensions:

- shorter messages
- more evening and night activity
- more concentrated pair activity
- somewhat weaker reciprocity

That is exactly the kind of pattern that supports feature engineering and multi-feature modelling.

## 6. Are The Analyses Good And Useful?

Short answer:

- yes, this EDA is useful
- yes, it gives real modelling insight
- no, it is not enough by itself
- no, it should not be treated as proof that a simple rule can solve the task

### Why it is good

This EDA is good because:

- it uses the correct pair-level sample unit
- it validates the dataset structure properly
- it creates report-ready plots
- it gives interpretable features for later modelling
- it shows that the task is more complex than one easy heuristic

### Why it is useful

It is useful for:

- writing the dataset understanding section
- writing the EDA section
- justifying feature engineering choices
- designing baseline heuristics
- explaining why grouped evaluation is needed

### Why it is not enough on its own

It still has limits:

- only 10 positive samples exist at pair level
- the dataset is synthetic metadata, not raw conversation text
- this is descriptive EDA, not a predictive evaluation
- some mean differences may look strong but still fail on held-out scenarios
- there are no statistical significance tests here
- there is not yet a proper model evaluation section

So this EDA is strong as a foundation, but not the final answer.

## 7. What The Heuristic Check Tells Us

The heuristic ranking output is very useful.

### Rank of the true pair by message count

- top-1 in 0 out of 10 scenarios
- average rank = 4.2

### Rank of the true pair by duration

- top-1 in 3 out of 10 scenarios
- average rank = 2.7

### Rank of the true pair by reciprocity

- top-1 in 0 out of 10 scenarios
- average rank = 9.7

### Meaning

This is a strong result.

It tells us:

- message count alone is not enough
- reciprocity alone is actually a weak standalone clue
- duration is somewhat useful, but still not enough
- the real signal is probably a combination of features

This supports using:

- Random Forest
- SVM
- MLP

instead of relying only on hand-made rules.

## 8. Important Interpretation Notes

These points should be stated clearly in the final report:

1. The EDA is pair-level, not message-level.
   This is a strength because it matches the real task.

2. The positive class is very small.
   This means model evaluation must be careful and grouped by dataset folder.

3. The strongest feature patterns are plausible but not perfectly stable.
   For example, some scenarios such as `perp_4` and `perp_6` look harder than others in the ranking plots.

4. Some features may be scenario-specific.
   Raw values like message count can be influenced by overall scenario size, so normalized and relative features may become even more important later.

## 9. What We Need To Do Next

The next steps should be practical and ordered.

### Next step 1: Freeze the pair-level dataset

Use `pair_level_features.csv` as the working feature table for the modelling stage.

### Next step 2: Add a few stronger contextual features

Recommended additions:

- pair message count rank within scenario
- pair duration rank within scenario
- z-score of message count inside each scenario
- z-score of duration inside each scenario
- fraction of late-night messages after midnight only
- first-day intensity and last-day intensity
- ratio of very short messages
- direction-switch frequency

These features may be stronger than raw counts alone.

### Next step 3: Build baseline heuristics

Create simple baselines such as:

- highest message count
- longest duration
- shortest average message length
- highest evening activity
- weighted combination of 2 or 3 simple features

This gives a fair reference point before training full models.

### Next step 4: Run grouped evaluation by dataset folder

Use the 5 dataset folders as groups.

That means:

- train on 4 folders
- test on 1 held-out folder
- repeat for all 5 folds

This is much better than a random split for this dataset.

### Next step 5: Train the planned models

Train at least:

- Random Forest
- SVM
- MLP

Use the same folds and same feature table for all of them.

### Next step 6: Use the right metrics

The most relevant metrics for this task are:

- Top-1 Accuracy per scenario
- Mean Reciprocal Rank
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC

Top-1 Accuracy and MRR are especially important because the real task is to identify the correct pair among 11 candidates.

## 10. Final Judgement

This EDA is a good and useful piece of work.

It:

- follows the real task structure
- validates the data properly
- gives pair-level insight
- produces useful report evidence
- shows that multi-feature modelling is justified

But it should be described honestly:

- it is a strong exploratory foundation
- it is not yet a complete experiment
- it does not yet prove model performance

## 11. Recommended Report Wording

You can say something close to this in your report:

> Exploratory analysis was conducted at pair level rather than message level, because inspection of the PASYDA victim-network files showed that each scenario contains one central node connected to 11 contact nodes, with exactly one true grooming-related pair identified by the solutions file. The EDA confirmed consistent structure across all 10 scenarios and showed that positive pairs tend to differ from negative pairs in several behavioural features, including shorter message length, greater evening and night activity, higher conversation volume, and longer interaction duration. However, heuristic ranking based on any single feature was not sufficient to identify the true pair consistently, which justified the use of multi-feature machine learning models under grouped evaluation by dataset folder.

## 12. Bottom Line

If the question is:

“Are these analyses good and useful?”

The answer is:

- yes, for EDA and feature design
- yes, for report evidence
- yes, for justifying the modelling approach
- but only if the team now follows through with proper grouped model evaluation
