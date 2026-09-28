import os
import time
from azure.storage.blob import BlobServiceClient

ACCOUNT_NAME = "stgredesdazh2026"
SAS_TOKEN = "se=2026-09-26T00%3A00%3A00Z&sp=rwdlac&sv=2026-04-06&ss=b&srt=sco&sig=FdQ73gHIetecEvsXd2EyTiPS4%2BGPf8YP8X8WaUYS1Dg%3D"

CONTAINER_NAME = "practica-redes"
FILE_SIZE_MB = 10  # Tamaño del archivo de prueba en MB

ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"


def probar_rendimiento_red():
    print("Iniciando cliente de Azure Blob Storage con SAS Token...")

    # Cliente autenticado mediante SAS Token
    blob_service_client = BlobServiceClient(
        account_url=ACCOUNT_URL, credential=SAS_TOKEN
    )

    # 1. Obtener o crear contenedor
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
        print(f"Contenedor '{CONTAINER_NAME}' creado exitosamente.")
    except Exception:
        print(f"Conectado al contenedor '{CONTAINER_NAME}'.")

    # 2. Medición de Latencia (RTT)
    print("\n[1/3] Midiendo Latencia (RTT)...")
    small_data = os.urandom(1024)  # 1 KB
    rtt_blob_client = container_client.get_blob_client("rtt_ping.bin")

    t_inicio = time.perf_counter()
    rtt_blob_client.upload_blob(small_data, overwrite=True)
    t_fin = time.perf_counter()

    latencia_ms = (t_fin - t_inicio) * 1000
    rtt_blob_client.delete_blob()

    # 3. Medición de Subida (Upload)
    print(f"[2/3] Generando {FILE_SIZE_MB} MB y subiendo a 'westus'...")
    data_payload = os.urandom(FILE_SIZE_MB * 1024 * 1024)
    blob_client = container_client.get_blob_client("test_redes_10mb.bin")

    t_inicio = time.perf_counter()
    blob_client.upload_blob(data_payload, overwrite=True)
    t_fin = time.perf_counter()

    tiempo_subida = t_fin - t_inicio
    v_subida_mbs = FILE_SIZE_MB / tiempo_subida
    bw_subida_mbps = (FILE_SIZE_MB * 8) / tiempo_subida

    # 4. Medición de Descarga (Download)
    print("[3/3] Midiendo descarga del archivo...")

    t_inicio = time.perf_counter()
    download_stream = blob_client.download_blob()
    _ = download_stream.readall()
    t_fin = time.perf_counter()

    tiempo_descarga = t_fin - t_inicio
    v_descarga_mbs = FILE_SIZE_MB / tiempo_descarga
    bw_descarga_mbps = (FILE_SIZE_MB * 8) / tiempo_descarga

    # Limpieza
    blob_client.delete_blob()

    # 5. Despliegue de Resultados
    print("\n" + "=" * 50)
    print("        MÉTRICAS DE RED (AZURE WESTUS)")
    print("=" * 50)
    print(f"Latencia Estimada (RTT):  {latencia_ms:.2f} ms")
    print("-" * 50)
    print(f"Tiempo de Subida:         {tiempo_subida:.2f} seg")
    print(f"Velocidad de Subida:      {v_subida_mbs:.2f} MB/s")
    print(f"Ancho de Banda Subida:    {bw_subida_mbps:.2f} Mbps")
    print("-" * 50)
    print(f"Tiempo de Descarga:       {tiempo_descarga:.2f} seg")
    print(f"Velocidad de Descarga:    {v_descarga_mbs:.2f} MB/s")
    print(f"Ancho de Banda Descarga:  {bw_descarga_mbps:.2f} Mbps")
    print("=" * 50)


if __name__ == "__main__":
    probar_rendimiento_red()