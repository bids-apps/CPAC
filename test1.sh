BUILDIR=$(pwd)

docker build -t bids/cpac .

docker run -ti --rm --read-only \
    -v /tmp:/tmp \
    -v /var/tmp:/var/tmp \
    -v ${BUILDIR}/data/ds114_test1:/bids_dataset \
    -v ${BUILDIR}/outputs:/outputs \
    bids/cpac \
    /bids_dataset /outputs participant \
    --participant_label 01 \
    --n_cpus 2 \
    --pipeline_file /cpac_resources/test_pipeline.yaml

mkdir -p ${BUILDIR}/singularity_images
docker run --privileged -ti --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ${HOME}/singularity_images:/output \
    filo/docker2singularity "bids/cpac:latest"

for i in ${HOME}/singularity_images/*.img;
do

done