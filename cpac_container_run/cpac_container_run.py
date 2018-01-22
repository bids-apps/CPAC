
#!/usr/bin/env python
import argparse
import os
from subprocess import Popen, PIPE
import subprocess
import yaml
import sys

import datetime, time



def run(command, env={}):
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
        shell=True, env=env)
    while True:
        line = process.stdout.readline()
        line = str(line)[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break


def check_singularity():
    '''

    Check if singularity is installed.

    :param None
    :return: Boolean, True if the singularity executable
        is found on the path, False if it isn't
    '''

    print "checking for singularity"
    return

def check_download_singularity_image(singularity_image, singularity_image_path, singularity_repo):
    """
    Checks for singularity_image in singlarity_image_path and downloads it from singularity_repo
    if not found.

    :param singularity_image: name of the singularity image that is being sought
    :param singularity_image_path: directory that should contain the singularity image, if it
        is not available, then download from the repository
    :param singularity_repo: repository to download the singularity image from
    :return: returns the full path to the sought singularity image, or None if it couldn't be
        found or retrieved.
    :raises:
    """

    # before we do anything, lets make sure that singularity_image_path is legit
    if not os.path.isdir(singularity_image_path):
        raise OSError(2, "Directory not found", singularity_image_path)

    # use a lock file to avoid weirdness when multiple jobs are run using SGE or parallel
    import filelock
    lock_file = "/tmp/bids_cpac.lock"
    lock = filelock.FileLock(lock_file)

    # allow a 10 minute timeout, just so we don't wait forever
    try:
        with lock.acquire(timeout=600):
            pass
    except filelock.Timeout:
        print("Waited 10 minutes to acquire file lock {}, but never did".format(lock_file))
        pass


    return

def check_docker():
    '''

    :return: Boolean, True if docker executable is
         found on the path, False if it isn't
    '''

    print "checking for docker"
    return

if __name__ == "__main__":

    __version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    'version')).read()

    parser = argparse.ArgumentParser(description='C-PAC Container Runner')

    parser.add_argument('--analysis_level', help='Level of the analysis that will'
                        ' be performed.\n participant: execute the pipeline'
                        ' to preprocess data and calculate individual level'
                        ' outputs. GUI will open the CPAC graphical user interface'
                        ' (currently only works with singularity), write_config'
                        ' will run through the entire configuration process but will'
                        ' not execute the pipeline (configuration files will be'
                        ' written to cluster_dir, see below), and group is currently'
                        ' not implemented but included for compatibility with the'
                        ' BIDS_Apps specification.',choices=['participant', 'group',
                                                             'write_config', 'GUI'])

    parser.add_argument('--container_version', help='Version of C-PAC container to'
                        ' run. Default is the latest.')

    parser.add_argument('--docker', help='Run C-PAC using Docker')

    parser.add_argument('--singularity', help='Run C-PAC using Singularity')

    parser.add_argument('--singularity_image_dir', help='Directory containing'
                        ' singularity images. If configured to execute using'
                        ' singularity containers but the cpac singularity'
                        ' image is not found in this directory, it will be'
                        ' downloaded from the repository. Defaults to '
                        ' $HOME/bids_cpac/singularity_images.')

    parser.add_argument('--bids_dir', help='The directory with the input dataset '
                        ' formatted according to the BIDS standard. Use the'
                        ' format s3://bucket/path/to/bidsdir to read data directly'
                        ' from an S3 bucket. This may require AWS S3 credentials'
                        ' specificied via the --aws_input_creds option. If a'
                        ' data configuration file is specified, it will override'
                        ' this parameter.')

    parser.add_argument('--aws_input_creds', help='Credentials for reading from S3.'
                        ' If not provided and s3 paths are specified in the data config '
                        ' we will try to access the bucket anonymously',
                        default=None)

    parser.add_argument('--output_dir', help='The directory where the output files'
                        ' should be stored. If you are running group level analysis'
                        ' this folder should be prepopulated with the results of the'
                        ' participant level analysis. Us the format'
                        ' s3://bucket/path/to/bidsdir to write data directly to an S3 bucket.'
                        ' This may require AWS S3 credentials specificied via the'
                        ' --aws_output_creds option.')

    parser.add_argument('--aws_output_creds', help='Credentials for writing to S3.'
                        ' If not provided and s3 paths are specified in the output directory'
                        ' we will try to access the bucket anonymously',
                        default=None)

    parser.add_argument('--working_dir', help='Directory that will be used for'
                        ' intermediary files during processing. This should ideally'
                        ' be a locally connected hard drive rather than an NFS mount'
                        ' to maximize processing speed. If --save_working_dir is not'
                        ' set, this defaults to /tmp, if --save_working_dir is set'
                        ' then this defaults to output_dir/working_dir where'
                        ' output_dir is set from the --output_dir flag. If the output'
                        ' directory is S3, then there is no default and an error will'
                        ' result if the working directory isn\'t explicitly set using'
                        ' this flag. If not saving the working directory, this size of'
                        ' the working directory should be approximately 3GB for each'
                        ' pipeline run in parallel on a node (total_cpu_per_node / n_cpu).'
                        ' If saving the working directory, this directory should be 3GB'
                        ' for each pipeline run on the node.')

    parser.add_argument('--save_working_dir', action='store_true',
                        help='Save the contents of the working directory. See the'
                        ' description of --working_dir for more information about'
                        ' where the working directory will be saved', default=False)

    parser.add_argument('--pipeline_file', help='Path to the pipeline configuration'
                        ' file to use. Can be generated by the GUI.',
                        default="/cpac_resources/default_pipeline.yaml")

    parser.add_argument('--data_config_file', help='C-PAC data configuration YAML file'
                        ' containing the information about the data that is to be'
                        ' processed. This file is automatically generated from the'
                        ' contents of the BIDS input directory (see --bids_dir) or'
                        ' can be generated using the C-PAC GUI if a file structure'
                        ' other than BIDs is used. Generating a data config file from'
                        ' a BIDS directory is fairly fast, but consuming none the less'
                        ' if you will be running many pipelines in parallel (for example'
                        ' a cluster job) we recommend that you generate a data '
                        ' configuration file using the config_write analysis level, and'
                        ' pass this file to each subsequent pipeline execution using'
                        ' this flag.', default=None)

    parser.add_argument('--SGE', help='Indicates that configuration files for running on'
                        ' SGE should be generated.', default=False)

    parser.add_argument('--SGE_pe', help='Name of the parallel environment to use. Defaults'
                        ' to mpi_smp', default="mpi_smp")

    parser.add_argument('--parallel', help='Execute the jobs in parallel using GNU parallel,'
                        ' should be followed by the number of jobs to be run in parallel.',
                        default=0)

    parser.add_argument('--cluster_dir', help='The directory where configuration files'
                        ' as well as output and error logs are stored. Defaults to'
                        ' $HOME/bids_cpac/cluster_dir.')

    parser.add_argument('--n_cpus', help='Number of execution resources available for'
                        ' each pipeline', default="1")

    parser.add_argument('--mem_mb', help='Amount of RAM available to the pipeline in'
                        ' megabytes. Included for compatibility with BIDS-Apps standard,'
                        ' but mem_gb is preferred')

    parser.add_argument('--mem_gb', help='Amount of RAM available to the pipeline in'
                        ' gigabytes. If this is specified along with mem_mb, this flag'
                        ' will take precedence.')

    parser.add_argument('-v', '--version', action='version',
                        version='C-PAC BIDS-App version {}'.format(__version__))

    # get the command line arguments
    args = parser.parse_args()

    print("C-PAC Container Runner version {}".format(__version__))

    check_download_singularity_image("cpac_latest.img","/tmp/barbell","s3://doc")

