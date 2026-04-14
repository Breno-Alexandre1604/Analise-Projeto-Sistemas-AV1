import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 1. MODELO DE DOMÍNIO E BANCO (RNF01)
# ==========================================

class DBPadaria:
    def __init__(self):
        self.conn = sqlite3.connect("padaria.db", check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS produto (id INTEGER PRIMARY KEY, desc TEXT, preco REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS item_comanda (id INTEGER PRIMARY KEY AUTOINCREMENT, num_comanda INTEGER, prod_id INTEGER, qtd INTEGER, subtotal REAL)")
        
        # Carga inicial de produtos (RF01)
        c.execute("SELECT COUNT(*) FROM produto")
        if c.fetchone()[0] == 0:
            produtos = [(1, 'Pão de Sal', 0.50), (2, 'Café Expresso', 5.00), (3, 'Misto Quente', 12.00), (4, 'Suco Laranja', 8.00)]
            c.executemany("INSERT INTO produto VALUES (?,?,?)", produtos)
        self.conn.commit()

db = DBPadaria()

class Comanda:
    def __init__(self, numero):
        self.numero = numero

    def registrarConsumo(self, prod_id, preco, qtd):
        # RF03 e RF05: Registro com cálculo de subtotal
        subtotal = preco * qtd
        c = db.conn.cursor()
        c.execute("INSERT INTO item_comanda (num_comanda, prod_id, qtd, subtotal) VALUES (?,?,?,?)",
                 (self.numero, prod_id, qtd, subtotal))
        db.conn.commit()

    def calcularValorTotal(self):
        # RF06: Soma de todos os subtotais
        c = db.conn.cursor()
        c.execute("SELECT SUM(subtotal) FROM item_comanda WHERE num_comanda = ?", (self.numero,))
        res = c.fetchone()[0]
        return res if res else 0.0

    def finalizarCompra(self):
        # RF07: Limpeza da comanda
        c = db.conn.cursor()
        c.execute("DELETE FROM item_comanda WHERE num_comanda = ?", (self.numero,))
        db.conn.commit()

# ==========================================
# 2. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Doce Sabor - PDV", page_icon="🥐")
    
    st.sidebar.title("🏪 Padaria Doce Sabor")
    modulo = st.sidebar.radio("Navegação:", ["Atendente (Lançar)", "Caixa (Fechar)"])

    if modulo == "Atendente (Lançar)":
        st.header("📋 Lançamento de Itens (RF03)")
        num_c = st.number_input("Nº da Comanda", min_value=1, step=1)
        comanda = Comanda(num_c)

        st.divider()
        # Busca produtos do banco para o select
        prods = pd.read_sql_query("SELECT * FROM produto", db.conn)
        prod_sel = st.selectbox("Selecione o Produto", prods['desc'].tolist())
        qtd = st.number_input("Quantidade", min_value=1, value=1)
        
        if st.button("➕ Lançar na Comanda", type="primary"):
            p_data = prods[prods['desc'] == prod_sel].iloc[0]
            comanda.registrarConsumo(p_data['id'], p_data['preco'], qtd)
            st.success(f"Item lançado na comanda {num_c}!")

    else:
        st.header("💰 Fechamento de Comanda (RF04)")
        num_c = st.number_input("Ler Comanda Nº", min_value=1, step=1)
        comanda = Comanda(num_c)

        # RF04: Busca itens da comanda no banco
        query = f"""SELECT p.desc as Produto, i.qtd as Qtd, p.preco as Unitario, i.subtotal as Subtotal 
                    FROM item_comanda i JOIN produto p ON i.prod_id = p.id 
                    WHERE i.num_comanda = {num_c}"""
        df_itens = pd.read_sql_query(query, db.conn)

        if df_itens.empty:
            st.info("Comanda sem itens lançados.")
        else:
            st.table(df_itens)
            total = comanda.calcularValorTotal()
            st.metric("Total a Pagar (RF06)", f"R$ {total:.2f}")

            if st.button("✅ Finalizar e Liberar Comanda", type="primary"):
                comanda.finalizarCompra()
                st.success("Venda finalizada com sucesso!")
                st.rerun()

if __name__ == "__main__":
    main()
