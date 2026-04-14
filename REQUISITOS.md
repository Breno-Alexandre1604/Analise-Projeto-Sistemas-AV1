# 📋 Documentação de Requisitos - APS (Lista 01)

Este documento detalha os Requisitos Funcionais (RF) e Não Funcionais (RNF) para cada um dos problemas analisados no projeto.

---

## ⚡ 01. Sistema de Gestão: Conta de Luz

### 1.1 Requisitos Funcionais (RF)
* **RF01 - Cadastro de Medição:** O sistema deve permitir a entrada detalhada dos dados de consumo de energia, incluindo a data da leitura (dia/mês/ano), o número sequencial registrado no relógio de luz, a quantidade de quilowatts (kW) consumidos no período, o valor total da fatura em moeda corrente (R$), a data em que o pagamento foi efetuado e a média histórica de consumo.
* **RF02 - Listagem de Histórico:** O sistema deve apresentar todos os registros armazenados em uma estrutura de tabela clara e organizada, permitindo a visualização cronológica dos gastos de luz.
* **RF03 - Análise de Eficiência (Menor Consumo):** O sistema deve processar a base de dados para identificar e destacar automaticamente o registro que possui o menor valor de kW gasto, informando ao usuário o mês correspondente.
* **RF04 - Análise de Pico (Maior Consumo):** O sistema deve processar a base de dados para identificar e destacar automaticamente o registro com o maior valor de kW gasto para fins de acompanhamento de picos de consumo.

### 1.2 Requisitos Não Funcionais (RNF)
* **RNF01 - Interface Web:** A aplicação deve ser desenvolvida utilizando o framework **Streamlit**, garantindo uma interface responsiva e intuitiva.
* **RNF02 - Linguagem e Estrutura:** O desenvolvimento deve utilizar **Python 3.x** seguindo os princípios de Orientação a Objetos (OO).
* **RNF03 - Validação de Integridade:** O sistema não deve permitir a entrada de valores negativos para campos de consumo (kW) e valores monetários (R$).
* **RNF04 - Cibersegurança (Sanitização de Dados):** O sistema deve tratar todas as entradas do usuário para prevenir ataques de *Injection*. Os dados devem ser tipados rigorosamente (ex: `float`, `int`) para evitar execução de scripts maliciosos.
* **RNF05 - Cibersegurança (Privacidade):** O sistema deve garantir que os dados de consumo sejam armazenados apenas em memória de sessão segura (`st.session_state`), evitando exposição em logs ou URLs.

---
### Diagrama de Classe - Questão 01
```mermaid
classDiagram
    class ContaLuz {
        +dataLeitura
        +numLeitura
        +kwGasto
        +valorPagar
        +dataPagamento
        +mediaConsumo
    }
    class GerenciadorConsumo {
        +list listaContas
        +adicionarConta(conta)
        +verificarMenorConsumo()
        +verificarMaiorConsumo()
    }
    GerenciadorConsumo "1" --> "*" ContaLuz
```
---

## 🖥️ 02. Exercício: Classe TextoSaída

### 2.1 Requisitos Funcionais (RF)
* **RF01 - Definição de Conteúdo:** O sistema deve permitir que o usuário insira um texto (conteúdo) que será processado pela classe.
* **RF02 - Configuração Estética:** O sistema deve permitir configurar o tamanho da letra, a cor da fonte e a cor de fundo do texto.
* **RF03 - Seleção de Componente:** O sistema deve permitir a escolha do tipo de componente visual para exibição, restrito às opções: **Label** (rótulo estático), **Edit** (campo de linha única) e **Memo** (área de texto multilinha).
* **RF04 - Restrição de Cores:** O sistema deve limitar as cores de fonte e fundo exclusivamente aos tons: preto, branco, azul, amarelo ou cinza.
* **RF05 - Renderização Visual:** O sistema deve aplicar as configurações em tempo real e exibir o resultado visual simulando o componente escolhido.

### 2.2 Requisitos Não Funcionais (RNF)
* **RNF01 - Independência Visual:** A classe de domínio (`TextoSaida`) deve ser pura, ou seja, não deve herdar classes visuais de frameworks específicos, garantindo portabilidade.
* **RNF02 - Padronização com Enums:** Devem ser utilizados tipos enumerados (Enums) para garantir que apenas cores e componentes válidos sejam processados (Cibersegurança/Integridade).
* **RNF03 - Interface Web:** O front-end deve ser implementado via **Streamlit** com uso de injeção de CSS controlado para simular as propriedades visuais.
* **RNF04 - Cibersegurança (XSS Prevention):** O sistema deve tratar a exibição de HTML para garantir que apenas o estilo pretendido seja renderizado, sem execução de scripts externos.

