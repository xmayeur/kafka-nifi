# NIFI & KAFKA Sandbox setup

This repository contains a docker-containerized sandbox environment 
to setup a Kafka broker & Nifi or Python Faust streaming environment

- Confluent Kafka Broker & Schema registry setup

- Apache Nifi flow and registry setup

  A small flow is included to publish a testTopic when dropping the msg.json file into the files folder
  and to perform a basic data mapping on the injected data. Result is sinked into new harvestDataTopic topic

  Note: 
	please check this [link](https://medium.com/geekculture/host-a-fully-persisted-apache-nifi-service-with-docker-ffaa6a5f54a3)
        for instruction on the initial setup of Nifi for persisted operations if starting from scratch

- Zookeeper for global coordination

- Python faust-streaming example to susbscribe to kafka events.
  This example listens to the two topics mentionned above and displays them on the console
 



