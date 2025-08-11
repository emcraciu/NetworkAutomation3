from pprint import pformat

def _parse_vlans(s: str) -> list[int]:
    vl = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            raise ValueError(f"Invalid VLAN: {part}")
        v = int(part)
        if v < 1 or v > 4094:
            raise ValueError(f"VLAN out of range (1-4094): {v}")
        vl.append(v)
    # non-dupe with order
    seen, out = set(), []
    for v in vl:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

def collect_switch_config() -> dict:
    result: dict[str, dict] = {}

    while True:
        sw = input("Switch name (q to stop): ").strip()
        if sw.lower() == "q":
            break
        if not sw:
            print("Empty switch name. Try again.")
            continue

        if sw not in result:
            result[sw] = {}
        else:
            print(f"[info] Working on existing switch: {sw}")

        # Ports loop for this switch
        while True:
            port = input(f"Port for {sw} (q to finish this switch): ").strip()
            if port.lower() == "q":
                # finish current switch, go back to switch selection
                break
            if not port:
                print("Empty port name. Try again.")
                continue

            # Warn on duplicate port
            if port in result[sw]:
                ans = input(f"[warning] {sw}/{port} already exists. Overwrite VLANs? (y/n): ").strip().lower()
                if ans != "y":
                    print("Not overwriting. Choose another port.")
                    continue

            # VLANs collection for this port
            vlans: list[int] = []
            while True:
                raw = input(f"VLANs for {sw}/{port} (e.g. 100,200,300 or q to stop): ").strip()
                if raw.lower() == "q":
                    # stop VLAN entry for this port
                    break
                try:
                    vlans.extend(_parse_vlans(raw))
                except ValueError as e:
                    print(e)
                    continue

                more = input("Add more VLANs? (q to stop, anything else to continue): ").strip().lower()
                if more == "q":
                    break

            # non-duplicate
            seen, ordered = set(), []
            for v in vlans:
                if v not in seen:
                    seen.add(v)
                    ordered.append(v)

            result[sw][port] = {"vlans": ordered}
            print(f"[ok] Set {sw}/{port} -> {ordered}")

    return result

if __name__ == "__main__":
    cfg = collect_switch_config()
    print("result = " + pformat(cfg, sort_dicts=False, width=80))

