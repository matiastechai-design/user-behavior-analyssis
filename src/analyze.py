"""Reproduce the descriptive user-behavior analysis and save its figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "users_behavior.csv"
FIGURE_DIR = ROOT / "reports" / "figures"
REQUIRED_COLUMNS = {
    "user_id",
    "age",
    "time_on_platform",
    "clicks",
    "session_time",
    "decision",
    "drop_out",
}


def load_and_validate(path: Path) -> pd.DataFrame:
    """Load the source CSV and fail clearly when its basic contract changes."""
    frame = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if frame.empty:
        raise ValueError("The dataset is empty.")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Required columns contain missing values.")
    if frame["user_id"].duplicated().any():
        raise ValueError("user_id must be unique.")
    if not frame["drop_out"].isin([0, 1]).all():
        raise ValueError("drop_out must contain only 0 or 1.")
    if not frame["decision"].isin(["yes", "no"]).all():
        raise ValueError("decision must contain only 'yes' or 'no'.")

    non_negative = ["age", "time_on_platform", "clicks", "session_time"]
    if (frame[non_negative] < 0).any().any():
        raise ValueError("Numeric engagement fields cannot be negative.")

    return frame


def summarize(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the verified descriptive metrics used in the README."""
    summary = (
        frame.groupby("drop_out")
        .agg(
            users=("user_id", "count"),
            average_age=("age", "mean"),
            average_time_on_platform=("time_on_platform", "mean"),
            average_clicks=("clicks", "mean"),
            average_session_time=("session_time", "mean"),
        )
        .rename(index={0: "retained", 1: "dropout"})
        .round(1)
    )
    return summary


def save_figures(frame: pd.DataFrame, output_dir: Path) -> None:
    """Create recruiter-friendly descriptive figures without predictive claims."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    plot_frame = frame.assign(
        status=frame["drop_out"].map({0: "Retained", 1: "Dropout"})
    )
    metrics = [
        ("time_on_platform", "Time on platform"),
        ("clicks", "Clicks"),
        ("session_time", "Session time (seconds)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for axis, (column, label) in zip(axes, metrics):
        sns.barplot(
            data=plot_frame,
            x="status",
            y=column,
            hue="status",
            errorbar=None,
            palette={"Retained": "#287271", "Dropout": "#D65A4A"},
            legend=False,
            ax=axis,
        )
        axis.set(xlabel="", ylabel=label)
        axis.set_title(label)
    fig.suptitle("Average engagement by dropout status", fontweight="bold")
    fig.tight_layout()
    fig.savefig(output_dir / "engagement_by_dropout.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    matrix = pd.crosstab(frame["decision"], frame["drop_out"])
    matrix = matrix.reindex(index=["yes", "no"], columns=[0, 1], fill_value=0)
    fig, axis = plt.subplots(figsize=(6, 4))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axis)
    axis.set(
        title="Decision and dropout are perfectly aligned",
        xlabel="Dropout (0 = retained, 1 = dropout)",
        ylabel="Decision",
    )
    fig.tight_layout()
    fig.savefig(output_dir / "decision_dropout_matrix.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    frame = load_and_validate(DATA_PATH)
    print(f"Rows: {len(frame)} | Columns: {len(frame.columns)}")
    print(f"Missing values: {int(frame.isna().sum().sum())}")
    print(f"Duplicate user IDs: {int(frame['user_id'].duplicated().sum())}")
    print("\nSummary by outcome:")
    print(summarize(frame).to_string())
    print("\nDecision/dropout cross-tabulation:")
    print(pd.crosstab(frame["decision"], frame["drop_out"]).to_string())
    save_figures(frame, FIGURE_DIR)
    print(f"\nFigures saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
