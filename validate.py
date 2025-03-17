#!/usr/bin/env python3
"""Template validation script.

At a minimum, you will need to customize the following variables
and the `validate` function to fit your specific validation needs.
You can add additional functions and dependencies as needed.
"""
import json

import pandas as pd
import typer
from cnb_tools import validation_toolkit as vtk
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


def validate(gold_file: str, pred_file: str) -> list[str]:
    """Sample validation function.

    Checks include:
        - Prediction file has the expected columns and data types
        - There is exactly one prediction for each ID
        - Every ID has a prediction
        - There are no predictions for IDs not present in the goldstandard
        - Prediction values are not null
        - Prediction values are between 0 and 1, inclusive

    Returns a list of error messages. An empty list signifies successful
    validation.

    !!! Note: any updates to this function must maintain the return type
    of a list of strings.
    """
    errors = []
    gold = pd.read_csv(
        gold_file,
        usecols=GOLDSTANDARD_COLS,
        dtype=GOLDSTANDARD_COLS,
    )
    try:
        pred = pd.read_csv(
            pred_file,
            usecols=PREDICTION_COLS,
            dtype=PREDICTION_COLS,
            float_precision="round_trip",
        )
    except ValueError as err:
        errors.append(
            f"Invalid column names and/or types: {str(err)}. "
            f"Expecting: {str(PREDICTION_COLS)}."
        )
    else:
        errors.append(vtk.check_duplicate_keys(pred["id"]))
        errors.append(vtk.check_missing_keys(gold["id"], pred["id"]))
        errors.append(vtk.check_unknown_keys(gold["id"], pred["id"]))
        errors.append(vtk.check_nan_values(pred["probability"]))
        errors.append(
            vtk.check_values_range(
                pred["probability"],
                min_val=0,
                max_val=1,
            )
        )

    # Remove any empty strings from the list before return.
    return filter(None, errors)


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
        typer.Option(help="Path to save the results JSON file."),
    ] = "results.json",
):
    """Validates the predictions file in preparation for evaluation."""

    # ----- IMPORTANT: Core Workflow Function Logic -----
    # This function contains essential logic for interacting with ORCA
    # workflow. Modifying this function is strongly discouraged and may
    # cause issues with ORCA. Proceed with caution.
    # ---------------------------------------------------

    if "INVALID" in predictions_file:
        with open(predictions_file, encoding="utf-8") as f:
            errors = [f.read()]
    else:
        gold_file = extract_gs_file(goldstandard_folder)
        errors = validate(gold_file=gold_file, pred_file=predictions_file)

    invalid_reasons = "\n".join(errors)
    status = "INVALID" if invalid_reasons else "VALIDATED"

    # Truncate validation errors if >500 (char limit for sending Synapse email)
    if len(invalid_reasons) > 500:
        invalid_reasons = invalid_reasons[:496] + "..."
    res = {
        "validation_status": status,
        "validation_errors": invalid_reasons,
    }

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(json.dumps(res))
    print(status)


if __name__ == "__main__":
    # Prevent replacing underscore with dashes in CLI names.
    typer.main.get_command_name = lambda name: name
    typer.run(main)
