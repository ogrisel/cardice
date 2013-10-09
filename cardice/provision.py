from libcloud.compute.providers import get_driver


class Provisioner(object):
    """Component in charge of provisioning cloud resources for the cluster"""

    def __init__(self, cluster_config):
        self.cluster_config = cluster_config
        driver_type = get_driver(cluster_config.driver['driver'])
        self.driver = driver_type(
            cluster_config.driver['key'],
            secret=cluster_config.driver.get('secret'),
        )

    def status(self):
        """Check that nodes from the roster"""
        # TODO: use salt-ssh to ping
        return []

    def start(self, n_nodes=1, name_prefix="node", grains=None):
        """Launch new or restart stopped instances from the cluster."""
        raise NotImplementedError("start is not yet implemented")

    def grow(self, n_nodes=1, name_prefix="node", grains=None):
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
