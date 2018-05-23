docker run -it --rm \
     -v /home/ccraddock/CPAC:/mnt \
     -v /home/ccraddock/CPAC/working:/scratch \
     -e AWS_BATCH_JOB_ARRAY_INDEX=11 \
     --entrypoint=/mnt/run.py \
     bids/cpac \
     s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/ \
     /mnt/outputs \
     test_config \
     --n_cpus 8 \
     --mem_gb 16 \
     --pipeline_file s3://fcp-indi/data/Projects/ABIDE/cpac_pipeline_config.yml \
     --data_config_file s3://fcp-indi/data/Projects/ABIDE/cpac_data_config.yml \
     --participant_label Stanford+0051160
     #--participant_ndx -1 
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
