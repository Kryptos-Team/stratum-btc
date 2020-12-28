###########
# BUILDER #
###########

# Python Version
ARG PYTHON_VERSION=3.7

# Pull the official base image
FROM python:${PYTHON_VERSION}-alpine AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV BUILD_DIR /usr/src/stratum

# Install system libraries for building dependencies
RUN apk update
RUN apk add build-base gcc g++

# Install application specific dependencies
RUN mkdir -p $BUILD_DIR/wheels && mkdir -p $BUILD_DIR/bin
COPY requirements.txt $BUILD_DIR
RUN pip install --upgrade pip
RUN pip wheel --wheel-dir $BUILD_DIR/wheels -r $BUILD_DIR/requirements.txt

#########
# FINAL #
#########

# Pull the official base image
FROM python:${PYTHON_VERSION}-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV BUILD_DIR /usr/src/stratum
ENV PRJ_DIR /opt/kryotos

# Install system libraries for running dependencies
RUN apk update
RUN apk add g++

# Create application user
RUN addgroup --system kryptos && adduser --disabled-password --system --no-create-home --ingroup kryptos kryptos

# Copy compiled files from base
COPY --from=base $BUILD_DIR/wheels /opt/wheels
COPY --from=base $BUILD_DIR/requirements.txt /opt
COPY --from=base $BUILD_DIR/bin /usr/local/bin

# Install application specific dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache /opt/wheels/*
RUN rm -rf /opt/wheels

# Copy project
COPY . $PRJ_DIR

# Fix permissions
RUN chown -R kryptos:kryptos $PRJ_DIR

# Change the user to kryptos
USER kryptos

# Update work directory
WORKDIR $PRJ_DIR

# Run the sh command
CMD ["sh"]
