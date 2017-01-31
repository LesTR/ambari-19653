#!/usr/bin/env python
from resource_management.libraries.script import Script
from resource_management import *

import json
from ambari_commons import OSCheck


class Ambari19653Workaround(Script):
    def install_packages(self,env):
        """
        List of packages that are required< by service is received from the server
        as a command parameter. The method installs all packages
        from this list

        exclude_packages - list of regexes (possibly raw strings as well), the
        packages which match the regex won't be installed.
        NOTE: regexes don't have Python syntax, but simple package regexes which support only * and .* and ?
        """
        config = self.get_config()
        if 'host_sys_prepped' in config['hostLevelParams']:
            # do not install anything on sys-prepped host
            if config['hostLevelParams']['host_sys_prepped'] == True:
                Logger.info("Node has all packages pre-installed. Skipping.")
                return
            pass
        try:
            package_list_str = config['hostLevelParams']['package_list']
            agent_stack_retry_on_unavailability = bool(config['hostLevelParams']['agent_stack_retry_on_unavailability'])
            agent_stack_retry_count = int(config['hostLevelParams']['agent_stack_retry_count'])

            if isinstance(package_list_str, basestring) and len(package_list_str) > 0:
                package_list = json.loads(package_list_str)
                for package in package_list:
                    # HACK: Original line:
                    #if Script.check_package_condition(package):
                    if self.check_package_condition(package):
                        name = self.format_package_name(package['name'])
                        # HACK: On Windows, only install ambari-metrics packages using Choco Package Installer
                        # TODO: Update this once choco packages for hadoop are created. This is because, service metainfo.xml support
                        # <osFamily>any<osFamily> which would cause installation failure on Windows.
                        if OSCheck.is_windows_family():
                            if "ambari-metrics" in name:
                                Package(name)
                        else:
                            Package(name,
                                retry_on_repo_unavailability=agent_stack_retry_on_unavailability,
                                retry_count=agent_stack_retry_count)
        except KeyError:
            pass  # No reason to worry

        if OSCheck.is_windows_family():
            #TODO hacky install of windows msi, remove it or move to old(2.1) stack definition when component based install will be implemented
            hadoop_user = config["configurations"]["cluster-env"]["hadoop.user.name"]
            install_windows_msi(config['hostLevelParams']['jdk_location'],
                                config["hostLevelParams"]["agentCacheDir"], ["hdp-2.3.0.0.winpkg.msi", "hdp-2.3.0.0.cab", "hdp-2.3.0.0-01.cab"],
                                hadoop_user, self.get_password(hadoop_user),
                                str(config['hostLevelParams']['stack_version']))
            reload_windows_env()

    # Copied from ambari + hacked
    def check_package_condition(self,package):
        from resource_management.libraries.script import Script
        condition = package['condition']
        name = package['name']
        if not condition:
            return True
        if hasattr(self,condition):
            methodCondition = getattr(self,condition)
        else:
            methodCondition = getattr(Script,condition)
        return methodCondition()

    # Copied from ambari-common/src/main/python/resource_management/libraries/functions/package_conditions.py
    def _has_local_components(self,config, components, indicator_function = any):
        if 'role' not in config:
            return False
        if config['role'] == 'install_packages':
            # When installing new stack version for upgrade, all packages on a host are installed by install_packages.
            # Check if
            if 'localComponents' not in config:
                return False
            return indicator_function([component in config['localComponents'] for component in components])
        else:
            return config['role'] in components

    def _has_applicable_local_component(self, config, components):
        return self._has_local_components(config, components, any)
    def should_install_nginx(self):
        return self._has_applicable_local_component(self.get_config(), ["AMBARI_19653_NGINX"])
    def should_install_apache(self):
        return self._has_applicable_local_component(self.get_config(), ["AMBARI_19653_APACHE"])
