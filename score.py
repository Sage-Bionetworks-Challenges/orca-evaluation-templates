#!/usr/bin/env python3
"""Template scorintg script.

Script is currently designed for evaluating submissions for a
single-task challenge.

At a minimum, you will need to:
    1. Define the expected data structures (see GROUNDTRUTH_COLS and
       PREDICTION_COLS)
    2. Customize score_task1() to fit your specific scoring needs
    3. Add helper functions and manage dependencies as needed for your
       scoring process

For challenges with multiple tasks, create additional `score_task*()`
functions and update the `score()` function to route evaluation to
the appropriate task.
"""
import json

import pandas as pd
import typer
from sklearn.metrics import auc, precision_recall_curve, roc_auc_score
from typing_extensions import Annotated

from utils import extract_gt_file

# ---- CUSTOMIZATION REQUIRED ----

# Groundtruth columns and data type.
GROUNDTRUTH_COLS = {
    "id": str,
    "disease": int,
}

# Expected columns and data types for predictions file.
PREDICTION_COLS = {
    "id": str,
    "probability": float,
}


def score_task1(gt_file: str, pred_file: str) -> dict[str, int | float]:
    """Sample scoring function.

    Metrics returned:
        - AUC-ROC
        - AUCPR

    !!! Note: any updates to this function must maintain the return type
    of a dictionary, where keys are the metric names and values are the
    corresponding scores.
    """
    pred = pd.read_csv(
        pred_file,
        usecols=PREDICTION_COLS,
        dtype=PREDICTION_COLS,
        float_precision="round_trip",
    )
    truth = pd.read_csv(
        gt_file,
        usecols=GROUNDTRUTH_COLS,
        dtype=GROUNDTRUTH_COLS,
    )

    # Join the two dataframes to ensure the order of the IDs are the same
    # between groundtruth and prediction before scoring.
    merged = truth.merge(pred, how="left", on="id")
    roc = roc_auc_score(merged["disease"], merged["probability"])
    precision, recall, _ = precision_recall_curve(
        merged["disease"], merged["probability"]
    )
    return {"auc_roc": roc, "auprc": auc(recall, precision)}


# --- Add more scoring functions for different tasks if needed ---
# def score_task2(gt_file: str, pred_file: str) -> dict[str, int | float]:
#     pass


def score(challenge_task: str, gt_file: str, pred_file: str) -> dict[str, int | float]:
    """
    Routes evaluation to the appropriate task-specific function.
    """
    scoring_func = {
        "task1": score_task1,
        # --- Add more tasks and their validation functions here ---
        # "task_2": score_task2,
    }.get(challenge_task)

    if scoring_func:
        return scoring_func(gt_file=gt_file, pred_file=pred_file)
    raise LookupError


# ----- END OF CUSTOMIZATION -----


def main(
    predictions_file: Annotated[
        str,
        typer.Option(
            "-p",
            "--predictions_file",
            help="Path to the prediction file.",
        ),
    ],
    groundtruth_folder: Annotated[
        str,
        typer.Option(
            "-g",
            "--groundtruth_folder",
            help="Path to the folder containing the groundtruth file.",
        ),
    ],
    task: Annotated[
        str,
        typer.Option(
            "-t",
            "--task",
            help="Challenge task for which to evaluate the predictions file.",
        ),
    ] = "task1",
    output_file: Annotated[
        str,
        typer.Option(
            "-o",
            "--output_file",
            help="Path to save the results JSON file.",
        ),
    ] = "results.json",
):
    """
    Scores predictions against the groundtruth and updates the results
    JSON file with scoring status and metrics.
    """

    # ----- IMPORTANT: Core Workflow Function Logic -----
    # This function contains essential logic for interacting with ORCA
    # workflow. Modifying this function is strongly discouraged and may
    # cause issues with ORCA. Proceed with caution.
    # ---------------------------------------------------

    scores = {}
    status = "INVALID"
    try:
        with open(output_file, encoding="utf-8") as out:
            res = json.load(out)
    except (FileNotFoundError, json.decoder.JSONDecodeError):

        # Notify that absent validation results may lead to inaccurate
        # or skewed scores (e.g. due to multiple predictions per ID, etc).
        res = {
            "validation_status": "",
            "validation_errors": (
                "Validation results not found. Proceeding with scoring but it "
                "may fail or results may be inaccurate."
            ),
        }

    # Do not attempt to score if previous validations failed. Otherwise,
    # proceed with evaluating predictions.
    if res.get("validation_status") == "INVALID":
        errors = "Submission could not be evaluated due to validation errors."
    else:
        gt_file = extract_gt_file(groundtruth_folder)
        try:
            scores = score(
                challenge_task=task,
                gt_file=gt_file,
                pred_file=predictions_file,
            )
            status = "SCORED"
            errors = ""
        except ValueError:
            errors = "Error encountered during scoring; submission not evaluated."
        except LookupError:
            errors = f"Invalid challenge task specified: `{task}`"

    res |= {
        "score_status": status,
        "score_errors": errors,
        **scores,
    }
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(json.dumps(res))
    print(status)


if __name__ == "__main__":
    # Prevent replacing underscore with dashes in CLI names.
    typer.main.get_command_name = lambda name: name
    typer.run(main)
