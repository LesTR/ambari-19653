#!/usr/bin/env python
from resource_management import *


class NginxComponent(Script):
    def install(self, env):
        import params
        env.set_params(params)
        self.install_packages(env)
    def stop(self, env):
        Execute('service nginx stop', timeout=10 )
    def start(self, env):
        Execute('service nginx start', timeout=10 )
    def status(self, env):
        try:
            Execute(format("service nginx status | grep 'nginx is running'"), timeout=10 )
        except Fail:
            raise ComponentIsNotRunning()

if __name__ == "__main__":
    NginxComponent().execute()
