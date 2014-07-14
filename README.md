glance-cli-tests
================

A set of tests exercising the glance client api with actual files

install
=======

git clone https://github.com/arnaudleg/glance-cli-tests.git

pip install -r requirements.txt

update etc/openstack.conf

use
===

python -m unittest discover glance-cli-tests

python -m unittest test_image
