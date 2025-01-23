#!/usr/bin/python
#
# Module to cleanup Elasticsearch logs
#

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'Ranjith Gowder',
                    'metadata_version': '0.1'}

DOCUMENTATION = '''
---
module: curator_es_cleanup

description:
  - Deletes logs from elasticsearch

author: Ranjith Gowder

options:
  host:
    description:
      - The fully qualified host name to interact with [ Elasticsearch endpoint]
    required: true

  port:
    description:
      - elasticsearch host port
    required: true
    default: 443

  time_unit:
    required: True
    choice: "hours", "days", "weeks", "months"
    default: days

  unit_count:
    required: true
    default: 45

requirements: [ elasticsearch, elasticsearch-curator ]
'''

EXAMPLES = '''
- name: Cleaning elasticsearch indices
  curator_es_cleanup:
    host: demo.us-east-1.es.amazonaws.com
    port: 443
    time_unit: days
    unit_count: 45
'''

import boto3
import elasticsearch
import curator
from requests_aws4auth import AWS4Auth

from ansible.module_utils.aws.core import AnsibleAWSModule


def setup_module_object():
    argument_spec = dict(
        host=dict(required=True),
        port=dict(default=443, type='int'),
        unit_count=dict(default=45, type='int'),
        time_unit=dict(default="days", choices=["hours", "days", "weeks", "months"]),
    )

    return AnsibleAWSModule(
        argument_spec=argument_spec,
    )


def cleanup(module):
    changed = False
    index = {}
    host = module.params.get('host')
    port = module.params.get('port')
    unit_count = module.params.get('unit_count')
    time_unit = module.params.get('time_unit')

    try:
        index = delete_old_indices(host, port, unit_count, time_unit, module)
        if len(index) > 0:
            changed = True
    except AttributeError as e:
        module.fail_json(e)
    except curator.exceptions.NoIndices as e:
        module.exit_json(changed=changed, msg="No Indices to be deleted")
    except curator.exceptions.FailedExecution as e:
        module.fail_json(msg="Failed to delete Indices, validate client connection")
    return changed, index


def delete_old_indices(host, port, unit_count, time_unit, module):
    service = 'es'
    region = 'eu-west-1'
    credentials = boto3.Session().get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region, service, session_token=credentials.token)

    # Create the ES object
    client = elasticsearch.Elasticsearch(
        http_auth=awsauth,
        hosts=[{
            'host': host,
            'port': port}],
        use_ssl=True,
        verify_certs=True,
        connection_class=elasticsearch.RequestsHttpConnection
    )

    indices = curator.IndexList(client)
    indices.filter_by_age(source='name', direction='older', timestring="%Y.%m.%d", unit=time_unit,
                          unit_count=int(unit_count))

    indices.empty_list_check()
    delete_indices = curator.DeleteIndices(indices)
    delete_indices.do_action()
    return indices.working_list()


def main():
    module = setup_module_object()

    (changed, index) = cleanup(module)
    module.exit_json(changed=changed, index=index)


if __name__ == '__main__':
    main()
