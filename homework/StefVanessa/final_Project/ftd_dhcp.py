"""
This test will configure the FTD interfaces and deploy the changes
"""

import re
import time
import ipaddress
import requests
from pathlib import Path
from pyats import aetest, topology

requests.packages.urllib3.disable_warnings()

from lib.connectors.swagger_connection import SwaggerConnection


def _items(obj):
    """Return list of items from bravado model or dict; otherwise []."""
    if obj is None:
        return []
    it = getattr(obj, "items", None)
    if it is not None:
        return it or []
    if isinstance(obj, dict):
        return obj.get("items", []) or []
    return []


def _discover_base_url_from_swagger(swagger):
    base_root = getattr(swagger, "_url", None)
    if base_root:
        return base_root.rstrip("/")
    m = re.search(r"SwaggerClient\((https?://[^)]+)\)", str(swagger))
    if m:
        return m.group(1).rstrip("/")
    return None


def _discover_headers_from_swagger(swagger):
    hdrs = getattr(swagger, "_headers", None)
    if hdrs:
        return dict(hdrs)
    try:
        return dict(swagger.swagger_spec.http_client.session.headers)
    except Exception:
        return {}


def deploy_pending_changes(swagger, connection=None, timeout_sec=1200, poll_sec=5):
    """Trigger a deploy on FDM if there are pending changes and wait for completion."""
    base_root = _discover_base_url_from_swagger(swagger)
    headers = _discover_headers_from_swagger(swagger)

    if (not base_root or base_root == "") and connection is not None:
        base_root = getattr(connection, "_url", None)
    if (not headers or not headers.get("Authorization")) and connection is not None:
        conn_hdrs = getattr(connection, "_headers", None)
        if conn_hdrs:
            headers.update(conn_hdrs)

    if not base_root:
        raise RuntimeError("Cannot determine FDM base URL for deploy.")

    base_url = base_root.rstrip("/") + "/api/fdm/latest"

    s = requests.Session()
    s.verify = False
    if headers:
        s.headers.update(headers)

    r = s.get(f"{base_url}/operational/pendingchanges", timeout=30)
    r.raise_for_status()
    if not _items(r.json()):
        print("[deploy] No pending changes; deploy not required.")
        return {"state": "NO_CHANGES"}

    r = s.post(f"{base_url}/operational/deploy", timeout=30)
    r.raise_for_status()
    job_id = r.json().get("id")
    if not job_id:
        raise RuntimeError("Did not receive job_id from /operational/deploy")

    print(f"[deploy] Started job: {job_id}")

    start = time.time()
    while True:
        st = s.get(
            f"{base_url}/operational/deploy/{job_id}",
            timeout=30,
            headers={"Connection": "close"},
        )
        st.raise_for_status()
        js = st.json()
        state = (js.get("state") or "").upper()
        msg = js.get("message") or ""
        print(f"[deploy] state={state} msg={msg}")
        if state in ("DEPLOYED", "SUCCESS"):
            return {"state": state, "job": js}
        if state in ("FAILED", "CANCELLED", "ERROR"):
            raise RuntimeError(f"Deploy failed: state={state}, message={msg}")
        if time.time() - start > timeout_sec:
            raise TimeoutError("Timed out waiting for deploy to complete.")
        time.sleep(poll_sec)


def _get_ip_netmask(tb_intf):
    """
    Accepts either an ip/netmask structure or a CIDR string.
    Returns (ip_str, netmask_str).
    """
    ipv4 = getattr(tb_intf, "ipv4", None)
    # YAML as a CIDR string
    if isinstance(ipv4, str):
        net = ipaddress.ip_interface(ipv4)
        return str(net.ip), str(net.network.netmask)
    # pyATS object with fields
    ip_obj = getattr(ipv4, "ip", None)
    mask_obj = getattr(ipv4, "netmask", None)
    if hasattr(ip_obj, "compressed") and hasattr(mask_obj, "exploded"):
        return ip_obj.compressed, mask_obj.exploded
    # fallback – try to convert
    if ip_obj and mask_obj:
        return str(ip_obj), str(mask_obj)
    raise ValueError(f"Cannot extract ip/netmask from {tb_intf}")


