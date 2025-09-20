# 🎌 Top Animes - Sistema de Rankings

Um sistema completo para gerar rankings de anime baseados em dados do MyAnimeList, com duas modalidades:
- **Top Anime Episodes**: Os melhores episódios da semana
- **Most Anticipated Animes**: Os animes mais esperados da temporada atual

## 📋 Funcionalidades

### Rankings Disponíveis
1. **Top 50 Anime Episodes da Semana**
   - Baseado nas notas dos episódios lançados na última semana
   - Atualização semanal
   - Filtragem por número mínimo de membros

2. **Top 50 Most Anticipated Animes**
   - Baseado no número de "Plan to Watch" members
   - Focado na temporada atual (Fall 2025)
   - Ordenação por popularidade/interesse

### Características do Sistema
- ✅ **Menu de Navegação**: Navegue facilmente entre os rankings
- ✅ **Design Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- ✅ **Animações Suaves**: Interface moderna com transições fluidas
- ✅ **Sistema Anti-Duplicatas**: Evita dados repetidos
- ✅ **Tratamento de Erros**: Log detalhado de erros
- ✅ **Configuração Flexível**: Personalize cores, URLs e parâmetros

## 🚀 Instalação e Configuração

### Pré-requisitos
```bash
python 3.7+
pip install -r requirements.txt
```

### Dependências
```bash
pip install requests beautifulsoup4 lxml
```

### Estrutura do Projeto
```
projeto/
├── main.py                          # Script original (episódios)
├── main_integrated.py               # Script principal integrado ⭐
├── anticipated_animes_scraper.py    # Scraper para animes esperados ⭐
├── anticipated_html_generator.py    # Gerador HTML para animes esperados ⭐
├── scraper_utils.py                 # Funções auxiliares existentes
├── html_generator.py                # Gerador HTML existente
├── styles.css → updated_styles.css  # CSS atualizado com menu ⭐
├── script.js → script_updated.js    # JavaScript atualizado ⭐
├── config.json → config_updated.json # Configuração atualizada ⭐
├── requirements.txt                 # Dependências Python
├── assets/                          # Imagens e recursos
│   ├── logo_transparent.png
│   ├── MAL_logo.png
│   └── placeholder.png              # Nova: imagem fallback ⭐
├── episodes_data.json               # Dados dos episódios (gerado)
├── anticipated_animes_data.json     # Dados dos animes esperados (gerado) ⭐
├── top_anime_episodes.html          # Página de episódios (gerada)
├── top_anticipated_animes.html      # Página de animes esperados (gerada) ⭐
└── error_log.txt                    # Log de erros
```

## 🔧 Como Usar

### Modo Interativo (Recomendado)
```bash
python main_integrated.py --interactive
```

Você verá um menu como este:
```
🎌 TOP ANIMES - SISTEMA DE RANKINGS
====================================
Escolha uma opção:
1. Gerar ranking de episódios da semana
2. Gerar ranking de animes mais esperados  
3. Gerar ambos os rankings
4. Apenas atualizar menus de navegação
0. Sair
```

### Modo Linha de Comando
```bash
# Gerar apenas episódios da semana
python main_integrated.py --mode weekly

# Gerar apenas animes esperados
python main_integrated.py --mode anticipated

# Gerar ambos os rankings
python main_integrated.py --mode both

# Atualizar apenas menus
python main_integrated.py --mode menu
```

### Uso Individual dos Módulos
```bash
# Apenas animes esperados
python anticipated_animes_scraper.py

# Apenas gerar HTML dos esperados
python anticipated_html_generator.py
```

## ⚙️ Configuração

### Arquivo config_updated.json
```json
{
  "anticipated_animes": {
    "max_animes": 50,
    "min_members": 1000,
    "season": "Fall 2025"