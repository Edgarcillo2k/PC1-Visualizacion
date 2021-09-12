# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 12:05:37 2021

@author: Edgar
"""

# Preprocesado de datos

import pandas as pd
import json

# Importar el data set
dataset = pd.read_csv('Exports-2019---Click-to-Select-a-Product.csv')

group_level1 = dataset.groupby(by=['Section']).sum()
group_level2 = dataset.groupby(by=['HS2','Section']).sum() 

#Script para transformacion de datos para D3
tree = {}   
for index, row in group_level1.iterrows():
    tree[index] = {
        "name": index,
        "value": row[3],
        "children": [],
        "childrenDict": {},
        "dummy_val": 0
    }
    
for index, row in group_level2.iterrows():
    element = {
        "name": index[0],
        "value": row[3],
        "children": [],
        "dummy_val": 0
    }
    tree[index[1]].get("children").append(element)
    tree[index[1]].get("childrenDict")[element.get("name")] = element
    
for index, row in dataset.iterrows():
    element = {
        "name": row[5],
        "value": row[6],
        "dummy_val": 1
    }
    tree[row[1]].get("childrenDict")[row[3]].get("children").append(element)

tree = {
    "name": "Exportations",
    "children": list(tree.values()), 
    "value": dataset['Trade Value'].sum(),
    "color": 1,
    "dummy_val": 1183 #Cantidad de filas, en caso de usar otro archivo especificar len(dataset)
}

#Asignacion de peso del color entre 0 y 1 y los dummy values
def set_tree_color(tree):
    try:
        seq = [x["value"] for x in tree["children"]]
        max_val = max(seq)
        dummy_val = tree["dummy_val"]/len(tree["children"])
        for element in tree["children"]:
            element["dummy_val"] = dummy_val
            element["color"] = element["value"]/max_val
            set_tree_color(element)
    except: #except es el caso base donde llega a un hijo
        pass
            
set_tree_color(tree)
           
#Salvar json con el arbol 
with open('processed_data.json','w') as fp:
    json.dump(tree,fp)
    
#Script para transformacion de datos para plotly
def tree_to_list(tree, elements, parents, trade_values, colors, dummy_values):
    elements.append(tree["name"])
    trade_values.append(tree["value"])
    colors.append(tree["color"])
    dummy_values.append(tree["dummy_val"])
    try:
        for element in tree["children"]:
            parents.append(tree["name"])
            tree_to_list(element,elements,parents,trade_values,colors,dummy_values)
    except: #except es el caso base donde llega a un hijo
        pass
    
elements = []
parents = [""] #Comienza con un string vacio que es la raiz que no tiene padre
trade_values = []
colors = []
dummy_values = []

tree_to_list(tree, elements, parents, trade_values, colors,dummy_values)

#Salvar csv con los datos
processed_data = pd.DataFrame({'element': elements, 'parent': parents, 'trade_value': trade_values, 'color': colors, 'dummy_value': dummy_values})
processed_data.to_csv(r'processed_data.csv',index=False)