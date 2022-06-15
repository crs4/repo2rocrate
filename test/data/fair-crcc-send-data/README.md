# Snakemake workflow: FAIR CRCC - send data

[![Snakemake](https://img.shields.io/badge/snakemake-≥6.3.0-brightgreen.svg)](https://snakemake.github.io)
[![GitHub actions status](https://github.com/crs4/fair-crcc-send-data/workflows/Tests/badge.svg?branch=main)](https://github.com/crs4/fair-crcc-send-data/actions?query=branch%3Amain+workflow%3ATests)


A Snakemake workflow for securely sharing Crypt4GH-encrypted sensitive data from
the [CRC
Cohort](https://www.bbmri-eric.eu/scientific-collaboration/colorectal-cancer-cohort/)
to a destination approved through a successful [access
request](https://www.bbmri-eric.eu/services/access-policies/).

The recommendation is to create a directory for the request that has been
approved;  it will be used as the working directory for the run.  Copy there the
recipient's crypt4gh key and prepare the run configuration.  The configuration
will specify the repository, the destination of the data, and the list of
files/directories to transfer.


## What's the CRC Cohort?

The CRC Cohort is a collection of clinical data and digital high-resolution
digital pathology images pertaining to tumor cases.  The collection has been
assembled from a number of participating biobanks and other partners through the
[ADOPT BBMRI-ERIC](https://www.bbmri-eric.eu/scientific-collaboration/adopt-bbmri-eric/) project.

Researchers interested in using the data for science can file an application for
access.  If approved, the part of the dataset required for the planned and
approved work can be copied to the requester's selected secure storage location
(using this workflow).


## Usage

### Example

    mkdir request_1234 && cd request_1234
    # Now write the configuration, specifying crypt4gh keys, destination and files to send.
    # Finally, execute workflow.
    snakemake --snakefile ../fair-crcc-send-data/workflow/Snakefile --profile ../profile/ --configfile config.yml --use-singularity --cores


#### Run configuration example

```
recipient_key: ./recipient_key
repository:
  path: "/mnt/rbd/data/sftp/fair-crcc/"
  private_key: bbmri-key
  public_key: bbmri-key.pub
sources:
  glob_extension: ".tiff.c4gh"
  items:
  - some/directory/to/glob
  - another/individual/file.tiff.c4gh
destination:
  type: "S3"
  root_path: "my-bucket/prefix/"
  connection:  # all elements will be passed to the selected snakemake remote provider
    access_key_id: "MYACCESSKEY"
    secret_access_key: "MYSECRET"
    host: http://localhost:9000
    verify: false # don't verify ssl certificates
```


TODO

The usage of this workflow is described in the [Snakemake Workflow Catalog](https://snakemake.github.io/snakemake-workflow-catalog/?usage=crs4%2Ffair-crcc-send-data).

If you use this workflow in a paper, don't forget to give credits to the authors by citing the URL of this (original) fair-crcc-send-datasitory and its DOI (see above).
