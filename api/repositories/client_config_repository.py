

import os
from api.core.utils import logger
import yaml

class ClientAuthorization:
    def __init__(self, service: str, quotas: int | None):
        self.service = service
        self.quotas = quotas
    def __repr__(self):
        return f"ClientAuthorization(service={self.service}, quota={self.quotas})"

class ClientConfig:
    def __init__(
            self,
            name: str,
            client_id: str,
            client_secret: str | None = None,
            authorizations: dict[str,ClientAuthorization] | None = None):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorizations = authorizations or {}

    def __repr__(self):
        return f"ClientConfig(name={self.name}, client_id={self.client_id}, client_secret={self.client_secret}, authorizations={self.authorizations})"


class ClientsConfigException(Exception):
    """Custom exception for ServicesConfigRepository errors."""
    pass


class ClientConfigRepository:
    
    # Singleton instance to hold the services configuration
    CLIENTS: dict[str, ClientConfig] = {}

    @staticmethod
    def load_clients_config(client_file: str):
        try:
            with open(client_file) as file:
                config = yaml.load(file, Loader=yaml.SafeLoader)
                ClientConfigRepository.CLIENTS = ClientConfigRepository._parse_yaml_struct(config)
        except FileNotFoundError as e:
            logger.error(f"Configuration file {client_file} not found: {e}")
            raise ClientsConfigException(f"Configuration file {client_file} not found.")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {client_file}: {e}")
            raise ClientsConfigException(f"Error parsing YAML file {client_file}.")

    @staticmethod
    def _parse_yaml_struct(config) -> dict[str, ClientConfig]:
        """
        Parses the YAML structure and returns a dictionary with service names as keys
        and their configurations as values.
        """
        if not isinstance(config, list):
            raise ClientsConfigException("Invalid configuration format. Expected a list of clients.")
        
        clients = {}
        for config_item in config:
            if not isinstance(config_item, dict):
                raise ClientsConfigException(f"Invalid configuration item at: {config_item}. Expected a dictionary.")
            if 'name' not in config_item:
                raise ClientsConfigException("Each client configuration must contain a 'name' key.")
            client_name = config_item['name']
            if 'client_id' not in config_item:
                raise ClientsConfigException("Each client configuration must contain a 'client_id' key.")
            client_id = config_item['client_id']
            client_secret = config_item.get('client_secret', None)
            client_secret = ClientConfigRepository._resolve_secret(client_secret)

            authorisations_part = config_item.get('authorizations', [])
            authorisations: dict[str,ClientAuthorization] = {}
            if not isinstance(authorisations_part, list):
                raise ClientsConfigException(f"Invalid authorizations format for client {client_name}. Expected a list.")

            for auth in authorisations_part:
                if not isinstance(auth, dict):
                    raise ClientsConfigException(f"Invalid authorization item for client {client_name}: {auth}. Expected a dictionary.")
                if 'service' not in auth:
                    raise ClientsConfigException("Each authorization must contain a 'service' key.")
                service_name = auth['service']
                quotas = auth.get('quotas', None)
                authorisations[service_name] = ClientAuthorization(service=service_name, quotas=quotas)

            client_config = ClientConfig(
                name=client_name,
                client_id=client_id,
                client_secret=client_secret,
                authorizations=authorisations
            )
            clients[client_name] = client_config
        return clients

    @staticmethod
    def _resolve_secret(secret: str | None) -> str | None:
        """
        Resolves the client secret, which can be a string or None.
        If the secret is None, it returns None.
        """
        if secret is None:
            return None
        if not secret.startswith("$"):
            return secret
        
        env_secret = os.environ.get(secret[1:])
        if env_secret is None:
            raise ClientsConfigException(f"Env variable : '{secret}' not found.")
        
        return env_secret

    def all_clients(self) -> dict[str, ClientConfig]:
        """
        Returns all clients configurations.
        """
        if ClientConfigRepository.CLIENTS is None:
            raise ClientsConfigException("Clients configuration not loaded. Call load_clients_config first.")
        return ClientConfigRepository.CLIENTS