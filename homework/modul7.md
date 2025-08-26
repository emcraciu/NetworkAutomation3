# Using map/filter
1) Extend the functionality for class in homework 6 with 2 methods 
    - method1 "reduce_config" will use filter and change the configuration file to remove the extra "!"
    - method2 "rename_interfaces" will use map and allow the changing of the interface names in the configuration file  
      - example  GigabitEthernet0/0 > Ethernet1/1, GigabitEthernet0/1 > Ethernet1/2 ...
      - use generator to produce the incremental interface names 