from __future__ import print_function

from time import time
from time import sleep
import os
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeState
from concurrent.futures import ThreadPoolExecutor


def create_node(node_spec, timeout=600):
    # The libcloud driver classes are not thread safe, hence the delayed
    # instanciation
    driver = node_spec['driver_type'](node_spec['key'], node_spec['secret'])
    config = node_spec['config']
    node_name = node_spec['name']
    config.log.debug('creating node %s on %s',
                     node_name, node_spec['provider'])
    node = driver.create_node(
        name=node_spec['name'],
        image=node_spec['image'],
        size=node_spec['size'])

    config.log.debug('registering %s at %s', node_name, node.public_ip)
    config.register_node(node_spec, node)

    driver.wait_until_running([node], timeout=timeout)

    # TODO: use salt-ssh to deploy the cluster independent states maybe with
    # state.sls in parallel


class Provisioner(object):
    """Component in charge of provisioning cloud resources for the cluster"""

    def __init__(self, config, max_workers=50):
        self.config = config
        self.max_workers = max_workers

    def status(self):
        """Check that nodes from the roster"""
        # TODO: use salt-ssh to ping
        return []

    def start(self, profile_name, n_nodes=1, name_prefix="node",
              refresh_period=20):
        """Launch new or restart stopped instances from the cluster."""
        tic = time()

        # TODO: detect if there is an existing roster to restart it if the
        # profile supports it
        # TODO: move this code
        profile = self.config.get_profile(profile_name)

        # Fetch params before entering thread pool to fail early
        # if some mandatory param is missing.
        provider = profile['provider']
        driver_type = get_driver(provider)
        image_name = profile.get('image')
        size_name = profile.get('size')

        # TODO: make it possible to fetch the credentials from the cluster
        # config
        key_varname = 'CARDICE_{}_KEY'.format(provider.upper())
        secret_varname = 'CARDICE_{}_SECRET'.format(provider.upper())
        if not key_varname in os.environ:
            raise RuntimeError(
                "Please set credentials in environment variables"
                " {} and {}".format(key_varname, secret_varname))
        key = os.environ[key_varname]
        secret = os.environ.get(secret_varname)

        # Check that the size and images are valid, otherwise pickup the
        # first available image and size
        driver = driver_type(key, secret=secret)
        images = driver.list_images()
        if image_name is None:
            image = images[0]
        else:
            matching_images = [i for i in images if i.name == image_name]
            if matching_images:
                image = matching_images[0]
            else:
                raise RuntimeError('could not find image %s on %s'
                                   % (image_name, provider))
            self.config.log.debug("using image %s", image.name)

        sizes = driver.list_sizes()
        if size_name is None:
            size = sizes[0]
        else:
            matching_sizes = [s for s in sizes if s.name == size_name]
            if matching_sizes:
                size = matching_sizes[0]
            else:
                raise RuntimeError('could not find size %s on %s'
                                   % (size_name, provider))
        self.config.log.debug("using size %s", size.name)

        node_specs = [
        {
            'provider': provider,
            'driver_type': driver_type,
            'key': key,
            'secret': secret,
            'image': image,
            'size': size,
            'config': self.config,
            'name': "{}{:03d}".format(name_prefix, i)
        } for i in range(n_nodes)]

        self.config.log.info('starting %d nodes with profile %s',
            n_nodes, profile_name)
        with ThreadPoolExecutor(self.max_workers) as e:
            tasks = [e.submit(create_node, spec) for spec in node_specs]
            while True:
                sleep(refresh_period)
                completed = [t for t in tasks if t.done()]
                for t in completed:
                    # Raise the exception in case of failure
                    t.result()
                self.config.log.info(
                    "waiting for nodes to start (%03d/%03d)...",
                    len(completed), n_nodes)
                if len(completed) == n_nodes:
                    break

        d_min, d_sec = divmod(time() - tic, 60)
        self.config.log.info('started %d nodes in %d minutes and %d seconds',
            n_nodes, d_min, d_sec)

    def grow(self, profile, n_nodes=1, name_prefix="node", grains=None):
        """Add new nodes to the current cluster."""
        raise NotImplementedError("grow is not yet implemented")

    def shrink(self, n_nodes=1, name_prefix="node", grains=None):
        """Shutdown nodes from current cluster."""
        raise NotImplementedError("shrink is not yet implemented")

    def stop(self):
        """Stop instances from the current roster"""
        raise NotImplementedError("stop is not yet implemented")

    def terminate(self):
        """Shutdown the instances from the roster

        Release all related cloud resources. Unbacked data (e.g. on block
        devices) will be lost.
        """
        raise NotImplementedError("terminate is not yet implemented")

    def _get_nodes(self):
        # TODO: filter out nodes that don't match the cluster roster
        return self.drive.list_nodes()
