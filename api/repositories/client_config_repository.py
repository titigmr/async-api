import os

import yaml

from api.core.utils import logger


class ClientAuthorization:
    def __init__(self, service: str, quotas: int | None) -> None:
        self.service = service
        self.quotas = quotas

    def __repr__(self) -> str:
        return f"ClientAuthorization(service={self.service}, quota={self.quotas})"


class ClientConfig:
    def __init__(
        self,
        client_id: str,
        client_secret: str | None = None,
        authorizations: dict[str, ClientAuthorization] | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorizations = authorizations or {}

    def __repr__(self) -> str:
        return f"ClientConfig(client_id={self.client_id}, client_secret={self.client_secret}, authorizations={self.authorizations})"


class ClientsConfigException(Exception):

    """Custom exception for ServicesConfigRepository errors."""



class ClientConfigRepository:
    # Singleton instance to hold the services configuration
    CLIENTS: dict[str, ClientConfig] = {}

    @staticmethod
    def load_clients_config(client_file: str) -> None:
        try:
            with open(client_file) as file:
                config = yaml.load(file, Loader=yaml.SafeLoader)
                ClientConfigRepository.CLIENTS = ClientConfigRepository._parse_yaml_struct(config)
        except FileNotFoundError as e:
            logger.error(f"Configuration file {client_file} not found: {e}")
            msg = f"Configuration file {client_file} not found."
            raise ClientsConfigException(msg)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {client_file}: {e}")
            msg = f"Error parsing YAML file {client_file}."
            raise ClientsConfigException(msg)

    @staticmethod
    def _parse_yaml_struct(config) -> dict[str, ClientConfig]:
        """Parses the YAML structure and returns a dictionary with service names as keys
        and their configurations as values.
        """
        if not isinstance(config, list):
            msg = "Invalid configuration format. Expected a list of clients."
            raise ClientsConfigException(msg)

        clients = {}
        for config_item in config:
            if not isinstance(config_item, dict):
                msg = f"Invalid configuration item at: {config_item}. Expected a dictionary."
                raise ClientsConfigException(msg)
            if "client_id" not in config_item:
                msg = "Each client configuration must contain a 'client_id' key."
                raise ClientsConfigException(msg)
            client_id = config_item["client_id"]
            client_secret = config_item.get("client_secret", None)
            client_secret = ClientConfigRepository._resolve_secret(client_secret)

            authorisations_part = config_item.get("authorizations", [])
            authorisations: dict[str, ClientAuthorization] = {}
            if not isinstance(authorisations_part, list):
                msg = f"Invalid authorizations format for client {client_id}. Expected a list."
                raise ClientsConfigException(msg)

            for auth in authorisations_part:
                if not isinstance(auth, dict):
                    msg = f"Invalid authorization item for client {client_id}: {auth}. Expected a dictionary."
                    raise ClientsConfigException(
                        msg,
                    )
                if "service" not in auth:
                    msg = "Each authorization must contain a 'service' key."
                    raise ClientsConfigException(msg)
                service_name = auth["service"]
                quotas = auth.get("quotas", None)
                authorisations[service_name] = ClientAuthorization(service=service_name, quotas=quotas)

            client_config = ClientConfig(
                client_id=client_id, client_secret=client_secret, authorizations=authorisations,
            )
            clients[client_id] = client_config
        return clients

    @staticmethod
    def _resolve_secret(secret: str | None) -> str | None:
        """Resolves the client secret, which can be a string or None.
        If the secret is None, it returns None.
        """
        if secret is None:
            return None
        if not secret.startswith("$"):
            return secret

        env_secret = os.environ.get(secret[1:])
        if env_secret is None:
            msg = f"Env variable : '{secret}' not found."
            raise ClientsConfigException(msg)

        return env_secret

    def all_clients(self) -> dict[str, ClientConfig]:
        """Returns all clients configurations."""
        if ClientConfigRepository.CLIENTS is None:
            msg = "Clients configuration not loaded. Call load_clients_config first."
            raise ClientsConfigException(msg)
        return ClientConfigRepository.CLIENTS

    def get_client(self, client_id: str) -> ClientConfig | None:
        """Returns the client configuration for the given client_id.
        If the client does not exist, returns None.
        """
        return self.all_clients().get(client_id)
