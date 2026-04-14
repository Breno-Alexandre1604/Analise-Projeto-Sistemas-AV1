import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 1. MODELO DE DOMÍNIO E PERSISTÊNCIA (RNF02)
# ==========================================

class ColecaoDB:
    def __init__(self):
        self.conn = sqlite3.connect("colecao_cds.db", check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT, artista TEXT, tipo TEXT, ano INTEGER)''')
        self.conn.commit()

    def query(self, sql, params=()):
        return pd.read_sql_query(sql, self.conn, params=params)

db = ColecaoDB()

# ==========================================
# 2. LOGICA DE NEGOCIO (UML)
# ==========================================

class CD:
    def __init__(self, titulo, artista, tipo, ano):
        self.titulo = titulo
        self.artista = artista
        self.tipo = tipo
        self.ano = ano

    def salvar(self):
        c = db.conn.cursor()
        c.execute("INSERT INTO cds (titulo, artista, tipo, ano) VALUES (?,?,?,?)",
                 (self.titulo, self.artista, self.tipo, self.ano))
        db.conn.commit()

# ==========================================
# 3. INTERFACE (STREAMLIT - Estilo Palm-top)
# ==========================================

def main():
    st.set_page_config(page_title="CD Collection", page_icon="💿", layout="centered")
    
    st.title("💿 Minha Coleção de CDs")
    st.caption("Organização digital para Palm-top")

    tab_lista, tab_novo = st.tabs(["🔍 Ver Coleção", "➕ Novo CD"])

    with tab_novo:
        st.subheader("Cadastrar Álbum (RF01)")
        with st.form("form_cd", clear_on_submit=True):
            titulo = st.text_input("Título do CD")
            artista = st.text_input("Artista / Banda")
            col1, col2 = st.columns(2)
            tipo = col1.selectbox("Categoria", ["Cantor Solo", "Conjunto/Banda"])
            ano = col2.number_input("Ano de Lançamento", 1900, 2030, 2024)
            
            if st.form_submit_button("💾 Salvar na Memória", use_container_width=True):
                if titulo and artista:
                    novo_cd = CD(titulo, artista, tipo, ano)
                    novo_cd.salvar()
                    st.success("CD catalogado!")
                    st.rerun()
                else:
                    st.error("Campos Título e Artista são obrigatórios.")

    with tab_lista:
        # RF04: Busca em tempo real
        busca = st.text_input("Pesquisar na coleção...", placeholder="Digite título ou artista")
        
        # RF03: Ordem Alfabética via SQL
        sql = "SELECT * FROM cds WHERE titulo LIKE ? OR artista LIKE ? ORDER BY titulo ASC"
        termo = f"%{busca}%"
        df = db.query(sql, (termo, termo))

        if df.empty:
            st.info("Nenhum item encontrado na sua coleção.")
        else:
            for _, row in df.iterrows():
                # RNF01: Layout em cards para fácil visualização mobile
                with st.expander(f"📀 {row['titulo']} — {row['artista']}"):
                    st.write(f"**Ano:** {row['ano']}")
                    st.write(f"**Tipo:** {row['tipo']}")
                    
                    if st.button("🗑️ Remover", key=row['id'], type="secondary"):
                        c = db.conn.cursor()
                        c.execute("DELETE FROM cds WHERE id = ?", (int(row['id']),))
                        db.conn.commit()
                        st.toast(f"'{row['titulo']}' removido.")
                        st.rerun()

if __name__ == "__main__":
    main()
