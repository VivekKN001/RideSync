"""Live mode: the simulator and the matcher as separate services talking over Kafka.

- ``schema``    topics and message types
- ``bus``       Bus interface and an in-memory implementation; ``kafka_bus`` is the Kafka one
- ``world``     the live simulator (source of truth)
- ``matcher``   the matcher service (proposes offers)
- ``lockstep``  both in one process with zero latency; reproduces the offline simulator exactly
- ``sim``       CLI for a live run; ``topics`` creates the Kafka topics
"""
