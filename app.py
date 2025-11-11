import zipfile
import subprocess
from rclone_python import rclone
from rclone_python.remote_types import RemoteTypes
import os
import glob
import hashlib

artifact_folder = os.environ.get("ARTIFACT_FOLDER", "./workflow-github-action")
remote_connection = "https://grupomateus-my.sharepoint.com/personal/guilherme_macedo_grupomateus_com/Documents/Analise%Encartes%Concorrencia"


# 1. Name of your configured Rclone remote (e.g., set up via 'rclone config')
#RCLONE_REMOTE_NAME = 'onedrive_remote' 

# 2. The *destination* folder on your OneDrive where the local folders will be uploaded
#ONEDRIVE_DESTINATION_FOLDER = 'extracted_data'

#(1) process files and extract them for repository
def process_files():
    print(f"Procurando por arquivos .zip em {artifact_folder}...")
    zip_pattern = os.path.join(artifact_folder, "**", "*.zip")
    zip_files = glob.glob(zip_pattern, recursive=True)
    extracted_dirs = []

    if not zip_files:
        print("Nenhum arquivo .zip encontrado. Verificando arquivos existentes...")
    else:
        print(f"Encontrados {len(zip_files)} arquivos .zip. Extraindo...")
        for zip_path in zip_files:
            try:
                extract_directory = os.path.dirname(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_directory)
                    extracted_dirs.append(extract_directory)
                print(f"Extraído: {zip_path} -> {extract_directory}")
            except zipfile.BadZipFile:
                print(f"Erro: {zip_path} não é um arquivo zip válido ou está corrompido.")
            except Exception as e:
                print(f"Erro ao extrair {zip_path}: {e}")
        print("Extração de Zips concluída.\n")  

#(2) Verify if the files is on path (identiticator erros)
def files_onpath():
    print(f"Identificando arquivos na pasta {remote_connection}...")
    os.path.join(artifact_folder)
    
    if not artifact_folder:
        print("Nenhuma pasta encontrada.")
    else:
        print(f"Pasta encontrada {artifact_folder}")
        for files in os.listdir(artifact_folder):
            try:
                print(f"Procurando arquivos na pasta")
                if os.path.isfile(artifact_folder): #identificando se os arquivos estão na pasta
                    print(f"Arquivos encontrados {files}")
            except:
                print(f"Arquivos não encontrados na pasta {artifact_folder}")

#(3) identificator of same files (identificator erros)
def same_files(files):
    print(f"Identificando se os arquivos são iguais na pasta {remote_connection}...")
    
    try:
        for i in files(artifact_folder):
            encode = hashlib.sha512() #encodando os arquivos com algoritmo (sha512)
            files = i(encode)
            hex_digest = encode.hexdigest() #pegando o sha512 de cada arquivo
            if files == hex_digest:
                print(f"Arquivos iguais {files}")
    except:
        print(f"Arquivos não são iguais {files}") 
        
#(4) select all files and upload
def select_files(extracted_dirs):
    for pastas in os.walk(extracted_dirs):
        print(f"Selecionando todos as pastas {pastas}")
        
        try:
            os.path.join(extracted_dirs)
            command = [
                'rclone',
                'sync',
                extracted_dirs,
                remote_connection,
                '-P'
            ]
            print(f"Colocando todos os arquivos no OneDrive")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Upado todos as pastas para o OneDrive {result}")
        
        except subprocess.CalledProcessError as e:
            print(f"Não foi possivel executar o comando {result}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
    
    
#(5) create folders according to (data)
def create_folders():
       

#(6) main_function (rclone)