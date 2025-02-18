import streamlit as st
import pandas as pd
import uuid
import base64
import os

# Verificar se os arquivos Excel existem antes de carregá-los
file_path_pratos = "custos.xlsx"
file_path_insumos = "insumos.xlsx"

df_pratos = pd.DataFrame()
df_insumos = pd.DataFrame()

if os.path.exists(file_path_pratos):
    df_pratos = pd.read_excel(file_path_pratos, engine="openpyxl")
else:
    st.error("Arquivo 'custos.xlsx' não encontrado. Verifique o upload no GitHub.")

if os.path.exists(file_path_insumos):
    df_insumos = pd.read_excel(file_path_insumos, engine="openpyxl")
else:
    st.error("Arquivo 'insumos.xlsx' não encontrado. Verifique o upload no GitHub.")

# Criar um dicionário para armazenar os pratos e preps salvos
if "pratos_salvos" not in st.session_state:
    st.session_state.pratos_salvos = []
if "preps_salvos" not in st.session_state:
    st.session_state.preps_salvos = []
if "ingredientes_utilizados" not in st.session_state:
    st.session_state.ingredientes_utilizados = []
if "insumos_utilizados" not in st.session_state:
    st.session_state.insumos_utilizados = []

st.title("Simulador de Custo")

# Escolher modo de operação
modo = st.radio("Escolha uma opção:", ["Simular Prato Novo", "Criar Novo Prep"])

if modo == "Simular Prato Novo" and not df_pratos.empty:
    st.header("Simulação de Prato Novo")
    nome_prato = st.text_input("Nome do Prato")
    st.subheader("Adicionar Ingredientes")
    preps_disponiveis = df_pratos["Prep"].unique().tolist() + [prep["Nome"] for prep in st.session_state.preps_salvos]
    ingrediente = st.selectbox("Escolha um ingrediente", options=preps_disponiveis)
    quantidade_usada = st.number_input("Quantidade utilizada", min_value=0.0, step=0.1)
    
    if st.button("Adicionar Ingrediente") and ingrediente:
        if ingrediente in df_pratos["Prep"].values:
            unidade_medida = df_pratos.loc[df_pratos["Prep"] == ingrediente, "UM"].values[0]
            custo_unitario = df_pratos.loc[df_pratos["Prep"] == ingrediente, "Custo"].values[0]
        else:
            unidade_medida = next(prep["Unidade"] for prep in st.session_state.preps_salvos if prep["Nome"] == ingrediente)
            custo_unitario = next(prep["Custo Total"] for prep in st.session_state.preps_salvos if prep["Nome"] == ingrediente)
        
        st.session_state.ingredientes_utilizados.append((ingrediente, quantidade_usada, unidade_medida, custo_unitario))
    
    st.subheader("Ingredientes Selecionados")
    for ing in st.session_state.ingredientes_utilizados:
        st.write(f"{ing[0]} - {ing[1]} {ing[2]} - Custo Unitário: R$ {ing[3]:.2f}")
    
    custo_total = sum(qtd * custo for ing, qtd, um, custo in st.session_state.ingredientes_utilizados)
    st.subheader("Resumo do Cálculo")
    st.write(f"Custo Total do Prato: R$ {custo_total:.2f}")
    
    if st.button("Salvar Prato") and nome_prato:
        prato_id = str(uuid.uuid4())[:8]
        prato = {
            "ID": prato_id,
            "Nome": nome_prato,
            "Ingredientes": str(st.session_state.ingredientes_utilizados),
            "Custo Total": custo_total
        }
        st.session_state.pratos_salvos.append(prato)
        st.session_state.ingredientes_utilizados = []
        st.success(f"Prato '{nome_prato}' salvo com sucesso! ID: {prato_id}")

elif modo == "Criar Novo Prep" and not df_insumos.empty:
    st.header("Criação de Novo Prep")
    nome_prep = st.text_input("Nome do Prep")
    unidade_prep = st.selectbox("Unidade de Medida do Prep", ["KG", "L", "UN"])
    st.subheader("Adicionar Insumos")
    insumo = st.selectbox("Escolha um insumo", options=df_insumos["Insumo"].unique())
    quantidade_usada = st.number_input("Quantidade utilizada", min_value=0.0, step=0.1)
    
    if st.button("Adicionar Insumo") and insumo:
        unidade_medida = df_insumos.loc[df_insumos["Insumo"] == insumo, "UM"].values[0]
        custo_unitario = df_insumos.loc[df_insumos["Insumo"] == insumo, "Custo"].values[0]
        st.session_state.insumos_utilizados.append((insumo, quantidade_usada, unidade_medida, custo_unitario))
    
    rendimento_total = st.number_input("Rendimento total do Prep", min_value=0.01, step=0.1)
    
    st.subheader("Resumo do Cálculo")
    custo_total = sum(qtd * custo for ins, qtd, um, custo in st.session_state.insumos_utilizados)
    st.write(f"Custo Total do Prep: R$ {custo_total:.2f}")
    
    if st.button("Salvar Prep") and nome_prep:
        prep_id = str(uuid.uuid4())[:8]
        prep = {
            "ID": prep_id,
            "Nome": nome_prep,
            "Unidade": unidade_prep,
            "Rendimento": rendimento_total,
            "Insumos": str(st.session_state.insumos_utilizados),
            "Custo Total": custo_total
        }
        st.session_state.preps_salvos.append(prep)
        st.session_state.insumos_utilizados = []
        st.success(f"Prep '{nome_prep}' salvo com sucesso! ID: {prep_id}")
