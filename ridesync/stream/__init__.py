"""Stream processing (M4): per-zone features from the live event stream.

- ``zones``     taxi zone lookup (dependency-free, runs inside Flink)
- ``features``  the feature logic as plain functions with explicit state
- ``job``       the PyFlink job that runs it on Kafka
"""
