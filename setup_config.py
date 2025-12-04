#!/usr/bin/env python3
"""
Setup Configuration Script for VeloCloud API

This script prompts for common configuration values and stores them
securely in a .env file for use by other scripts in this repository.
"""

import os
import getpass
from pathlib import Path


def read_existing_env():
    """Read existing .env file and return config dictionary."""
    env_path = Path(__file__).parent / '.env'
    config = {}

    if not env_path.exists():
        return config

    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Could not read existing .env file: {e}")

    return config


def prompt_for_config():
    """Prompt user for configuration values."""
    print("=" * 60)
    print("VeloCloud API Configuration Setup")
    print("=" * 60)

    # Read existing configuration
    existing_config = read_existing_env()

    if existing_config:
        print("\n✓ Found existing .env file with configuration.")
        print("  Press Enter to keep existing values, or type new value to update.\n")
    else:
        print("\nThis script will create a .env file with your configuration.")
        print("The .env file will NOT be committed to git.\n")

    config = {}

    # VCO URL
    print("1. VCO Hostname or IP Address")
    print("   Examples: vco123.velocloud.net or 192.168.1.100")
    existing_host = existing_config.get('VCO_HOSTNAME', '')
    if existing_host:
        print(f"   Current value: {existing_host}")
        vco_host = input("   Enter VCO hostname/IP (or press Enter to keep): ").strip()
        config['VCO_HOSTNAME'] = vco_host if vco_host else existing_host
    else:
        vco_host = input("   Enter VCO hostname/IP: ").strip()
        config['VCO_HOSTNAME'] = vco_host

    # API Token
    print("\n2. API Token")
    print("   Enter just the token value (the 'Token ' prefix will be added automatically)")
    print("   Note: Obtain your API token from the VCO web interface")
    existing_token = existing_config.get('VCO_TOKEN', '')
    if existing_token:
        # Strip "Token " prefix if present for display
        token_value = existing_token[6:] if existing_token.startswith('Token ') else existing_token
        masked_token = token_value[:10] + "..." if len(token_value) > 10 else "***"
        print(f"   Current value: {masked_token}")
        token = getpass.getpass("   Enter API token value (or press Enter to keep, input hidden): ").strip()
        if token:
            # Add "Token " prefix if not already present
            config['VCO_TOKEN'] = f"Token {token}" if not token.startswith('Token ') else token
        else:
            config['VCO_TOKEN'] = existing_token
    else:
        token = getpass.getpass("   Enter API token value (input hidden): ").strip()
        if token:
            # Add "Token " prefix if not already present
            config['VCO_TOKEN'] = f"Token {token}" if not token.startswith('Token ') else token

    # Enterprise ID (optional)
    print("\n3. Enterprise ID (optional - can be provided per script)")
    existing_ent_id = existing_config.get('VCO_ENTERPRISE_ID', '')
    if existing_ent_id:
        print(f"   Current value: {existing_ent_id}")
        enterprise_id = input("   Enter default Enterprise ID (or press Enter to keep): ").strip()
        if enterprise_id:
            config['VCO_ENTERPRISE_ID'] = enterprise_id
        else:
            config['VCO_ENTERPRISE_ID'] = existing_ent_id
    else:
        enterprise_id = input("   Enter default Enterprise ID (or press Enter to skip): ").strip()
        if enterprise_id:
            config['VCO_ENTERPRISE_ID'] = enterprise_id

    # Enterprise Logical ID (optional)
    print("\n4. Enterprise Logical ID (optional - needed for API v2)")
    existing_ent_logical_id = existing_config.get('VCO_ENTERPRISE_LOGICAL_ID', '')
    if existing_ent_logical_id:
        print(f"   Current value: {existing_ent_logical_id}")
        enterprise_logical_id = input("   Enter Enterprise Logical ID (or press Enter to keep): ").strip()
        if enterprise_logical_id:
            config['VCO_ENTERPRISE_LOGICAL_ID'] = enterprise_logical_id
        else:
            config['VCO_ENTERPRISE_LOGICAL_ID'] = existing_ent_logical_id
    else:
        enterprise_logical_id = input("   Enter Enterprise Logical ID (or press Enter to skip): ").strip()
        if enterprise_logical_id:
            config['VCO_ENTERPRISE_LOGICAL_ID'] = enterprise_logical_id

    # Edge ID (optional)
    print("\n5. Edge ID (optional - default edge for testing)")
    existing_edge_id = existing_config.get('VCO_EDGE_ID', '')
    if existing_edge_id:
        print(f"   Current value: {existing_edge_id}")
        edge_id = input("   Enter default Edge ID (or press Enter to keep): ").strip()
        if edge_id:
            config['VCO_EDGE_ID'] = edge_id
        else:
            config['VCO_EDGE_ID'] = existing_edge_id
    else:
        edge_id = input("   Enter default Edge ID (or press Enter to skip): ").strip()
        if edge_id:
            config['VCO_EDGE_ID'] = edge_id

    # SSL Verification
    print("\n6. SSL Certificate Verification")
    print("   Production: True | Development/Testing: False")
    existing_ssl = existing_config.get('VCO_VERIFY_SSL', '')
    if existing_ssl:
        current_ssl = "Yes" if existing_ssl.lower() == 'true' else "No"
        print(f"   Current value: {current_ssl}")
        ssl_input = input("   Verify SSL certificates? (y/N/Enter to keep): ").strip().lower()
        if ssl_input == '':
            config['VCO_VERIFY_SSL'] = existing_ssl
        else:
            config['VCO_VERIFY_SSL'] = 'true' if ssl_input == 'y' else 'false'
    else:
        ssl_verify = input("   Verify SSL certificates? (y/N): ").strip().lower()
        config['VCO_VERIFY_SSL'] = 'true' if ssl_verify == 'y' else 'false'

    return config


