# Reading user input for switch config

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
 - make sure that vlans do not repeat for port - hint: set()
 - check if user provides same port name a second time
 - check if user provides same switch name a second time  


## Exercise 2 - read module3 first

Create function that will take as input a cart of items and shops where the products can be purchased. 
Function will return a dict with shop name where the specified cart items and quantities 
fave the smallest total cost and the total cost in that shop

```python
cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

```
#### Info: 
 - in the cart the value represents the number or units of that item
 - in shop_X the value represents the cost per unit of a specific item

### Considerations:
 - cart can have items that are not in some shops and in this case shop needs to be excluded
 - shops can have large number of items compared to the cart so optimise your for loops
