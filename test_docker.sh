docker run -it --rm \
     -v /home/ccraddock/CPAC:/mnt \
     -v /home/ccraddock/CPAC/working:/scratch \
     -e AWS_BATCH_JOB_ARRAY_INDEX=11 \
     -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
     -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
     -u $UID:$UID \
     --entrypoint=/mnt/run.py\
     cpac_next \
     s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/Caltech \
     s3://dms-iaic/cpac_test/test1/output \
     test_config \
     --aws_data_input_creds anon \
     --n_cpus 8 \
     --mem_gb 16 \
     --pipeline_file s3://dms-iaic/cpac_test/test1/output/cpac_pipeline_config_20180526200954.yml \
     --participant_label '0051480 0051481' \
     --participant_ndx 1 

     #--aws_output_creds env \

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
