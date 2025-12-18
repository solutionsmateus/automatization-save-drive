import zipfile
import subprocess
import os
import glob
import sys
from datetime import datetime
from rclone_python import rclone


RCLONE_REMOTE_NAME = 'gdrive' 
ROOT_DESTINATION = 'Encartes PDF'

# Dicionário para traduzir o mês para Português
MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def get_current_month():
    return MESES[datetime.now().month]

def process_files():
    artifact_folder = os.environ.get("ARTIFACT_FOLDER", "artifacts")
    print(f"--- Procurando arquivos em: {artifact_folder} ---")
    
    zip_pattern = os.path.join(artifact_folder, "**", "*.zip")
    zip_files = glob.glob(zip_pattern, recursive=True)
    extracted_roots = []

    if not zip_files:
        print("Nenhum ZIP encontrado. Verificando se há pastas diretas...")
        # Se não houver zip, assume que os artefatos já são as pastas dos supermercados
        for item in os.listdir(artifact_folder):
            path = os.path.join(artifact_folder, item)
            if os.path.isdir(path):
                extracted_roots.append(path)
        return extracted_roots

    for zip_path in zip_files:
        try:
            # Extrai o zip dentro de uma pasta com o nome do zip (que deve ser o nome do supermercado)
            extract_directory = zip_path.replace('.zip', '')
            os.makedirs(extract_directory, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_directory)
                extracted_roots.append(extract_directory)
            print(f"Extraído: {zip_path}")
        except Exception as e:
            print(f"Erro ao extrair {zip_path}: {e}")
    
    return extracted_roots

def sync_to_gdrive(local_folders):
    if not local_folders:
        print("Nada para sincronizar.")
        return

    month_folder = get_current_month()
    
    for local_path in local_folders:
        # Pega o nome da pasta (ex: Assai Atacadista)
        supermarket_name = os.path.basename(os.path.normpath(local_path))
        
        # Constrói o caminho: gdrive:Encartes - PDF/Assai Atacadista/Dezembro
        remote_path = f"{RCLONE_REMOTE_NAME}:{ROOT_DESTINATION}/{supermarket_name}/{month_folder}"
        
        print(f"\n>> Sincronizando: {supermarket_name}")
        print(f">> Destino: {remote_path}")

        try:
            # Usamos o sync para garantir que o que está no local seja igual ao remoto
            rclone.sync(
                source=local_path,
                dest=remote_path,
                flags=['--progress', '--drive-acknowledge-abuse']
            )
            print(f"SUCESSO: {supermarket_name} atualizado.")
        except Exception as e:
            print(f"ERRO ao sincronizar {supermarket_name}: {e}")

def main():
    print("INÍCIO DO PROCESSO - GOOGLE DRIVE")
    folders = process_files()
    if not folders:
        print("ERRO: Nenhuma pasta de supermercado encontrada para sincronizar.")
        return
    sync_to_gdrive(folders)
    print("\n--- PROCESSO CONCLUÍDO ---")

if __name__ == "__main__":
    main()
