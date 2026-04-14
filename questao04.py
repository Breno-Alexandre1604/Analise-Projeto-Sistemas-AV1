import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date

# ==========================================
# 1. MODELO DE DOMÍNIO E PERSISTÊNCIA (RNF01)
# ==========================================

class DBManager:
    """Gerencia a persistência no SQLite (RNF03)."""
    def __init__(self):
        self.conn = sqlite3.connect("remedios.db", check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS prescricao (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, paciente TEXT, 
                        remedio TEXT, dosagem TEXT, data_inicio DATE, 
                        dias INTEGER, vezes_dia INTEGER, data_fim DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dose (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, prescricao_id INTEGER,
                        data_dose DATE, hora_esperada TEXT, hora_real TEXT, 
                        status TEXT, FOREIGN KEY(prescricao_id) REFERENCES prescricao(id))''')
        self.conn.commit()

    def executar(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        self.conn.commit()
        return c

# ==========================================
# 2. LÓGICA DE NEGÓCIO (RF01 a RF08)
# ==========================================

db = DBManager()

def gerar_grade_horarios(p_id, data_ini, hora_ini, dias, vezes):
    """RF02, RF03 e RF05: Gera todas as doses do tratamento."""
    intervalo = 24 / vezes
    data_atual = data_ini
    primeira_dose_dt = datetime.combine(data_ini, hora_ini)

    for d in range(dias):
        for v in range(vezes):
            hora_dose = primeira_dose_dt + timedelta(hours=v * intervalo)
            # Apenas doses daquele dia de iteração
            data_dose_efetiva = data_atual + timedelta(days=d)
            db.executar("INSERT INTO dose (prescricao_id, data_dose, hora_esperada, status) VALUES (?,?,?,?)",
                       (p_id, data_dose_efetiva, hora_dose.strftime("%H:%M"), "PENDENTE"))

def registrar_e_reorganizar(dose_id, p_id, data_dose, hora_esp):
    """RF07 e RF08: Registra dose e recalcula atrasos."""
    agora = datetime.now()
    hora_real = agora.strftime("%H:%M")
    
    # Cálculo de atraso
    h_esp = datetime.strptime(hora_esp, "%H:%M")
    atraso_minutos = (agora.hour * 60 + agora.minute) - (h_esp.hour * 60 + h_esp.minute)
    
    status = "TOMADA" if atraso_minutos <= 15 else "ATRASADA"
    db.executar("UPDATE dose SET hora_real = ?, status = ? WHERE id = ?", (hora_real, status, dose_id))

    if atraso_minutos > 15:
        # Reorganiza doses futuras do MESMO DIA (RF08)
        doses_futuras = db.executar("SELECT id, hora_esperada FROM dose WHERE prescricao_id = ? AND data_dose = ? AND status = 'PENDENTE' AND id > ?", 
                                   (p_id, data_dose, dose_id)).fetchall()
        for df_id, df_hora in doses_futuras:
            nova_hora = (datetime.strptime(df_hora, "%H:%M") + timedelta(minutes=atraso_minutos)).strftime("%H:%M")
            db.executar("UPDATE dose SET hora_esperada = ? WHERE id = ?", (nova_hora, df_id))

# ==========================================
# 3. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Controle de Remédios", page_icon="💊")
    
    menu = st.sidebar.selectbox("Ir para:", ["Agenda de Hoje", "Nova Prescrição", "Histórico Completo"])

    if menu == "Nova Prescrição":
        st.header("📋 Nova Prescrição (RF01)")
        with st.form("cad_remedio"):
            paciente = st.text_input("Nome do Paciente")
            remedio = st.text_input("Nome do Remédio")
            col1, col2 = st.columns(2)
            dose = col1.text_input("Dosagem (ex: 500mg)")
            dias = col2.number_input("Dias de Tratamento", min_value=1)
            vezes = st.slider("Vezes ao dia", 1, 12, 3)
            
            data_ini = st.date_input("Data de Início")
            hora_ini = st.time_input("Horário da 1ª Dose (RF03)")
            
            if st.form_submit_button("Gerar Plano de Saúde"):
                data_fim = data_ini + timedelta(days=dias-1)
                res = db.executar("INSERT INTO prescricao (paciente, remedio, dosagem, data_inicio, dias, vezes_dia, data_fim) VALUES (?,?,?,?,?,?,?)",
                                 (paciente, remedio, dose, data_ini, dias, vezes, data_fim))
                gerar_grade_horarios(res.lastrowid, data_ini, hora_ini, dias, vezes)
                st.success(f"Tratamento gerado! Término em: {data_fim.strftime('%d/%m/%Y')}")

    elif menu == "Agenda de Hoje":
        st.header("📅 Agenda do Dia (RF06)")
        hoje = date.today().isoformat()
        dados = db.executar('''SELECT d.id, p.remedio, d.hora_esperada, d.status, d.prescricao_id, d.data_dose 
                               FROM dose d JOIN prescricao p ON d.prescricao_id = p.id 
                               WHERE d.data_dose = ? ORDER BY d.hora_esperada''', (hoje,)).fetchall()
        
        for id_d, nome_r, h_esp, status, p_id, d_dose in dados:
            with st.expander(f"{h_esp} - {nome_r} [{status}]"):
                if status == "PENDENTE":
                    if st.button(f"Confirmar Dose: {nome_r}", key=id_d):
                        registrar_e_reorganizar(id_d, p_id, d_dose, h_esp)
                        st.rerun()
                else:
                    st.write(f"Status: {status}")

    elif menu == "Histórico Completo":
        st.header("📊 Planilha de Horários (RF05)")
        df = pd.read_sql_query("SELECT p.paciente, p.remedio, d.data_dose, d.hora_esperada, d.status FROM dose d JOIN prescricao p ON d.prescricao_id = p.id", db.conn)
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
