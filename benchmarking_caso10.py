import os
import time
import h5py
import numpy as np
import boto3
from moto import mock_aws

# Nombre del bucket y del archivo para el Caso 10
BUCKET_NAME = "bucket-grafo-caso10"
FILE_NAME = "grafo_social_caso10.h5"

# 1. Crear dataset .H5 de prueba para el Caso 10 (Grafos Sociales)
def crear_archivo_h5(nombre_archivo, tamano_mb=50):
    print(f" Generando dataset .H5 ({tamano_mb} MB)...")
    num_elementos = (tamano_mb * 1024 * 1024) // 8
    datos = np.random.rand(num_elementos)
    
    with h5py.File(nombre_archivo, 'w') as f:
        f.create_dataset("matriz_interacciones", data=datos, compression="gzip")
    
    peso_real = os.path.getsize(nombre_archivo) / (1024 * 1024)
    print(f" Archivo '{nombre_archivo}' listo ({peso_real:.2f} MB).\n")

# 2. Benchmarking S3 simulado localmente con @mock_aws (Sin dependencias externas)
@mock_aws
def ejecutar_benchmark_s3(file_path):
    print("--- INICIANDO BENCHMARKING DE S3 (ENTORNO LOCAL) ---")
    
    # Cliente de S3 simulado en memoria
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket=BUCKET_NAME)

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    object_name = os.path.basename(file_path)

    # Medir Subida (PUT)
    start_time = time.time()
    s3_client.upload_file(file_path, BUCKET_NAME, object_name)
    upload_time = time.time() - start_time
    upload_throughput = file_size_mb / upload_time if upload_time > 0 else file_size_mb / 0.001

    print(f"  Subida S3 completada en {upload_time:.4f} s | Throughput: {upload_throughput:.2f} MB/s")

    # Medir Descarga (GET)
    download_path = "descargado_" + object_name
    start_time = time.time()
    s3_client.download_file(BUCKET_NAME, object_name, download_path)
    download_time = time.time() - start_time
    download_throughput = file_size_mb / download_time if download_time > 0 else file_size_mb / 0.001

    print(f"  Descarga S3 completada en {download_time:.4f} s | Throughput: {download_throughput:.2f} MB/s")

    # Limpieza del archivo descargado
    if os.path.exists(download_path):
        os.remove(download_path)

# 3. Proyección de Costos (Requisito de la rúbrica)
def mostrar_proyeccion_costos(gb_totales=15):
    print("\n==========================================")
    print(f" PROYECCIÓN DE COSTOS MENSUALES ({gb_totales} GB)")
    print("==========================================")
    costo_s3_std = gb_totales * 0.023
    costo_azure_hot = gb_totales * 0.018
    print(f" AWS S3 Standard:     ${costo_s3_std:.3f} USD / mes")
    print(f" Azure Blob Hot Tier: ${costo_azure_hot:.3f} USD / mes")

if __name__ == "__main__":
    if not os.path.exists(FILE_NAME):
        crear_archivo_h5(FILE_NAME, tamano_mb=50)
    
    ejecutar_benchmark_s3(FILE_NAME)
    mostrar_proyeccion_costos(gb_totales=15)