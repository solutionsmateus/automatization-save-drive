import zipfile
import subprocess
from rclone_python import rclone
from rclone_python.remote_types import RemoteTypes
import os
import glob
import hashlib

artifact_folder = os.environ.get("ARTIFACT_FOLDER", "./workflow-github-action")
remote_connection = "https://grupomateus-my.sharepoint.com/personal/guilherme_macedo_grupomateus_com/Documents/Analise%Encartes%Concorrencia"


#(1) Verify if the files is on path (identiticator erros)
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

#(2) identificator of same files (identificator erros)
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


#(3) process files and extract them for repository
def process_files():
    print(f"Procurando por arquivos .zip em {artifact_folder}...")
    zip_pattern = os.path.join(artifact_folder, "**", "*.zip")
    zip_files = glob.glob(zip_pattern, recursive=True)

    if not zip_files:
        print("Nenhum arquivo .zip encontrado. Verificando arquivos existentes...")
    else:
        print(f"Encontrados {len(zip_files)} arquivos .zip. Extraindo...")
        for zip_path in zip_files:
            try:
                extract_directory = os.path.dirname(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_directory)
                print(f"Extraído: {zip_path} -> {extract_directory}")
            except zipfile.BadZipFile:
                print(f"Erro: {zip_path} não é um arquivo zip válido ou está corrompido.")
            except Exception as e:
                print(f"Erro ao extrair {zip_path}: {e}")
        print("Extração de Zips concluída.\n")   
        
#(4) select all files



#(5) create folders according to (data)

#(6) main_function (rclone)
