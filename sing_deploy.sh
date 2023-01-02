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
docker run -ti --rm \
    --privileged \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ${BUILDIR}/singularity_images:/output \
    filo/docker2singularity "bids/cpac:latest"

sing_img=$(ls -t ${BUILDIR}/singularity_images | head -n 1)
version=$( git describe --tags )
if [ -n ${sing_img} ]
then
    echo "Copying ${sing_img} into bucket"
    aws s3 cp --acl public-read ${BUILDIR}/singularity_images/${sing_img} s3://fcp-indi/resources/singularity_images/C-PAC_latest.img
    aws s3 cp --acl public-read ${BUILDIR}/singularity_images/${sing_img} s3://fcp-indi/resources/singularity_images/C-PAC_${version}.img
else
    echo "Singularity image not found in ${BUILDIR}/singularity_images"
fi
