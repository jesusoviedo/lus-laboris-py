#!/usr/bin/env python3
"""
Google Cloud Platform Utilities for lus-laboris-py project

This script provides utilities for managing GCP resources, specifically
for creating storage buckets needed for Terraform state management.

Usage:
    uv run gcp_utils.py gcs-create <bucket_name>
    uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state
    
    # Alternative (if dependencies are installed globally):
    python3 gcp_utils.py gcs-create <bucket_name>
"""

import argparse
from google.cloud import storage
from google.cloud.exceptions import Conflict
import sys
import os
import glob
from pathlib import Path
from typing import Optional

# Supported actions
TUP_TIPO_ACCION = ("gcs-create", "gcs-list", "gcs-delete")

def params() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Utilidades Google Cloud Platform para lus-laboris-py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Create a bucket for Terraform state
        uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state
        
        # List all buckets
        uv run gcp_utils.py gcs-list
        
        # Delete a bucket (use with caution)
        uv run gcp_utils.py gcs-delete py-labor-law-rag-terraform-state
        """
    )
    
    parser.add_argument(
        "action", 
        type=str, 
        choices=TUP_TIPO_ACCION, 
        help="Tipo de acción a realizar"
    )
    parser.add_argument(
        "bucket_name", 
        type=str, 
        help="Nombre del bucket", 
        nargs="?"
    )
    parser.add_argument(
        "--location", 
        type=str, 
        default="southamerica-east1",
        help="Ubicación del bucket (default: southamerica-east1)"
    )
    parser.add_argument(
        "--project-id", 
        type=str, 
        help="ID del proyecto GCP (si no se especifica, usa el proyecto por defecto)"
    )
    
    args = parser.parse_args()
    
    # Validate required arguments
    if args.action in [TUP_TIPO_ACCION[0], TUP_TIPO_ACCION[2]] and not args.bucket_name:
        parser.error(f"El argumento 'bucket_name' es obligatorio cuando la acción es '{args.action}'")
    
    return args

def get_project_id_from_credentials(project_id: Optional[str] = None) -> Optional[str]:
    """Get the GCP project ID from the JSON credentials file"""
    if project_id:
        return project_id
    
    # Get from credentials file
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        try:
            import json
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                if 'project_id' in creds:
                    return creds['project_id']
                else:
                    print("❌ El archivo de credenciales no contiene 'project_id'")
                    print(f"   Archivo: {credentials_path}")
                    print("💡 Asegúrate de que el archivo JSON incluya el campo 'project_id'")
        except (json.JSONDecodeError, KeyError, IOError) as e:
            print(f"❌ Error al leer el archivo de credenciales: {e}")
            print(f"   Archivo: {credentials_path}")
    
    print("❌ No se pudo obtener el project_id del archivo de credenciales")
    print("💡 Verifica que:")
    print("   1. GOOGLE_APPLICATION_CREDENTIALS esté configurada correctamente")
    print("   2. El archivo JSON existe y es válido")
    print("   3. El archivo JSON contiene el campo 'project_id'")
    
    return None

def setup_gcp_credentials() -> bool:
    """Setup GCP credentials by searching for JSON files in .gcpcredentials/ folder"""
    # Check if GOOGLE_APPLICATION_CREDENTIALS is already set
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print(f"✅ Variable GOOGLE_APPLICATION_CREDENTIALS ya está configurada: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        return True
    
    # Look for .gcpcredentials folder in current directory and parent directories
    current_dir = Path.cwd()
    search_paths = [current_dir, current_dir.parent, current_dir.parent.parent]
    
    credentials_file = None
    
    for search_path in search_paths:
        gcp_credentials_dir = search_path / '.gcpcredentials'
        if gcp_credentials_dir.exists() and gcp_credentials_dir.is_dir():
            print(f"🔍 Buscando credenciales en: {gcp_credentials_dir}")
            
            # Look for JSON files in the directory
            json_files = list(gcp_credentials_dir.glob('*.json'))
            
            if json_files:
                # If multiple JSON files, prefer the one with 'service-account' in the name
                if len(json_files) == 1:
                    credentials_file = json_files[0]
                else:
                    # Look for service account file first
                    service_account_files = [f for f in json_files if 'service-account' in f.name.lower()]
                    if service_account_files:
                        credentials_file = service_account_files[0]
                    else:
                        # Use the first JSON file found
                        credentials_file = json_files[0]
                
                print(f"📁 Archivo de credenciales encontrado: {credentials_file.name}")
                break
    
    if credentials_file:
        # Set the environment variable
        credentials_path = str(credentials_file.absolute())
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        print(f"✅ Variable GOOGLE_APPLICATION_CREDENTIALS configurada: {credentials_path}")
        return True
    else:
        print("⚠️  No se encontraron archivos JSON en .gcpcredentials/")
        print("💡 Asegúrate de tener un archivo JSON de cuenta de servicio en:")
        print("   - .gcpcredentials/ (directorio actual)")
        print("   - ../.gcpcredentials/ (directorio padre)")
        print("   - ../../.gcpcredentials/ (directorio abuelo)")
        return False

def check_credentials() -> bool:
    """Check if GCP credentials are available"""
    try:
        # Try to create a client to check credentials
        storage.Client()
        return True
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        print("💡 Asegúrate de tener configuradas las credenciales de GCP:")
        print("   1. Archivo JSON de cuenta de servicio en .gcpcredentials/")
        print("   2. Variable de entorno GOOGLE_APPLICATION_CREDENTIALS")
        print("   3. O ejecutar 'gcloud auth application-default login'")
        return False

def create_bucket(bucket_name: str, location: str = "southamerica-east1", project_id: Optional[str] = None) -> bool:
    """Create a Google Cloud Storage bucket"""
    try:
        # Get project ID from credentials file
        project_id = get_project_id_from_credentials(project_id)
        if not project_id:
            print("💡 Opciones para resolver:")
            print("   1. Usar --project-id para especificar el proyecto")
            print("   2. Verificar que el archivo JSON de credenciales contenga 'project_id'")
            return False
        
        print(f"🏗️  Usando proyecto: {project_id}")
        storage_client = storage.Client(project=project_id)
        
        # Check if bucket already exists
        try:
            bucket = storage_client.get_bucket(bucket_name)
            print(f"⚠️  El bucket '{bucket_name}' ya existe.")
            print(f"   Ubicación: {bucket.location}")
            print(f"   Proyecto: {bucket.project_number}")
            return True
        except Exception:
            pass  # Bucket doesn't exist, continue with creation
        
        # Create bucket
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"✅ Bucket '{bucket.name}' creado exitosamente.")
        print(f"   Ubicación: {bucket.location}")
        print(f"   Proyecto: {bucket.project_number}")
        print(f"   URL: https://console.cloud.google.com/storage/browser/{bucket_name}")
        
        # Enable versioning for Terraform state
        bucket.versioning_enabled = True
        bucket.patch()
        print(f"✅ Versionado habilitado para el bucket '{bucket_name}'")
        
        return True
        
    except Conflict:
        print(f"⚠️  El bucket '{bucket_name}' ya existe.")
        return True
    except Exception as e:
        print(f"❌ Error al crear el bucket: {e}")
        return False

def list_buckets(project_id: Optional[str] = None) -> bool:
    """List all buckets in the project"""
    try:
        # Get project ID from credentials file
        project_id = get_project_id_from_credentials(project_id)
        if not project_id:
            print("💡 Opciones para resolver:")
            print("   1. Usar --project-id para especificar el proyecto")
            print("   2. Verificar que el archivo JSON de credenciales contenga 'project_id'")
            return False
        
        print(f"🏗️  Listando buckets del proyecto: {project_id}")
        storage_client = storage.Client(project=project_id)
        buckets = list(storage_client.list_buckets())
        
        if not buckets:
            print("📭 No se encontraron buckets en el proyecto.")
            return True
            
        print(f"📦 Buckets encontrados ({len(buckets)}):")
        print("-" * 80)
        for bucket in buckets:
            print(f"  • {bucket.name}")
            print(f"    Ubicación: {bucket.location}")
            print(f"    Creado: {bucket.time_created}")
            print(f"    Versionado: {'Sí' if bucket.versioning_enabled else 'No'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al listar buckets: {e}")
        return False

def delete_bucket(bucket_name: str, project_id: Optional[str] = None) -> bool:
    """Delete a Google Cloud Storage bucket (use with caution)"""
    try:
        # Get project ID from credentials file
        project_id = get_project_id_from_credentials(project_id)
        if not project_id:
            print("💡 Opciones para resolver:")
            print("   1. Usar --project-id para especificar el proyecto")
            print("   2. Verificar que el archivo JSON de credenciales contenga 'project_id'")
            return False
        
        print(f"🏗️  Eliminando bucket del proyecto: {project_id}")
        storage_client = storage.Client(project=project_id)
        
        # Check if bucket exists
        try:
            bucket = storage_client.get_bucket(bucket_name)
        except Exception:
            print(f"⚠️  El bucket '{bucket_name}' no existe.")
            return True
        
        # Check if bucket is empty
        blobs = list(bucket.list_blobs())
        if blobs:
            print(f"⚠️  El bucket '{bucket_name}' no está vacío ({len(blobs)} objetos).")
            print("   Para eliminar un bucket con contenido, primero elimina todos los objetos.")
            return False
        
        # Delete bucket
        bucket.delete()
        print(f"✅ Bucket '{bucket_name}' eliminado exitosamente.")
        return True
        
    except Exception as e:
        print(f"❌ Error al eliminar el bucket: {e}")
        return False

def main() -> None:
    """Main function"""
    print("🚀 Utilidades Google Cloud Platform - lus-laboris-py")
    print("=" * 60)
    
    # Setup GCP credentials automatically
    print("🔧 Configurando credenciales de GCP...")
    if not setup_gcp_credentials():
        print("❌ No se pudieron configurar las credenciales automáticamente.")
        print("💡 Opciones alternativas:")
        print("   1. Coloca un archivo JSON en .gcpcredentials/")
        print("   2. Configura manualmente GOOGLE_APPLICATION_CREDENTIALS")
        print("   3. Ejecuta 'gcloud auth application-default login'")
        sys.exit(1)
    
    print()
    
    # Check credentials
    print("🔍 Verificando credenciales...")
    if not check_credentials():
        sys.exit(1)
    
    args = params()
    
    success = False
    
    if args.action == TUP_TIPO_ACCION[0]:  # gcs-create
        print(f"📦 Creando bucket: {args.bucket_name}")
        print(f"📍 Ubicación: {args.location}")
        if args.project_id:
            print(f"🏗️  Proyecto: {args.project_id}")
        print()
        
        success = create_bucket(
            args.bucket_name, 
            location=args.location,
            project_id=args.project_id
        )
        
    elif args.action == TUP_TIPO_ACCION[1]:  # gcs-list
        print("📋 Listando buckets...")
        print()
        success = list_buckets(project_id=args.project_id)
        
    elif args.action == TUP_TIPO_ACCION[2]:  # gcs-delete
        print(f"🗑️  Eliminando bucket: {args.bucket_name}")
        print("⚠️  Esta acción es irreversible!")
        print()
        
        # Ask for confirmation
        confirm = input("¿Estás seguro? Escribe 'yes' para confirmar: ")
        if confirm.lower() != 'yes':
            print("❌ Operación cancelada.")
            return
        
        success = delete_bucket(args.bucket_name, project_id=args.project_id)
    
    if success:
        print("\n✅ Operación completada exitosamente.")
    else:
        print("\n❌ La operación falló.")
        sys.exit(1)

if __name__ == "__main__":
    main()
