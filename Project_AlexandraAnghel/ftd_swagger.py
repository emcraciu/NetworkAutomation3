from pyats import aetest, topology


class ConnectFTDREST(aetest.Testcase):
    @aetest.test
    def load_testbed(self, steps):
        with steps.start("Load testbed"):
            self.tb = topology.loader.load('ftd_testbed.yaml')
            self.parent.parameters.update(tb=self.tb)

    @aetest.test
    def connect_via_rest(self, steps):
        with steps.start("Connect via rest"):
            for device in self.tb.devices:
                if self.tb.devices[device].type != 'ftd':
                    continue
                if "swagger" not in self.tb.devices[device].connections:
                    continue
                connection = self.tb.devices[device].connect(via='swagger')
                print(connection)
                swagger = connection.get_swagger_client()
                print(swagger)


if __name__ == '__main__':
    aetest.main()
