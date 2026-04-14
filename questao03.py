import streamlit as st
import plotly.graph_objects as go
from enum import Enum

# ==========================================
# 1. MODELO DE DOMÍNIO (UML)
# ==========================================

class EnumDirecao(Enum):
    CIMA = "Cima"
    BAIXO = "Baixo"
    DIREITA = "Direita"
    ESQUERDA = "Esquerda"
    PARADO = "Parado"

class Boneco:
    """Representa o boneco e suas regras de movimento (RNF01 e RNF02)."""
    LIMITE_MIN = 0.0
    LIMITE_MAX = 10.0
    PASSO = 1.0

    def __init__(self, nome: str, posX: float, posY: float):
        self._nome = nome
        self._posicaoX = posX
        self._posicaoY = posY
        self._direcaoAtual = EnumDirecao.PARADO

    def mover(self, direcao: EnumDirecao) -> bool:
        """RF02 e RF03: Altera a posição baseada na direção e limites."""
        novo_x, novo_y = self._posicaoX, self._posicaoY

        if direcao == EnumDirecao.CIMA: novo_y += self.PASSO
        elif direcao == EnumDirecao.BAIXO: novo_y -= self.PASSO
        elif direcao == EnumDirecao.DIREITA: novo_x += self.PASSO
        elif direcao == EnumDirecao.ESQUERDA: novo_x -= self.PASSO

        # RNF01: Validação de fronteira
        if self.LIMITE_MIN <= novo_x <= self.LIMITE_MAX and self.LIMITE_MIN <= novo_y <= self.LIMITE_MAX:
            self._posicaoX, self._posicaoY = novo_x, novo_y
            self._direcaoAtual = direcao
            return True
        return False

    def parar(self):
        self._direcaoAtual = EnumDirecao.PARADO

    def obterPosicao(self):
        return (self._posicaoX, self._posicaoY, self._direcaoAtual.value, self._nome)

    def alterarNome(self, novoNome: str):
        self._nome = novoNome

# ==========================================
# 2. INTERFACE (STREAMLIT + PLOTLY)
# ==========================================

def main():
    st.set_page_config(page_title="Questão 03 - Boneco", layout="wide")
    st.title("🕹️ Simulador de Movimento (UML)")

    if 'boneco_obj' not in st.session_state:
        st.session_state['boneco_obj'] = Boneco("Herói", 5.0, 5.0)
    
    b = st.session_state['boneco_obj']
    x, y, direcao, nome = b.obterPosicao()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.subheader("Controles (RF02)")
        # D-Pad simples
        st.write("")
        col_up = st.columns([1, 1, 1])
        if col_up[1].button("▲", use_container_width=True): 
            if not b.mover(EnumDirecao.CIMA): st.toast("Limite atingido!", icon="⚠️")
            st.rerun()

        col_mid = st.columns([1, 1, 1])
        if col_mid[0].button("◀", use_container_width=True):
            if not b.mover(EnumDirecao.ESQUERDA): st.toast("Limite atingido!", icon="⚠️")
            st.rerun()
        if col_mid[1].button("■", use_container_width=True):
            b.parar()
            st.rerun()
        if col_mid[2].button("▶", use_container_width=True):
            if not b.mover(EnumDirecao.DIREITA): st.toast("Limite atingido!", icon="⚠️")
            st.rerun()

        col_down = st.columns([1, 1, 1])
        if col_down[1].button("▼", use_container_width=True):
            if not b.mover(EnumDirecao.BAIXO): st.toast("Limite atingido!", icon="⚠️")
            st.rerun()

        st.divider()
        novo_n = st.text_input("Renomear (RF01):", value=nome)
        if st.button("Confirmar Nome"):
            b.alterarNome(novo_n)
            st.rerun()

    with col2:
        # Renderização do Grid (RNF03)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="text", text=["🧍‍♂️"], textfont=dict(size=40)))
        fig.update_layout(
            xaxis=dict(range=[-0.5, 10.5], dtick=1, showgrid=True),
            yaxis=dict(range=[-0.5, 10.5], dtick=1, showgrid=True),
            width=450, height=450, margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="#f0f2f6"
        )
        st.plotly_chart(fig, config={'displayModeBar': False})

    with col3:
        st.subheader("Status (RF05)")
        st.metric("Personagem", nome)
        st.metric("X", x)
        st.metric("Y", y)
        st.info(f"Direção: {direcao}")

if __name__ == "__main__":
    main()
