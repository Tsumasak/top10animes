import traceback
from datetime import datetime, timedelta

def debug_print(message, level=1):
    """Função para debug com indentação baseada no nível"""
    indent = "  " * level
    print(f"{indent}{message}")

def log_error(e):
    """Registra erros em arquivo de log"""
    with open('error_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} - {str(e)}\n")
        f.write(traceback.format_exc() + "\n\n")

def parse_members_count(text):
    """Converte texto de contagem de membros para número inteiro"""
    try:
        text = text.strip().upper().replace(',', '')
        if 'K' in text:
            return int(float(text.replace('K','')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M','')) * 1000000)
        else:
            return int(text)
    except:
        return 0

def parse_air_date(date_str):
    """Converte string de data para objeto date"""
    try:
        date_str = date_str.strip()
        today = datetime.now().date()
        if date_str == 'Today':
            return today
        elif date_str == 'Yesterday':
            return today - timedelta(days=1)
        for fmt in ('%b %d, %Y', '%Y-%m-%d', '%m/%d/%y'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    except Exception as e:
        debug_print(f"Erro ao parsear data '{date_str}': {e}", 2)
        log_error(e)
        return None

def get_ranking_colors():
    """Retorna esquema de cores para diferentes posições no ranking"""
    return {
        1: {"bg": "#88FE70", "text": "#212121"},  # Green
        2: {"bg": "#FE70A9", "text": "#212121"},  # Pink  
        3: {"bg": "#FE70A9", "text": "#212121"},  # Pink
        "other": {"bg": "#FECB70", "text": "#212121"}  # Yellow
    }
