import zipfile
import subprocess
import os
import glob
import sys
import shutil # Adicionado para exclusão de pastas
from datetime import datetime
from rclone_python import rclone


RCLONE_REMOTE_NAME = 'gdrive' 
ROOT_DESTINATION = 'Encartes PDF'

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

SUPERMARKET_MAPPING = {
    'novoatacarejo': 'Novo Atacarejo',
    'gbardosa': 'GBarbosa',
    'frangolandia': 'Frangolândia',
    'cometa': 'Cometa Supermercados',
    'atakarejo': 'Atakarejo',
    'atacadao': 'Atacadão',
    'assaiatacadista': 'Assaí Atacadista',
}

def get_current_month():
    return MESES[datetime.now().month]

def process_files():
    artifact_folder = os.environ.get("ARTIFACT_FOLDER", "artifacts")
    print(f"--- Procurando pastas em: {artifact_folder} ---")
    
    extracted_roots = []
    
    if not os.path.isdir(artifact_folder):
        print(f"ERRO: Pasta de artifacts '{artifact_folder}' não encontrada.")
        return extracted_roots

    for item in os.listdir(artifact_folder):
        path = os.path.join(artifact_folder, item)
        if os.path.isdir(path) and not item.startswith('.'):
            extracted_roots.append(path)

    if not extracted_roots:
        print("Aviso: Nenhuma pasta de supermercado (subdiretório) encontrada. Verifique a estrutura do artifact.")
        
    return extracted_roots

def sync_to_gdrive(local_folders):
    if not local_folders:
        print("Nada para sincronizar.")
        return

    month_folder_name = get_current_month()
    
    for local_path in local_folders:
        now = datetime.now()
        month_folder = now.strftime(f"{month_folder_name}-%Y") 
        day_folder = now.strftime("%d-%m-%Y") 
        
        artifact_filename = os.path.basename(os.path.normpath(local_path))
        
        try:
            name_part = artifact_filename.split('-')[-2]
            name_key = name_part.split('.')[0].lower()
            supermarket_name = SUPERMARKET_MAPPING.get(name_key, name_key.capitalize())
        except IndexError:
            supermarket_name = artifact_filename
            print(f"Aviso: Não foi possível extrair nome formal do artefato. Usando: {supermarket_name}")

        remote_path = f"{RCLONE_REMOTE_NAME}:{ROOT_DESTINATION}/{supermarket_name}/{day_folder}/{month_folder}"
        
        print(f"\n>> Sincronizando: {supermarket_name} (Pasta de execução: {day_folder})")
        print(f">> Destino: {remote_path}")

        try:
            rclone.sync(
                local_path,
                remote_path,
                ['--progress', '--drive-acknowledge-abuse', '--transfers=8', '--drive-chunk-size=64M', '--tpslimit=5'],
            )
            print(f"SUCESSO: {supermarket_name} atualizado para o dia {day_folder}")
            
            shutil.rmtree(local_path)
            print(f"SUCESSO: Pasta local de artefato excluída: {local_path}")
            
        except Exception as e:
            print(f"ERRO ao sincronizar {supermarket_name}: {e}. Pasta local MANTIDA: {local_path}")
            
        
def main():
    print("INÍCIO DO PROCESSO - GOOGLE DRIVE")
    folders = process_files()
    if not folders:
        print("AVISO: Nenhuma pasta de supermercado encontrada para sincronizar.")
        return
    sync_to_gdrive(folders)
    print("\n--- PROCESSO CONCLUÍDO ---")

if __name__ == "__main__":
    main()