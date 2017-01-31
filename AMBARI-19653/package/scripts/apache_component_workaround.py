#!/usr/bin/env python
from resource_management import *
from workaround import Ambari19653Workaround

class ApacheComponent(Ambari19653Workaround):
    def install(self, env):
        import params
        env.set_params(params)
        self.install_packages(env)
    def stop(self, env):
        Execute('service apache2 stop', timeout=10 )
    def start(self, env):
        Execute('service apache2 start', timeout=10 )
    def status(self, env):
        try:
            Execute(format("service apache2 status | grep 'apache2 is running'"), timeout=10 )
        except Fail:
            raise ComponentIsNotRunning()


if __name__ == "__main__":
    ApacheComponent().execute()
