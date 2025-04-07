import os
import asyncio
import aiohttp
from twitchio.ext import commands
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des variables essentielles depuis le .env
bot_token = os.getenv('TOKEN')
client_id = os.getenv('CLIENT_ID')
moderator_id = os.getenv('MOD_ID')
broadcaster_ids = [b.strip() for b in os.getenv('BROADCASTER_ID', '').split(',')]
sheet_url = os.getenv('SHEET_URL')
channels = [f'#{channel.strip()}' for channel in os.getenv('CHANNELS', '').split(',')]

class Bot(commands.Bot):
    def __init__(self):
        # Initialisation du bot
        super().__init__(token=bot_token, prefix='!', initial_channels=channels)
        self.session = None

    async def event_ready(self):
        # Événement
        print(f'Connecté en tant que | {self.nick}')
        print(f'ID utilisateur | {self.user_id}')
        self.session = aiohttp.ClientSession()
        await self.check_bans()
        self.loop.create_task(self.ban_check_loop())

    async def ban_check_loop(self):
        # Vérifie les bannissements toutes les 3 minutes
        while True:
            await self.check_bans()
            await asyncio.sleep(180)

    async def check_bans(self):
        # Fonction principale de vérification des utilisateur·ices à bannir
        if not sheet_url:
            print("Erreur : L'URL du Google Sheet est absente du fichier .env")
            return

        try:
            # Récupère les données du Google Sheet
            async with self.session.get(sheet_url) as response:
                if response.status == 401:
                    print("Erreur 401 : Accès non autorisé. Vérifiez que le fichier est public.")
                    return
                response.raise_for_status()
                csv_data = await response.text()

            # Transforme les lignes du CSV en tableaux
            comptes_a_bannir = [row.split(',') for row in csv_data.splitlines() if row]
            print(f"Comptes à bannir : {comptes_a_bannir[1:]}")  # Ignore la première ligne (entête CSV)

            for row in comptes_a_bannir[1:]:
                if len(row) < 2:
                    print("Ligne invalide ignorée :", row)
                    continue
                username = row[0].strip()
                reason = row[1].strip() if len(row) > 1 else "Violation des règles" # Si pas de motif, met la valeur par défaut "Violation des règles"
                user_id = await self.fetch_user_id(username)

                if user_id:
                    already_banned = await self.check_if_banned(user_id)
                    if already_banned:
                        print(f"Déjà banni : {user_id}")
                    else:
                        await self.ban_user(user_id, reason)
                else:
                    print(f"{username} est déjà banni ou ID introuvable.")
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")

    async def fetch_user_id(self, username):
        # Récupère l'ID utilisateur·ice Twitch à partir de son nom d'utilisateur·ice
        url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = {"Authorization": f"Bearer {bot_token}", "Client-Id": client_id}

        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data'][0]['id'] if data['data'] else None
            print(f"Erreur récupération ID {username} : {response.status}")
            return None

    async def check_if_banned(self, user_id):
        # Vérifie si un·e utilisateur·ice est déjà banni sur une ou plusieurs chaînes
        for broadcaster_id in broadcaster_ids:
            url = f"https://api.twitch.tv/helix/moderation/banned?broadcaster_id={broadcaster_id}&user_id={user_id}"
            headers = {"Authorization": f"Bearer {bot_token}", "Client-Id": client_id}

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['data']:
                        return True
        return False

    async def ban_user(self, user_id, reason):
        # Envoie une requête de bannissement à l'API Twitch pour chaque chaîne
        for broadcaster_id in broadcaster_ids:
            url = f"https://api.twitch.tv/helix/moderation/bans?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}"
            headers = {
                "Authorization": f"Bearer {bot_token}",
                "Client-Id": client_id,
                "Content-Type": "application/json"
            }
            json_data = {"data": {"user_id": user_id, "reason": reason}}

            async with self.session.post(url, headers=headers, json=json_data) as response:
                if response.status in {200, 204}:
                    print(f"Utilisateur·ices {user_id} banni sur {broadcaster_id}.")
                else:
                    print(f"Erreur bannissement {user_id} sur {broadcaster_id} : {response.status} - {await response.text()}")

    async def close(self):
        # Ferme la session HTTP proprement
        if self.session:
            await self.session.close()

async def main():
    # Point d'entrée principal du bot
    bot = Bot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("Bot arrêté manuellement.")
    finally:
        await bot.close()

# Exécute le bot si ce fichier est le script principal
if __name__ == "__main__":
    asyncio.run(main())
