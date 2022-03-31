import ssl
import json
import pathlib
import urllib.request

from os import path
from builtins import input
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


def read_url(url):
    url = url.replace(path.sep, '/')
    resp = urllib.request.urlopen(url, context=ssl._create_unverified_context())
    return resp.read()


class LivePipelineManager:

    def __init__(self):
        config = json.loads(pathlib.Path('settings/appsettings.json').read_text())

        self.api_version = '1.0'
        self.device_id = config['deviceId']
        self.module_id = config['moduleId']
        self.registry_manager = IoTHubRegistryManager(config['IoThubConnectionString'])

    def invoke(self, method_name, payload):
        if method_name == 'pipelineTopologySet':
            self.pipeline_topology_set(payload)
            return

        if method_name == 'WaitForInput':
            print(payload['message'])
            input()
            return

        self.invoke_module_method(method_name, payload)

    def invoke_module_method(self, method_name, payload):
        payload['@apiVersion'] = self.api_version

        module_method = CloudToDeviceMethod(method_name=method_name, payload=payload, response_timeout_in_seconds=30)

        print(f"\n-----------------------  Request: {method_name}  --------------------------------------------------\n")
        print(json.dumps(payload, indent=4))

        resp = self.registry_manager.invoke_device_module_method(self.device_id, self.module_id, module_method)
        print(f"\n---------------  Response: {method_name} - Status: {resp.status}  ---------------\n")

        if resp.payload is not None:
            print(json.dumps(resp.payload, indent=4))

    def pipeline_topology_set(self, op_parameters):
        if op_parameters is None:
            raise Exception('Operation parameters missing')

        if op_parameters.get('pipelineTopologyUrl') is not None:
            topology_json = read_url(op_parameters['pipelineTopologyUrl'])

        elif op_parameters.get('pipelineTopologyFile') is not None:
            topology_path = pathlib.Path(__file__).parent.joinpath(op_parameters['pipelineTopologyFile'])
            topology_json = topology_path.read_text()

        else:
            raise Exception('Neither pipelineTopologyUrl nor pipelineTopologyFile is specified')

        topology = json.loads(topology_json)
        self.invoke_module_method('pipelineTopologySet', topology)


if __name__ == '__main__':
    manager = LivePipelineManager()

    operations_data = json.loads(pathlib.Path('settings/operations_demo_2.json').read_text())

    for operation in operations_data['operations']:
        manager.invoke(operation['opName'], operation['opParams'])
