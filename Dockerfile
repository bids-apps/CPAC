FROM ubuntu:trusty
MAINTAINER John Pellman <john.pellman@childmind.org>

RUN apt-get update && apt-get install -y wget
RUN wget -O cpac_install.sh \
    https://raw.githubusercontent.com/FCP-INDI/C-PAC/0.4.0_development/scripts/cpac_install.sh \
    && bash cpac_install.sh

ENV FSLDIR /usr/share/fsl/5.0
ENV FSLOUTPUTTYPE NIFTI_GZ
ENV FSLMULTIFILEQUIT TRUE
ENV FSLTCLSH /usr/bin/tclsh
ENV FSLWISH /usr/bin/wish
ENV FSLBROWSER /etc/alternatives/x-www-browser
ENV ANTSPATH /opt/ants/bin/
ENV DYLD_FALLBACK_LIBRARY_PATH /opt/afni
ENV LD_LIBRARY_PATH /usr/lib/fsl/5.0:${LD_LIBRARY_PATH}
ENV PATH /opt/c3d/bin:/opt/ants/bin:/opt/afni:/usr/lib/fsl/5.0\
    :/usr/local/bin/miniconda/bin:${PATH} 

RUN mkdir /scratch && mkdir /local-scratch && mkdir -p /code
COPY run.py /code/run.py

ENTRYPOINT ["/code/run.py"]
