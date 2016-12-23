#!/usr/bin/env python
import argparse
import os
from glob import glob
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

parser = argparse.ArgumentParser(description='C-PAC Pipeline Runner')
parser.add_argument('bids_dir', help='The directory with the input dataset '
    'formatted according to the BIDS standard. Use the format'
    ' s3://bucket/path/to/bidsdir to read data directly from an S3 bucket.'
    ' This may require AWS S3 credentials specificied via the'
    ' --aws_input_creds option.')
parser.add_argument('output_dir', help='The directory where the output files '
    'should be stored. If you are running group level analysis '
    'this folder should be prepopulated with the results of the '
    'participant level analysis. Us the format '
    ' s3://bucket/path/to/bidsdir to write data directly to an S3 bucket.'
    ' This may require AWS S3 credentials specificied via the'
    ' --aws_output_creds option.')
parser.add_argument('analysis_level', help='Level of the analysis that will '
    ' be performed. Multiple participant level analyses can be run '
    ' independently (in parallel) using the same output_dir. '
    ' GUI will open the CPAC gui (currently only works with singularity) and'
    ' test_config will run through the entire configuration process but will'
    ' not execute the pipeline.',
    choices=['participant', 'group', 'test_config', 'GUI'])
parser.add_argument('--pipeline_file', help='Name for the pipeline '
    ' configuration file to use',
    default="/cpac_resources/default_pipeline.yaml")
parser.add_argument('--data_config_file', help='Yaml file containing the location'
    ' of the data that is to be processed. Can be generated from the CPAC gui.'
    ' This file is not necessary if the data in bids_dir is organized according to'
    ' the BIDS format. This enables support for legacy data organization and'
    ' cloud based storage. A bids_dir must still be specified when using this'
    ' option, but its value will be ignored.',
    default=None)
parser.add_argument('--aws_input_creds', help='Credentials for reading from S3.'
    ' If not provided and s3 paths are specified in the data config '
    ' we will try to access the bucket anonymously',
    default=None)
parser.add_argument('--aws_output_creds', help='Credentials for writing to S3.'
    ' If not provided and s3 paths are specified in the output directory'
    ' we will try to access the bucket anonymously',
    default=None)
parser.add_argument('--n_cpus', help='Number of execution '
    ' resources available for the pipeline', default="1")
parser.add_argument('--mem_mb', help='Amount of RAM available to the pipeline in megabytes.'
    ' Included for compatibility with BIDS-Apps standard, but mem_gb is preferred')
parser.add_argument('--mem_gb', help='Amount of RAM available to the pipeline in gigabytes.'
    ' if this is specified along with mem_mb, this flag will take precedence.')
parser.add_argument('--save_working_dir', action='store_true',
    help='Save the contents of the working directory.', default=False)
parser.add_argument('--participant_label', help='The label of the participant'
    ' that should be analyzed. The label '
    'corresponds to sub-<participant_label> from the BIDS spec '
    '(so it does not include "sub-"). If this parameter is not '
    'provided all subjects should be analyzed. Multiple '
    'participants can be specified with a space separated list. To work correctly this should '
    'come at the end of the command line', nargs="+")
parser.add_argument('--participant_ndx', help='The index of the participant'
    ' that should be analyzed. This corresponds to the index of the participant in'
    ' the subject list file. This was added to make it easier to accomodate SGE'
    ' array jobs. Only a single participant will be analyzed. Can be used with'
    ' participant label, in which case it is the index into the list that follows'
    ' the particpant_label flag.', default=None)

# get the command line arguments
args = parser.parse_args()

print(args)

# if we are running the GUI, then get to it
if args.analysis_level == "GUI":
    print "Startig CPAC GUI"
    import CPAC
    CPAC.GUI.run()
    sys.exit(1)

# check to make sure that the input directory exists
if not args.bids_dir.lower().startswith("s3://") and not os.path.exists(args.bids_dir):
    print "Error! Could not find %s"%(args.bids_dir)
    sys.exit(0)

# check to make sure that the output directory exists
if not args.output_dir.lower().startswith("s3://") and not os.path.exists(args.output_dir):
    print "Error! Could not find %s"%(args.output_dir)
    sys.exit(0)

