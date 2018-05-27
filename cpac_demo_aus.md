# C-PAC Tutorial


C-PAC combines elements of AFNI, ANTS, and FSL with custom code in a customizable Nipype pipeline to provide a near comprehensive tool for functional connectomics.  In this tutorial, we will use C-PAC to process and analyze 5 datasets from the NKI Rockland Sample data sharing initiative (http://fcon_1000.projects.nitrc.org). The data required for C-PAC process is a T1 weighted anatomical image, one or more functional images, and optionally one or more field maps. From these data C-PAC will generate a variety of derivatives for follow-on group level analyses.

#### C-PAC System Requirements:
- *Minimum:* 1 processor core, 4 GB RAM, 32 GB free disk space
- *Recommended:* 4 processor cores (or threads), 8 GB of RAM, 32 GB free disk space

#### C-PAC Installation:
Due to its complexity and the tools it uses, C-PAC can be very difficult to install locally and will only run natively on Linux (preferably Ubuntu or NeuroDebian) and Mac OS X. Alternatively, C-PAC can be run from a container, which is a single large binary file that contains all the tools and libraries necessary for it to run. We will use Docker (http://www.docker.io) containers for this demo since they are easy to install and work on most operating systems. Although Docker is a user friendly and mature toolset, there are some security issues with Docker that make unsuitable for some scenarios, such as running on large-scale multi-user high performance computing clusters. We also provide Singularity containers for C-PAC which are better suited for these situations, but we will not cover them in this tutorial. In-depth instructions for C-PAC containers can be found at https://github.com/bids-apps/cpac.

##### Basic installation steps
1. Install Docker CE (community edition) from https://store.docker.com/editions/community.

2. Once docker is running, download the C-PAC container by typing the following into the terminal: ```docker pull bids/cpac```

#### Running C-PAC
The C-PAC container is run using the following template:

    docker run --rm \
        -u $UID:$UID \
        -e $AWS_SECRET_KEY_ID:AWS_SECRET_KEY_ID \
        -e $AWS_SECRET_KEY:AWS_SECRET_KEY \
        -v /tmp:/scratch \
        -v ~/cpac_configs:/configs \
        -v /data/example_data:/bids_dataset \
        -v ~/cpac_outputs:/outputs \
        bids/cpac \
        [c-pac input arguments]

The container executes in a protected environment that has minimum access to the host system. Resources such as environment variables or the file system must be mapped into the container in order for them to be used.
- The argument ```-v from_path:to_path``` maps directories into the container so that they can be used by C-PAC, the host system path ```from_path``` is mapped to the ```to_path``` path inside the container. Paths passed as parameters to code running inside the container should be in reference to ```to_path```. For C-PAC ```/scratch``` is used for temporary storage and must be mapped at invocation. The ```/configs```, ```/bids_dataset```, and ```/outputs``` directories will be used to form C-PAC input arguments (more below) and can follow any convention.
- The ```-e from_var:to_var``` argument sets an environment variable inside the container. The ```to_var``` environment variable will be given the value of ```from_var```. The ```$``` used in the above syntax uses the value of the host system's environment variable to set the container environment variable. These are not required, but may be useful. This example passes AWS keys, which may be needed if the data is being read or written to S3.
- All code run inside the container is executed as ```root``` by default. This may cause some problems because all of the output files will be owned by ```root```. To changes this we use the argument ```-u user_id:group_id```. This syntax is a bit different in that the value before the colon is not mapped to the value after the colon, instead the colon separates the user and group ids. It is important that you pass in user id and group id and not user name and group name. The above example assumes that there is a ```UID``` environment variable on the host system that contains this information for the current user.

The command line arguments for C-PAC are:

     usage: run.py [-h] [--pipeline_file PIPELINE_FILE]
                   [--data_config_file DATA_CONFIG_FILE]
                   [--aws_data_input_creds AWS_DATA_INPUT_CREDS]
                   [--aws_config_input_creds AWS_CONFIG_INPUT_CREDS]
                   [--aws_output_creds AWS_OUTPUT_CREDS] [--n_cpus N_CPUS]
                   [--mem_mb MEM_MB] [--mem_gb MEM_GB] [--save_working_dir]
                   [--disable_file_logging]
                   [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                   [--participant_ndx PARTICIPANT_NDX]
                   [--anat_select_string ANAT_SELECT_STRING] [-v]
                   [--bids_validator_config BIDS_VALIDATOR_CONFIG]
                   [--skip_bids_validator]
                   bids_dir output_dir {participant,group,test_config,GUI}

     C-PAC Pipeline Runner

     positional arguments:
       bids_dir              The directory with the input dataset formatted
                             according to the BIDS standard. Use the format
                             s3://bucket/path/to/bidsdir to read data directly from
                             an S3 bucket. This may require AWS S3 credentials
                             specificied via the --aws_input_creds option.
       output_dir            The directory where the output files should be stored.
                             If you are running group level analysis this folder
                             should be prepopulated with the results of the
                             participant level analysis. Us the format
                             s3://bucket/path/to/bidsdir to write data directly to
                             an S3 bucket. This may require AWS S3 credentials
                             specificied via the --aws_output_creds option.
       {participant,group,test_config,GUI}
                             Level of the analysis that will be performed. Multiple
                             participant level analyses can be run independently
                             (in parallel) using the same output_dir. GUI will open
                             the CPAC gui (currently only works with singularity)
                             and test_config will run through the entire
                             configuration process but will not execute the
                             pipeline.

     optional arguments:
       -h, --help            show this help message and exit
       --pipeline_file PIPELINE_FILE
                             Name for the pipeline configuration file to use. Use
                             the format s3://bucket/path/to/pipeline_file to read
                             data directly from an S3 bucket. This may require AWS
                             S3 credentials specificied via the --aws_input_creds
                             option.
       --data_config_file DATA_CONFIG_FILE
                             Yaml file containing the location of the data that is
                             to be processed. Can be generated from the CPAC gui.
                             This file is not necessary if the data in bids_dir is
                             organized according to the BIDS format. This enables
                             support for legacy data organization and cloud based
                             storage. A bids_dir must still be specified when using
                             this option, but its value will be ignored. Use the
                             format s3://bucket/path/to/data_config_file to read
                             data directly from an S3 bucket. This may require AWS
                             S3 credentials specificied via the --aws_input_creds
                             option.
       --aws_data_input_creds AWS_DATA_INPUT_CREDS
                             Credentials for reading data from S3. If not provided
                             and s3 paths are specified in the data config or for
                             the bids input directory we will try to access the
                             bucket using credententials read from the environment.
                             Use the string "anon" to indicate that data should be
                             read anonymously (e.g. for public S3 buckets).
       --aws_config_input_creds AWS_CONFIG_INPUT_CREDS
                             Credentials for configuration files from S3. If not
                             provided and s3 paths are specified for the config
                             files we will try to access the bucket using
                             credententials read from the environment. Use the
                             string "anon" to indicate that data should be read
                             anonymously (e.g. for public S3 buckets). This was
                             added to allow configuration files to be read from
                             different bucket than the data.
       --aws_output_creds AWS_OUTPUT_CREDS
                             Credentials for writing to S3. If not provided and s3
                             paths are specified in the output directory we will
                             try to access the bucket anonymously use the string
                             "env" to indicate that output credentials should read
                             from the environment. (E.g. when using AWS iam roles).
       --n_cpus N_CPUS       Number of execution resources available for the
                             pipeline
       --mem_mb MEM_MB       Amount of RAM available to the pipeline in megabytes.
                             Included for compatibility with BIDS-Apps standard,
                             but mem_gb is preferred
       --mem_gb MEM_GB       Amount of RAM available to the pipeline in gigabytes.
                             if this is specified along with mem_mb, this flag will
                             take precedence.
       --save_working_dir    Save the contents of the working directory.
       --disable_file_logging
                             Disable file logging, this is useful for clusters that
                             have disabled file locking.
       --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                             The label of the participant that should be analyzed.
                             The label corresponds to sub-<participant_label> from
                             the BIDS spec (so it does not include "sub-"). If this
                             parameter is not provided all participants should be
                             analyzed. Multiple participants can be specified with
                             a space separated list. To work correctly this should
                             come at the end of the command line
       --participant_ndx PARTICIPANT_NDX
                             The index of the participant that should be analyzed.
                             This corresponds to the index of the participant in
                             the data config file. This was added to make it easier
                             to accomodate SGE array jobs. Only a single
                             participant will be analyzed. Can be used with
                             participant label, in which case it is the index into
                             the list that follows the particpant_label flag. Use
                             the value "-1" to indicate that the participant index
                             should be read from the AWS_BATCH_JOB_ARRAY_INDEX
                             environment variable.
       --anat_select_string ANAT_SELECT_STRING
                             C-PAC requires an anatomical file for each session,
                             but cannot make use of more than one anatomical file.
                             If the session contains multiple _T1w files, it will
                             arbitrarily choose one to process, and this may not be
                             consistent across sessions. Use this flag and a string
                             to select the anat to use when more than one option is
                             available. Examples might be "run-01" or "acq-Sag3D."
       -v, --version         show program's version number and exit
       --bids_validator_config BIDS_VALIDATOR_CONFIG
                             JSON file specifying configuration of bids-validator:
                             See https://github.com/INCF/bids-validator for more
                             info
       --skip_bids_validator
                          skips bids validation


##### Some notes

1. You can either perform a custom processing using a YAML configuration file or use the default processing pipeline. A GUI can be invoked to assist in pipeline customization by specifying `GUI` command line argument.

2. The default behavior is to read in data that is organized in the BIDS format. This includes data that is in Amazon AWS S3 by using the format `s3://<bucket_name>/<bids_dir>` for the `bids_dir` command line argument. Outputs can be written to S3 using the same format for the output_dir. Credentials for accessing these buckets can be specified on the command line (using `--aws_input_creds` or `--aws_output_creds`).

3. Non-BIDS organized data can processed using a C-PAC data configuration yaml file. This file can be generated using the C-PAC GUI (start the app with the `GUI` argument, also see instructions [below](#GUI)) or can be created using other means, please refer to [CPAC
documentation](http://fcp-indi.github.io/docs/user/subject_list_config.html) for more information.

4. When the app is run, a data configuration file is written to the working directory. This file can be passed into subsequent runs, which avoids the overhead of re-parsing the BIDS input directory on each run (i.e. for cluster or cloud runs). These files can be generated without executing the C-PAC pipeline using the `test_run` command line argument.

5. The `participant_label` and `participant_ndx` arguments allow the user to specify which of the many datasets should be processed, this are useful when parallelizing the run of multiple participants.

#### Putting it all together

After installing Docker and downloading the C-PAC container:

1. Download and uncompress the test data somewhere on your filesystem.
2. Run a test of C-PAC to write out data and pipeline configuration files.

        docker run --rm \
            -u $UID:$UID \
            -v /tmp:/scratch \
            -v [location of data]:/bids_dataset \
            -v [desired output directory]:/outputs \
            bids/cpac \
                /bids_dataset \
                /outputs \
                test_config

3. Check the output files and customize them to your needs.
4. Process one of the datasets.

        docker run --rm \
            -u $UID:$UID \
            -v /tmp:/scratch \
            -v [location of data]:/bids_dataset \
            -v [desired output directory]:/outputs \
            bids/cpac \
                /bids_dataset \
                /outputs \
                participant \
                --pipeline_file /outputs/[pipeline_file_name] \
                --data_config_file /outputs/[data_config_file_name] \
                --n_cpus [number of cpus available for processing] \
                --mem_gb [amount of RAM available for processing] \
                --participant_ndx [index of pt to process]

5. Familiarize yourself with the resulting data.
