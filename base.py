import time

import testtools


class Base(testtools.TestCase):

    # 41 MB - preallocated - lsiLogic
    http_image = ('http://partnerweb.vmware.com/programs/vmdkimage/'
                  'cirros-0.3.0-i386-disk.vmdk')

    # 1 GB - preallocated - lsiLogic
    # http_image = ('http://partnerweb.vmware.com/programs/vmdkimage/'
    #             'debian-2.6.32-i686.vmdk')

    @property
    def keystone_creds(self):
        d = {}
        d['username'] = self.config['username']
        d['password'] = self.config['password']
        d['tenant_name'] = self.config['tenant_name']
        d['auth_url'] = self.config['keystone_endpoint']
        return d

    @property
    def nova_creds(self):
        d = {}
        d['username'] = self.config['username']
        d['api_key'] = self.config['password']
        d['auth_url'] = self.config['keystone_endpoint']
        d['project_id'] = self.config['tenant_name']
        return d

    def wait_for_image_status(self, image, status):
        while image.status != status:
            if image.status == 'killed':
                self.fail('image %s killed' % image.id)
            image = self.glance.images.get(image.id)
            time.sleep(1)
