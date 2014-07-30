import ConfigParser
import os
import time

from hurry.filesize import size

import base
from keystoneclient.v2_0 import client as keystone_cli
import glanceclient


def read_config(path):
    cp = ConfigParser.RawConfigParser()
    cp.read(path)
    return cp


def parse_config(config):
    out = {}
    options = [
        'username',
        'password',
        'tenant_name',
        'glance_endpoint',
        'glance_api_version',
        'keystone_endpoint',
    ]
    for option in options:
        out[option] = config.defaults()[option]
    return out


class ImageTest(base.Base):

    def setUp(self):
        super(ImageTest, self).setUp()
        config_path = os.environ.get('TEST_CONF')
        if not config_path:
            config_path = os.path.join(os.getcwd(), 'etc/openstack.conf')
        raw_config = read_config(config_path)
        self.config = parse_config(raw_config)
        params = {}
        self.keystone = keystone_cli.Client(**self.keystone_creds)
        params['token'] = self.keystone.auth_token
        self.glance = glanceclient.Client(
            str(self.config['glance_api_version']), endpoint=self.config
            ['glance_endpoint'], **params)

    def test_image_lifecycle_copy_from(self):
        test_name = 'test_image_lifecycle_copy_from'
        start_time = time.time()
        image = self.glance.images.create(
            name='image_test1',
            container_format='bare',
            is_public=True,
            disk_format='vmdk',
            copy_from=self.http_image,
            properties={'vmware-disktype': 'sparse',
                 'vmware-adaptertype': 'ide'})
        self.wait_for_image_status(image, 'active')
        print (
            test_name, '%s uploaded in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))

        start_time = time.time()
        self.glance.images.data(image)
        print (
            test_name, '%s got in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))

        start_time = time.time()
        self.glance.images.delete(image)
        print (
            test_name, '%s deleted in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))

    def test_image_lifecycle_from_local(self):
        test_name = 'test_image_lifecycle_from_local'
        start_time = time.time()
        data = os.path.join(os.getcwd(), 'files/cirros-0.3.0-i386-disk.vmdk')
        image = self.glance.images.create(
            name='image_test1',
            container_format='bare',
            is_public=True,
            disk_format='vmdk',
            data=open(data, 'rb'),
            properties={'vmware-disktype': 'sparse',
                 'vmware-adaptertype': 'ide'})
        self.wait_for_image_status(image, 'active')
        print (
            test_name, '%s uploaded in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))

        start_time = time.time()
        self.glance.images.data(image)
        print (
            test_name, '%s got in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))

        start_time = time.time()
        self.glance.images.delete(image)
        print (
            test_name, '%s deleted in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))
