from typing import Literal

import discord

class PermissionEmbedFactory:
    @staticmethod
    def from_permission_modification(
            mode: Literal['add', 'remove'],
            role_name: str,
            affected_commands: list[str]
    ) -> discord.Embed:

        if mode == 'add':
            if affected_commands:
                return discord.Embed(
                    title='Permissions added',
                    color=discord.Color.green(),
                    description=(
                        f'Added command execution permissions to **{role_name}**\n\n'
                        f'Commands: {', '.join([f'**{c}**' for c in affected_commands])}'
                    )
                )
            else:
                return discord.Embed(
                    title='Failed to add permissions',
                    color=discord.Colour.red(),
                    description=(
                        f'Failed to add permissions to **{role_name}**\n\n'
                        'Commands provided either wrong or already assigned to this role'
                    )
                )
        elif mode == 'remove':
            if affected_commands:
                return discord.Embed(
                    title='Permissions removed',
                    color=discord.Color.green(),
                    description=(
                        f'Removed command execution permissions from **{role_name}**\n\n'
                        f'Commands: {', '.join([f'**{c}**' for c in affected_commands])}'
                    )
                )
            else:
                return discord.Embed(
                    title='Failed to remove permissions',
                    color=discord.Colour.red(),
                    description=(
                        f'Failed to remove permissions from **{role_name}**\n\n'
                        'Commands provided either invalid or not assigned to this role'
                    )
                )
        else:
            raise ValueError('Mode must be either "add" or "remove"')

    @staticmethod
    def role_permissions(roles: dict[str, set[str]], single_role: bool) -> discord.Embed:
        if len(roles) == 0:
            if not single_role:
                return discord.Embed(
                    title='Elevated roles',
                    color=discord.Color.blue(),
                    description='There are no roles with permissions assigned to them'
                )
            else:
                return discord.Embed(
                    title='Role permissions',
                    color=discord.Color.blue(),
                    description='There are no permissions assigned to this role'
                )

        if single_role:
            return discord.Embed(
                title=f'Permissions for role {list(roles.keys())[0]}',
                color=discord.Color.blue(),
                description=', '.join(roles[list(roles.keys())[0]])
            )

        embed = discord.Embed(
            title='Elevated roles',
            color=discord.Color.blue(),
        )

        roles_names: list[str] = []
        permissions_strs: list[str] = []
        for role_name, permissions in roles.items():
            roles_names.append(f'**{role_name}**')
            permissions_strs.append(', '.join(permissions))

        embed.add_field(name='Role', value='\n'.join(roles_names))
        embed.add_field(name='Permissions', value='\n'.join(permissions_strs))

        return embed