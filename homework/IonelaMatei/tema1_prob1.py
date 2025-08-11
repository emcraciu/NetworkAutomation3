'''# Reading user input for switch config

## Exercise 1 - read module3 first

Create and call python function that will collect vlan information
for each port of a switch and return a dictionary as in the example below:
```python
result = {
    'SW1': {
        'Ethernet1/1': {'vlans': [100, 200, 300]},
        'Ethernet1/2': {'vlans': [100, 500, 20]},
    },
    'SW2': {
        'Ethernet1/1': {'vlans': [10, 20, 30]},
        'Ethernet1/4': {'vlans': [11, 12, 13]},
    }
}
```

### Steps:
 - ask user for switch name
 - ask user for switch port
 - ask user for vlans corresponding to above port
   - user will provide vlans as "100,200,300"
   - user will be asked to add more vlans or press q
 - if no more vlans are provided user will be asked to provide additional port or press 'q'
 - if no more ports are provided user will be asked ro provide additional switch or press 'q'

### Checks:
 - make sure that vlans do not repeat for port - hint: set() -> pe acelasi port vlan-urile sa nu se repete
 - check if user provides same port name a second time
 - check if user provides same switch name a second time
'''

def adauga_vlan(port):
    while True:
        vlan_input = input("Introduceti consecutiv vlan-urile separate prin ',' sau q pentru a iesi: ")
        if vlan_input.lower() != 'q':
            vlan_list = vlan_input.split(',')
            for input_str in vlan_list:
                if input_str.isdigit():
                    vlan_number = int(input_str)
                    port['vlans'].append(vlan_number)
                else:
                    print("Valoarea din sir nu este un numar asa ca nu se adauga la lista! ")
            port['vlans'] = list(set(port['vlans']))
            while True:
                continuare_adaugare = input("Doriti sa adaugati si alte vlan-uri? (da/nu): ").lower()
                if continuare_adaugare not in ['da', 'nu']:
                    print("Trebuie sa introduceti da sau nu!")
                else:
                    break

            if continuare_adaugare == 'nu':
                break
        else:
            print("Adaugarea de vlan-uri s-a terminat ! ")
            break


def adauga_porturi(switch, result):
    while True:
        porturi_input = input("Introduceti numele portului sau q pentru a iesi: ")
        if porturi_input.lower() != 'q':
            if porturi_input in result[switch]:
                print("Portul a fost deja adaugat ! ")

            else:
                result[switch][porturi_input] = {'vlans': []}
                adauga_vlan(result[switch][porturi_input])
                while True:
                    continuare_adaugare = input("Doriti sa adaugati si alte porturi ? (da/nu): ").lower()
                    if continuare_adaugare not in ['da', 'nu']:
                        print("Trebuie sa introduceti da sau nu!")
                    else:
                        break

                if continuare_adaugare == 'nu':
                    break

        else:
            print("Adaugarea de porturi s-a terminat! ")
            break


def adauga_switch():
    result = {}
    while True:
        switch_input = input("Introduceti numele switch-ului sau q pentru a iesi : ").upper()
        if switch_input not in result and switch_input.lower() != 'q':
            result[switch_input] = {}
            adauga_porturi(switch_input, result)
            while True:
                continuare_adaugare = input("Doriti sa adaugati si alte switch-uri? (da/nu): ").lower()
                if continuare_adaugare not in ['da', 'nu']:
                    print("Trebuie sa introduceti da sau nu!")
                else:
                    break

            if continuare_adaugare == 'nu':
                break

        else:
            if switch_input.lower() == 'q':
                print("Programul s-a terminat! ")
                break
            elif switch_input in result:
                print("Switch-ul a fost deja introdus")
            else:
                print("Nu ati introdus un input corect! ")

    for switch, ports in result.items():
        print(f"{switch}:")
        for port, data in ports.items():
            print(f"  {port}: {data}")


adauga_switch()




