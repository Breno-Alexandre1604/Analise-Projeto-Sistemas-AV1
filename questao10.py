import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, time, timedelta

# ==========================================
# 1. MODELO DE DOMÍNIO E BANCO (RNF02)
# ==========================================
class DBReserva:
    def __init__(self):
        self.conn = sqlite3.connect("reservas_salas.db", check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS funcionario (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cargo TEXT, ramal TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS sala (id INTEGER PRIMARY KEY AUTOINCREMENT, numero TEXT UNIQUE, capacidade INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS reuniao (id INTEGER PRIMARY KEY AUTOINCREMENT, func_id INTEGER, sala_id INTEGER, data DATE, h_ini TEXT, h_fim TEXT, assunto TEXT)")
        
        # Carga inicial de salas para teste
        c.execute("SELECT COUNT(*) FROM sala")
        if c.fetchone()[0] == 0:
            c.executemany("INSERT INTO sala (numero, capacidade) VALUES (?,?)", [("101", 10), ("105", 8), ("201", 15)])
        self.conn.commit()

db = DBReserva()

# ==========================================
# 2. LÓGICA DE NEGÓCIO (RF03, RF04, RF05)
# ==========================================
class GestorReservas:
    @staticmethod
    def verificar_conflito(sala_id, data, h_ini, h_fim, ignore_id=None):
        """RNF01: Lógica de colisão de horários."""
        c = db.conn.cursor()
        query = "SELECT id FROM reuniao WHERE sala_id = ? AND data = ? AND ((h_ini < ? AND h_fim > ?) OR (h_ini < ? AND h_fim > ?))"
        params = [sala_id, data, h_fim, h_ini, h_fim, h_ini]
        if ignore_id:
            query += " AND id != ?"
            params.append(ignore_id)
        return c.execute(query, params).fetchone() is not None

# ==========================================
# 3. INTERFACE (STREAMLIT)
# ==========================================
def main():
    st.set_page_config(page_title="Reserva de Salas", layout="wide", page_icon="🏢")
    st.title("🏢 Sistema de Gestão de Salas (Patrícia)")

    menu = st.sidebar.radio("Navegação", ["Agenda Diária", "Novo Agendamento", "Salas Livres"])

    if menu == "Agenda Diária":
        st.header("📅 Visão Geral do Dia (RF06)")
        d_alvo = st.date_input("Data", date.today())
        
        # Busca salas e reuniões
        salas = pd.read_sql_query("SELECT numero FROM sala ORDER BY numero", db.conn)['numero'].tolist()
        df_r = pd.read_sql_query("SELECT r.*, s.numero as sala_num FROM reuniao r JOIN sala s ON r.sala_id = s.id WHERE data = ?", db.conn, params=(d_alvo,))
        
        if not salas:
            st.warning("Cadastre salas primeiro.")
        else:
            # Cria a grade de 30 em 30 min
            tempos = [(datetime.combine(date.today(), time(8, 0)) + timedelta(minutes=30*i)).strftime("%H:%M") for i in range(21)]
            grade = pd.DataFrame(index=tempos, columns=salas).fillna("")
            
            for _, r in df_r.iterrows():
                for t in tempos:
                    if r['h_ini'] <= t < r['h_fim']:
                        grade.at[t, r['sala_num']] = r['assunto']
            
            st.table(grade)

    elif menu == "Novo Agendamento":
        st.header("➕ Nova Alocação (RF03)")
        with st.form("form_reserva"):
            assunto = st.text_input("Assunto da Reunião")
            col1, col2 = st.columns(2)
            data = col1.date_input("Data", min_value=date.today())
            
            salas_df = pd.read_sql_query("SELECT id, numero FROM sala", db.conn)
            sala_map = dict(zip(salas_df['numero'], salas_df['id']))
            sala_sel = col2.selectbox("Sala", list(sala_map.keys()))
            
            h_in = col1.time_input("Início", value=time(9,0))
            h_out = col2.time_input("Término", value=time(10,0))
            
            if st.form_submit_button("💾 Confirmar Reserva"):
                if h_in >= h_out:
                    st.error("Horário inválido.")
                elif GestorReservas.verificar_conflito(sala_map[sala_sel], data, h_in.strftime("%H:%M"), h_out.strftime("%H:%M")):
                    st.error("⚠️ Conflito: Esta sala já está ocupada neste horário!")
                else:
                    db.conn.cursor().execute("INSERT INTO reuniao (sala_id, data, h_ini, h_fim, assunto) VALUES (?,?,?,?,?)",
                                           (sala_map[sala_sel], data, h_in.strftime("%H:%M"), h_out.strftime("%H:%M"), assunto))
                    db.conn.commit()
                    st.success("Reserva realizada!")

    elif menu == "Salas Livres":
        st.header("🔍 Consultar Salas Livres (RF05)")
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Data")
        hi = c2.time_input("Das", value=time(14,0))
        hf = c3.time_input("Até", value=time(15,0))
        
        if st.button("Buscar Disponibilidade"):
            query = """SELECT numero, capacidade FROM sala WHERE id NOT IN 
                       (SELECT sala_id FROM reuniao WHERE data = ? AND ((h_ini < ? AND h_fim > ?) OR (h_ini < ? AND h_fim > ?)))"""
            livres = pd.read_sql_query(query, db.conn, params=(d, hf.strftime("%H:%M"), hi.strftime("%H:%M"), hf.strftime("%H:%M"), hi.strftime("%H:%M")))
            st.dataframe(livres, use_container_width=True)

if __name__ == "__main__":
    main()
