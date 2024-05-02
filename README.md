<h1 align="center">
  Evaluation Script Templates
</h1>
<h3 align="center">
  
  Templates for creating evaluation scripts to be plugged into the [Synapse ORCA workflow]
    
</h3>

You can either build off of this repository template or use it as reference to
build your scripts from scratch.  Provided here is a sample evaluation template
in Python. R support TBD.

### Requirements
* Python 3.10+
* Docker (if containerizing manually)

---

### ✅ Write your validation script

1. Determine the format of the predictions file, as this will help create the list
   validation checks.  Things to consider include:

     - file type (CSV? TSV?)
     - number of columns
     - column header names
     - column types
     - if column type is a number or float, is there is minimum value? Maximum?

   In addition to format, also consider:

     - can there be more than one prediction per ID/sample/patient?
     - does every ID/sample/patient need a prediction, or can some be null/NA?

2. Update `validate.py` so that it fits your needs. The template currently implements
   the following checks:

     - two columns named `id` and `probability` (extraneous columns will be ignored)
     - `id` values are strings
     - `probability` values are floats between 0.0 and 1.0, and cannot be null/None
     - there is one prediction per patient (so, no missing patient IDs or duplicate patient IDs)
     - there are no extra predictions (so, no unknown patient IDs)
  
3. Update `requirements.txt` with any additional libraries/packages used by the script.

4. (optional) Locally run `validate.py` to ensure it can run successfully.

   ```
   python validate.py \
     -p PATH/TO/PREDICTIONS_FILE.CSV \
     -g PATH/TO/GOLDSTANDARD_FILE.CSV
   ```

   STDOUT will either be `VALIDATED` or `INVALID`, and full details of the validation check
   will be printed to `results.json`.

### 🏆 Write your scoring script

1. Determine the evaluation metrics and how they can be computed.  We recommend evaluating
   at least two metrics: one for primary ranking and the other for breaking ties. You
   can also include additional metrics to give the participants more information about
   their performance, such as sensitivity, specificity, precision, etc.

2. Update `score.py` so that it fits your needs. The template currently evaluates for:

     - Area under the receiver operating characteristic curve (AUROC)
     - Area under the precision-recall curve (AUPRC)

3. Update `requirements.txt` with any additional libraries/packages used by the script.

4. (optional) Locally run `score.py` to ensure it can run successfully in addition to
   returning expected scores.

   ```
   python score.py \
     -p PATH/TO/PREDICTIONS_FILE.CSV \
     -g PATH/TO/GOLDSTANDARD_FILE.CSV
   ```

   STDOUT will either be `SCORED` or `INVALID`, and scores will be appended to an
   existing `results.json`.

### 🐳 Dockerize your scripts

#### Automated containerization

This template repository comes with a workflow that will containerize the scripts for
you. To trigger the workflow, you will need to [create a new release]. For tag versioning,
we recommend following the [SemVar versioning schema].

This workflow will create a new image within your repository, accessible under **Packages**.
Here is an example of [the deployed image] for this template.

#### Manual containerization

You can also use a Docker registry other than ghcr, for example: DockerHub. The only
requirement is that the image must be publicly accessible so that the ORCA workflow
can access it.

To containerize your scripts:

1. Open a terminal and switch directories to your local copy of the repository.

2. Run the command:

   ```
   docker build -t IMAGE_NAME:TAG_VERSION FILEPATH/TO/DOCKERFILE
   ```

   where:

     - _IMAGE_NAME_: name of your image.
     - _TAG_VERSION_: version of the image.  If TAG_VERSION is not supplied, `latest` will be used.
     - _FILEPATH/TO/DOCKERFILE_: filepath to the Dockerfile, in this case, it will be the current directory (`.`)
  
3. If needed, log into your registry of choice.

4. Push the image:

    ```
   docker push IMAGE_NAME:TAG_VERSION
   ```

[Synapse ORCA workflow]: https://github.com/Sage-Bionetworks-Workflows/nf-synapse-challenge/tree/main
[create a new release]: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release
[SemVar versioning schema]: https://semver.org/
[the deployed image]: https://github.com/orgs/Sage-Bionetworks-Challenges/packages?repo_name=orca-evaluation-templates
