# test before rebuildling

BUILDIR=$(pwd)

#docker build -t bids/cpac .

docker run -ti --rm --read-only \
    -v /tmp:/scratch \
    -v /var/tmp:/var/tmp \
    -v ${BUILDIR}:/code \
    -v ${BUILDIR}/data/ds114_test1:/bids_dataset \
    -v ${BUILDIR}/outputs:/outputs \
    --entrypoint /code/run.py \
    bids/cpac \
    /bids_dataset /outputs test_config \
    --participant_label 01 \
    --n_cpus 2 \
    --pipeline_file /cpac_resources/test_pipeline.yaml
