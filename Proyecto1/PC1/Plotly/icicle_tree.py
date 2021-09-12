# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 12:05:37 2021

@author: Edgar
"""

# Cómo importar las librerías
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *
from plotly.subplots import make_subplots
import textwrap

#Usar 20 para horizontal y 15 para vertical en width
def customwrap(s,width=15):
    if(type(s) == str):
        return "<br>".join(textwrap.wrap(s,width=width))
    return ""

init_notebook_mode()

# Importar el data set
dataset = pd.read_csv('processed_data.csv')

dataset["element"] = dataset["element"].map(customwrap)
dataset["parent"] = dataset["parent"].map(customwrap)

#Grafico
fig = make_subplots(1, 2, specs=[[{"type": "domain"}, {"type": "domain"}]],)

fig.add_trace(Icicle(
    labels=dataset['element'],
    parents=dataset['parent'],
    values=dataset['dummy_value'],
    branchvalues='total',
    text = ['Trade Value: {}'.format(int(value)) for value in dataset.iloc[:,2]],
    textinfo = 'label',
    marker=dict(
        colors=dataset['color'],
        colorscale='YlOrRd',
        showscale=True,
        colorbar=dict(
            title="Trade Value<br>max relative <br>to section",
            titlefont=dict(
                color="#000000",
                size=15,
                family="Roboto"
            ),
            bordercolor="#000000",
            tickfont=dict(family="Roboto",size=15),
        )
    ),
    hovertemplate='<b>%{label} </b> <br>%{text}<br>',
    name='',
    maxdepth=2,
    textfont=dict(
        size=20
    ),
    #Descomentar esta linea cuando se quiera usar en vertical
    tiling = dict(orientation='v')
))
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25), font_family="Roboto")
plot(fig)