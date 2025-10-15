from datetime import date, timedelta

# Teste da lógica de "Última semana"
today = date.today()
print(f'Hoje é: {today} (weekday: {today.weekday()})')

# Lógica implementada (versão final)
if today.weekday() == 6:  # Hoje é domingo
    start_date = today - timedelta(days=6)  # Domingo da semana passada  
    end_date = today  # Hoje (domingo)
else:
    # Encontrar o domingo da semana atual
    days_since_sunday = (today.weekday() + 1) % 7
    current_sunday = today - timedelta(days=days_since_sunday)
    
    # Do domingo até o sábado desta semana (ou hoje se ainda não é sábado)
    start_date = current_sunday
    week_saturday = current_sunday + timedelta(days=6)
    end_date = min(today, week_saturday)

print(f'Período: {start_date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")}')

# Verificar se está correto
expected_start = date(2025, 10, 6)  # Domingo 06/10
expected_end = date(2025, 10, 12)   # Sábado 12/10

print(f'Esperado: {expected_start.strftime("%d/%m/%Y")} até {expected_end.strftime("%d/%m/%Y")}')
print(f'Resultado correto: {start_date == expected_start and end_date == expected_end}')