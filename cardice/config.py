import os
import re
import yaml
import logging
import shutil

from cardice import templates


LOGGING_FORMAT = "[%(cluster)s] %(message)s"


TEMPLATE_FOLDER = templates.__path__[0]


class Configurator(object):
	"""Manage the cardice configuration folder"""

	default_cluster_filename = "default_cluster"

	valid_cluster_name = re.compile(r"^[\w_-]+$")

	default_cluster = None

	def __init__(self, options):
		# Configure logging
		level = getattr(logging, options.log_level.upper())
		logging.basicConfig(level=level, format=LOGGING_FORMAT)

	    # Setup config folder
		self.options = options
		config_folder = os.path.abspath(os.path.expanduser(
			options.cardice_folder))
		if not os.path.exists(config_folder):
			os.makedirs(config_folder)
			shutil.copyfile(
				os.path.join(TEMPLATE_FOLDER, 'default_profiles.yaml'),
				os.path.join(config_folder, 'profiles.yaml'))

		self.config_folder = config_folder
		self.log = self.get_logger()
		self.log.debug("initialized configuration in: %s", config_folder)

	def get_cluster_folder(self):
		"""Fetch the configuration folder path for the active cluster"""
		cluster_name = self.get_active_cluster()
		cluster_folder = os.path.join(self.config_folder, cluster_name)
		if not os.path.exists(cluster_folder):
			raise RuntimeError("Cluster configuration folder not found: "
				               + cluster_folder)
		return cluster_folder

	def get_active_cluster(self, force_read=False):
		"""The cluster selected from the command line or the default"""
		if self.options.cluster is not None:
			return self.options.cluster

		if not force_read and self.default_cluster is not None:
			# Reuse cached info to limit FS access
			return self.default_cluster
		default_cluster_filepath = os.path.join(
			self.config_folder, self.default_cluster_filename)
		if not os.path.exists(default_cluster_filepath):
			return None
		cluster_name = open(default_cluster_filepath, 'rb').read().strip()
		if not cluster_name:
			return None
		return cluster_name

	def set_default_cluster(self, cluster_name):
		"""Select a specific configuration as the active cluster"""
		if self.get_active_cluster(force_read=True) == cluster_name:
			# Nothing to do
			return

		cluster_folder = os.path.join(self.config_folder, cluster_name)
		if not os.path.exists(cluster_folder):
			raise RuntimeError("cluster configuration %s does not exist in %s"
				% (cluster_name, self.config_folder))

		default_cluster_filepath = os.path.join(
			self.config_folder, self.default_cluster_filename)
		open(default_cluster_filepath, 'wb').write(cluster_name)
		self.default_cluster = cluster_name
		self.log = self.get_logger()
		self.log.debug('selected new default cluster')

	def init_cluster(self, cluster_name):
		cluster_folder = os.path.join(self.config_folder, cluster_name)
		if not self.valid_cluster_name.match(cluster_name):
			raise RuntimeError("invalid cluster name: %s"
				% cluster_name)
		if os.path.exists(cluster_folder):
			raise RuntimeError("cluster %s already configured in %s"
				% (cluster_name, cluster_folder))
		os.makedirs(cluster_folder)
		self.set_default_cluster(cluster_name)

	def get_logger(self, name="cardice"):
		return logging.LoggerAdapter(logging.getLogger(name),
			dict(cluster=self.get_active_cluster() or '<cardice>'))

	def get_profile(self, profile_name):
		all_profiles = {}
		cardice_profiles = os.path.join(self.config_folder, 'profiles.yaml')
		if os.path.exists(cardice_profiles):
			self.log.debug('reading profiles from %s', cardice_profiles)
			with open(cardice_profiles, 'rb') as f:
				all_profiles.update(yaml.load(f))

		cluster_profiles = os.path.join(self.get_cluster_folder(), 'profiles.yaml')
		if os.path.exists(cluster_profiles):
			self.log.debug('reading cluster profiles from %s', cluster_profiles)
			with open(cluster_profiles, 'rb') as f:
				all_profiles.update(yaml.load(f))

		if not all_profiles:
			raise RuntimeError("could not find any profile definition in "
							   + self.config_folder)

		if profile_name not in all_profiles:
			raise RuntimeError("no such profile " + profile_name)

		return all_profiles[profile_name]

	def register_node(self, node_spec, node):
		# TODO: implement me: save the info in a roster compatibel file
		pass