def colectare():

    result = {}

    while True:
        sw = input("Introdu numele unui switch sau apasă Q pentru ieșire: ").strip()
        if sw.lower() == 'q':
            break
        if sw in result:
            print("Acest switch este deja introdus, introdu altul.")
            continue
        result[sw] = {}

        while True:
            port = input(f"Introdu un port pentru {sw} sau apasă Q pentru ieșire: ").strip()
            if port.lower() == 'q':
                break
            if port in result[sw]:
                print("Acest port a fost deja introdus, introdu altul.")
                continue
            vlan_set = set()
            first = input(f"Introdu VLAN-urile pentru {sw} {port} (de exemplu 100,200 ...): ").strip()
            if first:
                for p in (x.strip() for x in first.split(',') if x.strip()):
                    if p.isdigit():
                        vlan_set.add(int(p))

            while True:
                more = input("Adaugă un alt VLAN pentru acest port sau apasă Q pentru ieșire: ").strip()
                if more.lower() == 'q':
                    break
                for p in (x.strip() for x in more.split(',') if x.strip()):
                    if p.isdigit():
                        vlan_set.add(int(p))
            result[sw][port] = {'vlans': sorted(vlan_set)}
    return result

switch_data = colectare()

print("\nRezultat:")
print(switch_data)