---
### Diagrama de Classe - Questão 02

```mermaid
classDiagram
    class TextoSaida {
        -conteudoTexto: str
        +tamanhoLetra: int
        +corFonte: str
        +corFundo: str
        +tipoComponente: str
        +set_conteudoTexto(texto: str)
        +configTexto(tamanho, fonte, fundo)
        +definirComponente(tipo)
        +exibir() dict
    }
```
---

## 🕹️ 03. Exercício: Classe Boneco em Movimento

### 3.1 Requisitos Funcionais (RF)
* **RF01 - Identificação do Personagem:** O sistema deve permitir atribuir e alterar o nome do boneco.
* **RF02 - Controle de Movimentação:** O sistema deve permitir mover o boneco em quatro direções: Cima, Baixo, Direita e Esquerda.
* **RF03 - Gestão de Coordenadas:** O sistema deve manter e atualizar as coordenadas cartesianas (X e Y) do boneco a cada movimento realizado.
* **RF04 - Monitoramento de Direção:** O sistema deve registrar a última direção tomada ou indicar se o boneco está parado.
* **RF05 - Relatório de Status:** O sistema deve exibir em tempo real a posição atual (X, Y) e o nome do boneco na interface.

### 3.2 Requisitos Não Funcionais (RNF)
* **RNF01 - Restrição de Fronteira:** O sistema deve impedir que o boneco ultrapasse os limites definidos da tela (Grid de 0 a 10), garantindo a integridade do cenário.
* **RNF02 - Encapsulamento Rigoroso:** Os atributos de posição e direção devem ser privados (`_`), sendo acessados apenas por métodos específicos (Cibersegurança/Arquitetura).
* **RNF03 - Interface Gráfica:** A visualização deve ser feita via **Plotly** integrado ao **Streamlit**, permitindo uma representação visual clara do movimento no plano cartesiano.
* **RNF04 - Cibersegurança (Validação de Entrada):** O sistema deve validar o nome do boneco para evitar entradas de scripts maliciosos em campos de texto.

---
### Diagrama de Classe - Questão 03

```mermaid
classDiagram
    class Boneco {
        -nome: str
        -posicaoX: float
        -posicaoY: float
        -direcaoAtual: str
        +mover(direcao) bool
        +parar()
        +obterPosicao() tuple
        +alterarNome(novoNome)
    }
```
---

## 💊 04. Exercício: Horário de Remédios

### 4.1 Requisitos Funcionais (RF)
* **RF01 - Cadastro de Prescrição:** O sistema deve permitir o cadastro do paciente, nome do remédio, dosagem, data de início, duração do tratamento (dias) e frequência diária.
* **RF02 - Sugestão de Horários:** Ao definir a frequência, o sistema deve sugerir automaticamente os intervalos de horários para as doses.
* **RF03 - Personalização de Cronograma:** O usuário deve poder escolher o horário da primeira dose, e o sistema deve calcular os demais horários com base nisso.
* **RF04 - Cálculo de Término:** O sistema deve informar automaticamente a data final do tratamento.
* **RF05 - Geração de Planilha:** O sistema deve gerar uma grade completa de horários para todo o período do tratamento.
* **RF06 - Agenda Diária:** O sistema deve filtrar e exibir apenas os remédios programados para o dia atual.
* **RF07 - Registro de Dose:** O usuário deve marcar quando tomou o remédio. O sistema deve registrar o horário real.
* **RF08 - Reorganização por Atraso:** Caso uma dose seja tomada com atraso, o sistema deve recalcular automaticamente os horários das doses restantes **apenas para aquele dia**.

### 4.2 Requisitos Não Funcionais (RNF)
* **RNF01 - Persistência de Dados:** Uso de **SQLite** para garantir que os dados não sejam perdidos ao fechar o navegador (Diferencial Sênior).
* **RNF02 - Notificação Simulada:** O sistema deve destacar visualmente doses pendentes e atrasadas na interface.
* **RNF03 - Cibersegurança (SQL Injection):** Uso de *Parameterized Queries* para todas as interações com o banco de dados.
* **RNF04 - Integridade Temporal:** O sistema não deve permitir cadastros de tratamentos com datas retroativas.

---
### Diagrama de Classe - Questão 04

```mermaid
classDiagram
    class Prescricao {
        +paciente: str
        +remedio: str
        +dosagem: str
        +dataInicio: date
        +dias: int
        +vezesAoDia: int
        +dataFim: date
        +doses: List~Dose~
        +calcularDataFim()
    }
    class Dose {
        +dataDose: date
        +horaEsperada: time
        +horaReal: time
        +status: str
        +prescricaoPai: Prescricao
    }
    Prescricao "1" -- "*" Dose : gerencia
```
