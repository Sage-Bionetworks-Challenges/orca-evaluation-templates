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

from utils import extract_gs_file

# ---- CUSTOMIZATION REQUIRED ----

# Goldstandard columns and data type.
GOLDSTANDARD_COLS = {
    "id": str,
    "disease": int,
}

# Expected columns and data types for predictions file.
PREDICTION_COLS = {
    "id": str,
    "probability": float,
}


def score(gold_file: str, pred_file: str) -> dict:
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
    gold = pd.read_csv(
        gold_file,
        usecols=GOLDSTANDARD_COLS,
        dtype=GOLDSTANDARD_COLS,
    )

    # Join the two dataframes so to ensure the order of the IDs are the same
    # between goldstandard and prediction before scoring.
    merged = gold.merge(pred, how="left", on="id")
    roc = roc_auc_score(merged["disease"], merged["probability"])
    precision, recall, _ = precision_recall_curve(
        merged["disease"], merged["probability"]
    )
    return {"auc_roc": roc, "auprc": auc(recall, precision)}


# ----- END OF CUSTOMIZATION -----


def main(
    predictions_file: Annotated[
        str,
        typer.Option(help="Path to the prediction file."),
    ],
    goldstandard_folder: Annotated[
        str,
        typer.Option(
            help="Path to the folder containing the goldstandard file.",
        ),
    ],
    output_file: Annotated[
        str,
        typer.Option(help="Path to save/update the results JSON file."),
    ] = "results.json",
):
    """
    Scores predictions against the goldstandard and updates the results
    JSON file with scoring status and metrics.
    """
    # ----- IMPORTANT: Core Workflow Function Logic -----
    # This function contains essential logic for interacting with ORCA
    # workflow. Modifying this function is strongly discouraged and may
    # cause issues with ORCA. Proceed with caution.
    # ---------------------------------------------------

    scores = {}
    status = "INVALID"
    with open(output_file, encoding="utf-8") as out:
        res = json.load(out)

    if res.get("validation_status") == "VALIDATED":
        gold_file = extract_gs_file(goldstandard_folder)
        try:
            scores = score(gold_file, predictions_file)
            status = "SCORED"
            errors = ""
        except ValueError:
            errors = "Error encountered during scoring; submission not evaluated."
    else:
        errors = "Submission could not be evaluated due to validation errors."

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
