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

