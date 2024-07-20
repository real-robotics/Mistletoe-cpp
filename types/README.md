# Naming conventions for LCM channels  

Since we have multiple channels that would be named the same, (ie. sending state from the control to compute vs. sending state from compute to dashboard), to avoid confusion, duplicate channels have the format:  

`CHANNELNAME_X2X`  

where CHANNELNAME is the channel name, and X would be either C or D, denoting Control/Compute or Dashboard, and the order is publisher, listener.  

Ex. `STATE_C2D` would denote the channel that sends the state from compute module (publisher) to dashboard (listener).