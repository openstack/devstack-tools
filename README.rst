===============================
devstack-tools
===============================

Devstack Helper Tools in Python

This is a set of cli tools for supporting devstack. It moves some of
the complexity out of bash and into python where it's easier to have
comprehensive testing of behavior.

Currently this includes the ``dsconf`` tool, which provides a cli for
manipulating local.conf and ini files.

::

  usage: dsconf [-h]
              {iniset,inicomment,iniuncomment,inirm,extract-localrc,extract,setlc,setlc_raw,setlc_conf,merge_lc}
              ...

  optional arguments:
    -h, --help            show this help message and exit

  commands:
    {iniset,inicomment,iniuncomment,inirm,extract-localrc,extract,setlc,setlc_raw,setlc_conf,merge_lc}
                        sub-command help
    iniset              set item in ini file
    inicomment          comment item in ini file
    iniuncomment        uncomment item in ini file
    inirm               delete item from ini file
    extract-localrc     extract localrc from local.conf
    extract             extract and merge config from local.conf
    setlc               set variable in localrc of local.conf
    setlc_raw           set raw line at the end of localrc in local.conf
    setlc_conf          set variable in ini section of local.conf
    merge_lc            merge local.conf files


* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/devstack-tools
* Source: http://git.openstack.org/cgit/openstack/devstack-tools
* Bugs: http://bugs.launchpad.net/replace with the name of the project on launchpad

Features
--------

* TODO
