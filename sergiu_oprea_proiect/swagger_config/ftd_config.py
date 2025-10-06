import logging

from pyats import aetest, topology

from lib.connectors.swagger_con import SwaggerConnector
from sergiu_oprea_proiect.path_helper import resource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ConnectFTDREST(aetest.Testcase):
    @aetest.setup
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            testbed_path = str(resource("testbeds/ftd_swagger_testbed.yaml"))
            self.tb = topology.loader.load(testbed_path)
            log.info("Successfully loaded testbed")
            self.parent.parameters.update(tb=self.tb)

    @aetest.test
    def connect_via_rest(self, steps):
        with steps.start("Connect via rest"):
            for device in self.tb.devices:
                if self.tb.devices[device].type != 'ftd':
                    continue
                if "swagger" not in self.tb.devices[device].connections:
                    continue
                connection: SwaggerConnector = self.tb.devices[device].connect()
                log.info(f"Successfully connected via rest {connection}")
                swagger = connection.get_swagger_client()
                if not swagger:
                    self.failed('No swagger connection')
                log.info(swagger)

        with steps.start("Delete existing DHCP server"):
                dhcp_servers = swagger.DHCPServerContainer.getDHCPServerContainerList().result()
                for dhcp_server in dhcp_servers['items']:
                    dhcp_serv_list = dhcp_server['servers']
                    print(dhcp_serv_list)
                    dhcp_server.servers = []
                    response = swagger.DHCPServerContainer.editDHCPServerContainer(
                        objId=dhcp_server.id,
                        body=dhcp_server,
                    ).result()
                    print(response)

        with steps.start('Delete FTD Interface Configuration'):
            existing_interfaces = swagger.Interface.getPhysicalInterfaceList().result()
            ftd_pc2 = connection.device.interfaces['ftd_pc2']
            for interface in existing_interfaces['items']:
                if interface.hardwareName == ftd_pc2.name:
                    interface.ipv4.ipAddress = None
                    interface.ipv4.ipType = 'DHCP'
                    interface.ipv4.dhcp = True
                    response = swagger.Interface.editPhysicalInterface(
                        objId=interface.id,
                        body=interface,
                    ).result()
                    print(response)

        with steps.start('Configure FTD Interfaces'):
            existing_interfaces = swagger.Interface.getPhysicalInterfaceList().result()
            csr_ftd = connection.device.interfaces['csr_ftd']
            ftd_pc2 = connection.device.interfaces['ftd_pc2']
            log.info(f'csr_ftd {ftd_pc2} and ftd_ep2 {ftd_pc2}')

            for interface in existing_interfaces['items']:
                if interface.hardwareName == csr_ftd.name:
                    if interface.ipv4.ipAddress is None:
                        ipaddress_model = swagger.get_model('IPv4Address')
                        interface.ipv4.ipAddress = ipaddress_model(
                            ipAddress=csr_ftd.ipv4.ip.compressed,
                            netmask=csr_ftd.ipv4.netmask.exploded
                        )
                    else:
                        interface.ipv4.ipAddress.ipAddress = csr_ftd.ipv4.ip.compressed
                        interface.ipv4.ipAddress.netmask = csr_ftd.ipv4.netmask.exploded
                    interface.ipv4.dhcp = False
                    interface.ipv4.ipType = 'STATIC'
                    interface.enable = True
                    interface.name = csr_ftd.alias
                    response = swagger.Interface.editPhysicalInterface(
                        objId=interface.id,
                        body=interface,
                    ).result()
                    print(response)
                if interface.hardwareName == ftd_pc2.name:
                    if interface.ipv4.ipAddress is None:
                        ipaddress_model = swagger.get_model('IPv4Address')
                        interface.ipv4.ipAddress = ipaddress_model(
                            ipAddress=ftd_pc2.ipv4.ip.compressed,
                            netmask=ftd_pc2.ipv4.netmask.exploded
                        )
                    else:
                        interface.ipv4.ipAddress.ipAddress = ftd_pc2.ipv4.ip.compressed
                        interface.ipv4.ipAddress.netmask = ftd_pc2.ipv4.netmask.exploded
                    interface.ipv4.dhcp = False
                    interface.ipv4.ipType = 'STATIC'
                    interface.enable = True
                    interface.name = ftd_pc2.alias
                    response = swagger.Interface.editPhysicalInterface(
                        objId=interface.id,
                        body=interface,
                    ).result()
                    interface_for_dhcp = interface
                    print(response)

        with steps.start("Delete routes"):
            virtual_routers = swagger.Routing.getVirtualRouterList().result()
            vr_id = virtual_routers['items'][0]['id']

            existing_routes = swagger.Routing.getStaticRouteEntryList(parentId=vr_id).result()
            routes_to_delete = ['route_to_192_168_210']

            for route in existing_routes.items:
                if route.name in routes_to_delete:
                    print(f"Deleting route: {route.name} (ID: {route.id})")
                    delete_response = swagger.Routing.deleteStaticRouteEntry(
                        parentId=vr_id,
                        objId=route.id
                    ).result()
                    print(f"Route deleted: {route.name}")
                    log.info(f"Deleted route: {route.name}")

        with steps.start("Add route"):
            virtual_routers = swagger.Routing.getVirtualRouterList().result()
            log.info(f"Virtual routers: {virtual_routers}")

            vr_id = virtual_routers['items'][0]['id']

            existing_routes = swagger.Routing.getStaticRouteEntryList(parentId=vr_id).result()
            log.info(f"Existing routes: {existing_routes}")

            csr_ftd_interface = None
            for iface in virtual_routers.items[0].interfaces:
                if iface.name == 'csr_ftd':
                    csr_ftd_interface = iface
                    break

            route_model = swagger.get_model('StaticRouteEntry')
            network_model = swagger.get_model('NetworkObject')
            reference_model = swagger.get_model('ReferenceModel')

            destination_network = network_model(
                name='NETTY_192_168_192_0',
                subType='NETWORK',
                value='192.168.192.0/18',
                type='networkobject'
            )
            dest_net_response = swagger.NetworkObject.addNetworkObject(body=destination_network).result()
            print(f"Destination network created: {dest_net_response}")

            gateway_network = network_model(
                name='GW_192_168_240_10',
                subType='HOST',
                value='192.168.240.10',
                type='networkobject'
            )
            gateway_response = swagger.NetworkObject.addNetworkObject(body=gateway_network).result()
            print(f"Gateway network created: {gateway_response}")

            new_route = route_model(
                name='route_to_192_168_192',
                iface=reference_model(
                    id=csr_ftd_interface.id,
                    name=csr_ftd_interface.name,
                    type='physicalinterface'
                ),
                networks=[reference_model(
                    id=dest_net_response.id,
                    name=dest_net_response.name,
                    type='networkobject'
                )],
                gateway=reference_model(
                    id=gateway_response.id,
                    name=gateway_response.name,
                    type='networkobject'
                ),
                metricValue=1,
                ipType='IPv4',
                type='staticrouteentry'
            )

            response = swagger.Routing.addStaticRouteEntry(parentId=vr_id, body=new_route).result()
            log.info(f"Route added: {response}")
            print(f"Route added successfully: {response}")


if __name__ == '__main__':
    aetest.main()
