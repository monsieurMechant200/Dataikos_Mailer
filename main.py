from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import smtplib
import asyncio
import logging
import io
import pandas as pd
from email.message import EmailMessage
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465
    timeout: int = 30
    delay_between_sends: float = 1.0

class EmailSender:
    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
        
    def create_email_message(self, sender, recipient, subject, body) -> EmailMessage:
        email = EmailMessage()
        email["From"] = sender
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(body, subtype='plain')
        if "<html>" in body.lower():
            email.add_alternative(body, subtype='html')
        return email

    async def add_attachments(self, email: EmailMessage, attachments: List[UploadFile]):
        for attachment in attachments:
            if attachment.filename:
                # IMPORTANT: On lit le contenu
                content = await attachment.read()
                # On détermine le type (très simplifié ici pour l'exemple)
                email.add_attachment(
                    content,
                    maintype='application',
                    subtype='octet-stream',
                    filename=attachment.filename
                )
                # On "rewind" le fichier pour le prochain email de la boucle
                await attachment.seek(0)

    def send_single_smtp(self, sender, pwd, email_obj):
        with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port, timeout=self.config.timeout) as smtp:
            smtp.login(sender, pwd)
            smtp.send_message(email_obj)

# --- Initialisation API ---
app = FastAPI(title="DATAIKÔS Mailer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

email_service = EmailSender()

@app.post("/send-email/")
async def send_email(
    sender_email: str = Form(...),
    app_password: str = Form(...),
    recipient_email: Optional[str] = Form(None),
    subject: str = Form(...),
    message: str = Form(...),
    send_count: int = Form(1),
    attachments: Optional[List[UploadFile]] = File(None),
    recipients_csv: Optional[UploadFile] = File(None)
):
    try:
        recipients = []
        errors = []
        success_count = 0

        # 1. Collecte des destinataires
        if recipients_csv:
            content = await recipients_csv.read()
            df = pd.read_csv(io.BytesIO(content), names=['Noms', 'adresse mail'], sep=None, engine='python', encoding='utf-8')
            
            if 'Noms' not in df.columns or 'adresse mail' not in df.columns:
                raise HTTPException(400, "Le CSV doit contenir les colonnes 'Noms' et 'adresse mail'")
            
            for _, row in df.iterrows():
                # Personnalisation du message si {nom} est présent
                msg_body = message.replace('{nom}', str(row['Noms']))
                recipients.append((row['adresse mail'], msg_body))
        elif recipient_email:
            recipients.append((recipient_email, message))
        else:
            raise HTTPException(400, "Aucun destinataire fourni")

        # 2. Boucle d'envoi
        for email_addr, email_body in recipients:
            for i in range(send_count):
                try:
                    # Création du mail
                    email_obj = email_service.create_email_message(sender_email, email_addr, subject, email_body)
                    
                    # Ajout des PJ
                    if attachments:
                        await email_service.add_attachments(email_obj, attachments)
                    
                    # Envoi SMTP (synchrone mais exécuté proprement)
                    email_service.send_single_smtp(sender_email, app_password, email_obj)
                    success_count += 1
                    
                    if len(recipients) > 1:
                        await asyncio.sleep(email_service.config.delay_between_sends)
                except Exception as e:
                    errors.append(f"Erreur vers {email_addr}: {str(e)}")

        return {
            "status": "completed",
            "successful": success_count,
            "failed": len(recipients) * send_count - success_count,
            "errors": errors if errors else None,
            "message": f"{success_count} emails envoyés avec succès."
        }

    except Exception as e:
        logger.error(f"FATAL: {str(e)}")
        raise HTTPException(500, detail=str(e))

# Montage des fichiers statiques (ton HTML)
# Assure-toi que ton index.html est dans un dossier nommé 'static'
app.mount("/", StaticFiles(directory="static", html=True), name="static")