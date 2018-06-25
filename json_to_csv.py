#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Convert JSON or JSON-Lines file with complex structures into CSV using
namespacing, with '.' characters

This version adds:
 * argparse (due to support for JSON or JSON-Lines)
 * Removal from the root of the initial '.' in the key name of CSV fields

Original version by vinay20045
Additions by copyright@mzpqnxow.com
"""
from argparse import ArgumentParser
from json import (
    load as load_json,
    loads as load_jsons)
import csv


def to_string(s):
    try:
        return str(s)
    except Exception:
        return s.encode('utf-8')

##
# This function converts an item like
# {
#   "item_1":"value_11",
#   "item_2":"value_12",
#   "item_3":"value_13",
#   "item_4":["sub_value_14", "sub_value_15"],
#   "item_5":{
#       "sub_item_1":"sub_item_value_11",
#       "sub_item_2":["sub_item_value_12", "sub_item_value_13"]
#   }
# }
# To
# {
#   "node_item_1":"value_11",
#   "node_item_2":"value_12",
#   "node_item_3":"value_13",
#   "node_item_4_0":"sub_value_14",
#   "node_item_4_1":"sub_value_15",
#   "node_item_5_sub_item_1":"sub_item_value_11",
#   "node_item_5_sub_item_2_0":"sub_item_value_12",
#   "node_item_5_sub_item_2_0":"sub_item_value_13"
# }
##


def reduce_item(key, value):
    global reduced_item

    # Reduction Condition 1
    if type(value) is list:
        i = 0
        for sub_item in value:
            reduce_item('{}{}{}'.format(
                key, '.', to_string(i)),
                sub_item)
            i += 1

    # Reduction Condition 2
    elif type(value) is dict:
        if not key:
            nschar = ''
        else:
            nschar = '.'
        sub_keys = value.keys()
        for sub_key in sub_keys:
            reduce_item('{}{}{}'.format(
                key, nschar, to_string(sub_key)),
                value[sub_key])
    # Base Condition
    else:
        reduced_item[to_string(key)] = to_string(value)


def handle_cli():
    """Reading arguments"""
    parser = ArgumentParser(description='Description of your program')
    parser.add_argument('-i', '--in', dest='infile', help='Input JSON file', required=True)
    parser.add_argument('-o', '--out', dest='outfile', help='Output CSV file', required=True)
    parser.add_argument('-n', '--nodename', dest='node', help='Node', required=False, default='')
    parser.add_argument('-J', '--json', dest='json', help='Node', required=False)
    parser.add_argument('-j', '--jsonlines', dest='jsonlines', help='Node', required=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = handle_cli()
    json_file_path = args.infile
    csv_file_path = args.outfile
    node = args.node

    jsonlines = args.jsonline
    jsonregular = args.json

    if not filter(None, (jsonlines, jsonregular)):
        print('Must specify --json or --jsonlines !!')
        exit

    raw_data = list()
    fp = open(json_file_path, 'r')

    if jsonlines:
        for line in fp.readlines():
            raw_data.append(load_jsons(line.strip()))
    elif jsonregular:
        raw_data = load_json(fp)
    else:
        raise RuntimeError('Expected json-lines or json')

    assert isinstance(raw_data, list)

    try:
        data_to_be_processed = raw_data[node]
    except Exception:
        data_to_be_processed = raw_data

    processed_data = []
    header = []
    for item in data_to_be_processed:
        reduced_item = {}
        reduce_item(node, item)
        header += reduced_item.keys()
        processed_data.append(reduced_item)
    header = list(set(header))
    header.sort()

    with open(csv_file_path, 'w+') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)
    print('Completed writing csv file with {} columns'.format(header))
