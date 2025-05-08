import os
import tarfile
import zipfile
from glob import glob


def _is_hidden(member):
    """Check whether file is hidden or not."""
    hidden = ("__", "._", "~", ".DS_Store")
    return os.path.split(member)[1].startswith(hidden) or ".idea" in member


def _filter_tar(members, pattern):
    """Filter out directory name and hidden files in tarfile."""
    files_to_extract = []
    for member in members:
        if member.isfile() and not _is_hidden(member.name) and pattern in member.name:
            files_to_extract.append(member)
    return files_to_extract


def _filter_zip(members, pattern):
    """Filter out directory name and hidden files in zipfile."""
    files_to_extract = []
    for member in members:
        if (
            not member.is_dir()
            and not _is_hidden(member.filename)
            and pattern in member.filename
        ):
            files_to_extract.append(member.filename)
    return files_to_extract


def inspect_zip(f, unzip=True, path=".", pattern=""):
    """Inspect and optionally extract files from a tarfile/zipfile."""
    files = []
    if zipfile.is_zipfile(f):
        with zipfile.ZipFile(f) as zip_ref:
            files = _filter_zip(zip_ref.infolist(), pattern)
            if unzip:
                zip_ref.extractall(path=path, members=files)
    elif tarfile.is_tarfile(f):
        with tarfile.open(f) as tar_ref:
            members = _filter_tar(tar_ref, pattern)
            if unzip:
                tar_ref.extractall(path=path, members=members)
            files = [member.name for member in members]
    return files


def extract_gt_file(folder):
    """Extract groundtruth file from folder."""
    files = glob(os.path.join(folder, "*"))

    # Filter out the manifest file
    files = [f for f in files if os.path.basename(f) != "SYNAPSE_METADATA_MANIFEST.tsv"]

    if len(files) != 1:
        raise ValueError(
            "Expected exactly one groundtruth file in folder. "
            f"Got {len(files)}. Exiting."
        )
    return files[0]
