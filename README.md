# Mt. Data

[![Continuous Integration](https://github.com/glesica/mtdata/actions/workflows/ci.yml/badge.svg)](https://github.com/glesica/mtdata/actions/workflows/ci.yml)
[![Scheduled](https://github.com/glesica/mtdata/actions/workflows/scheduled.yml/badge.svg)](https://github.com/glesica/mtdata/actions/workflows/scheduled.yml)
A tool to help anyone build a mountain of public data.

Includes a simple Python script that can be configured to extract
data from various sources. This is run periodically through GitHub
actions and the updated data are committed back to the repository.

  * [Documentation](https://mt-data.readthedocs.io/en/latest/)

## Datasets

Check out the README in the `data/` directory for a list of
data included in the repo from the bundled datasets.

## Development

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/).
To install dependencies for development, use `pipenv sync --dev`.

Once everything is installed, the easiest way to work with the repo
is to use `pipenv shell` to drop into the virtual environment.

To run the test suite, just run `python -m pytest`.

To run a specific scraper, run
`python -m mtdata -d dataset_name -s store-name`

### Dependencies

Add or update dependencies in `Pipfile`, then run
`./tool/update-deps.sh`. This will update the dependencies, create a
new lock file, and then update the `requirements.txt` file used to
build the Docker image.

### Checks

Prior to making a pull request, run the various check scripts and
fix any problems they identify.

  * `./tool/check-tests.sh`
  * `./tool/check-types.sh`
  * `./tool/check-format.sh`
  * `./tool/check-lints.sh`

If the formatter needs to be run, do this with `./tool/run-format.sh`.

### Documentation

When the API changes, the auto-generated documentation needs to be
updated. To do this, run `./tool/update-docs.sh`, then commit any
changes that result.

### Docker Image

The Docker image specified in `Dockerfile` bundles the code to make
it easy to run Mt. Data in other environments. To build the container
image based on the current version of the code, run
`./tool/build-container`. To push the container to Docker Hub, run
`./tool/push-container.sh`.
