import streamlit as st
from datetime import date

# ==========================================
# 1. MODELO DE DOMÍNIO (Superclasse e Herança)
# ==========================================

class Pessoa:
    """Superclasse que contém os atributos comuns (RNF01)."""
    def __init__(self, nome, data_nasc, endereco, telefones):
        self.nome = nome
        self.data_nasc = data_nasc
        self.endereco = endereco
        self.telefones = telefones

    def obterIdade(self) -> int:
        """RF02: Método comum a todas as subclasses."""
        hoje = date.today()
        return hoje.year - self.data_nasc.year - ((hoje.month, hoje.day) < (self.data_nasc.month, self.data_nasc.day))

class Funcionario(Pessoa):
    """Subclasse com atributos específicos de trabalho (RF01/RF03)."""
    def __init__(self, nome, data_nasc, endereco, telefones, matricula, salario, admissao, cargo):
        super().__init__(nome, data_nasc, endereco, telefones)
        self.matricula = matricula
        self.salario = salario
        self.admissao = admissao
        self.cargo = cargo

    def reajustarSalario(self, percentual):
        """RF04: Ação específica de funcionário."""
        self.salario *= (1 + percentual / 100)

class Cliente(Pessoa):
    """Subclasse com atributos específicos de consumo (RF01/RF06)."""
    def __init__(self, nome, data_nasc, endereco, telefones, codigo, limite, profissao):
        super().__init__(nome, data_nasc, endereco, telefones)
        self.codigo = codigo
        self.limite = limite
        self.profissao = profissao

# ==========================================
# 2. INTERFACE (STREAMLIT)
# ==========================================

def main():
    st.set_page_config(page_title="Gestão de Pessoas", layout="wide", page_icon="👥")
    st.title("👥 Gestão de Pessoas (Herança)")

    if 'db_pessoas' not in st.session_state:
        st.session_state['db_pessoas'] = []

    tab_cad, tab_list = st.tabs(["➕ Cadastrar", "📋 Visualizar Acervo"])

    with tab_cad:
        tipo = st.radio("Tipo de Cadastro:", ["Funcionário", "Cliente"])
        
        with st.form("form_pessoa", clear_on_submit=True):
            st.subheader("Dados Pessoais (Superclasse)")
            nome = st.text_input("Nome Completo")
            dnasc = st.date_input("Data de Nascimento", date(1990, 1, 1))
            
            st.divider()
            if tipo == "Funcionário":
                st.subheader("Dados Funcionais")
                mat = st.number_input("Matrícula", min_value=1)
                sal = st.number_input("Salário Base", min_value=0.0)
                cargo = st.selectbox("Cargo", ["Dev", "Analista", "Gerente"])
                adm = st.date_input("Admissão")
                
                if st.form_submit_button("💾 Salvar Funcionário"):
                    obj = Funcionario(nome, dnasc, "Rua A", ["(11) 999"], mat, sal, adm, cargo)
                    st.session_state['db_pessoas'].append(obj)
                    st.success("Funcionário cadastrado!")
            else:
                st.subheader("Dados de Cliente")
                cod = st.text_input("Código")
                lim = st.number_input("Limite de Crédito", min_value=0.0)
                prof = st.text_input("Profissão")
                
                if st.form_submit_button("💾 Salvar Cliente"):
                    obj = Cliente(nome, dnasc, "Rua B", ["(11) 888"], cod, lim, prof)
                    st.session_state['db_pessoas'].append(obj)
                    st.success("Cliente cadastrado!")

    with tab_list:
        if not st.session_state['db_pessoas']:
            st.info("Nenhum registro no sistema.")
        else:
            for p in st.session_state['db_pessoas']:
                tipo_p = "Funcionário" if isinstance(p, Funcionario) else "Cliente"
                with st.expander(f"{p.nome} ({tipo_p})"):
                    st.write(f"**Idade (RF02):** {p.obterIdade()} anos")
                    if isinstance(p, Funcionario):
                        st.write(f"Salário: R$ {p.salario:.2f} | Cargo: {p.cargo}")
                        if st.button(f"Reajuste 10% ({p.nome})"):
                            p.reajustarSalario(10)
                            st.rerun()
                    else:
                        st.write(f"Limite: R$ {p.limite:.2f} | Profissão: {p.profissao}")

if __name__ == "__main__":
    main()
