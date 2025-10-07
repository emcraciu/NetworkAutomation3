import ipaddress
import re
import time
import requests
from pathlib import Path
from pyats import topology

requests.packages.urllib3.disable_warnings()

from lib.connectors.swagger_connection import SwaggerConnection


def configure_ospf(self, vrf_id, name, process_id, area_id, if_to_cidr, deploy=True, deploy_timeout=1200):
    """
    Creează/actualizează procesul OSPF în VRF-ul dat și configurează areaNetworks
    pentru fiecare pereche (interfață, rețea) din if_to_cidr.

    self.client  -> SwaggerClient (bravado) deja autentificat (ex: ftd.client = swagger_client)
    vrf_id       -> ex. "default"
    name         -> numele procesului OSPF (string)
    process_id   -> ex. 1
    area_id      -> 0 / "0" / "0.0.0.0" (orice -> normalizat la "0")
    if_to_cidr   -> listă de tuple [(if_key, "X.Y.Z.W/len"), ...]
                    'if_key' poate fi numele logic FDM (ex. 'inside') sau hardwareName (ex. 'GigabitEthernet0/1')
    deploy       -> dacă True, rulează /operational/deploy când există pending changes
    """

    Ref = self.ssh.get_model("ReferenceModel")

    def _fmt_area(a):
        return "0" if str(a) in ("0", "0.0.0.0") else str(a)

    def _items(obj):
        if obj is None:
            return []
        it = getattr(obj, "items", None)
        if it is not None:
            return it or []
        if isinstance(obj, dict):
            return obj.get("items", []) or []
        return []

    def ensure_netobj(cidr: str):
        net = ipaddress.ip_network(cidr, strict=False)
        netname = f"NET_{net.network_address}_{net.prefixlen}"
        existing = self.ssh.NetworkObject.getNetworkObjectList(filter=f"name:{netname}").result()
        ex_items = _items(existing)
        if ex_items:
            return ex_items[0]
        body = {
            "type": "networkobject",
            "name": netname,
            "subType": "NETWORK",
            "value": f"{net.network_address}/{net.prefixlen}",
        }
        return self.ssh.NetworkObject.addNetworkObject(body=body).result()

    def _find_interface(if_list_items, key: str):
        for itf in if_list_items:
            if getattr(itf, "name", None) == key:
                return itf
        for itf in if_list_items:
            if getattr(itf, "hardwareName", None) == key:
                return itf
        return None

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

    def _deploy_if_needed(swagger):
        base_root = _discover_base_url_from_swagger(swagger)
        if not base_root:
            raise RuntimeError("Cannot determine FDM base URL for deploy.")
        headers = _discover_headers_from_swagger(swagger)

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
            st = s.get(f"{base_url}/operational/deploy/{job_id}", timeout=30,
                       headers={"Connection": "close"})
            st.raise_for_status()
            js = st.json()
            state = (js.get("state") or "").upper()
            msg = js.get("message") or ""
            print(f"[deploy] state={state} msg={msg}")
            if state in ("DEPLOYED", "SUCCESS"):
                return {"state": state, "job": js}
            if state in ("FAILED", "CANCELLED", "ERROR"):
                raise RuntimeError(f"Deploy failed: state={state}, message={msg}")
            if time.time() - start > deploy_timeout:
                raise TimeoutError("Timed out waiting for OSPF deploy to finish.")
            time.sleep(5)


    if_list = self.ssh.Interface.getPhysicalInterfaceList().result()
    if_items = _items(if_list)
    if not if_items:
        raise RuntimeError("Received no interfaces from FDM (Interface.getPhysicalInterfaceList).")

    area_networks = []
    for if_key, cidr in if_to_cidr:
        itf = _find_interface(if_items, if_key)
        if not itf:
            raise RuntimeError(f"Interface '{if_key}' does not exist on FTD (searched by 'name' and 'hardwareName').")
        netobj = ensure_netobj(cidr)
        area_networks.append({
            "type": "areanetwork",
            "ipv4Network": Ref(id=netobj.id, name=netobj.name, type="networkobject"),
            "tagInterface": Ref(
                id=itf.id, name=getattr(itf, "name", None), type="physicalinterface",
                hardwareName=getattr(itf, "hardwareName", None)
            ),
        })

    area_id_str = "0" if str(area_id) in ("0", "0.0.0.0") else str(area_id)

    body_base = {
        "type": "ospf",
        "name": name,
        "processId": str(process_id),
        "neighbors": [],
        "summaryAddresses": [],
        "redistributeProtocols": [],
        "filterRules": [],
        "logAdjacencyChanges": {"type": "logadjacencychanges", "logType": "DETAILED"},
        "processConfiguration": {
            "type": "processconfiguration",
            "administrativeDistance": {
                "type": "administrativedistance",
                "intraArea": 110, "interArea": 110, "external": 110
            },
            "timers": {
                "type": "timers",
                "floodPacing": 33,
                "lsaArrival": 1000,
                "lsaGroup": 240,
                "retransmission": 66,
                "lsaThrottleTimer": {
                    "type": "lsathrottletimer",
                    "initialDelay": 0, "minimumDelay": 5000, "maximumDelay": 5000
                },
                "spfThrottleTimer": {
                    "type": "spfthrottletimer",
                    "initialDelay": 5000, "minimumHoldTime": 10000, "maximumWaitTime": 10000
                }
            }
        }
    }

    area_obj = {
        "type": "area",
        "areaId": area_id_str,
        "areaNetworks": area_networks,
        "virtualLinks": [],
        "areaRanges": [],
        "filterList": [],
    }

    try:
        existing = self.ssh.OSPF.getOSPFList(vrfId=vrf_id).result()
        ospf_items = _items(existing)
    except Exception:
        ospf_items = []

    if ospf_items:
        ospf = ospf_items[0]
        areas = list(getattr(ospf, "areas", []) or [])
        idx = next((i for i, a in enumerate(areas)
                    if str(getattr(a, "areaId", "")) == area_id_str), None)
        if idx is None:
            areas.append(area_obj)
        else:
            old = areas[idx]
            old.areaNetworks = area_networks
            old.areaId = area_id_str
            areas[idx] = old
        ospf.areas = areas or [area_obj]
        ospf.name = name
        ospf.processId = str(process_id)
        result = self.ssh.OSPF.editOSPF(vrfId=vrf_id, objId=ospf.id, body=ospf).result()
    else:
        body = dict(body_base)
        body["areas"] = [area_obj]
        result = self.ssh.OSPF.addOSPF(vrfId=vrf_id, body=body).result()

    if deploy:
        _deploy_if_needed(self.ssh)

    return result

if __name__ == "__main__":
    tb_path = Path(__file__).resolve().parent / "testbed_ospf.yaml"
    tb = topology.loader.load(str(tb_path))

    ftd = tb.devices["FTD"]

    conn = SwaggerConnection(ftd).connect()
    client = conn.get_swagger_client()

    setattr(client, "_url",     getattr(client, "_url", conn._url))
    setattr(client, "_headers", getattr(client, "_headers", conn._headers))


    ftd.ssh = client

    res = configure_ospf(
        ftd,
        vrf_id="default",
        name="ospf_1",
        process_id=1,
        area_id=0,
        if_to_cidr=[
            ("outside", "192.168.240.0/24"),
            ("inside",  "192.168.250.0/24"),
        ],
        deploy=True,          # pornește deploy dacă sunt pending changes
        deploy_timeout=1200,  # 20 minute
    )

    print("OSPF configuration on FTD completed:", res)
