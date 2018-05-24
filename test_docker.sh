docker run -it --rm \
     -v /home/ccraddock/CPAC:/mnt \
     -v /home/ccraddock/CPAC/working:/scratch \
     -e AWS_BATCH_JOB_ARRAY_INDEX=11 \
     -u $UID:$UID \
     --entrypoint=/mnt/run.py\
     cpac_next \
     s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/Caltech \
     /mnt/outputs \
     participant \
     --n_cpus 8 \
     --mem_gb 16 \
     --pipeline_file /cpac_resources/test_pipeline.yaml \
     --participant_label 0051480
     #--participant_ndx -1 
     #--data_config_file s3://fcp-indi/data/Projects/ABIDE/cpac_data_config.yml \
#docker run -it --rm \
     #-v /home/ccraddock/CPAC/outputs:/mnt \
     #-v /home/ccraddock/CPAC/working:/scratch \
     #bids/cpac \
     #s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/ \
     #/mnt \
     #participant \
     #--participant_ndx 1 \
     #--n_cpus 8 \
     #--mem_gb 16
