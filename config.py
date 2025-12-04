"""
VeloCloud API Configuration Helper

This module loads configuration from environment variables (typically from .env file)
and provides a simple interface for scripts to access VCO credentials and settings.

Usage:
    from config import get_config

    config = get_config()
    # Or with overrides:
    config = get_config(enterprise_id=456)

    # Access values:
    headers = {"Content-Type": "application/json", "Authorization": config['token']}
    vco_url = config['vco_url']
"""

import os
import sys
from pathlib import Path


def load_dotenv():
    """
    Load environment variables from .env file.
    Uses python-dotenv if available, otherwise reads file manually.
    """
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        return False

    try:
        # Try to use python-dotenv if available
        from dotenv import load_dotenv as dotenv_load
        dotenv_load(env_path)
        return True
    except ImportError:
        # Fallback: manually parse .env file
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True


def get_config(enterprise_id=None, enterprise_logical_id=None, edge_id=None, verify_ssl=None):
    """
    Get VeloCloud API configuration from environment variables.

    Args:
        enterprise_id: Override default enterprise ID (optional)
        enterprise_logical_id: Override default enterprise logical ID (optional)
        edge_id: Override default edge ID (optional)
        verify_ssl: Override SSL verification setting (optional)

    Returns:
        dict: Configuration dictionary with keys:
            - token: API authentication token
            - vco_hostname: VCO hostname/IP
            - vco_url_v1: Full URL for REST API v1
            - vco_url_v2: Full URL for REST API v2
            - enterprise_id: Enterprise ID (if set)
            - enterprise_logical_id: Enterprise Logical ID (if set)
            - edge_id: Edge ID (if set)
            - verify_ssl: Boolean for SSL verification
            - headers: Pre-built headers dict for requests

    Raises:
        SystemExit: If required environment variables are missing
    """
    # Load .env file
    load_dotenv()

    # Get required values
    token = os.getenv('VCO_TOKEN')
    hostname = os.getenv('VCO_HOSTNAME')

    if not token or not hostname:
        print("Error: Missing required configuration!", file=sys.stderr)
        print("\nPlease run setup_config.py to configure your environment:", file=sys.stderr)
        print("  python setup_config.py\n", file=sys.stderr)
        print("Or manually create a .env file with:", file=sys.stderr)
        print("  VCO_TOKEN=Token your-token-here", file=sys.stderr)
        print("  VCO_HOSTNAME=your-vco-hostname\n", file=sys.stderr)
        sys.exit(1)

    # Get optional values with overrides
    ent_id = enterprise_id or os.getenv('VCO_ENTERPRISE_ID')
    ent_logical_id = enterprise_logical_id or os.getenv('VCO_ENTERPRISE_LOGICAL_ID')
    edg_id = edge_id or os.getenv('VCO_EDGE_ID')

    # SSL verification (default to False for backward compatibility)
    if verify_ssl is not None:
        ssl_verify = verify_ssl
    else:
        ssl_verify = os.getenv('VCO_VERIFY_SSL', 'false').lower() == 'true'

    # Build URLs
    vco_url_v1 = f'https://{hostname}/portal/rest/'
    vco_url_v2 = f'https://{hostname}/api/sdwan/v2/'

    # Build headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    # Return configuration
    config = {
        'token': token,
        'vco_hostname': hostname,
        'vco_url_v1': vco_url_v1,
        'vco_url_v2': vco_url_v2,
        'headers': headers,
        'verify_ssl': ssl_verify
    }

    # Add optional values if present
    if ent_id:
        try:
            config['enterprise_id'] = int(ent_id)
        except ValueError:
            print(f"Warning: Invalid enterprise_id '{ent_id}', must be numeric", file=sys.stderr)

    if ent_logical_id:
        config['enterprise_logical_id'] = ent_logical_id

    if edg_id:
        try:
            config['edge_id'] = int(edg_id)
        except ValueError:
            print(f"Warning: Invalid edge_id '{edg_id}', must be numeric", file=sys.stderr)

    return config


def check_config():
    """
    Check if configuration is set up properly.

    Returns:
        bool: True if configuration exists and is valid, False otherwise
    """
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        return False

    load_dotenv()

    token = os.getenv('VCO_TOKEN')
    hostname = os.getenv('VCO_HOSTNAME')

    return bool(token and hostname)


if __name__ == "__main__":
    """Test configuration when run directly."""
    print("Testing VeloCloud API Configuration...\n")

    if not check_config():
        print("❌ Configuration not found or incomplete")
        print("\nRun setup_config.py to configure:")
        print("  python setup_config.py")
        sys.exit(1)

    try:
        config = get_config()
        print("✓ Configuration loaded successfully!\n")
        print("Configuration values:")
        print(f"  VCO Hostname: {config['vco_hostname']}")
        print(f"  API v1 URL: {config['vco_url_v1']}")
        print(f"  API v2 URL: {config['vco_url_v2']}")
        print(f"  Token: {config['token'][:15]}..." if len(config['token']) > 15 else "  Token: (set)")
        print(f"  SSL Verify: {config['verify_ssl']}")

        if 'enterprise_id' in config:
            print(f"  Enterprise ID: {config['enterprise_id']}")
        else:
            print("  Enterprise ID: (not set)")

        if 'enterprise_logical_id' in config:
            print(f"  Enterprise Logical ID: {config['enterprise_logical_id']}")
        else:
            print("  Enterprise Logical ID: (not set)")

        if 'edge_id' in config:
            print(f"  Edge ID: {config['edge_id']}")
        else:
            print("  Edge ID: (not set)")

        print("\n✓ Configuration is valid and ready to use!")

    except SystemExit:
        print("❌ Configuration test failed")
        sys.exit(1)
