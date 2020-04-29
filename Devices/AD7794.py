class Info():
    def __init__(self, id):
        self.Info = {}
        #        button String, firmware command
        self.Info['Id'] = [[id, f'_{id}']]
        self.Info['AnalogIn'] = []
        self.Info['AnalogOut'] = []
        self.Info['Digital'] = []

        self.Info['Id'].append(['Read Data',  f'{self.Info["Id"][0][1]}.ReadData()'])
        self.Info['Id'].append(['ComTest',    f'{self.Info["Id"][0][1]}.SendData(00000000)'])
        self.Info['Id'].append(['ICID',       f'{self.Info["Id"][0][1]}.SendData(00020000)'])
        self.Info['Id'].append(['Temperature',f'{self.Info["Id"][0][1]}.SendData(00040000)'])

        for i in range(1, 7):
            self.Info['AnalogIn'].append(['AIn' + str(i), f'{self.Info["Id"][0][1]}.SendData(00060{i})'])
        for i in range(0, 8):
            self.Info['AnalogIn'].append(['Gain' + str(2**i), f'0{i}'])
        for i in range(0 , 8):
            self.Info['Digital'].append(['A'+ str(i), f'{self.Info["Id"][0][1]}.SendData(00070{i})'])
        for i in range(2, 10):
            self.Info['Digital'].append(['D'+ str(i), f'{self.Info["Id"][0][1]}.SendData(00070{i})'])

    def get(self):
        return self.Info
