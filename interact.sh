BUILDIR=$(pwd)

docker run -ti --rm --read-only \
    -v /tmp:/tmp \
    -v /var/tmp:/var/tmp \
    -v ${BUILDIR}/data/ds114_test1:/bids_dataset \
    -v ${BUILDIR}/outputs:/outputs \
    --entrypoint /bin/bash \
    bids/cpac
