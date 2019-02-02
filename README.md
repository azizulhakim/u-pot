# u-pot
Honeypot framework for UPnP Device.
Create a emulated device from the UPnP device description file of an UPnP device. The framework itself does not create the emulated device. It generates a **C** code that can be compiled against **[gupnp](https://github.com/GNOME/gupnp)** library to create an executable. The executable works as the emulated device. 

# Related Paper Published on [IPCCC' 2018](http://ipccc.org/)
https://arxiv.org/pdf/1812.05558.pdf



**How to run:**
 `python main.py <ip> <port> <description_file_name>`
