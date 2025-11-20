# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import copy
from torch.nn.utils import parameters_to_vector

NETCONF = [46,50,10,3]
NetConf = NETCONF


class NeuralNetwork(nn.Module):
    def __init__(self):
        # NetConf = [31,10,10,2]
        input_size = NetConf[0]
        # for l in NetConf[1:-1]:
        #    hidden[]=.............................................................
        hidden_size = NetConf[1]
        output_size = NetConf[3]
        self.hidden = torch.zeros(1, NetConf[1])

        super().__init__()
        self.hidden_size = hidden_size
        self.i2h = nn.Linear(input_size + self.hidden_size, self.hidden_size)
        self.h2o = nn.Linear(self.hidden_size, output_size)
        #self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.softmax = nn.Sigmoid()

    def forward(self, input):
        if type(input) == list:
            #print("LIST LIST LIST")
            # input = torch.FloatTensor(input)
            input = torch.tensor(input)
            input = input[None, :]
            input.shape
        #print (input.size())
        #print (self.hidden.size())
        #print ("self.hiddenself.hiddenself.hiddenself.hiddenself.hidden")
        #print (self.hidden)




        # 2024-01-26 Пробуем без обучения скрытого слоя - он будет всегда нулевой, потом посмотрим как сойдется.
        # Сейчас пока сетка - считай прямого распространения.
        self.hidden = torch.zeros(1, 50)




        combined = torch.cat((input, self.hidden), 1)
        self.hidden = torch.sigmoid(self.i2h(combined))
        output = self.h2o(self.hidden)
        #output = self.i2o(combined)
        output = self.softmax(output)
        return output

    def calc(self, input):
        res1 = self.forward(input)
        res2 = res1.tolist()[0]
        #print (res2)
        return res2

    def initHidden(self):
        print("Clear hidden")
        self.hidden = torch.zeros(1, self.hidden_size)
        return self.hidden

    def mutate(self, mut_prob, mut_strength):
        # print("MUTATION")
        for param in self.parameters():
            # Тут хитрые вычисления Создается тензон размерности с исходный тензор, 
            # он заполняется случайными значениями и сравнивается меньше ли он вероятности мутации, если True
            # то True.int() = 1
            # Иначе False.int() = 0
            # ебучая магия
            param.data += mut_strength * torch.randn_like(param) * (torch.rand(size=param.data.size()) < mut_prob).int()

    # def __deepcopy__(self, memo):
    #     cls = self.__class__ # Extract the class of the object
    #     result = cls.__new__(cls) # Create a new instance of the object based on extracted class
    #     #memo[id(self)] = result
    #     #for k, v in self.__dict__.items():
    #     #    setattr(result, k, copy.deepcopy(v, memo)) # Copy over attributes by copying directly or in case of complex objects like lists for exaample calling the `__deepcopy()__` method defined by them. Thus recursively copying the whole tree of objects.
    #     result.load_state_dict(copy.deepcopy(memo.state_dict()))
    #     return result


    def debug_print(self):
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # print(self._inputs)
        # print(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ")
        # print(self.hidden)
        # print(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ")
        # print(self)
        print(". . . . . . . . . . . . . .  ВСЕ ВЕСА:. . . . . . . . . . . . . . . . . . . . . . ")
        for name, param in self.named_parameters():
            print(name, param.data)
        # print(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ")
        # print(self._outs)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        for layer in self.children():
            print("- - - ")
            for param in layer.parameters():
                print(param)
        # for name, param in self.named_parameters():
        #     print(name, param.data)



    def weights_matrix(self):
        # self.debug_print()
        matrix_layers = []
        # fake_neuron = [-0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # matrix_layers.append([fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron])
        # matrix_layers.append([fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron])
        # matrix_layers.append([fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron, fake_neuron])
        # for param in self.parameters():
        #for param in self.parameters():
        for name, param in self.named_parameters():
            # i2h.weight
            # i2h.bias
            # h2o.weight
            # h2o.bias
            if name[4:]=="weight":
                matrix_layers.append(param.tolist())
        # print ("################# matrix_layers #######################")
        # print(matrix_layers)
        # print ("######################################################")
        return matrix_layers
