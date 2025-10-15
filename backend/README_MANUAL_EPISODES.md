# Sistema de Adição Manual de Episódios

## 📖 Visão Geral

Este sistema permite adicionar episódios manualmente ao ranking quando eles ainda não estão disponíveis na API do Jikan (MyAnimeList). Útil para episódios recém-lançados que demoram para aparecer na API.

## 🚀 Como Usar

### 1. Executar o Sistema

**Opção A - Via Menu Principal (Recomendado):**
```bash
cd backend/src
python main.py
# Escolha opção 4: 🔧 Adicionar Episódios Manuais
```

**Opção B - Direto:**
```bash
cd backend/src
python manual_episodes.py
```

### 2. Interface do Sistema

O sistema apresenta um menu interativo:

```
🎬 SISTEMA DE ADIÇÃO MANUAL DE EPISÓDIOS
==================================================
📦 Cache atual: 0 episódio(s)

1️⃣  Adicionar episódio ao cache
2️⃣  Ver resumo do cache
3️⃣  Salvar todos no banco de dados
4️⃣  Limpar cache
0️⃣  Sair
```

### 3. Workflow Completo

#### 3.1 Adicionar Episódios (Opção 1)
Para cada episódio, você precisa fornecer:

- **🆔 Anime ID**: ID do anime no MyAnimeList (ex: 21 para One Piece)
- **📺 Número do episódio**: Número sequencial do episódio
- **📝 Nome do episódio**: Título do episódio
- **📅 Data de lançamento**: Data que o episódio foi ao ar (formato YYYY-MM-DD)
- **⭐ Dados de rating**: Dados copiados do MAL no formato:
  ```
  5Loved it! 72.7% 197
  4Liked it! 21.0% 57
  3It was OK 4.8% 13
  2Disliked it 0.4% 1
  1Hated it 1.1% 3
  ```

#### 3.2 Verificar Cache (Opção 2)
Mostra todos os episódios adicionados no cache antes de salvar.

#### 3.3 Salvar no Banco (Opção 3)
Processa todos os episódios do cache e os salva no banco de dados.

### 4. Gerar JSON Final
```bash
cd backend/src
python export_data.py
```

## 🔧 Funcionalidades

### ✅ Processamento em Lote
- Adicione múltiplos episódios em uma sessão
- Cache temporário para revisão antes de salvar
- Processamento transacional (all-or-nothing)

### ✅ Validações Automáticas
- Verificação se anime existe na API do Jikan
- Detecção de episódios duplicados
- Validação dos dados de rating
- Cálculo automático da média ponderada

### ✅ Integração Completa
- Episódios manuais aparecem no ranking junto com os automáticos
- Indicador visual no frontend (🔧) para episódios manuais
- Compatibilidade total com sistema existente

## 📊 Cálculo de Rating

O sistema converte automaticamente os dados de rating do MAL:
- Extrai votos por categoria (1-5 estrelas)
- Calcula média ponderada
- Converte para escala MAL (1-10)

**Exemplo:**
```
Entrada: 5=197 votos, 4=57 votos, 3=13 votos, 2=1 voto, 1=3 votos
Resultado: 4.64 (na escala MAL 1.00-5.00)
```

## 🗃️ Estrutura do Banco

### Tabela `manual_episodes`
```sql
CREATE TABLE manual_episodes (
    id TEXT PRIMARY KEY,           -- "manual_{anime_id}_{episode_number}"
    anime_id INTEGER,              -- ID do anime no MAL
    title TEXT,                    -- Nome do episódio
    episode_number INTEGER,        -- Número do episódio
    rating REAL,                   -- Rating calculado (1.00-5.00)
    anime_title TEXT,              -- Nome do anime
    anime_image_url TEXT,          -- URL da imagem do anime
    episode_url TEXT,              -- URL do episódio no MAL
    anime_type TEXT,               -- Tipo do anime (TV, ONA, etc)
    date_added TEXT,               -- Data de adição no sistema
    air_date TEXT,                 -- Data de lançamento do episódio
    is_manual INTEGER DEFAULT 1    -- Sempre 1 para episódios manuais
);
```

## 🎯 Exemplo Prático

### Cenário: "A Wild Last Boss Appeared!" EP 2

1. **Problema**: Episódio lançado mas ainda não disponível na API
2. **Solução**: Usar sistema manual

**Passos:**
1. Encontrar anime ID no MAL: `59027`
2. Executar `python manual_episodes.py`
3. Escolher opção 1 (Adicionar episódio)
4. Inserir dados:
   - ID: `59027`
   - Episódio: `2`
   - Nome: `"The Wild Last Boss Shows His Power"`
   - Rating: colar dados do MAL
5. Salvar no banco (opção 3)
6. Executar `python export_data.py`

**Resultado**: Episódio aparece no ranking com indicador 🔧

## 📁 Arquivos Relacionados

- `manual_episodes.py` - Sistema principal
- `database_setup.py` - Criação da tabela (atualizado)
- `export_data.py` - Export incluindo episódios manuais (atualizado)
- `EpisodeCard.tsx` - Frontend com indicador visual (atualizado)
- `demo_manual_episodes.py` - Demonstração e testes

## 🛡️ Segurança e Validações

- ✅ Verificação de existência do anime na API
- ✅ Prevenção de episódios duplicados
- ✅ Validação dos dados de rating
- ✅ Transações atômicas no banco
- ✅ Rollback automático em caso de erro
- ✅ Rate limiting respeitoso com a API do Jikan

## 🎨 Interface Visual

Os episódios manuais são identificados no frontend com:
- **🔧 Ícone**: Aparece ao lado do nome do episódio
- **Funcionalidade**: Mesma dos episódios automáticos
- **Ranking**: Integrados naturalmente por rating

---

**🎉 Sistema pronto para uso! Execute `python manual_episodes.py` para começar.**