FROM neurodebian:xenial-non-free
MAINTAINER John Pellman <john.pellman@childmind.org>

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
ENV PATH /code:/opt/c3d/bin:/opt/ants/bin:/opt/afni:${FSLDIR}/bin:/usr/local/bin/miniconda/envs/cpac/bin:${PATH}

# create scratch directories for singularity
RUN mkdir /scratch && mkdir /local-scratch && mkdir -p /code && mkdir -p /cpac_resources

## install wget
RUN apt-get update && apt-get install -y wget

## Install the validator
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_4.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN npm install -g bids-validator

# install FSL
# and remove big atlases we do not use
RUN apt-get update && \
            apt-get install -y fsl-5.0-core fsl-5.0-doc fsl-atlases fslview && \
            apt-get autoclean -y && \
            apt-get clean -y && \
            apt-get autoremove -y


# install C3d
RUN  wget http://sourceforge.net/projects/c3d/files/c3d/c3d-0.8.2/c3d-0.8.2-Linux-x86_64.tar.gz && \
     tar xfz c3d-0.8.2-Linux-x86_64.tar.gz && \
     mv c3d-0.8.2-Linux-x86_64 /opt/c3d && \
     export PATH=/opt/c3d/bin:$PATH && \
     echo '# Path to C3D' >> ~/cpac_env.sh && \
     echo 'export PATH=/opt/c3d/bin:$PATH' >> ~/cpac_env.sh && \
     rm c3d-0.8.2-Linux-x86_64.tar.gz

# install ANTS
RUN apt-get update && \
    apt-get install -y ants && \
    apt-get autoclean -y && \
    apt-get clean -y && \
    apt-get autoremove -y

# install AFNI
RUN apt-get install -y afni=16.2.07~dfsg.1-5~nd16.04+1 && \
    export PATH=/usr/lib/afni/bin:$PATH && \
    export DYLD_FALLBACK_LIBRARY_PATH=/usr/lib/afni/bin && \
    echo '# Path to AFNI' >> ~/cpac_env.sh && \
    echo 'export PATH=/usr/lib/afni/bin:$PATH' >> ~/cpac_env.sh && \
    echo 'export DYLD_FALLBACK_LIBRARY_PATH=/usr/lib/afni/bin' >> ~/cpac_env.sh

COPY cpac_install.sh /tmp/cpac_install.sh

# install system dependencies
# install python dependencies
# install CPAC
RUN /tmp/cpac_install.sh -s -p -n cpac

COPY version /code/version
COPY bids_utils.py /code/bids_utils.py
COPY run.py /code/run.py
COPY cpac_templates.tar.gz /cpac_resources/cpac_templates.tar.gz
RUN chmod +x /code/run.py && cd /cpac_resources \
   && tar xzvf /cpac_resources/cpac_templates.tar.gz \
   && rm -f /cpac_resources/cpac_templates.tar.gz

COPY default_pipeline.yaml /cpac_resources/default_pipeline.yaml
COPY test_pipeline.yaml /cpac_resources/test_pipeline.yaml

ENTRYPOINT ["/code/run.py"]
