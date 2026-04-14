import streamlit as st
import pandas as pd

# ==========================================
# 1. MODELO DE DOMÍNIO (UML)
# ==========================================

class Produto:
    def __init__(self, nome, unidade, preco):
        self.nome = nome
        self.unidadeMedida = unidade
        self.precoEstimado = preco

class ItemCompra:
    """Representa a linha da planilha (Atributo Derivado de Produto)"""
    def __init__(self, produto, qtd_prev, qtd_efet):
        self.produto = produto
        self.qtdPrevista = qtd_prev
        self.qtdEfetiva = qtd_efet
        self.subtotal = self.calcularSubtotal()

    def calcularSubtotal(self):
        return self.qtdEfetiva * self.produto.precoEstimado

# ==========================================
# 2. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Lista de Compras - Carolina", page_icon="🛒", layout="wide")
    st.title("🛒 Planejamento de Compras Mensal")

    if 'lista_compras' not in st.session_state:
        # Dados iniciais baseados no exemplo da Carolina
        st.session_state['lista_compras'] = pd.DataFrame([
            {"Produto": "Arroz", "Unid": "Kg", "Qtd Mês": 8.0, "Qtd Compra": 7.0, "Preço Est.": 1.80},
            {"Produto": "Feijão", "Unid": "Kg", "Qtd Mês": 6.0, "Qtd Compra": 6.0, "Preço Est.": 2.10},
            {"Produto": "Açúcar", "Unid": "Kg", "Qtd Mês": 3.0, "Qtd Compra": 2.0, "Preço Est.": 1.05},
        ])

    st.subheader("Planilha de Controle (RF01, RF02, RF03)")
    
    # RNF02: Data Editor para eficiência igual ao Excel
    df_editado = st.data_editor(
        st.session_state['lista_compras'],
        num_rows="dynamic",
        column_config={
            "Produto": st.column_config.TextColumn("Nome do Produto", required=True),
            "Unid": st.column_config.SelectboxColumn("Unid. Medida", options=["Kg", "Litro", "Unid", "Caixa", "Pacote"]),
            "Qtd Mês": st.column_config.NumberColumn("Previsto (Mês)", min_value=0.0),
            "Qtd Compra": st.column_config.NumberColumn("Efetivo (Compra)", min_value=0.0),
            "Preço Est.": st.column_config.NumberColumn("Preço Estimado (R$)", format="%.2f", min_value=0.0)
        },
        use_container_width=True
    )
    st.session_state['lista_compras'] = df_editado

    if not df_editado.empty:
        st.divider()
        st.subheader("Análise Financeira (RF04)")
        
        # Lógica de cálculo (Simulando os métodos da classe UML)
        df_calculado = df_editado.copy()
        df_calculado['Subtotal'] = df_calculado['Qtd Compra'] * df_calculado['Preço Est.']
        
        # Exibição dos resultados
        st.dataframe(df_calculado, use_container_width=True, hide_index=True)
        
        total_geral = df_calculado['Subtotal'].sum()
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Gasto Total Estimado", f"R$ {total_geral:.2f}")
        with c2:
            itens_acima = df_calculado[df_calculado['Qtd Compra'] > df_calculado['Qtd Mês']].shape[0]
            st.warning(f"Itens com compra acima do previsto: {itens_acima}") if itens_acima > 0 else st.success("Compra dentro do planejamento mensal!")

if __name__ == "__main__":
    main()
