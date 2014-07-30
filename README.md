openstack-cli-tests
================

A set of tests exercising the openstack client api with actual files

install
=======

git clone https://github.com/arnaudleg/openstack-cli-tests.git

cd openstack-cli-tests && pip install -r requirements.txt

update etc/openstack.conf with appropriate values

use
===

python -m unittest discover openstack-cli-tests

python -m unittest test_image

python -m unittest test_compute
