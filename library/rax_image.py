#!/usr/bin/env python

# This is a DOCUMENTATION stub specific to this module, it extends
# a documentation fragment located in ansible.utils.module_docs_fragments
DOCUMENTATION = '''
---
module: rax_image
short_description: create / delete a custom image snapshot in Rackspace Public Cloud
description:
     - creates / deletes a Rackspace Public Cloud custom image snapshot.
options:
  instance_id:
    description:
      - server instance id to create a server from
    default: null
  instance_name:
    description:
      - server instance name to create a server from.  Must be unique name.  If you have
        multiple servers with the same name, use instance_id instead.
    default: null
  meta:
    description:
      - A metadata keypair, specifying ImageType or ImageVersion, for example.
    default: null
  image_name:
    description:
      - The name of the new image.
    default: null
  state:
    description:
      - Indicate desired state of the resource
    choices:
      - present
      - absent
    default: present
  wait:
    description:
      - wait for the image to be in state 'active' before returning
    default: "no"
    choices:
      - "yes"
      - "no"
  wait_timeout:
    description:
      - how long before wait gives up, in seconds
    default: 300
author: 
    - "Dimitry Ushakove (@dimtruck)"
extends_documentation_fragment: rackspace.openstack
'''

EXAMPLES = '''
- name: Build a Cloud Image snapshot
  gather_facts: False
  tasks:
    - name: Server image build request
      local_action:
        module: rax_image
        credentials: ~/.raxpub
        image_name: rax-image1
        instance_name: my_best_server
        wait: yes
        state: present
- name: Delete a Cloud Image snapshot
  gather_facts: False
  tasks:
    - name: Server image build request
      local_action:
        module: rax_image
        credentials: ~/.raxpub
        image_name: rax_image1
        wait: yes
        state: absent
'''

import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)


try:
    import pyrax
    HAS_PYRAX = True
except ImportError:
    HAS_PYRAX = False


def cloudservers(module, state=None, name=None, instance_id=None,
                 meta={}, wait=True, wait_timeout=300):
    '''
    Defines image creation and deletion based on state
    '''
    cs = pyrax.cloudservers
    
    changed = False
    success = None
    error = None

    # act on the state
    if state == 'present':
        # get the server object first
        server = cs.servers.get(instance_id)

        if server is None:
            module.fail_json(msg='instance_id is not found')

        # create image
        # currently, metadata is not supported
        image_id = server.create_image(name)

        image = cs.images.get(image_id)

        logging.info('image %s', image)

        if wait:
            ret = pyrax.utils.wait_until(image, "status", ["ACTIVE", "ERROR"], attempts=0)
            if ret.status == "ACTIVE":
                success = "ACTIVE"
            else:
                error = "ERROR"
            changed = True
            logging.info('image result:: return: %s, success: %s, error: %s', ret, success, error)


        image_dict = {
            'id': image.id,
            'links': image.links,
            'metadata': image.metadata,
            'created': image.created,
            'minDisk': image.minDisk,
            'minRam': image.minRam,
            'name': image.name,
            'progress': image.progress,
            'status': image.status,
            'server': image.server
        }

        logging.info('image dict %s', image_dict)

        results = {
            'changed': changed,
            'action': 'create',
            'image': image_dict,
            'success': success,
            'error': error
        }

        if error:
            results['msg'] = 'Failed to build image snapshot'

        logging.info('results %s', results)

        if 'msg' in results:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

    elif state == 'absent':
        deleted_images = []
        images = cs.images.list()
        for image in images:
            # delete image
            if image.name == name:
                try:
                    cs.images.delete(image.id)
                except Exception, e:
                    module.fail_json(msg=e.message)
                else:
                    changed = True

                if wait:
                    end_time = time.time() + wait_timeout
                    while time.time() < end_time:
                        try: 
                            result = cs.images.get(image)
                            if result is None:
                                success = "DELETED"
                                break
                        except cs.exceptions.NotFound:
                            success = "DELETED"
                            break
                    else:
                        error = "ERROR"
                    changed = True
                    logging.info('image result:: return: %s, success: %s, error: %s', image, success, error)

                deleted_images.append({
                    'id': image.id,
                    'success': success,
                    'error': error
                })

        results = {
            'changed': changed,
            'action': 'delete',
            'images': deleted_images,
            'success': success,
            'error': error
        }

        if error:
            results['msg'] = 'Failed to delete all images'

        if 'msg' in results:
            module.fail_json(**results)
        else:
            module.exit_json(**results)

def main():
    '''
    main entry point for python ansible Module
    '''
    argument_spec = rax_argument_spec()
    argument_spec.update(
        dict(
            instance_id=dict(type='str'),
            meta=dict(type='dict', default={}),
            image_name=dict(),
            state=dict(default='present', choices=['present', 'absent']),
            wait=dict(default=False, type='bool'),
            wait_timeout=dict(default=300),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=rax_required_together(),
    )

    if not HAS_PYRAX:
        module.fail_json(msg='pyrax is required for this module')

    instance_id = module.params.get('instance_id')
    meta = module.params.get('meta')
    image_name = module.params.get('image_name')
    state = module.params.get('state')
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))

    if image_name is None:
        module.fail_json(msg='image_name is required for rax_image module')

    if instance_id is None and state == 'present':
        module.fail_json(msg='instance_id is required for present '
                             'state for rax_image module')

    setup_rax_module(module, pyrax)

    if pyrax.cloudservers is None:
        module.fail_json(msg='Failed to instantiate client. This '
                             'typically indicates an invalid region or an '
                             'incorrectly capitalized region name.')

    cloudservers(module, state, image_name, instance_id,
                 meta, wait, wait_timeout)


# import module snippets
# cannot speciy modules specifically due to
# fatal: [localhost]: FAILED! => 
# {"failed": true, "msg": "ERROR! error importing module in 
# /opt/ansible/library/rax_image.py, expecting 
# format like 'from ansible.module_utils.basic import *'"}
from ansible.module_utils.basic import *
from ansible.module_utils.rax import *

# invoke the module
main()
