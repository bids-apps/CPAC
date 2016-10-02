FROM ubuntu:trusty
MAINTAINER John Pellman <john.pellman@childmind.org>

#RUN apt-get update && apt-get install -y wget
#RUN wget -O cpac_install.sh \
    #https://raw.githubusercontent.com/FCP-INDI/C-PAC/0.4.0_development/scripts/cpac_install.sh \
    #&& bash cpac_install.sh

ENV FSLDIR /usr/share/fsl/5.0
ENV FSLOUTPUTTYPE NIFTI_GZ
ENV FSLMULTIFILEQUIT TRUE
ENV FSLTCLSH /usr/bin/tclsh
ENV FSLWISH /usr/bin/wish
ENV FSLBROWSER /etc/alternatives/x-www-browser
ENV ANTSPATH /opt/ants/bin/
ENV DYLD_FALLBACK_LIBRARY_PATH /opt/afni
ENV LD_LIBRARY_PATH /usr/lib/fsl/5.0:${LD_LIBRARY_PATH}
ENV PATH /code:/opt/c3d/bin:/opt/ants/bin:/opt/afni:${FSLDIR}/bin:/usr/local/bin/miniconda/bin:${PATH}

RUN mkdir /scratch && mkdir /local-scratch && mkdir -p /code && mkdir -p /cpac_resources
COPY cpac_install.sh /tmp/cpac_install.sh
RUN /tmp/cpac_install.sh -s
RUN /tmp/cpac_install.sh -p
RUN /tmp/cpac_install.sh -n afni
RUN /tmp/cpac_install.sh -n fsl
RUN /tmp/cpac_install.sh -n c3d
#RUN /tmp/cpac_install.sh -n ants
RUN apt-get install -y ants
RUN /tmp/cpac_install.sh -n cpac

## Install the validator
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_4.x | bash - && \
    apt-get remove -y curl && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN npm install -g bids-validator

COPY bids_utils.py /code/bids_utils.py
COPY run.py /code/run.py
COPY cpac_templates.tar.gz /cpac_resources/cpac_templates.tar.gz
RUN chmod +x /code/run.py && cd /cpac_resources \
   && tar xzvf /cpac_resources/cpac_templates.tar.gz \
   && rm -f /cpac_resources/cpac_templates.tar.gz

COPY default_pipeline.yaml /cpac_resources/default_pipeline.yaml
COPY test_pipeline.yaml /cpac_resources/test_pipeline.yaml

COPY version /version

ENTRYPOINT ["/code/run.py"]
