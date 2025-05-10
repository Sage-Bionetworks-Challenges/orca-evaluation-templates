<h1 align="center">
  Evaluation Script Templates
</h1>
<h3 align="center">

  Templates for creating evaluation scripts to be plugged into the [Synapse ORCA workflow]

</h3>
<p align="center">
  <img 
    alt="GitHub release (latest by date)" 
    src="https://img.shields.io/github/release/Sage-Bionetworks-Challenges/orca-evaluation-templates?label=latest%20release&display_name=release&style=flat-square"
  >
  <img 
    alt="GitHub Release Date" 
    src="https://img.shields.io/github/release-date/Sage-Bionetworks-Challenges/orca-evaluation-templates?style=flat-square&color=darkgreen"
  >
</p>

You can either build off of this repository template or use it as reference to
build your scripts from scratch. Provided here is a sample evaluation template
in Python. R support TBD.

### Requirements

- Python 3.11+
- Docker (if containerizing manually)

---

### ✅ Write your validation script

1. Determine the format of the predictions file, as this will help create the
   list of validation checks. Things to consider include:

   - File format (e.g. CSV, TSV, text)
   - Number of columns
   - Column header names
   - Column data types
   - For numerical columns (integers or floats), are there expected minimum
     and maximum values?

   Beyond the file structure, also think about the data content:

   - Can there be multiple prediction for a single ID/patient/sample?
   - Is a prediction required for every ID, or are missing values acceptable?

2. Adapt `validate.py` so that it fits your needs. The template currently
   implements the following checks:
   - Two columns named `id` and `probability` (any additional columns will be
     ignored)
   - `id` values are strings
   - `probability` values are floats between 0.0 and 1.0, and cannot be
     null/None
   - There is exactly one prediction per patient (no missing or duplicate IDs)
   - There are only predictions for patients found in the groundtruth
     (no unknown IDs)

> [!NOTE]
> The template is currently designed with the assumption that the challenge
> has a _single_ task.
> 
> If your challenge has _multiple_ tasks, create additional validation
> functions (e.g., `validate_task2()`, `validate_task3()`, ...) and update the
> `validate()` function to direct the validation process to the correct function
> for each task.

> [!IMPORTANT]
> The `main()` function is specifically designed for seamless interaction with
> ORCA. **Modifying this function is strongly discouraged** and could lead to
> compatibility issues. Unit tests are in place to ensure its proper integration.

3. Update `requirements.txt` with any additional libraries/packages used by the
   script.

4. (optional) Locally run `validate.py` to verify its functionality, by replacing
   the placeholder paths with the filepaths to your data:

   ```bash
   python validate.py \
     --predictions_file PATH/TO/PREDICTIONS_FILE.CSV \
     --groundtruth_folder PATH/TO/GROUNDTRUTH_FOLDER/ [--output_file PATH/TO/OUTPUT_FILE.JSON] [--task_number TASK_NUMBER]
   ```

   Specify `--output_file` and `--task_number` as needed. Use `--help` for more
   details.

   The expected outcomes are:

   - STDOUT will display either `VALIDATED` or `INVALID`
   - Full validation details are saved in `results.json` (or the path specified
     by `--output_file`)

   If needed, you may use the sample data provided in `sample_data/`, however,
   thorough testing with your own data is recommended to ensure accurate validation.

---

### 🏆 Write your scoring script

1. Determine the evaluation metrics you will use to assess the predictions. It
   is recommended to include at least two metrics: a primary metric for ranking
   and a secondary metric for breaking ties. You can also include additional
   informative metrics such as sensitivity, specificity, etc.

2. Adapt `score.py` to calculate the metrics you have defined. The template
   currently provides implementations for:
   - Area under the receiver operating characteristic curve (AUROC)
   - Area under the precision-recall curve (AUPRC)

> [!NOTE]
> The template is currently designed with the assumption that the challenge
> has a _single_ task.
> 
> If your challenge has _multiple_ tasks, create additional scoring
> functions (e.g., `score_task2()`, `score_task3()`, ...) and update the
> `score()` function to direct the validation process to the correct function
> for each task.

> [!IMPORTANT]
> Like `validate.py`, modifying `main()` is strongly discouraged.

3. Update `requirements.txt` with any additional libraries/packages used by the script.

4. (optional) Locally run `score.py` to ensure it executes correctly and returns
   the expected scores:

   ```
   python score.py \
     --predictions_file  PATH/TO/PREDICTIONS_FILE.CSV \
     --groundtruth_folder PATH/TO/GROUNDTRUTH_FOLDER/  [--output_file PATH/TO/OUTPUT_FILE.JSON] [--task_number TASK_NUMBER]
   ```

   Specify `--output_file` and `--task_number` as needed. Use `--help` for more
   details.

   The expected outcomes are:

   - STDOUT will display either `SCORED` or `INVALID`
   - Scores are appended to `results.json` (or the path specified by `--output_file`)

---

### 🐳 Dockerize your scripts

#### Automated containerization

This template repository includes a workflow that builds a Docker container for
your scripts. To trigger the process, you will need to [create a new release].
For tag versioning, we recommend following the [SemVar versioning schema]. You can
follow the status of the release workflow by going to the **Actions** tab of
your repository.

This workflow will create a new image within your repository, which can be found
under **Packages**. Here is an example of [the deployed image] for this template.

#### Manual containerization

You can also use other public Docker registries, such as DockerHub. The only
requirement is that the Docker image must be publicly accessible so that ORCA
can pull and execute it.

To containerize your scripts:

1. Open a terminal and switch directories to your local copy of the repository.

2. Run the command:

   ```
   docker build -t IMAGE_NAME:TAG_VERSION FILEPATH/TO/DOCKERFILE
   ```

   where:

   - _IMAGE_NAME_: name of your image.
   - _TAG_VERSION_: version of the image. If TAG_VERSION is not supplied,
     `latest` will be used.
   - _FILEPATH/TO/DOCKERFILE_: filepath to the Dockerfile, in this case, it will
     be the current directory (`.`)

3. If needed, log into your registry of choice.

4. Push the image:

   ```
   docker push IMAGE_NAME:TAG_VERSION
   ```

---

### ⏭️ Next Steps

#### Already working with Sage Data Processing & Engineering (DPE) team?

Create a PR to the [nf-synapse-challenge] repository to add your container
image name to your challenge profile.

#### Need to connect with the DPE team?

Please reach out to the DPE team via their [DPE Service Desk] for more
information and support regarding challenge evaluation orchestration.


<!-- LINKS -->
[Synapse ORCA workflow]: https://github.com/Sage-Bionetworks-Workflows/nf-synapse-challenge/tree/main
[create a new release]: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release
[SemVar versioning schema]: https://semver.org/
[the deployed image]: https://github.com/orgs/Sage-Bionetworks-Challenges/packages?repo_name=orca-evaluation-templates
[nf-synapse-challenge]: https://github.com/Sage-Bionetworks-Workflows/nf-synapse-challenge
[DPE Service Desk]: https://sagebionetworks.jira.com/servicedesk/customer/portal/5/group/7/create/51
