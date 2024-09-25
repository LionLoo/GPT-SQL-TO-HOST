#!/usr/bin/python3
import os
import asyncio
import nats
import json
from datetime import datetime, timedelta
from dateutil import parser

print("Starting oatsmobile-fusion v0.1...")

# Define an acceptable time threshold to correlate messages
TIME_THRESHOLD = 0.01
# Get Avena Prefixes from env variable
prefix = os.getenv('AVENA_HOST')
vehicle = os.getenv('AVENA_VEHICLE')
# Define subject to publish
subject = f"{vehicle}.{prefix}.rfid.revent"

async def main():


    # Create nats object and connect to local nats server
    print('Connecting to NATS server...')
    try:
        nc = await nats.connect("nats://localhost:4222")
        print("NATS connection successful!")
    except:
        print("Failed to connect to NATS server")
    
    gps_messages = []
    rfid_messages = []

    async def correlate_data():
        
        # Lists to store correlated messages for deletion 
        correlated_gps = []
        correlated_rfid = []
        agg_msg = {}
    
        for gps_msg in gps_messages:
            # Some messages may come without a fix. For those, we will skip to the next iteration
            # once we get a proper fix.
            try:
                gps_msg['lat']
            except(KeyError):
                continue
            
            gps_time = datetime.timestamp(parser.parse(gps_msg['time']))

            for rfid_msg in rfid_messages:
                rfid_time = datetime.timestamp(parser.parse(rfid_msg['timestamp']))
                
                # Check if both RFID and GPS timestamps are reasonably close
                if abs(gps_time - rfid_time <= TIME_THRESHOLD):
                    
                    # Create aggregated message from both GPS and RFID streams
                    agg_msg['time'] = rfid_msg['timestamp']
                    agg_msg['lat'] = gps_msg['lat']
                    agg_msg['lon'] = gps_msg['lon']
                    agg_msg['track'] = gps_msg['track']
                    agg_msg['speed'] = gps_msg['speed']
                    agg_msg['gps_src'] = gps_msg['device']
                    agg_msg['id'] = rfid_msg['data']['idHex']
                    agg_msg['channel'] = rfid_msg['data']['channel']
                    agg_msg['rssi'] = rfid_msg['data']['peakRssi']
                    agg_msg['phase'] = rfid_msg['data']['phase']
                    agg_msg['antenna'] = rfid_msg['data']['antenna']
                    
                    # Publish aggregated message
                    print(f"{agg_msg}")
                    await nc.publish(subject, bytes(json.dumps(agg_msg), 'utf-8'))
                    # Remove processed messages from buffers
                    rfid_messages.remove(rfid_msg)
            
            gps_messages.remove(gps_msg)

    # Define handlers for messages
    async def gps_handler(msg):
        # Parse incoming msg as JSON object
        data = json.loads(msg.data.decode())
        gps_messages.append(data)
        await correlate_data()

    async def rfid_handler(msg):
        # Parse incoming msg as JSON object
        data = json.loads(msg.data.decode())
        rfid_messages.append(data)
        await correlate_data()
    
    # Get location from TPV signal
    gps_topic = f"{prefix}.gps.TPV"

    # Get RFID reading from tag event topic
    rfid_topic = f"{prefix}.rfid.tevents"

    # Subscribe to both GPS and RFID topics
    gps_sub = await nc.subscribe(gps_topic, cb=gps_handler)
    rfid_sub = await nc.subscribe(rfid_topic, cb=rfid_handler)

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
        
    try:
        #asyncio.run(main())
        loop.run_forever()
    except(KeyboardInterrupt):
        print("Stopping...")
        quit()
    loop.close()
