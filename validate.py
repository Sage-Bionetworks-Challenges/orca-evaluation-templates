#!/usr/bin/env python3
"""Template validation script.

Script is currently designed for validating submission for a single-
task challenge.

At a minimum, you will need to:
    1. Define the expected data structures (see GROUNDTRUTH_COLS and
       PREDICTION_COLS)
    2. Customize validate_task1() to fit your specific validation needs
    3. Add helper functions and manage dependencies as needed for your
       validation process

For challenges with multiple tasks, create additional `validate_task*()`
functions and update the `validate()` function to route validation to
the appropriate task.
"""
import json

import pandas as pd
import typer
from cnb_tools import validation_toolkit as vtk
from typing_extensions import Annotated

# Uncomment the following if any files are tarfile/zipfiles and require extraction.
from utils import extract_gt_file #,inspect zip

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


def validate_task1(gt_file: str, pred_file: str) -> list[str] | filter:
    """Sample validation function.

    Checks include:
        - Prediction file has the expected columns and data types
        - There is exactly one prediction for each ID
        - Every ID has a prediction
        - There are no predictions for IDs not present in the groundtruth
        - Prediction values are not null
        - Prediction values are between 0 and 1, inclusive

    Returns a list of error messages. An empty list signifies successful
    validation.

    !!! Note: any updates to this function must maintain the return type
    of a list of strings.
    """
    errors = []
    truth = pd.read_csv(
        gt_file,
        usecols=GROUNDTRUTH_COLS,
        dtype=GROUNDTRUTH_COLS,
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
        errors.append(vtk.check_missing_keys(truth["id"], pred["id"]))
        errors.append(vtk.check_unknown_keys(truth["id"], pred["id"]))
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


# --- Add more validation functions for different tasks as needed ---
# def validate_task2(gt_file: str, pred_file: str) -> list[str]:
#     """Validation function for Task 2.

#     !!! Reminder: return type must be a list.
#     """
#     return []


def validate(task_number: int, gt_file: str, pred_file: str) -> list[str] | filter:
    """
    Routes validation to the appropriate task-specific function.
    """
    validation_func = {
        1: validate_task1,
        # --- Add more tasks and their validation functions here ---
        # 2: validate_task2,
    }.get(task_number)

    if validation_func:
        return validation_func(gt_file=gt_file, pred_file=pred_file)
    return [f"Invalid challenge task number specified: `{task_number}`"]


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
            "--groundtruth_file",
            help="Path to the folder containing the groundtruth file.",
        ),
    ],
    task_number: Annotated[
        int,
        typer.Option(
            "-t",
            "--task_number",
            help="Challenge task number for which to validate the predictions file.",
        ),
    ] = 1,
    output_file: Annotated[
        str,
        typer.Option(
            "-o",
            "--output_file",
            help="Path to save the results JSON file.",
        ),
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
        gt_file = extract_gt_file(groundtruth_folder)
        errors = validate(
            task_number=task_number,
            gt_file=gt_file,
            pred_file=predictions_file,
        )

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
