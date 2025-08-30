# Loading initial configuration form file 

## Initial router configuration needs to be loaded from a file like the one we have saved.

- create configuration manually on IOU and IOSv that will include:
  - interface IP address 
  - creating user and password 
  - set hostname 
  - allow ssh access 
  - enable password (optional)
  - enable restconf (optinal)
 
- save the configuration of the IOU and IOSv to a file 
- modify some changes or revert the device to factory settings (optional create method to rest to factory and call it)
- get current configuration of the device and compare it to the saved configuration 
- extract the configuration blocks that need to be modified 
- execute only the required lines to bring the device back to the configuration done manually 