import streamlit as st
import pandas as pd
from datetime import date
import io

# ==========================================
# 1. MODELO DE DOMÍNIO (UML)
# ==========================================

class Gasto:
    def __init__(self, tipo, data, valor, forma):
        self.tipoGasto = tipo
        self.data = data
        self.valor = valor
        self.formaPagamento = forma

class FechamentoMensal:
    """Classe responsável por agregar os dados (Atributos Derivados)."""
    def __init__(self, mes_ref, lista_gastos):
        self.mesReferencia = mes_ref
        self._listaGastos = lista_gastos # Atributo derivado da lista de gastos

    def calcularTotalMensal(self):
        return sum(g.valor for g in self._listaGastos)

    def agruparTipoGasto(self):
        # Transforma a lista de objetos em um resumo por tipo
        resumo = {}
        for g in self._listaGastos:
            resumo[g.tipoGasto] = resumo.get(g.tipoGasto, 0) + g.valor
        return resumo

# ==========================================
# 2. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Gastos da Vera", page_icon="💸", layout="wide")
    st.title("💸 Controle de Gastos Diários")

    # Inicialização do "Banco de Dados" em memória
    if 'gastos_raw' not in st.session_state:
        st.session_state['gastos_raw'] = pd.DataFrame(columns=["Data", "Tipo", "Valor", "Pagamento"])

    tab1, tab2 = st.tabs(["📝 Lançamentos", "📊 Fechamento Mensal"])

    with tab1:
        st.subheader("Entrada de Dados (Simulação Excel)")
        # RNF01: Uso do data_editor para máxima produtividade
        categorias = ["Remédio", "Roupa", "Refeição", "Transporte", "Lazer", "Outros"]
        pagamentos = ["Dinheiro", "Cartão Crédito", "Cartão Débito", "Ticket Alimentação", "Refeição"]
        
        df_editado = st.data_editor(
            st.session_state['gastos_raw'],
            num_rows="dynamic",
            column_config={
                "Data": st.column_config.DateColumn("Data", required=True),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=categorias, required=True),
                "Valor": st.column_config.NumberColumn("Valor (R$)", min_value=0, format="%.2f"),
                "Pagamento": st.column_config.SelectboxColumn("Forma de Pagto", options=pagamentos)
            },
            use_container_width=True
        )
        st.session_state['gastos_raw'] = df_editado

    with tab2:
        if df_editado.empty:
            st.warning("Nenhum dado para processar.")
        else:
            # Lógica para converter o DataFrame em Objetos da Classe UML
            lista_objetos = []
            for _, row in df_editado.iterrows():
                if pd.notnull(row['Valor']):
                    lista_objetos.append(Gasto(row['Tipo'], row['Data'], row['Valor'], row['Pagamento']))
            
            # Interface de Fechamento (RF04, RF05, RF06)
            st.subheader("Resumo Consolidado")
            
            # Criando o fechamento
            fechamento = FechamentoMensal("Mês Atual", lista_objetos)
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Gasto", f"R$ {fechamento.calcularTotalMensal():.2f}")
            
            st.divider()
            
            # Exibição de Tabelas Agrupadas
            resumo_tipo = df_editado.groupby("Tipo")["Valor"].sum().reset_index()
            resumo_pagto = df_editado.groupby("Pagamento")["Valor"].sum().reset_index()
            
            col_a, col_b = st.columns(2)
            col_a.write("**Total por Tipo (RF05)**")
            col_a.dataframe(resumo_tipo, hide_index=True, use_container_width=True)
            
            col_b.write("**Total por Pagamento (RF06)**")
            col_b.dataframe(resumo_pagto, hide_index=True, use_container_width=True)

            # RNF04: Portabilidade
            csv = df_editado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Exportar para Excel (CSV)", csv, "gastos_vera.csv", "text/csv")

if __name__ == "__main__":
    main()
