# oatsmobile-fusion
Avena content abstraction service designed to perform data fusion 
between GPS and RFID data streams from the OATSMobile system.

This service subscribes to the *$avena_host*.gps.TPV and *$avena_host*.rfid.tevents 
topics to correlate both signal streams viatimestamp matching. Messages with 
timestamps that are within a 10ms threshold are considered related.

A new message containing relevant fields such as machine's position at the moment
of tag reading and the received signal strength indicator (RSSI) at which the 
tag was read will be created. This allows users to answer questions like "Where did 
I read tag XXXX?" from a data stream perspective, enabling real-time event insights. 

This software is part of the OATSMobile system, an implementation of the Avena 
software stack for integrating data flows from multiplesensor systems found in 
agricultural vehicles.

## Requirements
Two data sources are required: GPS and RFID. While no specific hardware is 
necessary, both data streams must be available over NATS under the appropriate 
topics. These data streams can be obtained from device drivers and Hardware 
Abstraction Services (HAS), which interact with the hardware and publish data 
payloads as JSON objects sent over NATS. Data payload messages must include 
the following fields:

GPS: 
  - 'time'
  - 'lat'
  - 'lon'
  - 'track'
  - 'speed'
RFID:
  - 'time'
  - 'rssi'
  - 'id'
  - 'phase'
  - 'channel'

For testing, the following hardware and software combinations were used: 

**GPS:** Navisys technology Ublox 8 GNSS Receiver, serial USB. gpsd and avena-gps 
were used as software interfaces to obtain position data.

**RFID:** Zebra FX9600 8-channel RFID reader, using the Zebra IoT Connector as an 
MQTT data source to publish RFID event data to a local NATS server. 

## Deploy
This software can be deployed using Podman or Docker by pulling the container image and
running on a Linux machine:

```
docker pull ghcr.io/oats-center/oatsmobile-fusion:main
```

## Usage
oatsmobile-fusion is a background service that subscribes to two topics of interest. 
The results are then published under the *$vehicle.$avena_host.rfid.revent* topic to the local 
NATS server.

## Acknowledgements

This work is supported by the IoT4Ag Engineering Research Center funded by the National
Science Foundation (NSF) under NSF Cooperative Agreement Number EEC-1941529. Any opinions, 
findings and conclusions, or recommendations expressed in this material are those of the 
author(s), and do not necessarily reflect those of the NSF.
