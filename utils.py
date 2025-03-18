import os
from glob import glob


def extract_gt_file(folder):
    """Extract groundtruth file from folder."""
    files = glob(os.path.join(folder, "*"))
    if len(files) != 1:
        raise ValueError(
            "Expected exactly one groundtruth file in folder. "
            f"Got {len(files)}. Exiting."
        )
    return files[0]
