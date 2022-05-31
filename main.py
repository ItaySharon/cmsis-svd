import cmsis_svd.model as model
import six
import json

from dict2xml import dict2xml
from cmsis_svd.parser import SVDParser

import os

from pwn import log

STARTPATH = '/home/user/PycharmProjects/SVDuh/cmsis-svd/data/'

# SVD_FILENAME = 'esp32c3.svd'
# OUTPUT_FILENAME = 'esp32c3-real.svd'


def snake2camel(word):
    temp = word.split('_')
    # joining result
    return temp[0] + ''.join(ele.title() for ele in temp[1:])


def _unpack(data):
    if isinstance(data, dict):
        return data.items()
    return data


def keys_to_camel_case(content):
    """
    Convert all keys for given dict to snake case
    :param content: dict
    :return: dict
    """
    if content is None:
        return {}
    return {snake2camel(key): value for key, value in content.items()}


def decode_keys(data):
    """
    Convert all keys for given dict/list to snake case recursively
    :param data: dict
    :return: dict
    """
    formatted = {}
    for key, value in _unpack(keys_to_camel_case(data)):
        if isinstance(value, dict):
            formatted[key] = decode_keys(value)
        elif isinstance(value, list) and len(value) > 0:
            formatted[key] = []
            sublings_name = key[:-1]
            for _, val in enumerate(value):
                formatted[key].append({sublings_name: decode_keys(val)})
        elif isinstance(value, bool):
            formatted[key] = str(value).lower()
        elif isinstance(value, int):
            formatted[key] = f'0x{value:X}'
        elif value is not None:
            formatted[key] = value

    return formatted


def doit(filename):
    parser = SVDParser.for_xml_file(filename)
    xml = dict2xml(decode_keys(parser.get_device().to_dict()))
    with open(filename, 'w') as out:
        out.write("""<?xml version="1.0" encoding="UTF-8"?>
<device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.1" xs:noNamespaceSchemaLocation="CMSIS-SVD_Schema_1_1.xsd">""")
        out.write(xml)
        out.write('</device>')


def main():
    for original, dirs, files in os.walk(STARTPATH):
        for file in files:
            if file.endswith('.svd'):
                log.info(f'Working on {file}...')
                doit(os.path.join(original, file))
        log.success(f'Finished dir {original}')

    log.success('Done!')


if __name__ == '__main__':
    main()
