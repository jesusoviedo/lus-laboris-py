#!/usr/bin/env python3
"""
JWT Token Generator

This script generates JWT tokens using RSA public/private key pairs.
It reads configuration from environment variables and provides a simple
command-line interface for token generation.

Usage:
    python generate_jwt_token.py --username admin 
    python generate_jwt_token.py --username admin --expiry 48
    python generate_jwt_token.py --username admin --output token.txt
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Colores para la salida
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    """Print success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Print error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Print info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


class JWTTokenGenerator:
    """JWT token generator using RSA keys"""
    
    def __init__(self):
        # Get project root directory (parent of utils directory)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        
        # Get key paths from environment variables
        private_path = os.getenv("JWT_PRIVATE_KEY_PATH", "keys/private_key.pem")
        public_path = os.getenv("JWT_PUBLIC_KEY_PATH", "keys/public_key.pem")
        
        # Convert relative paths to absolute paths relative to project root
        self.private_key_path = private_path if os.path.isabs(private_path) else os.path.join(self.project_root, private_path)
        self.public_key_path = public_path if os.path.isabs(public_path) else os.path.join(self.project_root, public_path)
        
        self.default_expiry_minutes = int(os.getenv("JWT_TOKEN_EXPIRY_MINUTES", "15"))
        self.algorithm = "RS256"
        
        # Keys will be loaded on demand
        self.private_key = None
        self.public_key = None
        
    def _load_private_key(self):
        """Load RSA private key from file"""
        if self.private_key is not None:
            return self.private_key
            
        try:
            with open(self.private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            print_info(f"Clave privada cargada desde: {self.private_key_path}")
            return self.private_key
        except FileNotFoundError:
            print_error(f"Archivo de clave privada no encontrado: {self.private_key_path}")
            print_error("Por favor ejecuta generate_jwt_keys.sh primero para generar las claves")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error al cargar la clave privada: {e}")
            sys.exit(1)
    
    def _load_public_key(self):
        """Load RSA public key from file"""
        if self.public_key is not None:
            return self.public_key
            
        try:
            with open(self.public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(), backend=default_backend()
                )
            print_info(f"Clave pública cargada desde: {self.public_key_path}")
            return self.public_key
        except FileNotFoundError:
            print_error(f"Archivo de clave pública no encontrado: {self.public_key_path}")
            print_error("Por favor ejecuta generate_jwt_keys.sh primero para generar las claves")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error al cargar la clave pública: {e}")
            sys.exit(1)
    
    def generate_token(
        self, 
        username: str, 
        expiry_minutes: Optional[int] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a JWT token with the given credentials and claims
        
        Args:
            username: Username for the token
            expiry_minutes: Token expiry in minutes (uses default if None)
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT token string
            
        Note:
            JWT tokens are decodable and should not contain sensitive information.
        """
        # Calculate expiry time
        if expiry_minutes is None:
            expiry_minutes = self.default_expiry_minutes
            
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=expiry_minutes)
        
        # Prepare payload (NO sensitive data like passwords)
        # JWT tokens are decodable and should only contain non-sensitive claims
        payload = {
            "sub": username,  # Subject (user identifier)
            "username": username,
            "iat": now,  # Issued at
            "exp": expiry,  # Expiry time
            "iss": "lus-laboris-api",  # Issuer
            "aud": "lus-laboris-client"  # Audience
        }
        
        # Add additional claims if provided
        if additional_claims:
            payload.update(additional_claims)
        
        # Generate token
        try:
            private_key = self._load_private_key()  # Load private key only when needed
            token = jwt.encode(payload, private_key, algorithm=self.algorithm)
            print_success(f"Token generado exitosamente para usuario: {username}")
            print_info(f"Token expira en: {expiry.strftime('%Y-%m-%d %H:%M:%S UTC')} ({expiry_minutes} minutos)")
            return token
        except Exception as e:
            print_error(f"Error al generar token: {e}")
            sys.exit(1)
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT token using the public key
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
        """
        try:
            # Load public key only when needed
            public_key = self._load_public_key()
            
            # Decode and validate token
            payload = jwt.decode(
                token, 
                public_key, 
                algorithms=[self.algorithm],
                audience="lus-laboris-client",
                issuer="lus-laboris-api"
            )
            
            print_success("Validación de token exitosa")
            return payload
            
        except FileNotFoundError:
            print_error(f"Archivo de clave pública no encontrado: {self.public_key_path}")
            sys.exit(1)
        except jwt.ExpiredSignatureError:
            print_error("El token ha expirado")
            sys.exit(1)
        except jwt.InvalidTokenError as e:
            print_error(f"Token inválido: {e}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error al validar token: {e}")
            sys.exit(1)


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Generar tokens JWT para autenticación de la API Lus Laboris",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Ejemplos:
        %(prog)s --username admin
        %(prog)s --username admin --expiry 120
        %(prog)s --username admin --output token.txt
        %(prog)s --username admin --claims '{"role": "admin", "permissions": ["read", "write"]}'
        %(prog)s --validate --token "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        """
    )
    
    # Token generation arguments
    parser.add_argument(
        "--username", 
        type=str, 
        help="Nombre de usuario para el token"
    )
    
    parser.add_argument(
        "--expiry", 
        type=int, 
        help="Expiración del token en minutos (por defecto: 15)"
    )
    
    parser.add_argument(
        "--claims", 
        type=str, 
        help="Claims adicionales como string JSON (ej., '{\"role\": \"admin\"}')"
    )

    parser.add_argument(
        "--output", 
        type=str, 
        help="Archivo de salida para guardar el token (opcional)"
    )
    
    # Token validation arguments
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validar un token existente"
    )
    parser.add_argument(
        "--token", 
        type=str, 
        help="Token a validar (requerido con --validate)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize token generator
    try:
        generator = JWTTokenGenerator()
    except SystemExit:
        return 1
    
    # Handle validation mode
    if args.validate:
        if not args.token:
            print_error("--token es requerido cuando se usa --validate")
            return 1
        
        try:
            payload = generator.validate_token(args.token)
            print_success("¡Token es válido!")
            print(f"{Colors.CYAN}📋 Payload del token:{Colors.END}")
            print(json.dumps(payload, indent=2, default=str))
            return 0
        except SystemExit:
            return 1
    
    # Handle generation mode
    if not args.username:
        print_error("--username es requerido para la generación de tokens")
        return 1
    
    # Parse additional claims if provided
    additional_claims = None
    if args.claims:
        try:
            additional_claims = json.loads(args.claims)
        except json.JSONDecodeError as e:
            print_error(f"JSON inválido en --claims: {e}")
            return 1
    
    # Generate token
    try:
        token = generator.generate_token(
            username=args.username,
            expiry_minutes=args.expiry,
            additional_claims=additional_claims
        )
        
        # Output token
        print(f"\n{Colors.BOLD}🔑 Token JWT Generado Exitosamente!{Colors.END}")
        print("=" * 50)
        print(token)
        print("=" * 50)
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(token)
                print_success(f"Token guardado en: {args.output}")
            except Exception as e:
                print_error(f"Error al guardar token en archivo: {e}")
                return 1
        
        # Show usage instructions
        print(f"\n{Colors.CYAN}📖 Instrucciones de Uso:{Colors.END}")
        print("1. Usa este token en el header Authorization:")
        print(f"   Authorization: Bearer {token[:50]}...")
        print("\n2. Prueba el token con:")
        print(f"   python {sys.argv[0]} --validate --token \"{token}\"")
        
        return 0
        
    except SystemExit:
        return 1


if __name__ == "__main__":
    sys.exit(main())
