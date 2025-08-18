import json
import yaml

def provide_information():
    type=input("Switch or Router:")
    name=input("Please enter your device name : ")
    nr_ports= int(input("Please enter your number of device ports : "))
    port=[]
    for i in range(nr_ports):
        ports= input("Please enter your device port : ")
        port.append(ports)

    speed=input("Please enter your device speed : ")
    nr_ips = int(input("Please enter your number of ip : "))
    ips=[]
    for i in range(nr_ips):
        ip= input("Please enter your device ip : ")
        ips.append(ip)

    details = {
        'type': type,
        'name': name,
        'speed': speed,
        'ports': port,
        'ips': ips
    }


    #JSON
    print("Device(JSON):")
    print(json.dumps(details, indent=4))
    #Yamal
    with open("device_info.yaml", "w") as f:
        yaml.safe_dump(details,f,indent=2,sort_keys=False)

if __name__ == "__main__":
    provide_information()
