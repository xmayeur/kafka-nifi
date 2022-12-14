#!/bin/env python3

import io
import json
from os.path import join
import sys
import fastavro
import faust
import names
import oyaml
from confluent_schema_registry_client import SchemaRegistryClient


def save_to_file(_json, _topic):
    path_name = r"/poc/OutputEvents"
    file_name = str(_json['GEPEventAVROSchemaHeader']['timestamp']) + '-' + _topic + '.json'
    json.dump(_json, open(join(path_name, file_name), 'w'), indent=4)


config = oyaml.load(open('config.yaml', 'r'), Loader=oyaml.Loader)
mode = config['default']['mode']
broker = config[mode]['broker']
sandbox = config['default']['sandbox']
registry = config[mode]['schema_registry']
generate_names = config['default']['generate_names']
# connect to kafka registry
c = SchemaRegistryClient(registry)


class AvroSchemaDecoder(faust.Schema):
    """An extension of Faust Schema class. The class is used by Faust when
    creating streams from Kafka topics. The decoder deserializes each message
    according to the AVRO schema injected in each message's header.
    """

    def __init__(self):
        super().__init__()
        self.schema_cache = {}

    def __fast_avro_decode(self, schema, encoded_message):
        stringio = io.BytesIO(encoded_message)
        # schema_id = int.from_bytes(stringio.read(5), byteorder='big')
        # print(schema_id)
        # if encoded_message[0] == 0:
        stringio.seek(5)
        return fastavro.schemaless_reader(stringio, schema)

    def loads_value(self, app, message, *, loads=None, serializer=None):
        # headers = dict(message.headers)
        # avro_schema = fastavro.parse_schema(json.loads(headers["avro.schema"]))
        # return self.__fast_avro_decode(avro_schema, message.value)
        _topic = message.topic
        if _topic in self.schema_cache:
            avro_schema = self.schema_cache[_topic]
        else:
            avro_schema = c.get_subject_latest_version(_topic + '-value')
            self.schema_cache[_topic] = avro_schema

        # avro_schema = fastavro.parse_schema(avro_schema)
        try:
            return self.__fast_avro_decode(avro_schema, message.value)
        except Exception as e:
            print(f'error {e}')
            return {}

    def loads_key(self, app, message, *, loads=None, serializer=None):
        if message.key:
            return json.loads(message.key)


class Names(faust.Record):
    first: str
    last: str


app = faust.App(
    'testData',
    broker=f'kafka://{broker}',
    value_serializer='json',
    topic_disable_leader=True,
)

if sandbox == '0.0':

    topic = app.topic('testTopic', value_type=Names)
    topics = ('testTopic',)
    input_topic = app.topic(
        *topics,
        value_type=str,
        key_type=str,
    )

    @app.agent(input_topic)
    async def msg(events):
        async for event in events:
            print('INPUT: ', event)


    topics2 = config['stream']['topics']
    out_topic = app.topic(
        *topics2,
        value_type=str,
        key_type=str,
    )

    @app.agent(out_topic)
    async def msg2(events2):
        async for event2 in events2:
            print('OUTPUT: ', event2)

    if generate_names:
        @app.timer(interval=0.3)
        async def send_names(message):
            await topic.send(value=Names(last=names.get_last_name(), first=names.get_first_name()), force=True)
            await app.maybe_start_client()


if __name__ == '__main__':
    app.main()
