import streamlit as st
from enum import Enum

# ==========================================
# 1. MODELO DE DOMÍNIO (UML)
# ==========================================

class Cor(Enum):
    PRETO = "PRETO"
    BRANCO = "BRANCO"
    AZUL = "AZUL"
    AMARELO = "AMARELO"
    CINZA = "CINZA"

class TipoComponente(Enum):
    LABEL = "LABEL"
    EDIT = "EDIT"
    MEMO = "MEMO"

class TextoSaida:
    """Classe pura conforme RNF01 - Sem vínculos com linguagens visuais."""
    def __init__(self):
        self._conteudoTexto = ""
        self.tamanhoLetra = 14
        self.corFonte = Cor.PRETO.value
        self.corFundo = Cor.BRANCO.value
        self.tipoComponente = TipoComponente.LABEL.value

    def set_conteudoTexto(self, texto: str):
        self._conteudoTexto = texto

    def configTexto(self, tamanho: int, fonte: str, fundo: str):
        self.tamanhoLetra = tamanho
        self.corFonte = fonte
        self.corFundo = fundo

    def definirComponente(self, tipo: str):
        self.tipoComponente = tipo

    def exibir(self) -> dict:
        """Retorna o estado interno para a camada de apresentação."""
        return {
            "texto": self._conteudoTexto,
            "tamanho": self.tamanhoLetra,
            "cor_fonte": self.corFonte,
            "cor_fundo": self.corFundo,
            "componente": self.tipoComponente
        }

# ==========================================
# 2. CAMADA DE APRESENTAÇÃO (STREAMLIT)
# ==========================================

MAPA_CORES_CSS = {
    "PRETO": "#000000", "BRANCO": "#FFFFFF",
    "AZUL": "#0000FF", "AMARELO": "#FFFF00", "CINZA": "#808080"
}

def main():
    st.set_page_config(page_title="Questão 02 - TextoSaída", page_icon="🖥️")
    st.title("🖥️ Renderizador de Componentes")
    st.markdown("---")

    if 'objeto_texto' not in st.session_state:
        st.session_state['objeto_texto'] = TextoSaida()
    
    objeto = st.session_state['objeto_texto']

    # --- Entrada de Dados (Sidebar) ---
    with st.sidebar:
        st.header("Configurações")
        texto_input = st.text_area("Texto de Saída (RF01):", placeholder="Digite aqui...")
        
        tamanho = st.slider("Tamanho da Letra (RF02):", 8, 72, 18)
        
        cores = [c.value for c in Cor]
        fonte = st.selectbox("Cor da Fonte (RF04):", cores, index=0)
        fundo = st.selectbox("Cor do Fundo (RF04):", cores, index=1)
        
        componentes = [t.value for t in TipoComponente]
        tipo = st.radio("Componente de Saída (RF03):", componentes)

        if st.button("🚀 Aplicar e Renderizar"):
            objeto.set_conteudoTexto(texto_input)
            objeto.configTexto(tamanho, fonte, fundo)
            objeto.definirComponente(tipo)

    # --- Resultado Visual (RF05) ---
    dados = objeto.exibir()
    
    if not dados["texto"]:
        st.info("Aguardando entrada de texto para renderizar...")
    else:
        st.subheader(f"Visualização: {dados['componente']}")
        
        # Estilização CSS Dinâmica (RNF03)
        estilo = (
            f"font-size: {dados['tamanho']}px; "
            f"color: {MAPA_CORES_CSS[dados['cor_fonte']]}; "
            f"background-color: {MAPA_CORES_CSS[dados['cor_fundo']]}; "
            f"padding: 15px; border-radius: 8px; border: 1px solid #ddd; width: 100%;"
        )

        if dados['componente'] == "LABEL":
            st.markdown(f'<div style="{estilo}">{dados["texto"]}</div>', unsafe_allow_html=True)
        
        elif dados['componente'] == "EDIT":
            st.markdown(f'<input type="text" value="{dados["texto"]}" style="{estilo}" readonly>', unsafe_allow_html=True)
            
        elif dados['componente'] == "MEMO":
            st.markdown(f'<textarea style="{estilo}" rows="5" readonly>{dados["texto"]}</textarea>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