def write_env_file(config):
    """Write configuration to .env file."""
    env_path = Path(__file__).parent / '.env'

    # Write .env file (overwrites existing)
    with open(env_path, 'w') as f:
        f.write("# VeloCloud API Configuration\n")
        f.write("# Generated by setup_config.py\n")
        f.write("# DO NOT commit this file to version control\n\n")

        for key, value in config.items():
            f.write(f"{key}={value}\n")

    # Set restrictive permissions (Unix/Linux/Mac)
    if os.name != 'nt':  # Not Windows
        os.chmod(env_path, 0o600)

    print(f"\n✓ Configuration saved to {env_path}")
    print(f"✓ File permissions set to restrict access")
    return True


def create_gitignore():
    """Ensure .env is in .gitignore."""
    gitignore_path = Path(__file__).parent / '.gitignore'

    # Read existing .gitignore if it exists
    existing_lines = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_lines = f.read().splitlines()

    # Check if .env is already ignored
    if '.env' not in existing_lines:
        with open(gitignore_path, 'a') as f:
            if existing_lines and not existing_lines[-1].strip():
                pass  # Already has newline
            elif existing_lines:
                f.write('\n')
            f.write('# Environment variables (contains secrets)\n')
            f.write('.env\n')
        print(f"✓ Added .env to .gitignore")
    else:
        print(f"✓ .env already in .gitignore")


def main():
    """Main setup function."""
    try:
        # Read existing config to compare later
        existing_config = read_existing_env()

        config = prompt_for_config()

        if write_env_file(config):
            create_gitignore()

            print("\n" + "=" * 60)
            print("Setup Complete!")
            print("=" * 60)

            # Show what was configured
            print("\nConfigured values:")
            print(f"  VCO Hostname: {config.get('VCO_HOSTNAME', 'not set')}")
            print(f"  API Token: {'***' if config.get('VCO_TOKEN') else 'not set'}")
            print(f"  Enterprise ID: {config.get('VCO_ENTERPRISE_ID', 'not set')}")
            print(f"  Enterprise Logical ID: {config.get('VCO_ENTERPRISE_LOGICAL_ID', 'not set')}")
            print(f"  Edge ID: {config.get('VCO_EDGE_ID', 'not set')}")
            ssl_value = "Yes" if config.get('VCO_VERIFY_SSL', 'false').lower() == 'true' else "No"
            print(f"  SSL Verify: {ssl_value}")

            print("\nNext steps:")
            print("1. Install python-dotenv: pip install python-dotenv")
            print("2. Use the config.py module in your scripts to load these values")
            print("3. See .env.example for the configuration format")
            print("\nExample usage in a script:")
            print("  from config import get_config")
            print("  config = get_config()")
            print("  token = config['token']")
            print("  vco_url = config['vco_url']")

    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nError during setup: {e}")


if __name__ == "__main__":
    main()
