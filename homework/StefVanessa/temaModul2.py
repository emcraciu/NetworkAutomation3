from pprint import pprint

def collect_vlan_info():
    data = {}

    while True:
        sw = input("Switch (or q): ").strip()
        if sw.lower() == 'q':
            break
        if sw not in data:
            data[sw] = {}

        while True:
            port = input(f"  Port on {sw} (or q): ").strip()
            if port.lower() == 'q':
                break


            current = set(data[sw].get(port, {}).get('vlans', []))

            while True:
                txt = input(f"    VLANs for {sw} {port} (e.g. 10,20) or q: ").strip()
                if txt.lower() == 'q':
                    break
                try:
                    nums = {int(x.strip()) for x in txt.split(',') if x.strip()}
                except ValueError:
                    print("    Please enter only integers separated by commas.")
                    continue
                current |= nums

            data[sw][port] = {'vlans': sorted(current)}  # salvez ca si lista sortata

    return data


if __name__ == "__main__":
    result = collect_vlan_info()
    print("\nFinal result:")
    pprint(result)
