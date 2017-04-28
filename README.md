Module Name
=========

Module to create and delete Rackspace image snapshots.

Requirements
------------

Requires rax ansible module as a dependency.

Module Variables
--------------

Available variables are listed below, along with default values:

```
instance_id: null
```

Server instance id to create a server from.  Your Rackspace account must have access to this server.

```
instance_name: null
```

Server instance name to create a server from.  Must be a unique name.  If you have multiple servers with the same name, use instance_id instead.  Your Rackspace account must have access to this server.

```
meta: null
```

A metadata keypair, specifying ImageType or ImageVersion, for example.

```
image_name: "new snapshot"
```

The name of the new image.

```
state: present
```

Indicates desired state of the resource.  Can be either `present` to create a snapshot or `absent` to delete a snapshot.

```
wait: no
```

Wait for the image to get into `ACTIVE` state before returning.  `no` would allow the playbook to return without waiting for the image to be created (and potentially swallow any creation errors).


```
wait_timeout: 300
```

How long before wait gives up, in seconds.

Dependencies
------------

None

Example Playbook
----------------

    - name: Delete previous snapshots with same name
      local_action:
        module: rax_image
        image_name: "my-old-image"
        region: "DFW"
        state: absent
        wait: yes
        wait_timeout: 600
     
    - name: Create snapshot
      local_action:
        module: rax_image
        image_name: "my-new-image"
        instance_id: "aaaa0000-bbbb-0000-cccc-dddddddddddd"
        region: "DFW"
        state: present
        wait: yes
        wait_timeout: 600

License
-------

MIT

Author Information
------------------

Dimitry Ushakov (@dimtruck)
