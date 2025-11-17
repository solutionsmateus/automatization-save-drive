import zipfile
import subprocess
from rclone_python import rclone
from rclone_python.remote_types import RemoteTypes # Importação mantida, mas não utilizada na versão final corrigida.
import os
import glob
import hashlib
import sys

artifact_folder = os.environ.get("ARTIFACT_FOLDER", "./workflow-github-action")
RCLONE_REMOTE_NAME = 'OneDrive_Remote' 
ONEDRIVE_DESTINATION_FOLDER = 'WorkflowUploads/'
REMOTE_CONNECTION = f"{RCLONE_REMOTE_NAME}:{ONEDRIVE_DESTINATION_FOLDER}"


def process_files():
    """Procura por arquivos .zip no artifact_folder e os extrai para o seu diretório."""
    print(f"Procurando por arquivos .zip em {artifact_folder}...")
    zip_pattern = os.path.join(artifact_folder, "**", "*.zip")
    zip_files = glob.glob(zip_pattern, recursive=True)
    extracted_roots = [] 

    if not zip_files:
        print("Nenhum arquivo .zip encontrado. Verificando arquivos existentes...")
        if os.path.isdir(artifact_folder):
            extracted_roots.append(artifact_folder)
        return extracted_roots 

    print(f"Encontrados {len(zip_files)} arquivos .zip. Extraindo...")
    for zip_path in zip_files:
        try:
            extract_directory = os.path.dirname(zip_path) 
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_directory)
                if extract_directory not in extracted_roots:
                    extracted_roots.append(extract_directory)
            print(f"Extraído: {zip_path} -> {extract_directory}")
        except zipfile.BadZipFile:
            print(f"Erro: {zip_path} não é um arquivo zip válido ou está corrompido.")
        except Exception as e:
            print(f"Erro ao extrair {zip_path}: {e}")
            
    print("Extração de Zips concluída.\n")
    return extracted_roots

def files_onpath():
    """Verifica se a pasta de artefatos existe."""
    if not os.path.isdir(artifact_folder):
        print(f"A pasta {artifact_folder} não foi encontrada. Encerrando.")
        sys.exit(1)
    else:
        print(f"Pasta de artefatos encontrada: {artifact_folder}")


def select_files(local_folders_to_sync):
    if not local_folders_to_sync:
        print("Nenhum diretório para sincronizar. Finalizando a etapa de upload.")
        return

    print(f"Iniciando sincronização para o destino: {REMOTE_CONNECTION}\n")
    
    for local_path in local_folders_to_sync:
        base_name = os.path.basename(os.path.normpath(local_path))
        if local_path == artifact_folder or not base_name:
            remote_destination = REMOTE_CONNECTION
        else:
            remote_destination = os.path.join(REMOTE_CONNECTION, base_name) 

        print(f"-> Sincronizando '{local_path}' para '{remote_destination}'...")

        try:
            rclone.sync(
                src=local_path,
                dst=remote_destination,
                flags=['--progress', '--track-renames'] # -P é --progress
            )
            print(f"SUCESSO: '{local_path}' sincronizado com sucesso.\n")
            
        except subprocess.CalledProcessError as e:
            print(f"ERRO: Falha ao executar rclone sync para {local_path}.")
            print(f"Comando: {' '.join(e.cmd)}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
        except Exception as e:
            print(f"ERRO INESPERADO: Falha ao sincronizar {local_path}. Erro: {e}")

def main():
    print("INÍCIO DO PROCESSO DE SINCRONIZAÇÃO RClone")
    files_onpath()
    
    folders_to_sync = process_files() 
    
    select_files(folders_to_sync) 
    print("--- PROCESSO DE SINCRONIZAÇÃO CONCLUÍDO ---")

if __name__ == "__main__":
    main()