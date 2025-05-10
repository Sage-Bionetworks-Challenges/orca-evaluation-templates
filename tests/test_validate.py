"""Test for validation script.

These tests are designed to test the general functionality for
interacting with ORCA, NOT the actual validation process written.
"""

import json
import os
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from validate import main, validate

app = typer.Typer()
app.command()(main)

runner = CliRunner()


# ----- Tests for validate() function -----
def test_validate_valid_task_number(gt_file, pred_file):
    """
    Test: validate() returns a list, filter, or tuple for valid
    task number.
    """
    task_number = 1
    errors = validate(
        task_number=task_number,
        gt_file=gt_file,
        pred_file=pred_file,
    )
    assert isinstance(errors, (list, filter, tuple))


def test_validate_invalid_task_number():
    """Test: validate() notifies about invalid task number."""
    task_number = 99999
    errors = validate(
        task_number=task_number,
        gt_file="dummy_gt.csv",
        pred_file="dummy_pred.csv",
    )
    assert f"Invalid challenge task number specified: `{task_number}`" in errors


# ----- Tests for main() function -----
@patch("validate.extract_gt_file")
@patch("validate.validate")
def test_main_valid_submission_type(
    mock_validate, mock_extract_gt_file, gt_file, pred_file, temp_dir
):
    """Test: final results should be INVALID or VALIDATED."""
    mock_extract_gt_file.return_value = gt_file
    mock_validate.return_value = []
    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "results.json")
    result = runner.invoke(
        app,
        [
            "-p",
            pred_file,
            "-g",
            groundtruth_dir,
            "-t",
            "1",
            "-o",
            output_file,
        ],
    )
    assert result.exit_code == 0

    # Ensure that STDOUT is one of `VALIDATED` or `INVALID`
    assert result.stdout.strip() in {"VALIDATED", "INVALID"}
    with open(output_file) as f:
        output_data = json.load(f)

    # If status is `VALIDATED`, there should be no error messages.
    if result.stdout.strip() == "VALIDATED":
        assert output_data["validation_status"] == "VALIDATED"
        assert output_data["validation_errors"] == ""

    # Otherwise, there should be error message(s) for `INVALID` predictions.
    else:
        assert output_data["validation_status"] == "INVALID"
        assert not output_data["validation_errors"]

    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_validate.assert_called_once_with(
        task_number=1, gt_file=gt_file, pred_file=pred_file
    )


@patch("validate.extract_gt_file")
@patch("validate.validate")
def test_main_invalid_submission_type(
    mock_validate, mock_extract_gt_file, groundtruth_dir, temp_dir
):
    """Test: final results should be INVALID for incorrect submission type."""
    invalid_file = os.path.join(temp_dir, "INVALID_predictions.txt")
    with open(invalid_file, "w") as f:
        f.write("foo")
    output_file = os.path.join(temp_dir, "results.json")
    result = runner.invoke(
        app,
        [
            "-p",
            invalid_file,
            "-g",
            groundtruth_dir,
            "-t",
            "1",
            "-o",
            output_file,
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == "INVALID"
    with open(output_file, "r") as f:
        output_data = json.load(f)
    assert output_data["validation_status"] == "INVALID"
    mock_extract_gt_file.assert_not_called()
    mock_validate.assert_not_called()


@patch("validate.extract_gt_file")
@patch("validate.validate")
def test_main_long_error_message(
    mock_validate, mock_extract_gt_file, gt_file, pred_file, temp_dir
):
    """Test: validation errors should never exceed 500 characters."""
    mock_extract_gt_file.return_value = gt_file

    # Create a dummy string longer than 500 characters.
    long_error_message = "foo" * 500
    mock_validate.return_value = [long_error_message]

    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "results.json")

    result = runner.invoke(
        app,
        [
            "-p",
            pred_file,
            "-g",
            groundtruth_dir,
            "-t",
            "1",
            "-o",
            output_file,
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == "INVALID"
    with open(output_file, "r") as f:
        output_data = json.load(f)
    assert output_data["validation_status"] == "INVALID"
    assert len(output_data["validation_errors"]) < 500
    assert output_data["validation_errors"].endswith("...")

    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_validate.assert_called_once_with(
        task_number=1, gt_file=gt_file, pred_file=pred_file
    )