def _match_fdmi(sw_ifaces, tb_intf):
    """
    Finds the FDM interface (from the swagger list) that corresponds to the testbed interface.
    Matches on hardwareName or name.
    """
    candidates = set()
    # Real name in testbed (e.g., 'GigabitEthernet0/1')
    if hasattr(tb_intf, "name") and tb_intf.name:
        candidates.add(tb_intf.name)
    # alias/link as fallback
    if getattr(tb_intf, "alias", None):
        candidates.add(tb_intf.alias)
    if getattr(tb_intf, "link", None):
        candidates.add(tb_intf.link)

    for iface in sw_ifaces:
        if getattr(iface, "hardwareName", None) in candidates:
            return iface
        if getattr(iface, "name", None) in candidates:
            return iface
    return None


class ConnectFTDREST(aetest.Testcase):
    """
    This test will configure the FTD interfaces
    """

    @aetest.test
    def load_testbed(self, steps):
        """Load testbed from a deterministic path."""
        with steps.start("Load testbed"):
            tb_path = Path(__file__).resolve().parent / "ftd_testbed.yaml"
            if not tb_path.exists():
                import os
                self.failed(f"Could not find testbed at: {tb_path}\nCWD: {os.getcwd()}")
            try:
                tb = topology.loader.load(str(tb_path))
            except Exception as e:
                self.failed(f"Error loading testbed: {e}")
            if tb is None:
                self.failed("Testbed returned None after load (invalid YAML?).")
            self.parent.parameters.update(tb=tb)

    @aetest.test
    def connect_via_rest(self, steps):  # pylint: disable=missing-function-docstring,too-many-locals
        tb = self.parent.parameters.get('tb')
        if tb is None:
            self.failed("Testbed is not loaded (tb=None). Check the previous step.")

        with steps.start("Connect via rest"):
            swagger = None
            connection = None
            for devname in tb.devices:
                dev = tb.devices[devname]
                # accept type firewall/ftd or os ftd
                if getattr(dev, "type", "") not in ("firewall", "ftd") and getattr(dev, "os", "") != "ftd":
                    continue
                if "swagger" not in dev.connections:
                    continue
                connection: SwaggerConnection = dev.connect(via='swagger')
                swagger = connection.get_swagger_client()
                if not swagger:
                    self.failed('No swagger connection')
                print(swagger)
                self.parent.parameters.update(swagger=swagger, connection=connection, device_obj=dev)
                break
            if swagger is None:
                self.failed("Did not find any device with a 'swagger' connection and FTD type/os.")

        with steps.start("Delete existing DHCP server"):
            swagger = self.parent.parameters['swagger']
            dhcp_servers = swagger.DHCPServerContainer.getDHCPServerContainerList().result()
            for dhcp_server in _items(dhcp_servers):
                dhcp_serv_list = getattr(dhcp_server, "servers", []) or []
                print(dhcp_serv_list)
                # clear the list – disables existing DHCP
                dhcp_server.servers = []
                response = swagger.DHCPServerContainer.editDHCPServerContainer(
                    objId=dhcp_server.id,
                    body=dhcp_server,
                ).result()
                print(response)

        with steps.start('Configure FTD Interfaces'):
            swagger = self.parent.parameters['swagger']
            connection = self.parent.parameters['connection']

            existing_interfaces = swagger.Interface.getPhysicalInterfaceList().result()
            existing = _items(existing_interfaces)

            csr_ftd_tb = connection.device.interfaces['csr_ftd']
            ftd_ep2_tb = connection.device.interfaces['ftd_ep2']

            csr_fdmi = _match_fdmi(existing, csr_ftd_tb)
            ftd_ep2_fdmi = _match_fdmi(existing, ftd_ep2_tb)

            if not csr_fdmi:
                self.failed(
                    "Could not find in FDM the interface for 'csr_ftd'. "
                    f"Searched by name/alias/link: "
                    f"{getattr(csr_ftd_tb,'name',None)}, {getattr(csr_ftd_tb,'alias',None)}, {getattr(csr_ftd_tb,'link',None)}"
                )

            if not ftd_ep2_fdmi:
                self.failed(
                    "Could not find in FDM the interface for 'ftd_ep2'. "
                    f"Searched by name/alias/link: "
                    f"{getattr(ftd_ep2_tb,'name',None)}, {getattr(ftd_ep2_tb,'alias',None)}, {getattr(ftd_ep2_tb,'link',None)}"
                )

            # configure csr_ftd
            ip_str, mask_str = _get_ip_netmask(csr_ftd_tb)
            csr_fdmi.ipv4.ipAddress.ipAddress = ip_str
            csr_fdmi.ipv4.ipAddress.netmask   = mask_str
            csr_fdmi.ipv4.dhcp = False
            csr_fdmi.ipv4.ipType = 'STATIC'
            csr_fdmi.enable = True
            # Do not rename the logical interface (keep 'outside'/'inside' if present)
            resp = swagger.Interface.editPhysicalInterface(objId=csr_fdmi.id, body=csr_fdmi).result()
            print(resp)

            # configure ftd_ep2
            ip_str, mask_str = _get_ip_netmask(ftd_ep2_tb)
            ftd_ep2_fdmi.ipv4.ipAddress.ipAddress = ip_str
            ftd_ep2_fdmi.ipv4.ipAddress.netmask   = mask_str
            ftd_ep2_fdmi.ipv4.dhcp = False
            ftd_ep2_fdmi.ipv4.ipType = 'STATIC'
            ftd_ep2_fdmi.enable = True
            resp = swagger.Interface.editPhysicalInterface(objId=ftd_ep2_fdmi.id, body=ftd_ep2_fdmi).result()
            print(resp)

            # For the DHCP step, set the correct existing FDM interface
            self.parent.parameters.update(interface_for_dhcp=ftd_ep2_fdmi)

        with steps.start("Add DHCP server to interface"):
            swagger = self.parent.parameters['swagger']
            interface_for_dhcp = self.parent.parameters.get('interface_for_dhcp')
            if interface_for_dhcp is None:
                # helpful diagnostics
                existing_interfaces = swagger.Interface.getPhysicalInterfaceList().result()
                existing = _items(existing_interfaces)
                names = [(getattr(i, "hardwareName", None), getattr(i, "name", None)) for i in existing]
                self.failed(f"interface_for_dhcp is None. FDM interfaces: {names}")

            dhcp_servers = swagger.DHCPServerContainer.getDHCPServerContainerList().result()
            if not _items(dhcp_servers):
                self.failed("No DHCPServerContainer exists on FDM – check FDM state or initialization.")

            for dhcp_server in _items(dhcp_servers):
                dhcp_server_model = swagger.get_model('DHCPServer')
                interface_ref_model = swagger.get_model('ReferenceModel')

                # NOTE: keep the existing logical name in FDM (e.g., 'inside'), if present
                iface_name = getattr(interface_for_dhcp, "name", None) or getattr(interface_for_dhcp, "hardwareName", None)

                dhcp_server.servers = [
                    dhcp_server_model(
                        addressPool='192.168.250.50-192.168.250.100',
                        enableDHCP=True,
                        interface=interface_ref_model(
                            id=interface_for_dhcp.id,
                            name=iface_name,
                            type='physicalinterface'
                        ),
                        type='dhcpserver'
                    )
                ]
                response = swagger.DHCPServerContainer.editDHCPServerContainer(
                    objId=dhcp_server.id,
                    body=dhcp_server,
                ).result()
                print(response)

        with steps.start("Deploy pending changes"):
            swagger = self.parent.parameters['swagger']
            connection = self.parent.parameters['connection']
            result = deploy_pending_changes(swagger, connection=connection)
            print("Deploy result:", result)


if __name__ == '__main__':
    aetest.main()
