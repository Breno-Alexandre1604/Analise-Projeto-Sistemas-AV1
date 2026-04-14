import streamlit as st
import pandas as pd
from datetime import date

# ==========================================
# 1. MODELO DE DOMÍNIO (UML)
# ==========================================
class ContaLuz:
    """Representa a entidade básica de uma conta de energia."""
    def __init__(self, dataLeitura: date, numLeitura: int, kwGasto: float, 
                 valorPagar: float, dataPagamento: date, mediaConsumo: float):
        # RNF04: Atributos tipados rigorosamente para garantir integridade
        self.dataLeitura = dataLeitura
        self.numLeitura = numLeitura
        self.kwGasto = kwGasto
        self.valorPagar = valorPagar
        self.dataPagamento = dataPagamento
        self.mediaConsumo = mediaConsumo

class GerenciadorConsumo:
    """Lógica de negócio e persistência em memória de sessão."""
    def __init__(self):
        # RNF05: Uso de Session State para privacidade e persistência local
        if 'listaContas' not in st.session_state:
            st.session_state['listaContas'] = []
        self.listaContas = st.session_state['listaContas']

    def adicionarConta(self, conta: ContaLuz):
        """RF01: Adiciona conta após validar integridade (RNF03)."""
        if conta.kwGasto >= 0 and conta.valorPagar >= 0:
            self.listaContas.append(conta)
            return True
        return False

    def verificarMenorConsumo(self):
        """RF03: Identifica o objeto com menor consumo."""
        if not self.listaContas: return None
        return min(self.listaContas, key=lambda c: c.kwGasto)

    def verificarMaiorConsumo(self):
        """RF04: Identifica o objeto com maior consumo."""
        if not self.listaContas: return None
        return max(self.listaContas, key=lambda c: c.kwGasto)

# ==========================================
# 2. INTERFACE DO USUÁRIO (Streamlit)
# ==========================================
def main():
    st.set_page_config(page_title="APS - Questão 01", page_icon="⚡")
    st.title("⚡ Gestão de Consumo de Energia")
    
    gerenciador = GerenciadorConsumo()

    # --- ÁREA DE CADASTRO (RF01) ---
    with st.sidebar:
        st.header("Entrada de Dados")
        with st.form("form_luz", clear_on_submit=True):
            d_leitura = st.date_input("Data da Leitura")
            n_leitura = st.number_input("Número da Leitura", min_value=0, step=1)
            kw = st.number_input("Consumo (kW)", min_value=0.0, format="%.2f")
            valor = st.number_input("Valor a Pagar (R$)", min_value=0.0, format="%.2f")
            d_pago = st.date_input("Data do Pagamento")
            media = st.number_input("Média Histórica", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("💾 Salvar Registro"):
                nova_conta = ContaLuz(d_leitura, n_leitura, kw, valor, d_pago, media)
                if gerenciador.adicionarConta(nova_conta):
                    st.success("Registro salvo com sucesso!")
                else:
                    st.error("Dados inválidos detectados.")

    # --- ÁREA DE EXIBIÇÃO (RF02, RF03, RF04) ---
    if not gerenciador.listaContas:
        st.info("Utilize o menu lateral para cadastrar as contas de luz.")
    else:
        # RF02: Listagem em Tabela
        st.subheader("📋 Histórico Registrado")
        df = pd.DataFrame([vars(c) for c in gerenciador.listaContas])
        # Renomeando colunas para o usuário final
        df.columns = ["Data Leitura", "Nº Leitura", "kW Gasto", "Valor (R$)", "Data Pagamento", "Média"]
        st.dataframe(df, use_container_width=True)

        st.divider()

        # RF03 e RF04: Verificações de Extremos
        menor = gerenciador.verificarMenorConsumo()
        maior = gerenciador.verificarMaiorConsumo()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("⬇️ Menor Consumo (RF03)", f"{menor.kwGasto} kW", 
                      f"Mês: {menor.dataLeitura.strftime('%m/%y')}")
        with col2:
            st.metric("⬆️ Maior Consumo (RF04)", f"{maior.kwGasto} kW", 
                      f"Mês: {maior.dataLeitura.strftime('%m/%y')}", delta_color="inverse")

if __name__ == "__main__":
    main()
