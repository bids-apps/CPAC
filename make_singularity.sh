docker run --privileged -ti --rm  \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ${PWD}/singularity_images:/output \
    filo/docker2singularity \
    bids/cpac
  
