#Exercise 1
print("#### Exercise 1 ########")

def collect():
    result={}
    while True:
        switch_name=input('Enter your switch name or press q to quit: ')
        if switch_name=='q':
            break
        if switch_name not in result:
            result[switch_name]={}
        else:
            print(f'{switch_name} already exists!')

        while True:
            switch_port=input('Enter your switch port or press q to quit: ')
            if switch_port=='q':
                break
            if switch_port in result[switch_name]:
                print(f"Port {switch_port} already exists!")
                continue
            vlans=[]
            while True:
                switch_vlans = input('Add more vlans or press q or press q to quit:')
                if switch_vlans=='q':
                    break
                else:
                    vlans.append(switch_vlans)
                result[switch_name][switch_port]={"vlans": sorted(set(vlans))}
    print("result = {")
    for sw in result:
        print(f"   '{sw}': {{")
        for port in result[sw]:
            print(f"      '{port}':{result[sw][port]},")
        print("}")
    print("}")
collect()
