import ConfigParser
import os
import time

from hurry.filesize import size
import testtools

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


class ImageCreateTest(testtools.TestCase):

    http_image = ('https://github.com/arnaudleg/glance-cli-tests/blob/master/'
                  'files/cirros-monosparse.vmdk?raw=true')

    def setUp(self):
        super(ImageCreateTest, self).setUp()
        config_path = os.environ.get('TEST_CONF')
        if not config_path:
            config_path = os.path.join(os.getcwd(), 'etc/openstack.conf')
        raw_config = read_config(config_path)
        self.config = parse_config(raw_config)
        params = {}
        params['token'] = self.keystone.auth_token
        self.glance = glanceclient.Client(
            str(self.config['glance_api_version']), endpoint=self.config
            ['glance_endpoint'], **params)

    @property
    def keystone(self):
        return keystone_cli.Client(username=self.config['username'],
                                   password=self.config['password'],
                                   tenant_name=self.config['tenant_name'],
                                   auth_url=self.config['keystone_endpoint'])

    def wait_for_status(self, image, status):
        while image.status != status:
            if image.status == 'killed':
                self.fail('image %s killed' % image.id)
            image = self.glance.images.get(image.id)
            time.sleep(1)

    def test_create_image_copy_from(self):
        start_time = time.time()
        image = self.glance.images.create(
            name='image_test1',
            container_format='bare',
            is_public=True,
            disk_format='vmdk',
            copy_from=self.http_image,
            properties={'vmware-disktype': 'sparse',
                 'vmware-adaptertype': 'ide'})
        self.wait_for_status(image, 'active')
        print (
            'test_create_image_copy_from', '%s uploaded in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))
        self.glance.images.delete(image)

    def test_create_image_from_local(self):
        start_time = time.time()
        data = os.path.join(os.getcwd(), 'files/cirros-monosparse.vmdk')
        image = self.glance.images.create(
            name='image_test1',
            container_format='bare',
            is_public=True,
            disk_format='vmdk',
            data=open(data, 'rb'),
            properties={'vmware-disktype': 'sparse',
                 'vmware-adaptertype': 'ide'})
        self.wait_for_status(image, 'active')
        print (
            'test_create_image_from_local', '%s uploaded in %s sec' %
            (str(size(image.size)), str(round(time.time() - start_time))))
        self.glance.images.delete(image)