# validate input dir
run("bids-validator %s"%args.bids_dir)

# otherwise, if we are running group, participant, or dry run we
# begin by conforming the configuration
c = yaml.load(open(os.path.realpath(args.pipeline_file), 'r'))

# set the parameters using the command line arguements
# TODO: we will need to check that the directories exist, and
# make them if they do not
c['outputDirectory'] = os.path.join(args.output_dir, "output")

if not "s3://" in args.output_dir.lower():
    c['crashLogDirectory'] = os.path.join(args.output_dir, "crash")
    c['logDirectory'] = os.path.join(args.output_dir, "log")
else:
    c['crashLogDirectory'] = os.path.join("/scratch", "crash")
    c['logDirectory'] = os.path.join("/scratch", "log")

if args.mem_gb:
    c['memoryAllocatedPerSubject'] = float(args.mem_gb)
elif args.mem_mb:
    c['memoryAllocatedPerSubject'] = float(args.mem_mb)/1024.0
else:
    c['memoryAllocatedPerSubject'] = 6.0

c['numCoresPerSubject'] = int(args.n_cpus)
c['numSubjectsAtOnce'] = 1
c['num_ants_threads'] = min(int(args.n_cpus), int(c['num_ants_threads']))

if args.aws_input_creds:
    if os.path.isfile(args.aws_input_creds):
        c['awsCredentialsFile'] = args.aws_input_creds
    else:
        raise IOError("Could not find aws credentials %s"%(args.aws_input_creds))

if args.aws_output_creds:
    if os.path.isfile(args.aws_output_creds):
        c['awsOutputBucketCredentials'] = args.aws_output_creds
    else:
        raise IOError("Could not find aws credentials %s"%(args.aws_output_creds))

if( args.save_working_dir == True ):
    if "s3://" not in args.output_dir.lower():
        c['removeWorkingDir'] = False
        c['workingDirectory'] = os.path.join(args.output_dir, "working")
    else:
        print ('Cannot write working directory to S3 bucket (%s).'
              ' Either change the output directory to something'
              ' local or turn off the --removeWorkingDir flag')
else:
    c['removeWorkingDir'] = True
    c['workingDirectory'] = os.path.join('/scratch', "working")

if args.participant_label:
    print ("#### Running C-PAC on %s"%(args.participant_label))
else:
    print ("#### Running C-PAC")

print ("Number of subjects to run in parallel: %d"%(c['numSubjectsAtOnce']))
print ("Output directory: %s"%(c['outputDirectory']))
print ("Working directory: %s"%(c['workingDirectory']))
print ("Crash directory: %s"%(c['crashLogDirectory']))
print ("Log directory: %s"%(c['logDirectory']))
print ("Remove working directory: %s"%(c['removeWorkingDir']))
print ("Available memory: %d (GB)"%(c['memoryAllocatedPerSubject']))
print ("Available threads: %d"%(c['numCoresPerSubject']))
print ("Number of threads for ANTs: %d"%(c['num_ants_threads']))

# create a timestamp for writing config files
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')

#update config file
if not "s3://" in args.output_dir.lower():
    config_file=os.path.join(args.output_dir,"cpac_pipeline_config_%s.yml"%(st))
else:
    config_file=os.path.join("/scratch","cpac_pipeline_config_%s.yml"%(st))

with open(config_file, 'w') as f:
    yaml.dump(c, f)

# we have all we need if we are doing a group level analysis
if args.analysis_level == "group":

    #print ("Starting group level analysis of data in %s using %s"%(args.bids_dir, config_file))
    #import CPAC
    #CPAC.pipeline.cpac_group_runner.run(config_file, args.bids_dir)
    #sys.exit(1)
    print ("Starting group level analysis of data in %s using %s"%(args.bids_dir, config_file))
    sys.exit(0)


