FROM python:3.10.0b2
# Stay on python 3.7 until PyPi gets a version of pymodm that includes
#   https://github.com/mongodb/pymodm/pull/64
# Current pymodm version (0.4.2 - https://pypi.org/project/pymodm/)
# does not play well with Python 3.8.
# See also: https://github.com/jsf9k/pca-core/issues/4
MAINTAINER Dave Redmin <david.redmin@trio.dhs.gov>
ENV PCA_HOME="/home/pca" \
    PCA_ETC="/etc/pca" \
    PCA_CORE_SRC="/usr/src/pca-core"

RUN groupadd --system pca && useradd --system --gid pca pca

RUN mkdir ${PCA_HOME} && chown pca:pca ${PCA_HOME}
RUN mkdir ${PCA_ETC} && chown pca:pca ${PCA_ETC}
VOLUME ${PCA_ETC} ${PCA_HOME}

WORKDIR ${PCA_CORE_SRC}

COPY . ${PCA_CORE_SRC}
RUN pip install --no-cache-dir .[dev]
RUN ln -snf ${PCA_CORE_SRC}/var/getenv /usr/local/bin

USER pca
WORKDIR ${PCA_HOME}
CMD ["getenv"]
