# Pesquisa Operacional  - 2018/1
# Engenharia de Sistemas UFMG
# Artur Mello - 2013030392
# Hernane Braga Pereira - 2014112627

import gurobipy as grb
import pandas as pd
from plot_results import *

filename = "bebidas.csv"
data_csv = pd.read_csv(filename)
data = pd.DataFrame(data_csv)

# Fórmula geral: C = A/(R*P)
# A = gramas de álcool [g]
# R = fator de conversão: 0.68 [homem]  e 0.55 [mulher]
# P = peso da pessoa [kg]
# C = gramas de álcool ingerida por kilo

# Taxa de álcool no sangue [TAS] = C/1.056
# TAS é expressa em [g/L] que é grama de álcool por litro de sangue
# Dividi-se por 1.056, pois é a densidade do sangue


def calculo_TAS(volume_ml, abv, peso, sexo):
    A = (abv*volume_ml*0.79)/100  # 0.79 para converter ml para grama de álcool
    if sexo == 2:
        R = 0.55
    else:
        R = 0.68
    C = A/(R*peso)
    TAS = C/1.056
    return TAS


''' Parametros de entrada do usuario e do modelo
peso em Kg
sexo - 1 - masculino / 2 - feminino
saldo - Quantidade de dinheiro para gastar em [R$]

TAS_min - Taxa de álcool no sangue para entrar em estado de embriaguez
TAS_max - Limite seguro para Taxa de álcool máxima no sangue

'''
# Usuário
peso = 60
sexo = 2
saldo = 300

# Modelo
TAS_min = 0.3   # Taxa de álcool no sangue para entrar em estado de embriaguez
TAS_max = 1.2   # Limite seguro para Taxa de álcool máxima no sangue


# Parametros do modelo


# Processamento de informacoes
TAS_itens = []
nome_itens = []
preco_itens = []
data_list = data.values.tolist()
N = len(data_list)

# Calculo de TAS para cada item
for item in data_list: 
    TAS_itens.append(calculo_TAS(item[1], item[3], peso, sexo))
    nome_itens.append(item[0])
    preco_itens.append(item[2])
    # item[i] se refere à coluna do dataset

# Create a new model
m = grb.Model('alcoolizador')

x = [m.addVar(vtype=grb.GRB.INTEGER, name=i) for i in nome_itens]

m.update()

obj = grb.quicksum([i*j for i,j in zip(x, TAS_itens)])
custo = grb.quicksum([i*j for i,j in zip(x, preco_itens)])

m.setObjective(obj, grb.GRB.MAXIMIZE)

# Restricoes do problema:
m.addConstr(obj <= TAS_max)
m.addConstr(obj >= TAS_min)
m.addConstr(custo <= saldo)

m.optimize()
status = m.status
if status == 4:
    print('Modelo infactível: saldo monetário insuficiente.')

# Caso o problema não seja infactivel
else:
    conta_do_bar = 0
    print('\n--- Resultado Final ----\n')
    print('Sexo: {0}\nPeso: {1} kg\nSaldo disponível: R${2:.2f}'.format(("masculino" if sexo == 1 else "feminino"), peso, float(saldo)))
    print('\n## QUANTIDADE DE ITENS COMPRADOS ##')
    items_index = []
    for index, v in enumerate(m.getVars()):
        if v.x > 0:
            print('{}: {}'.format(v.varName, round(v.x)))
            items_index.append({"id":index, "value": v.x})
        conta_do_bar += v.x * preco_itens[index]
        
    print('-------\nConta do bar: R${0:.2f} '.format(conta_do_bar))
    print('\nTAS final: %g g/L' % m.objVal)  
    perc = 100*(m.objVal/TAS_max)
    print('{}'.format(("Você atingiu o limite máximo de álcool no sangue para " if perc >= 99
          else "Você está {0:.2f}% perto do limite máximo de não desmaiar ".format(perc))))

    '''    
        # Plotar grátifcos
        # 1 - itens por TAS(g/L)
        # 2 - itens por dinheiros(R$)
    '''
    plot_tas_per_drink(data, TAS_itens, TAS_min, TAS_max, items_index, N, 4)
    plot_price_per_drink(data, preco_itens, 0, saldo, items_index, N, 4)
