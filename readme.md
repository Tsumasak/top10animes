# Top 50 Anime Episodes Scraper

Um scraper Python que coleta dados do MyAnimeList para gerar uma página HTML com os top 50 episódios de anime da semana.

## Estrutura do Projeto

```
projeto/
├── main.py              # Script principal
├── scraper_utils.py     # Funções auxiliares
├── html_generator.py    # Gerador de HTML
├── styles.css          # Estilos CSS
├── script.js           # JavaScript
├── config.json         # Configurações
├── requirements.txt    # Dependências Python
├── assets/             # Imagens e recursos
│   ├── logo_transparent.png
│   └── MAL_logo.png
├── episodes_data.json  # Dados dos episódios (gerado)
├── top_anime_episodes.html # Página final (gerada)
└── error_log.txt       # Log de erros (gerado)
```

## Instalação

1. Clone ou baixe os arquivos do projeto
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Adicione os logos na pasta `assets/`:
   - `logo_transparent.png` - Logo do Top 10 Animes (100x100px)
   - `MAL_logo.png` - Logo do MyAnimeList

## Uso

Execute o script principal:
```bash
python main.py
```

O script irá:
1. Coletar animes das temporadas do MyAnimeList
2. Buscar episódios lançados na última semana
3. Gerar arquivo JSON com os dados (`episodes_data.json`)
4. Criar página HTML final (`top_anime_episodes.html`)

## Configuração

Edite o arquivo `config.json` para personalizar:
- URLs de origem dos dados
- Número mínimo de membros para filtrar animes
- Cores do layout
- Caminhos dos arquivos
- Links das redes sociais

## Arquivos Gerados

- `episodes_data.json` - Dados brutos dos episódios em JSON
- `top_anime_episodes.html` - Página web final
- `error_log.txt` - Log de erros durante a execução

## Funcionalidades

### Script Principal (main.py)
- Coleta dados de múltiplas URLs do MyAnimeList
- Sistema anti-duplicatas
- Salva dados em JSON para reuso
- Gera HTML final

### Funções Auxiliares (scraper_utils.py)
- Parse de contagem de membros (K, M)
- Parse de datas
- Sistema de logging de erros
- Configurações de cores

### Gerador HTML (html_generator.py)
- Gera página HTML completa
- Suporte a templates
- Integração com CSS e JavaScript externos

### Frontend
- **CSS**: Design responsivo com cores vibrantes
- **JavaScript**: Scroll suave, botões fixos, carregamento dinâmico
- **Responsividade**: Desktop (850px max), Tablet, Mobile

## Características da Página

### Design
- Header fixo com logo e período
- Cards coloridos por ranking (Verde, Rosa, Amarelo)
- Gradientes e sombras
- Botões fixos para Instagram e scroll-to-top

### Mobile
- Header sem transparência (mesmo padrão desktop)
- Gradiente esquerda→direita
- Título/episódio centralizado e alinhado à esquerda
- Layout vertical adaptado

### Funcionalidades
- Links diretos para episódios no MyAnimeList
- Efeitos hover sutis
- Scroll suave para topo
- Integração com Instagram

## Personalização

### Cores
Modifique em `config.json` ou `scraper_utils.py`:
```python
colors = {
    1: {"bg": "#88FE70", "text": "#212121"},      # 1º lugar - Verde
    2: {"bg": "#FE70A9", "text": "#212121"},      # 2º/3º lugar - Rosa  
    "other": {"bg": "#FECB70", "text": "#212121"} # Outros - Amarelo
}
```

### Layout
- Edite `styles.css` para mudanças visuais
- Modifique `html_generator.py` para estrutura HTML
- Ajuste `script.js` para comportamentos

## Solução de Problemas

### Logs
Verifique `error_log.txt` para erros detalhados

### Dados Vazios
- Verifique se há animes com episódios na semana atual
- Ajuste `min_members` no config para valor menor
- Confirme se URLs do MyAnimeList estão acessíveis

### CSS/JS não Carrega
- Verifique se arquivos `styles.css` e `script.js` existem
- Confirme paths corretos no `html_generator.py`

## Dependências

- `requests` - HTTP requests
- `beautifulsoup4` - Parse HTML
- `lxml` - Parser XML/HTML rápido

## Licença

Projeto para uso educacional. Respeite os termos de uso do MyAnimeList.