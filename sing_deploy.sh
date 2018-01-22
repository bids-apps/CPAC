BUILDIR=$(pwd)
VERSION=
docker build -t bids/cpac .
mkdir -p ${BUILDIR}/singularity_images
docker run --privileged -ti --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ${HOME}/singularity_images:/output \
    filo/docker2singularity "bids/cpac:latest"

for i in ${HOME}/singularity_images/*.img;
do
    
done
