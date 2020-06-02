# coding: utf-8

import random
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# Criação da rede neural
class FlappyModel(nn.Module):
  def __init__(self):
    super(FlappyModel, self).__init__()
    self.fitness = 0
    # Entrada: distância horizontal, vertical, abertura canos
    self.fc1 = nn.Linear(3, 6)
    self.fc2 = nn.Linear(6, 1) # saída (sobe ou não sobe)

  def forward(self, x):
    # As camadas são conectadas por uma função de ativação (ReLU)
    return F.relu(self.fc2(F.relu(self.fc1(x))))

net = FlappyModel() # Criamos uma instância da rede neural

def mutacao(rede, forca_mutacao = 0.01):  
  for param in rede.parameters():
    t = param.data
    t.add_(torch.randn_like(t, dtype=torch.float) * forca_mutacao)

def cross_over(rede1, rede2):
  filho = FlappyModel()
  for pFilho, pPai, pMae in zip(filho.parameters(), rede1.parameters(), rede2.parameters()):
    if pFilho.dim() == 1:
      pFilho[:] = pPai if random.random() < 0.5 else pMae
    elif pFilho.dim() == 2:
      pFilho[:,:] = pPai if random.random() < 0.5 else pMae
    elif pFilho.dim() == 3:
      pFilho[:,:,:] = pPai if random.random() < 0.5 else pMae
    elif pFilho.dim() == 4:
      pFilho[:,:,:,:] = pPai if random.random() < 0.5 else pMae
    elif pFilho.dim() == 5:
      pFilho[:,:,:,:,:] = pPai if random.random() < 0.5 else pMae
  return filho

def evolui(populacao, pct_permanece = 0.1, pct_reproduz = 0.1, pct_mutacao = 0.7):
  qtd_individuos = len(populacao)
  qtd_permanece  = int(qtd_individuos * pct_permanece)
  qtd_reproduz   = int(qtd_individuos * pct_reproduz)
  qtd_mutacao    = int(qtd_individuos * pct_mutacao)
  qtd_novos      = qtd_individuos - (qtd_permanece + qtd_reproduz + qtd_mutacao)

  # calcula os erros de cada indivíduo
  scores = list(map(lambda individuo: (individuo, individuo.fitness), populacao))
  # ordena pelo score - decrescente
  scores.sort(key=lambda individuo: individuo[1], reverse=True)

  print('melhor score {} - pior score {}'.format(scores[0][1], scores[-1][1]))

  # obtem apenas os indivíduos
  populacao = list(map(lambda individuo: individuo[0], scores))
  
  # montando a próxima geracao
  proxima_geracao = []
  proxima_geracao += populacao[: qtd_permanece]

  for i in range(qtd_reproduz):
    pai = populacao[random.randint(0, qtd_permanece)]
    mae = populacao[random.randint(0, qtd_permanece)]
    proxima_geracao.append(cross_over(pai, mae))
  
  for i in range(qtd_mutacao):
    clone = FlappyModel()
    clone.load_state_dict(populacao[random.randint(0, qtd_permanece)].state_dict())
    mutacao(clone)
    proxima_geracao.append(clone)
  
  for i in range(qtd_novos):
    proxima_geracao.append(FlappyModel())
  
  return proxima_geracao, scores[0][1]
