# DATAIKÔS Mailer

Bienvenue sur DATAIKÔS Mailer — un petit service FastAPI pour envoyer des e-mails (avec pièces jointes et import CSV de destinataires).

[Tester en ligne ▶️](https://dataikos-mailer.onrender.com)

---

## Aperçu

- Framework : FastAPI
- Serveur recommandé : Uvicorn
- Lecture CSV : pandas
- Formulaires/fichiers : python-multipart

Test rapide : cliquez sur le lien de déploiement ci-dessus pour ouvrir l'interface web ou la documentation interactive (OpenAPI/Swagger) à /docs.

---

## Points forts

- Envoi d'e-mails via SMTP (ex. Gmail avec mot de passe d'application)
- Support des pièces jointes (UploadFile)
- Import de destinataires depuis un CSV contenant les colonnes `Noms` et `adresse mail`
- Personnalisation du message avec la variable `{nom}` dans le corps

---

## Raccourci pour tester

1. Ouvrez : https://dataikos-mailer.onrender.com
2. Accédez à l'interface interactive : https://dataikos-mailer.onrender.com/docs
3. Utilisez le endpoint `POST /send-email/` :
   - Remplissez `sender_email` (votre adresse Gmail)
   - `app_password` : mot de passe d'application (NE PAS UTILISER LE MOT DE PASSE PRINCIPAL)
   - `subject`, `message`
   - `recipient_email` ou `recipients_csv` (fichier CSV avec colonnes `Noms,adresse mail`)
   - Ajoutez des pièces jointes si besoin

Exemple curl (attention : expose le mot de passe dans la ligne de commande)

```bash
curl -X 'POST' \
  'https://dataikos-mailer.onrender.com/send-email/' \
  -F 'sender_email=mon.adresse@gmail.com' \
  -F 'app_password=MON_MDP_APPLI' \
  -F 'recipient_email=ami@example.com' \
  -F 'subject=Bonjour' \
  -F 'message=Salut {nom}, ceci est un test' \
  -F 'send_count=1'
```

Astuce : préférez l'UI Swagger pour tester les envois et les uploads.

---

## Exécution locale

1. Clonez le dépôt :

```bash
git clone https://github.com/monsieurMechant200/Dataikos_Mailer.git
cd Dataikos_Mailer
```

2. Installez les dépendances :

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

3. Lancez le serveur en développement :

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Puis ouvrez http://localhost:8000/docs

---

## Sécurité & bonnes pratiques

- N'envoyez jamais vos mots de passe directement dans des requêtes publiques. Pour un usage réel, fournissez les identifiants via des variables d'environnement ou un service secret.
- Pour Gmail, utilisez un mot de passe d'application (2FA requis).
- Limitez les envois massifs et respectez la politique d'envoi de votre fournisseur SMTP.

---

## Contribuer

Les contributions sont les bienvenues ! Ouvrez une issue ou une PR.

Idées :
- Ajout d'authentification (OAuth2/Gmail API)
- Gestion des quotas et des file d'attente
- Tests unitaires et CI

---

## Licence

MIT — voir le fichier LICENSE si présent.

---

Merci d'avoir essayé DATAIKÔS Mailer — clique sur ce lien pour tester immédiatement : https://dataikos-mailer.onrender.com
