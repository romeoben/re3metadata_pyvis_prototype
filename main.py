import warnings
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import pyvis
from pyvis.network import Network
from ast import literal_eval

from PIL import Image

st.set_page_config(page_title='re3data.org metadata', layout="wide")
warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)

repo_node_list = pd.read_csv("data/repo_node_list.csv")

ins_node_list = pd.read_csv("data/ins_node_list.csv")

repo_edge_list = pd.read_csv("data/repo_edge_list.csv")
repo_edge_list.edge = repo_edge_list.edge.apply(literal_eval)

ins_edge_list = pd.read_csv("data/ins_edge_list.csv")
ins_edge_list.edge = ins_edge_list.edge.apply(literal_eval)


layers = [
    "Knowledge",
    "Organization"
]

layers = {
    "Knowledge" : {
        'nodes' : repo_node_list,
        'edges' : repo_edge_list
    },
    "Organization" : {
        'nodes' : ins_node_list,
        'edges' : ins_edge_list
    }
}

st.sidebar.markdown('# re3data.org metadata')
st.sidebar.markdown('### Select layers to visualize:')
selected_layers = [
        layer for layer_name, layer in layers.items()
        if st.sidebar.checkbox(layer_name, True)]

if len(selected_layers) == 0:
    st.markdown('Select layers to visualize.')
else:
    #st.write(layers['Knowledge']['nodes'])
    #st.write(selected_layers)
    node_list = pd.concat([layer['nodes'] for layer in selected_layers], ignore_index=True)
    node_list.drop_duplicates(inplace=True, ignore_index=True)
    node_list['group'] = pd.Categorical(node_list['title']).codes
    edge_list = pd.concat([layer['edges'] for layer in selected_layers], ignore_index=True)

    G = nx.DiGraph()
    
    G.add_nodes_from(node_list['id'])
    nx.set_node_attributes(G, node_list.set_index('id').to_dict('index'))

    G.add_edges_from(edge_list['edge'])
    nx.set_edge_attributes(G, edge_list.set_index('edge').to_dict('index'))

    # Initiate PyVis network object
    N = Network(height='600px',width='100%',
            directed=True,
            bgcolor='#222222', font_color='white')
    N.from_nx(G)
    
    N.set_options("""
    var options = {
    "edges": {
    "color": {
      "color": "rgba(191,193,171,1)",
      "highlight": "rgba(248, 112, 2, 0.8)",
      "inherit": false
    },
    "smooth": false
    },
    "physics": {
    "forceAtlas2Based": {
      "springLength": 200
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
    }
    }
    """)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = './tmp'
        N.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = './html_files'
        N.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=600)
    