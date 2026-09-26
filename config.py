from pydantic import model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    discord_token: SecretStr | None = None
    stoat_token:  SecretStr | None = None
    db_url: SecretStr

    enable_discord: bool = True
    enable_stoat: bool = True

    model_config = SettingsConfigDict(
        env_file='.env'
    )

    @model_validator(mode='after')
    def require_one_platform(self):
        if self.discord_token is None and self.stoat_token is None:
            raise ValueError('Please provide either a discord_token or stoat_token or both')

        if self.enable_discord and self.discord_token is None:
            raise ValueError('A discord token has not been provided')

        if self.enable_stoat and self.stoat_token is None:
            raise ValueError('A stoat token has not been provided')

        return self