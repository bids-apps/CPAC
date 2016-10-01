#!/usr/bin/env python
import argparse
import os
from glob import glob
from subprocess import Popen, PIPE
from shutil import rmtree
import subprocess
import yaml
#import CPAC.utils as cpac_utils
import sys
from bids_utils import gen_bids_sublist
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
    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
    'should be stored. If you are running group level analysis '
    'this folder should be prepopulated with the results of the '
    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will '
    ' be performed. Multiple participant level analyses can be run '
    ' independently (in parallel) using the same output_dir.',
    choices=['participant', 'group'])
parser.add_argument('--participant_label', help='The label of the participant'
    ' that should be analyzed. The label '
    'corresponds to sub-<participant_label> from the BIDS spec '
    '(so it does not include "sub-"). If this parameter is not '
    'provided all subjects should be analyzed. Multiple '
    'participants can be specified with a space separated list.', nargs="+")
parser.add_argument(' ', help='Name for the pipeline '
    ' configuration file to use',
    default="/cpac_resources/default_pipeline.yaml")
parser.add_argument('--n_cpus', help='Number of execution '
    ' resources available for the pipeline', default="1")
parser.add_argument('--mem', help='Amount of RAM available to the pipeline'
    '(GB).', default="6")
parser.add_argument('--save_working_dir', action='store_true',
    help='Save the contents of the working directory.', default=False)

# get the command line arguments
args = parser.parse_args()

# validate input dir
run("bids-validator %s"%args.bids_dir)

print(args)

# get and set configuration
c = yaml.load(open(os.path.realpath(args.pipeline_file), 'r'))

# set the parameters using the command line arguements
# TODO: we will need to check that the directories exist, and
# make them if they do not
c['outputDirectory'] = os.path.join(args.output_dir, "output")
c['crashLogDirectory'] = os.path.join(args.output_dir, "crash")
c['logDirectory'] = os.path.join(args.output_dir, "log")

c['memoryAllocatedPerSubject'] = int(args.mem)
c['numCoresPerSubject'] = int(args.n_cpus)
c['numSubjectsAtOnce'] = 1
c['num_ants_threads'] = min(args.n_cpus, int(c['num_ants_threads']))

if( args.save_working_dir == True ):
    c['removeWorkingDir'] = False
    c['workingDirectory'] = os.path.join(args.output_dir, "working")
else:
    c['removeWorkingDir'] = True
    c['workingDirectory'] = os.path.join('/tmp', "working")

print ("#### Running C-PAC on %s"%(args.participant_label))
print ("Number of subjects to run in parallel: %d"%(c['numSubjectsAtOnce']))
print ("Output directory: %s"%(c['outputDirectory']))
print ("Working directory: %s"%(c['workingDirectory']))
print ("Crash directory: %s"%(c['crashLogDirectory']))
print ("Log directory: %s"%(c['logDirectory']))
print ("Remove working directory: %s"%(c['removeWorkingDir']))
print ("Available memory: %d (GB)"%(c['memoryAllocatedPerSubject']))
print ("Available threads: %d"%(c['numCoresPerSubject']))
print ("Number of threads for ANTs: %d"%(c['num_ants_threads']))

#create subject list
if args.analysis_level == "group":
    print "Group level analysis is not currently supported yet"
    sys.exit(0)


file_paths=[]

if args.participant_label:
    for pt in args.participant_label:
        file_paths+=glob(os.path.join(args.bids_dir,"sub-%s"%(pt),
            "*","*.nii*"))+glob(os.path.join(args.bids_dir,"sub-%s"%(pt),
            "*","*","*.nii*"))
else:
    file_paths=glob(os.path.join(args.bids_dir,"*","*.nii*"))+\
               glob(os.path.join(args.bids_dir,"*","*","*.nii*"))

sub_list = gen_bids_sublist(file_paths)

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
subject_list_file=os.path.join(args.output_dir,"bids_run_sublist_%s.yml"%(st))
with open(subject_list_file, 'w') as f:
    yaml.dump(sub_list, f)

#update config file
config_file=os.path.join(args.output_dir,"bids_run_config_%s.yml"%(st))
with open(config_file, 'w') as f:
    yaml.dump(c, f)

#build pipeline easy way
import CPAC
CPAC.pipeline.cpac_runner.run(config_file, subject_list_file)
