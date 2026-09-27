# Flink 1.20 with PyFlink and the Kafka connector.
# The ridesync package is mounted at /opt/ridesync (see docker-compose.yml), not copied,
# so code changes only need a job resubmit, not an image rebuild.
FROM flink:1.20.1-scala_2.12-java17

ARG KAFKA_CONNECTOR=3.3.0-1.20

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip python3-dev \
 && ln -sf /usr/bin/python3 /usr/bin/python \
 && rm -rf /var/lib/apt/lists/*

# PyFlink supports Python 3.8-3.11; this image's python3 is 3.10.
RUN pip3 install --no-cache-dir "apache-flink==1.20.1" "scipy<1.14"

RUN wget -q -P /opt/flink/lib \
    "https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${KAFKA_CONNECTOR}/flink-sql-connector-kafka-${KAFKA_CONNECTOR}.jar"

ENV PYTHONPATH=/opt/ridesync

# Checkpoint directory owned by the flink user (a new named volume copies this ownership).
RUN mkdir -p /opt/flink/checkpoints && chown flink:flink /opt/flink/checkpoints
