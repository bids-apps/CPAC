FROM neurodebian:xenial-non-free
MAINTAINER John Pellman <john.pellman@childmind.org>

# create scratch directories for singularity
RUN mkdir /scratch && mkdir /local-scratch && mkdir -p /code && mkdir -p /cpac_resources

# install wget
RUN apt-get update && apt-get install -y wget

# Install the validator
RUN apt-get update && \
     apt-get install -y curl && \
     curl -sL https://deb.nodesource.com/setup_4.x | bash - && \
     apt-get install -y nodejs && \
     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN npm install -g bids-validator

COPY cpac_install.sh /tmp/cpac_install.sh

# install system dependencies, python dependencies, and CPAC
RUN /tmp/cpac_install.sh -r

COPY version /code/version
COPY bids_utils.py /code/bids_utils.py
COPY run.py /code/run.py
COPY run.sh /code/run.sh
COPY cpac_templates.tar.gz /cpac_resources/cpac_templates.tar.gz
RUN chmod +x /code/run.py && cd /cpac_resources \
    && tar xzvf /cpac_resources/cpac_templates.tar.gz \
    && rm -f /cpac_resources/cpac_templates.tar.gz

COPY default_pipeline.yaml /cpac_resources/default_pipeline.yaml
COPY test_pipeline.yaml /cpac_resources/test_pipeline.yaml

ENTRYPOINT ["/code/run.sh"]
