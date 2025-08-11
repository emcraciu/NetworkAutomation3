def collect_info(input_func=input):
    result = {}


    while True:
        sw = input_func("Switch (q=stop): ").strip()
        if sw.lower() == 'q':
            break
        if not sw:
            continue

        if sw in result:
            print(f"Switch '{sw}' already exists: ports/VLANs will merge")
        else:
            result[sw] = {}


        while True:
            port = input_func(f"Port for {sw} (q=finish {sw}): ").strip()
            if port.lower() == 'q':
                break
            if not port:
                continue

            if port in result[sw]:
                print(f"Port '{port}' on '{sw}' exists: VLANs will merge")
                vlans = set(result[sw][port]['vlans'])
            else:
                vlans = set()


            while True:
                line = input_func(f"VLANs for {sw} {port} as '100,200' (q=stop VLANs): ").strip()
                if line.lower() == 'q':
                    break
                for p in line.split(','):
                    p = p.strip()
                    if p.isdigit():
                        vlans.add(int(p))
                print(f"Current VLANs: {sorted(vlans)}")

                more = input_func("Add more VLANs? (Enter=yes, q=no): ").strip().lower()
                if more == 'q':
                    break


            result[sw][port] = {'vlans': sorted(vlans)}

            more_ports = input_func(f"Another port for {sw}? (Enter=yes, q=no): ").strip().lower()
            if more_ports == 'q':
                break


        more_switches = input_func("Another switch? (Enter=yes, q=no): ").strip().lower()
        if more_switches == 'q':
            break

    return result


if __name__ == "__main__":
    data = collect_info()
    print("\nResult:")
    print(data)
