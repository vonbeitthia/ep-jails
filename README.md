# ep-jails
Script to create epair interfaces for my FreeBSD jails

## Installation

The _install_ file assumes scripts are to be installed in _/usr/local/scripts/_ and creates a symlink to that directory.
Possibly this needs to be done as root.

## Usage

First you should manually create the bridges, e.g. by putting the following lines in _/etc/rc.conf_:

```properties
cloned_interfaces="bridge0 bridge1"
ifconfig_bridge0_name="b0_wan"
ifconfig_bridge1_name="b1_dmz"
```

Next, assuming _/usr/local/scripts/_ is in the path, you can create a jail as such:

```properties
XXX {
   vnet;
   vnet.interface = e0a_b0_wan_$name, e0a_b1_dmz_$name;
   exec.prestart = "ep create $name b0_wan b1_dmz";
   exec.prestart = "ep destroy $name b0_wan b1_dmz";
}
```

Enjoy.
