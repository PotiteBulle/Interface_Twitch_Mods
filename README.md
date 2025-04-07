# Interface_Twitch_Mods

Bot de modération Twitch automatisé utilisant un fichier Google Sheet comme source de comptes à bannir.<br>
Il vérifie régulièrement les nouveaux pseudos à bannir, les identifie via l'API Twitch, vérifie s’iels sont déjà bannis, et les bannit automatiquement s’iels ne le sont pas encore.

## Fonctionnalités

- Connexion automatique à plusieurs chaînes Twitch
- Lecture d'un Google Sheet distant contenant des pseudos à bannir
- Vérification si le compte est déjà banni
- Bannissement automatique avec raison
- Rafraîchissement de la liste toutes les 3 minutes


## Détails
- Vérifie toutes les 3 minutes une feuille Google Sheet
- Récupère les pseudos à bannir + raison
- Vérifie si l'utilisateur·ice est déjà banni
- Bannit automatiquement les utilisateur·ices ciblés via l'API Twitch
- Support multi-chaînes Twitch
- Basé sur un système de token sécurisé (.env)

---

## Installation

1. Clone le dépôt :
   ```bash
   git clone https://github.com/PotiteBulle/Interface_Twitch_Mods.git
   cd Interface_Twitch_Mods
   ```

2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Crée un fichier `.env` à la racine avec ce contenu :

   ```env
   # Token d'authentification du bot Twitch (via Twitch Token Generator)
   TOKEN=ton_token_twitch

   # ID client Twitch (https://twitchinsights.net/checkuser)
   CLIENT_ID=ton_client_id

   # ID Twitch de lae modérateur·ice (le bot ou toi)
   MOD_ID=123456789

   # IDs Twitch des diffuseur·ices (séparés par des virgules si plusieurs - https://twitchinsights.net/checkuser)
   BROADCASTER_ID=123456789,987654321

   # Noms des chaînes (en minuscules, sans le #)
   CHANNELS=chaîne1,chaîne2

   # URL de la feuille Google Sheet publiée en CSV (exemple) // faire en sorte qu'iel y est toujours '/export?format=csv'
   SHEET_URL=https://docs.google.com/spreadsheets/d/1vfgdEI7fK85tPlHcqTv41ocK3ejIYCi-9-tjBJhAXL4/export?format=csv

   # (Optionnel) Refresh token si tu veux renouveler le token automatiquement
   REFRESH_TOKEN=ton_refresh_token

   # (Optionnel) Mode debug pour plus de logs
   DEBUG=True
   ```

---

## Obtenir les informations `.env`

### TOKEN & SCOPES

1. Va sur [twitchtokengenerator.com](https://twitchtokengenerator.com/)
2. Clique sur "Custom Scopes"
3. Coche :
   - `moderator:manage:banned_users`
   - `offline_access` (optionnel mais recommandé)
4. Génére ton token → copie `TOKEN` et `REFRESH_TOKEN` (si dispo)

---

## Format du Google Sheet

Ton fichier Google Sheet doit être accessible publiquement et publié en **CSV**.  
Format attendu :

```
username,reason
troll_user1,Spam haineux
toxic_guy2,Menaces
```

Pour obtenir le lien CSV :
1. Fichier > Partager > Publier sur le Web > Choisir "Format CSV"
2. Copier l’URL et l’utiliser dans `.env` sous `SHEET_URL`

---

exmeple de fichier CSV valide [CSV Exemple](https://docs.google.com/spreadsheets/d/1vfgdEI7fK85tPlHcqTv41ocK3ejIYCi-9-tjBJhAXL4/edit?usp=sharing)

## Lancer le bot

```bash
python interface_twitch_mod.py
```

Le bot affichera les utilisateur·ices à bannir et les actions effectuées dans la console.

---

## Arrêter proprement

Appuie sur `Ctrl+C` dans le terminal pour arrêter le bot proprement et fermer la session HTTP.


## Dépendances

Fichier `requirements.txt` :
```
twitchio
python-dotenv
aiohttp
```

---

## Licence

Ce projet est libre d'utilisation. Distribué sous licence [MIT](https://github.com/PotiteBulle/Interface_Twitch_Mods/blob/main/LICENSE).  
Développé avec ❤️ par Potate & Fronzenway