# otherwise we move on to conforming the data configuration
if not args.data_config_file:
    file_paths=[]

    if args.bids_dir.lower().startswith("s3://"):
        bucket_name = args.bids_dir.split('/')[2]
        s3_prefix = '/'.join(args.bids_dir.split('/')[:3])
        prefix = args.bids_dir.replace(s3_prefix, '').lstrip('/')

        creds_path = ""
        if args.aws_input_creds:
            if not os.path.isfile(args.aws_input_creds):
                 raise IOError("Could not filed aws_input_creds (%s)"%(args.aws_input_creds))
            creds_path = args.aws_input_creds

        from indi_aws import fetch_creds
        bucket = fetch_creds.return_bucket(creds_path, bucket_name)

        if args.participant_label:
             for pt in args.participant_label:
                 pt=pt.lstrip("sub-")
                 t_prefix="%/sub-%s"%(prefix,pt)

                 for s3_obj in bucket.objects.filter(Prefix=t_prefix):
                     file_paths.append(os.path.join(s3_prefix,str(s3_obj.key)))
        else:
            print "gathering files for %s"%(prefix)
            for s3_obj in bucket.objects.filter(Prefix=prefix):
                file_paths.append(os.path.join(s3_prefix,str(s3_obj.key)))
    
    elif args.participant_label:
        for pt in args.participant_label:
            if "sub-" not in pt:
                pt = "sub-%s"%(pt)
            file_paths+=glob(os.path.join(args.bids_dir,"%s"%(pt),
                "*","*.nii*"))+glob(os.path.join(args.bids_dir,"%s"%(pt),
                "*","*","*.nii*"))
    else:
        file_paths=glob(os.path.join(args.bids_dir,"*","*","*.nii*"))+\
                   glob(os.path.join(args.bids_dir,"*","*","*","*.nii*"))

    if not file_paths:
        print ("Did not find any files to process")
        sys.exit(1)

    from bids_utils import gen_bids_sublist
    sub_list = gen_bids_sublist(file_paths,args.aws_input_creds)

    if not sub_list:
        print "Did not find data in %s"%(args.bids_dir)
        sys.exit(1)


else:
    # load the file as a check to make sure it is available and readable
    sub_list = yaml.load(open(os.path.realpath(args.data_config_file), 'r'))

    if args.participant_label:
        t_sub_list = []
        for sub_dict in sub_list:
            if sub_dict["subject_id"] in args.participant_label or \
                sub_dict["subject_id"].replace("sub-","") in args.participant_label:
                t_sub_list.append(sub_dict)

        sub_list = t_sub_list
            
        if not sub_list:
            print ("Did not find data for %s in %s"%(", ".join(args.participant_label), args.data_config_file))
            sys.exit(1)

if args.participant_ndx:
    if 0 <= int(args.participant_ndx) < len(sub_list):
        # make sure to keep it a list
        sub_list = [sub_list[int(args.participant_ndx)]]
        subject_list_file = "cpac_data_config_pt%s_%s.yml" % (args.participant_ndx,st)
    else:
        print ("Participant ndx %d is out of bounds [0,%d)"%(int(args.participant_ndx),len(sub_list)))
        sys.exit(1)
else:
    # write out the data configuration file
    subject_list_file = "cpac_data_config_%s.yml"%(st)

if "s3://" not in args.output_dir.lower():
    subject_list_file = os.path.join(args.output_dir,subject_list_file)
else:
    subject_list_file = os.path.join("/scratch",subject_list_file)

with open(subject_list_file, 'w') as f:
    yaml.dump(sub_list, f)

if args.analysis_level == "participant":
    #build pipeline easy way
    import CPAC
    from nipype.pipeline.plugins.callback_log import log_nodes_cb

    plugin_args = {'n_procs': int(c['numCoresPerSubject']),
                   'memory_gb': int(c['memoryAllocatedPerSubject']),
                   'callback_log' : log_nodes_cb}

    print ("Starting participant level processing")
    CPAC.pipeline.cpac_runner.run(config_file, subject_list_file,
        plugin='MultiProc', plugin_args=plugin_args)
else:
    print ("This has been a test run, the pipeline and data configuration files should" + \
        " have been written to %s and %s respectively. CPAC will not be run."%(config_file,subject_list_file))

sys.exit(0)
