# Top Animes - Sistema com API Jikan

## 🔄 Migração Realizada

Este projeto foi **migrado da API oficial do MyAnimeList para a API Jikan** em 12/10/2025.

### ✨ Principais Melhorias

- **Sem autenticação necessária**: Não é mais preciso configurar tokens OAuth
- **Informações de score completas**: Acesso a ratings e scores detalhados
- **Mais dados disponíveis**: Gêneros, estúdios, status de transmissão
- **Rate limit mais generoso**: 3 requests por segundo (configurado para 2/seg)
- **Funcionalidades extras**: Busca por top animes, detalhes completos

## 🚀 Como Usar

### 1. Teste da Configuração
```bash
python authenticate_jikan.py
```

### 2. Teste da Migração
```bash
python test_migration.py
```

### 3. Executar o Sistema Principal
```bash
python main.py
```

## 📂 Arquivos Principais

### Novos Arquivos (Jikan)
- `jikan_api.py` - Nova API usando Jikan
- `authenticate_jikan.py` - Teste de conectividade (sem autenticação)
- `test_migration.py` - Testes das novas funcionalidades
- `revert_to_mal.py` - Script de reversão para API original

### Arquivos Atualizados
- `main.py` - Atualizado para usar Jikan API
- `config.json` - Nova seção `jikan_api` (removida seção `mal_api`)

### Arquivos de Backup
- `backup/` - Todos os arquivos originais para reversão

## 🔧 Configuração

A API Jikan não requer autenticação. As configurações em `config.json`:

```json
{
  "jikan_api": {
    "base_url": "https://api.jikan.moe/v4",
    "rate_limit_delay": 0.5,
    "max_retries": 3,
    "timeout": 30
  }
}
```

## 🆚 Comparação: Antes vs Depois

### ANTES (API MAL Oficial)
- ❌ Autenticação OAuth complexa
- ❌ Tokens com expiração
- ❌ Informações limitadas de score
- ❌ Rate limit restritivo
- ❌ Configuração complicada

### DEPOIS (API Jikan)
- ✅ Sem necessidade de autenticação
- ✅ Acesso completo a scores e ratings
- ✅ Informações detalhadas (gêneros, estúdios)
- ✅ Rate limit generoso
- ✅ Configuração simples
- ✅ Funcionalidades extras

## 🔄 Como Reverter

Se precisar voltar ao sistema anterior:

```bash
python revert_to_mal.py
```

Este script:
1. Faz backup dos arquivos Jikan
2. Restaura todos os arquivos originais
3. Restaura configuração original

## 📋 Funcionalidades Disponíveis

### Animes Sazonais
- Busca animes por temporada (Spring, Summer, Fall, Winter)
- Filtros por número mínimo de membros
- Ordenação por popularidade
- **NOVO**: Informações de score incluídas

### Animes Mais Esperados
- Top animes esperados de uma temporada
- **NOVO**: Dados de score e avaliação
- **NOVO**: Informações de status (airing/finished)

### Busca de Animes
- **NOVO**: Busca por nome
- **NOVO**: Top animes por score
- **NOVO**: Detalhes completos de qualquer anime

### Informações Extras (Novas)
- Score e número de avaliações
- Gêneros e estúdios
- Status de transmissão
- Número de episódios
- Ano de lançamento

## ⚙️ Dependências

```txt
requests==2.31.0
beautifulsoup4==4.12.2
```

Instalação:
```bash
pip install -r requirements.txt
```

## 🔗 Links Úteis

- [Documentação da API Jikan](https://docs.api.jikan.moe/)
- [GitHub da API Jikan](https://github.com/jikan-me/jikan)
- [MyAnimeList](https://myanimelist.net/)

## 🚨 Notas Importantes

1. **Rate Limit**: Respeite o limite de 3 requests/segundo da Jikan
2. **Backup**: Todos os arquivos originais estão em `backup/`
3. **Testes**: Execute `test_migration.py` antes do uso em produção
4. **Reversão**: Use `revert_to_mal.py` se precisar voltar ao sistema anterior

## 🔍 Troubleshooting

### API não responde
```bash
python authenticate_jikan.py
```

### Erro de rate limit
- Aumente o `rate_limit_delay` em config.json
- Verifique se não há múltiplas instâncias rodando

### Dados incompletos
- A API Jikan é dependente dos dados do MAL
- Alguns animes antigos podem ter informações limitadas

## 📝 Changelog

### v2.0 (12/10/2025) - Migração para Jikan
- Migração completa da API MAL para Jikan
- Adicionadas informações de score
- Removida necessidade de autenticação
- Adicionadas funcionalidades de busca avançada
- Sistema de backup e reversão implementado