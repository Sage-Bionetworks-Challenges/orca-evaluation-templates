#!/usr/bin/env python3
"""Template scoring script.

At a minimum, you will need to customize the following variables
and the `score` function to fit your specific scoring needs. You
can add additional functions and dependencies as needed.
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


def score(gt_file: str, pred_file: str) -> dict[str, int | float]:
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
    real = pd.read_csv(
        gt_file,
        usecols=GROUNDTRUTH_COLS,
        dtype=GROUNDTRUTH_COLS,
    )

    # Join the two dataframes to ensure the order of the IDs are the same
    # between groundtruth and prediction before scoring.
    merged = real.merge(pred, how="left", on="id")
    roc = roc_auc_score(merged["disease"], merged["probability"])
    precision, recall, _ = precision_recall_curve(
        merged["disease"], merged["probability"]
    )
    return {"auc_roc": roc, "auprc": auc(recall, precision)}


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
        res = {
            "validation_status": "",
            "validation_errors": "",
        }

    # Notify that absent validation results may lead to inaccurate scores
    # (e.g., due to multiple predictions per ID, missing predictions, etc).
    if not res.get("validation_status"):
        print(
            "Validation results not found. Proceeding with scoring but "
            "results may be inaccurate."
        )

    # Do not attempt to score if previous validations failed. Otherwise,
    # proceed with evaluating predictions.
    if res.get("validation_status") == "INVALID":
        errors = "Submission could not be evaluated due to validation errors."
    else:
        gt_file = extract_gt_file(groundtruth_folder)
        try:
            scores = score(gt_file, predictions_file)
            status = "SCORED"
            errors = ""
        except ValueError as err:
            errors = "Error encountered during scoring; submission not evaluated."
            print(f"Error encountered: {err}")

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
