# Dataset notes

`users_behavior.csv` is a small simulated dataset created for learning and portfolio demonstration.

- It contains 10 synthetic users and no personal information.
- `drop_out` is the analysis outcome: `0` means retained and `1` means dropout.
- `session_time` is treated as seconds.
- The original source does not define the unit for `time_on_platform`, the observation window for `clicks`, or the business event represented by `decision`.
- `decision` perfectly matches the inverse of `drop_out` in this sample. It must be treated as a possible leakage variable rather than a trustworthy model feature.

The dataset is too small for reliable inference or machine-learning evaluation. Results should be interpreted as demonstrations of an analytical workflow only.
