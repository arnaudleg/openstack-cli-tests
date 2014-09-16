import ConfigParser
import os
import time
import uuid

from hurry.filesize import size

import base
from keystoneclient.v2_0 import client as keystone_cli
import glanceclient
from novaclient import client as novaclient


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
        'nova_client_version',
        'keystone_endpoint',
    ]
    for option in options:
        out[option] = config.defaults()[option]
    return out


class ComputeTest(base.Base):

    def setUp(self):
        super(ComputeTest, self).setUp()
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
        self.nova = novaclient.Client(self.config['nova_client_version'],
                                      **self.nova_creds)

    def test_compute_lifecycle(self):
        test_name = 'test_compute_lifecycle'
        image_name = 'image_test_%s' % str(uuid.uuid4())
        start_time = time.time()
        image_start_time = time.time()
        image = self.glance.images.create(
            name=image_name,
            container_format='bare',
            is_public=True,
            disk_format='vmdk',
            copy_from=self.http_image,
            properties=base.Base.image_props)
        self.wait_for_image_status(image, 'active')
        print (test_name, '%s uploaded in %s sec' %
               (str(size(image.size)), str(round(
                time.time() - image_start_time))))

        flavor = self.nova.flavors.find(name=base.Base.flavor)
        im = self.nova.images.find(name=image_name)
        spawn_time = time.time()
        instance = self.nova.servers.create(name="test",
                                            image=im, flavor=flavor)
        status = instance.status
        while status == 'BUILD':
            time.sleep(3)
            instance = self.nova.servers.get(instance.id)
            status = instance.status
            print "status: %s" % status
        if instance.status != 'ACTIVE':
            print "Instance failed to spawn, status %s" % instance.status
        else:
            print (test_name, '%s spawned in %s sec' %
                   (str(size(image.size)),
                    str(round(time.time() - spawn_time))))
            print (test_name, '%s upload and spawned in %s sec' %
                   (str(size(image.size)),
                    str(round(time.time() - start_time))))
            # snapshot
            snapshot_start_time = time.time()
            snap_id = self.nova.servers.create_image(
                instance,
                "snapshot_%s" % str(
                    uuid.uuid4()))
            snapshot = self.glance.images.get(snap_id)
            self.wait_for_image_status(snapshot, 'active')
            print (test_name, 'VM snapshotted in %s sec' %
                   str(round(time.time() - snapshot_start_time)))
        delete_instance_start_time = time.time()
        self.nova.servers.delete(instance)
        print (test_name, 'VM deleted in %s sec' %
               str(round(time.time() - delete_instance_start_time)))
        image_start_time = time.time()
        self.glance.images.delete(image)
        print (test_name, '%s deleted in %s sec' %
               (str(size(image.size)), str(round(
                   time.time() - image_start_time))))
