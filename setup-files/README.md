# Files used for setup  

These files are used for setup.  

## Services Directory
In the `services` directory you can find files to configure the services that are used to run the compute/control modules.  
They should be placed in /etc/systemd/system/ and the paths to the compute/control module scripts/compiled binaries should be changed accordingly.  
After placing them there, run:  
```
sudo systemctl daemon-reload
sudo systemctl enable mistletoe-compute.service
sudo systemctl start mistletoe-compute.service
```  
You can do the same for the control service, but just replace the name with control instead of compute.  

## Network Configs Directory
Here you can find files that are used to configure the routing. The `manage-routes` file should be placed in the `/etc/network/if-up.d/` directory. This allows the multicast routes to be configured when the network interfaces are up. Check the orangepi-setup.md in `compute` for more details on this setup.
