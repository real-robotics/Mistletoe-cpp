# Network Configuration Guide

## 1. Set Up a Wi-Fi Hotspot

1. **Create the SSID for the hotspot on `wlan0`:**

    ```bash
    sudo nmcli connection add type wifi ifname wlan0 con-name testhotspot autoconnect yes ssid testhotspot
    ```

2. **Configure hotspot properties:**

    ```bash
    sudo nmcli connection modify testhotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
    ```

3. **Set up WPA2-PSK security:**

    Replace `your_password` with your desired password:

    ```bash
    sudo nmcli connection modify testhotspot wifi-sec.key-mgmt wpa-psk
    sudo nmcli connection modify testhotspot wifi-sec.psk your_password
    ```

4. **Activate the hotspot:**

    ```bash
    sudo nmcli connection up testhotspot
    ```

5. **Ensure the hotspot auto-connects on boot:**

    ```bash
    sudo nmcli connection modify testhotspot connection.autoconnect yes
    ```

6. **Deactivate the hotspot when needed:**

    ```bash
    sudo nmcli connection down testhotspot
    ```

7. **View active connections:**

    ```bash
    nmcli con show --active
    ```

## 2. Configure Static IP Address

1. **Check if you have a connection profile for `eth0`:**

    List existing connections:

    ```bash
    nmcli con show
    ```

    If `eth0` is not listed, create a new connection profile for `eth0`:

    ```bash
    sudo nmcli connection add type ethernet ifname eth0 con-name eth0
    ```

2. **Set a static IPv4 address (e.g., 192.168.1.10) on `eth0`:**

    ```bash
    sudo nmcli connection modify eth0 ipv4.addresses 192.168.1.10/24
    sudo nmcli connection modify eth0 ipv4.method manual
    ```

3. **Ensure `eth0` auto-connects on boot:**

    ```bash
    sudo nmcli connection modify eth0 connection.autoconnect yes
    sudo nmcli connection up eth0
    ```

## 3. Add Static IP Routes and Execute Python Script

1. **Add routes for multicast traffic and execute the Python script in `/etc/network/if-up.d/` directory:**

    Create or edit a script in `/etc/network/if-up.d/` (e.g., `manage-routes-and-script`):

    ```bash
    sudo nano /etc/network/if-up.d/manage-routes-and-script
    ```

    Add the following content:

    ```bash
    #!/bin/sh
    
    # Add routes
    route add -net 239.255.76.0 netmask 255.255.255.0 dev wlan0
    route add -net 239.255.77.0 netmask 255.255.255.0 dev eth0
    
    # Execute the Python script
    /usr/bin/python3 /path/to/compute/main.py
    ```

    Make the script executable:

    ```bash
    sudo chmod +x /etc/network/if-up.d/manage-routes-and-script
    ```

---

**Note:** Replace `your_password` with a custom password for the hotspot and `/path/to/compute/main.py` with the actual path to the `main.py` file. Ensure the script paths and IP addresses are correct for your system. (Although the IP addresses should work fine with the ones given.) This setup makes sure that the LCM traffic is routed correctly, and LCM doesn't work without it. 
