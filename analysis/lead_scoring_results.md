# Lead scoring results

- Leads: 8,000 (6,000 to train, 2,000 to test)
- Training period: 14 Jun 2017 to 15 Apr 2018
- Test period: 16 Apr 2018 to 31 May 2018
- Close rate in the test period: 10.5%

| Model                              |   ROC AUC |   Average precision | Close rate in top 10% of scores   | Lift over average   |
|:-----------------------------------|----------:|--------------------:|:----------------------------------|:--------------------|
| Channel close rate only (baseline) |     0.613 |               0.143 | 19.5%                             | 1.85x               |
| Logistic regression                |     0.69  |               0.19  | 23.0%                             | 2.18x               |
