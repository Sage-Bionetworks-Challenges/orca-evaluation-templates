"""Test for score script.

These tests are designed to test the general functionality for
interacting with ORCA, NOT the actual scoring process written.
"""

import json
import os
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from score import main, score

app = typer.Typer()
app.command()(main)

runner = CliRunner()


# ----- Tests for score() function -----
def test_score_valid_task_number(gt_file, pred_file):
    """Test: score() returns a dict for valid task number."""
    task_number = 1
    res = score(
        task_number=task_number,
        gt_file=gt_file,
        pred_file=pred_file,
    )
    assert isinstance(res, dict)


def test_score_invalid_task_number():
    """Test: score() raises KeyError for invalid task number."""
    task_number = 99999
    with pytest.raises(KeyError):
        score(
            task_number=task_number,
            gt_file="dummy_gt.csv",
            pred_file="dummy_pred.csv",
        )


# ----- Tests for main() function -----
@patch("score.extract_gt_file")
@patch("score.score")
def test_main_invalid_task_number(
    mock_score, mock_extract_gt_file, gt_file, pred_file, temp_dir
):
    """Test: final results should be INVALID for invalid task number."""
    task_number = 99999
    mock_extract_gt_file.return_value = gt_file
    mock_score.side_effect = KeyError

    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "results.json")
    with open(output_file, "w") as f:
        pass
    result = runner.invoke(
        app,
        [
            "-p",
            pred_file,
            "-g",
            groundtruth_dir,
            "-t",
            task_number,
            "-o",
            output_file,
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == "INVALID"
    with open(output_file, "r") as f:
        output_data = json.load(f)
    assert output_data["score_status"] == "INVALID"
    assert (
        output_data["score_errors"]
        == f"Invalid challenge task number specified: `{task_number}`"
    )
    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_score.assert_called_once_with(
        task_number=task_number, gt_file=gt_file, pred_file=pred_file
    )


@patch("score.extract_gt_file")
@patch("score.score")
def test_main_prior_validation_failed(
    mock_score,
    mock_extract_gt_file,
    temp_dir,
    invalid_predictions_json,
    groundtruth_dir,
):
    """Test: final results should be INVALID for invalid predictions file."""
    output_file = os.path.join(temp_dir, "results.json")
    with open(output_file, "w") as f:
        f.write(invalid_predictions_json)
    result = runner.invoke(
        app,
        [
            "-p",
            "dummy_pred.csv",
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
    assert output_data["score_status"] == "INVALID"
    assert (
        output_data["score_errors"]
        == "Submission could not be evaluated due to validation errors."
    )
    mock_extract_gt_file.assert_not_called()
    mock_score.assert_not_called()


@patch("score.extract_gt_file")
@patch("score.score")
def test_main_no_prior_validations(
    mock_score,
    mock_extract_gt_file,
    gt_file,
    pred_file,
    temp_dir,
):
    """Test: notice about no prior validation results should be given."""
    mock_extract_gt_file.return_value = gt_file
    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "dummy_results.json")
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
    assert result.stdout.strip() in {"SCORED", "INVALID"}
    with open(output_file) as f:
        output_data = json.load(f)
    assert output_data["validation_status"] == ""
    assert output_data["validation_errors"] == (
        "Validation results not found. Proceeding with scoring but it "
        "may fail or results may be inaccurate."
    )
    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_score.assert_called_once_with(
        task_number=1, gt_file=gt_file, pred_file=pred_file
    )


@patch("score.extract_gt_file")
@patch("score.score")
def test_main_valid_predictions_cannot_score(
    mock_score,
    mock_extract_gt_file,
    valid_predictions_json,
    gt_file,
    pred_file,
    temp_dir,
):
    """
    Test: final results should be INVALID when predictions cannot be scored
    (indicated by ValueError).
    """
    mock_extract_gt_file.return_value = gt_file
    mock_score.side_effect = ValueError

    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "results.json")
    with open(output_file, "w") as f:
        f.write(valid_predictions_json)
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
    with open(output_file) as f:
        output_data = json.load(f)
    assert output_data["score_status"] == "INVALID"
    assert (
        output_data["score_errors"]
        == "Error encountered during scoring; submission not evaluated."
    )
    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_score.assert_called_once_with(
        task_number=1, gt_file=gt_file, pred_file=pred_file
    )


@patch("score.extract_gt_file")
@patch("score.score")
def test_main_valid_predictions_can_score(
    mock_score,
    mock_extract_gt_file,
    valid_predictions_json,
    gt_file,
    pred_file,
    temp_dir,
):
    """
    Test: final results should be SCORED for successful scoring.
    """
    mock_extract_gt_file.return_value = gt_file
    groundtruth_dir = os.path.dirname(gt_file)
    output_file = os.path.join(temp_dir, "results.json")
    with open(output_file, "w") as f:
        f.write(valid_predictions_json)
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
    assert result.stdout.strip() == "SCORED"
    with open(output_file) as f:
        output_data = json.load(f)
    assert output_data["score_status"] == "SCORED"
    assert output_data["score_errors"] == ""
    mock_extract_gt_file.assert_called_once_with(groundtruth_dir)
    mock_score.assert_called_once_with(
        task_number=1, gt_file=gt_file, pred_file=pred_file
    )
