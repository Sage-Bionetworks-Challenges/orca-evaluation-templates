import json
import os
import sys
import tempfile

import pandas as pd
import pytest


def pytest_configure(config):
    """Allow test scripts to import scripts from parent folder."""
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, src_path)


@pytest.fixture(scope="module")
def temp_dir():
    """Creates a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="module")
def groundtruth_dir(temp_dir):
    """Creates a temporary groundtruth directory."""
    gt_dir = os.path.join(temp_dir, "groundtruth")
    os.makedirs(gt_dir)
    return gt_dir


@pytest.fixture(scope="module")
def gt_file(groundtruth_dir):
    """Creates a dummy groundtruth file."""
    truth = pd.DataFrame(
        {
            "id": ["A_01", "A_02", "A_03"],
            "disease": [1, 0, 1],
        }
    )
    gt_file = os.path.join(groundtruth_dir, "truth.csv")
    truth.to_csv(gt_file, index=False)
    return gt_file


@pytest.fixture(scope="module")
def pred_file(temp_dir):
    """Creates a dummy prediction file."""
    pred = pd.DataFrame(
        {
            "id": ["A_01", "A_02", "A_03"],
            "probability": [0.5, 0.5, 0.5],
        }
    )
    pred_file = os.path.join(temp_dir, "predictions.csv")
    pred.to_csv(pred_file, index=False)
    return pred_file


@pytest.fixture(scope="module")
def valid_predictions_json():
    """Creates a dummy valid results JSON."""
    return json.dumps(
        {
            "validation_status": "VALIDATED",
            "validation_errors": "",
        }
    )


@pytest.fixture(scope="module")
def invalid_predictions_json():
    """Creates a dummy invalid results JSON."""
    return json.dumps(
        {
            "validation_status": "INVALID",
            "validation_errors": "Something went wrong.",
        }
    )
