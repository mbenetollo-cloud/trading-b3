#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENTE DE ATUALIZAÇÃO DIÁRIA
==============================
Executa atualização de indicadores diariamente
Horários: 8h (antes pregão) ou 18h (após pregão)
"""

import schedule
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Caminhos
SCRIPT_DIR = Path(__file__).parent

def atualizar_indicadores():
    """Executa script de atualização de indicadores"""
    print(f"\n{'='*60}")
    print(f"AGENTE: Atualização de indicadores - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")
    
    try:
        # Executar atualizar_indicadores.py
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'atualizar_indicadores.py')],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"ERROS:\n{result.stderr}")
        
        # Commit automático
        print("\nCommitando alterações...")
        subprocess.run(['git', 'add', 'data/indicadores.json'], 
                      cwd=SCRIPT_DIR, capture_output=True)
        
        msg = f"update: Indicadores {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        result = subprocess.run(['git', 'commit', '-m', msg], 
                               cwd=SCRIPT_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Commit realizado com sucesso!")
            
            # Push
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                   cwd=SCRIPT_DIR, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Push realizado com sucesso!")
            else:
                print(f"Erro no push: {result.stderr}")
        else:
            print("Nenhuma alteração para commitar")
            
    except Exception as e:
        print(f"Erro ao executar agente: {e}")

def main():
    """Função principal - Agendador"""
    print("=" * 60)
    print("AGENTE DE ATUALIZAÇÃO DIÁRIA")
    print("=" * 60)
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    print("Horários configurados:")
    print("  - 08:00 (antes do pregão)")
    print("  - 18:00 (após o pregão)")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    
    # Agendar para 8h e 18h
    schedule.every().day.at("08:00").do(atualizar_indicadores)
    schedule.every().day.at("18:00").do(atualizar_indicadores)
    
    # Executar imediatamente na primeira vez
    print("\nExecutando atualização inicial...")
    atualizar_indicadores()
    
    # Manter aguardando
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
