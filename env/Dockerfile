FROM ubuntu:20.04

# Use bash as default shell.
SHELL ["/bin/bash", "-c"]

# basic utilities
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        sudo \
        wget \
        curl \
        git \
        zip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean 

# install conda
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}
RUN wget --quiet \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p ${CONDA_DIR} \
    && rm ~/miniconda.sh \
    && ln -s ${CONDA_DIR}/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc \
    && echo "conda activate base" >> ~/.bashrc

# create environment and install TWS API
COPY environment.yml .
COPY api ./api
RUN conda env create --file environment.yml \
    && conda run -n myenv pip install ./api \
    && conda clean -y --all

# add user (uid and gid can be modified by entrypoint.sh)
ARG NB_USER=user
ARG NB_GROUP=usergroup
ARG NB_UID=1000
ARG NB_GID=1000
RUN groupadd --gid ${NB_GID} ${NB_GROUP} \
    && useradd --create-home --shell /bin/bash --uid ${NB_UID} --gid ${NB_GID} ${NB_USER} \
    # && chown -R ${NB_USER}:${NB_GROUP} ${CONDA_DIR} \
    # && chmod -R 775 ${CONDA_DIR} \
    && echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> /home/${NB_USER}/.bashrc

# copy entrypoint.sh
COPY entrypoint.sh /usr/local/bin/
RUN chmod 777 /usr/local/bin/entrypoint.sh

# switch user
USER ${NB_USER}
WORKDIR /home/${NB_USER}/work
