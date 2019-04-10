# ep-jails
Script to create epair interfaces for my FreeBSD jails

## Introduction

The way I understand the `jib` script (_/usr/share/examples/jails/jib_) is that requires a physical interface to bind the bridge to.
That does not work for me as I only have one physical interface and want to use bridges that are completely isolated.
Lucas' solution in _FreeBSD mastery: Jails_ is to create a second loopback interface (p. 165) using:

```properties
cloned_interfaces = "lo1"
```

Alas, this did not work for me (12.0-RELEASE) and neither did it work for [others][1] (Marko Zec, 2016): "if_bridge(4) works only with ethernet interfaces, and lo(4) isn't such a thing".
This, added with the fact that I don't understand a thing of the script, my bash-fu is not that great, I decided to write my own script after figuring out how to make it work.

  [1]: https://lists.freebsd.org/pipermail/freebsd-net/2016-June/045640.html

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
   exec.poststop = "ep destroy $name b0_wan b1_dmz";
}
```

Enjoy.

## To-Do

The script needs error checking, e.g.:

  - Check whether the interfaces already exist before trying to create or delete them.
  - Catch and handle Exceptions.
