# context
1) Create a class for parsing configuration of switch/router
 - class will support __enter__ and __exit__ methods for loading and closing configuration file 
 - method get_config_block will return the configuration block that starts with the given words 
   - example: in the config block below the argument for the method will be "interface Ethernet0/3"
                and the return value would be "no ip address\nshutdown"
 ```text
interface Ethernet0/3
 no ip address
 shutdown
```