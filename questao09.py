import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 1. MODELO DE DOMÍNIO E PERSISTÊNCIA (RNF01)
# ==========================================

class Musica:
    def __init__(self, titulo, duracao):
        self.titulo = titulo
        self.duracao = duracao

class CD:
    def __init__(self, titulo, ano, is_coletanea, is_duplo):
        self.titulo = titulo
        self.ano = ano
        self.is_coletanea = is_coletanea
        self.is_duplo = is_duplo
        self.artistas = []  # Relacionamento derivado (N:N)
        self.faixas = []    # Relacionamento derivado (1:N)

class AcervoDB:
    def __init__(self):
        self.conn = sqlite3.connect("acervo_musical_v2.db", check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS artista (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS cd (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, ano INTEGER, is_col BOOLEAN, is_dup BOOLEAN)")
        c.execute("CREATE TABLE IF NOT EXISTS cd_artista (cd_id INTEGER, art_id INTEGER, FOREIGN KEY(cd_id) REFERENCES cd(id) ON DELETE CASCADE, FOREIGN KEY(art_id) REFERENCES artista(id) ON DELETE CASCADE)")
        c.execute("CREATE TABLE IF NOT EXISTS musica (id INTEGER PRIMARY KEY AUTOINCREMENT, cd_id INTEGER, titulo TEXT, duracao TEXT, FOREIGN KEY(cd_id) REFERENCES cd(id) ON DELETE CASCADE)")
        self.conn.commit()

db = AcervoDB()

# ==========================================
# 2. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Acervo V2", layout="wide", page_icon="🎧")
    st.title("🎧 Gerenciador de Acervo Musical (V2)")

    menu = st.sidebar.selectbox("Módulo:", ["Cadastrar CD", "Relatórios de Busca"])

    if menu == "Cadastrar CD":
        st.header("💿 Novo Cadastro (CD + Faixas)")
        
        with st.form("form_cd"):
            col1, col2 = st.columns(2)
            titulo = col1.text_input("Título do Álbum")
            ano = col2.number_input("Ano", 1900, 2030, 2024)
            
            c1, c2 = st.columns(2)
            is_col = c1.checkbox("É Coletânea (Vários Artistas)")
            is_dup = c2.checkbox("É CD Duplo")
            
            st.divider()
            st.subheader("Artistas (RF01)")
            art_input = st.text_area("Nomes dos Artistas (um por linha)").split('\n')
            
            st.subheader("Músicas e Durações (RF03)")
            st.caption("Formato: Nome da Música;Duração (Ex: Thriller;05:57)")
            mus_input = st.text_area("Músicas (Ex: Título;00:00 - Uma por linha)")

            if st.form_submit_button("💾 Salvar CD Completo"):
                if titulo and art_input and mus_input:
                    c = db.conn.cursor()
                    c.execute("INSERT INTO cd (titulo, ano, is_col, is_dup) VALUES (?,?,?,?)", (titulo, ano, is_col, is_dup))
                    cd_id = c.lastrowid
                    
                    for nome in art_input:
                        if nome.strip():
                            c.execute("INSERT OR IGNORE INTO artista (nome) VALUES (?)", (nome.strip(),))
                            c.execute("SELECT id FROM artista WHERE nome = ?", (nome.strip(),))
                            art_id = c.fetchone()[0]
                            c.execute("INSERT INTO cd_artista VALUES (?,?)", (cd_id, art_id))
                    
                    for m in mus_input:
                        if ";" in m:
                            m_nome, m_dur = m.split(";")
                            c.execute("INSERT INTO musica (cd_id, titulo, duracao) VALUES (?,?,?)", (cd_id, m_nome.strip(), m_dur.strip()))
                    
                    db.conn.commit()
                    st.success("CD e faixas integrados ao acervo!")

    else:
        st.header("🔍 Consultas ao Acervo (RF04/RF05)")
        busca = st.text_input("Pesquisar artista ou música")
        if busca:
            # Relatório: CDs que contêm o Artista ou a Música
            query = f"""
                SELECT DISTINCT c.titulo, c.ano, c.is_col as Coletanea 
                FROM cd c 
                LEFT JOIN cd_artista ca ON c.id = ca.cd_id 
                LEFT JOIN artista a ON ca.art_id = a.id
                LEFT JOIN musica m ON c.id = m.cd_id
                WHERE a.nome LIKE '%{busca}%' OR m.titulo LIKE '%{busca}%'
            """
            df = pd.read_sql_query(query, db.conn)
            st.table(df)

if __name__ == "__main__":
    main()
