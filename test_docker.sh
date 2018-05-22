docker run -it --rm \
     -v /home/ccraddock/CPAC/outputs:/mnt \
     -v /home/ccraddock/CPAC/working:/scratch \
     bids/cpac \
     s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/ \
     /mnt \
     participant \
     --participant_ndx 1 \
     --n_cpus 8 \
     --mem_gb 16
