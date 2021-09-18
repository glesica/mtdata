# Mt. Data

A tool to help anyone build a mountain of public data.

Includes a simple Python script that can be configured to extract data from
various sources. This is run periodically through GitHub actions and the updated
data are committed back to the repository.

## Datasets

The following datasets are currently included.

### Air Quality

Extracted from https://www.airnowapi.org.

### Missoula 911 Calls

Extracted from https://apps.missoulacounty.us/dailypublicreport/.

## Adding a Dataset

A dataset is implemented as a sub-class of the `Dataset` abstract class in the
`datasets` module. Once the dataset is implemented, add a factory function in
`manifest.py`. Once this is done, the new dataset will run when the `mtdata`
module is run.

## Development

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/). To install
dependencies for development, use `pipenv sync --dev`.

Once everything is installed, the easiest way to work with the repo is to
use `pipenv shell` to drop into the virtual environment.

To run the test suite, just run `python -m pytest`.
