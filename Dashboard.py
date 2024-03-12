import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide',)

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
           return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'



st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

## Criando os filtros
## filtro regiao
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''
## filtro ano
todos_anos = st.sidebar.checkbox('Dados de Todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)
## alocando os parametros para a API

query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
#formatação data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    

## Tabelas DE RECEITA
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

## TABELAS para -> Quantidade de vendas

# Construir um gráfico de mapa com a quantidade de vendas por estado.
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Construir um gráfico de linhas com a quantidade de vendas mensal.
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

# Construir um gráfico de barras com os 5 estados com maior quantidade de vendas.


# Construir um gráfico de barras com a quantidade de vendas por categoria de produto.
vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

## TABELAS ESTADOS 

estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].agg(['sum','count']))

## TABELAS VENDEDORES 
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))



## Gráficos

## GRAFICOS ABA 1


## FIGURA mapa para as receitas
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

## FIGURA para receita por estado
fig_receita_estados = px.bar(receita_estados.head(5),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top Estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

## FIGURA para receitas por categoria
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## FIGURA para receitas mensal

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y=(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

## GRAFICOS ABA 2 --------------------------------------------------


fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Vendas por Estado')

# Construir um gráfico de linhas com a quantidade de vendas mensal.
fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y=(0,vendas_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title= 'Quantidade de vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')


# Construir um gráfico de barras com os 5 estados com maior quantidade de vendas.
fig_qtde_vendas_estado_bar = px.bar(vendas_estados.head(5),
                                x = 'Local da compra',
                                y = 'Preço',
                                text_auto = True,
                                title = f'Top 5 estados (quantidade de vendas)')
fig_qtde_vendas_estado_bar.update_layout(yaxis_title = 'Vendas')

# Construir um gráfico de barras com a quantidade de vendas por categoria de produto.
fig_qtde_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por Categoria')
fig_qtde_categorias.update_layout(yaxis_title = 'Quantidade de vendas')


## Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
    
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtde_vendas_estado_bar, use_container_width=True)
        st.plotly_chart(fig_qtde_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores (1-10)', 1, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
            x = 'sum',
            y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)        

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
            x = 'count',
            y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
st.dataframe(dados)