import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import dkim
from typing import List, Optional, Dict, Any
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import ConfigurationEmail, CompteEmail

class ServiceEmail:
    """Service de gestion des emails"""
    
    def __init__(self, configuration: ConfigurationEmail):
        self.configuration = configuration
        self._smtp_connection = None
        self._imap_connection = None
    
    def get_smtp_connection(self) -> smtplib.SMTP:
        """Obtient une connexion SMTP"""
        if not self._smtp_connection:
            if self.configuration.smtp_use_ssl:
                self._smtp_connection = smtplib.SMTP_SSL(
                    self.configuration.smtp_host,
                    self.configuration.smtp_port
                )
            else:
                self._smtp_connection = smtplib.SMTP(
                    self.configuration.smtp_host,
                    self.configuration.smtp_port
                )
                if self.configuration.smtp_use_tls:
                    self._smtp_connection.starttls()
            
            self._smtp_connection.login(
                self.configuration.smtp_user,
                self.configuration.smtp_password
            )
        return self._smtp_connection
    
    def get_imap_connection(self) -> imaplib.IMAP4:
        """Obtient une connexion IMAP"""
        if not self._imap_connection:
            if self.configuration.imap_use_ssl:
                self._imap_connection = imaplib.IMAP4_SSL(
                    self.configuration.imap_host,
                    self.configuration.imap_port
                )
            else:
                self._imap_connection = imaplib.IMAP4(
                    self.configuration.imap_host,
                    self.configuration.imap_port
                )
            
            self._imap_connection.login(
                self.configuration.imap_user,
                self.configuration.imap_password
            )
        return self._imap_connection
    
    def close_connections(self):
        """Ferme les connexions SMTP et IMAP"""
        if self._smtp_connection:
            self._smtp_connection.quit()
            self._smtp_connection = None
        
        if self._imap_connection:
            self._imap_connection.logout()
            self._imap_connection = None
    
    def envoyer_email(
        self,
        expediteur: CompteEmail,
        destinataires: List[str],
        sujet: str,
        contenu_texte: str,
        contenu_html: Optional[str] = None,
        pieces_jointes: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Envoie un email
        
        Args:
            expediteur: Compte email de l'expéditeur
            destinataires: Liste des adresses email des destinataires
            sujet: Sujet de l'email
            contenu_texte: Contenu texte de l'email
            contenu_html: Contenu HTML de l'email (optionnel)
            pieces_jointes: Liste des pièces jointes (optionnel)
            cc: Liste des destinataires en copie (optionnel)
            bcc: Liste des destinataires en copie cachée (optionnel)
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Création du message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = sujet
            msg['From'] = f'{expediteur.utilisateur.get_full_name()} <{expediteur.adresse_email}>'
            msg['To'] = ', '.join(destinataires)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Ajout du contenu texte
            msg.attach(MIMEText(contenu_texte, 'plain'))
            
            # Ajout du contenu HTML s'il existe
            if contenu_html:
                msg.attach(MIMEText(contenu_html, 'html'))
            
            # Ajout de la signature
            signature = expediteur.signature_personnalisee or self.configuration.signature_defaut
            if signature:
                msg.attach(MIMEText(f'\n\n{signature}', 'plain'))
            
            # Ajout des pièces jointes
            if pieces_jointes:
                for piece in pieces_jointes:
                    part = MIMEApplication(
                        piece['contenu'],
                        _subtype=piece.get('type', 'octet-stream')
                    )
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=piece['nom']
                    )
                    msg.attach(part)
            
            # Signature DKIM
            if self.configuration.dkim_active:
                headers = ['From', 'To', 'Subject']
                if cc:
                    headers.append('Cc')
                if bcc:
                    headers.append('Bcc')
                
                sig = dkim.sign(
                    message=msg.as_bytes(),
                    selector=self.configuration.dkim_selector.encode(),
                    domain=self.configuration.dkim_domain.encode(),
                    privkey=self.configuration.dkim_private_key.encode(),
                    include_headers=headers
                )
                msg['DKIM-Signature'] = sig[len('DKIM-Signature: '):].decode()
            
            # Envoi de l'email
            smtp = self.get_smtp_connection()
            all_recipients = destinataires + (cc or []) + (bcc or [])
            smtp.send_message(msg, expediteur.adresse_email, all_recipients)
            
            return True
            
        except Exception as e:
            print(f'Erreur lors de l\'envoi de l\'email: {str(e)}')
            return False
        
        finally:
            self.close_connections()
    
    def lire_emails(
        self,
        compte: CompteEmail,
        dossier: str = 'INBOX',
        non_lus: bool = False,
        limite: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Lit les emails d'un compte
        
        Args:
            compte: Compte email
            dossier: Dossier à lire (par défaut: INBOX)
            non_lus: Ne lire que les emails non lus
            limite: Nombre maximum d'emails à lire
            
        Returns:
            List[Dict]: Liste des emails
        """
        try:
            imap = self.get_imap_connection()
            imap.select(dossier)
            
            # Critères de recherche
            criteres = ['ALL']
            if non_lus:
                criteres = ['UNSEEN']
            
            # Recherche des emails
            _, messages = imap.search(None, *criteres)
            messages = messages[0].split()
            
            # Limitation du nombre d'emails
            if limite:
                messages = messages[-limite:]
            
            emails = []
            for msg_num in messages:
                _, data = imap.fetch(msg_num, '(RFC822)')
                email_body = data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extraction des informations
                email_dict = {
                    'id': msg_num.decode(),
                    'sujet': email_message['subject'],
                    'de': email_message['from'],
                    'date': email_message['date'],
                    'contenu': self._extraire_contenu(email_message),
                    'pieces_jointes': self._extraire_pieces_jointes(email_message)
                }
                emails.append(email_dict)
            
            return emails
            
        except Exception as e:
            print(f'Erreur lors de la lecture des emails: {str(e)}')
            return []
            
        finally:
            self.close_connections()
    
    def _extraire_contenu(self, message: email.message.Message) -> Dict[str, str]:
        """Extrait le contenu texte et HTML d'un email"""
        contenu = {'texte': '', 'html': ''}
        
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    contenu['texte'] = part.get_payload(decode=True).decode()
                elif part.get_content_type() == 'text/html':
                    contenu['html'] = part.get_payload(decode=True).decode()
        else:
            if message.get_content_type() == 'text/plain':
                contenu['texte'] = message.get_payload(decode=True).decode()
            elif message.get_content_type() == 'text/html':
                contenu['html'] = message.get_payload(decode=True).decode()
        
        return contenu
    
    def _extraire_pieces_jointes(
        self,
        message: email.message.Message
    ) -> List[Dict[str, Any]]:
        """Extrait les pièces jointes d'un email"""
        pieces_jointes = []
        
        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            if filename:
                pieces_jointes.append({
                    'nom': filename,
                    'type': part.get_content_type(),
                    'taille': len(part.get_payload(decode=True)),
                    'contenu': part.get_payload(decode=True)
                })
        
        return pieces_jointes
    
    def marquer_comme_lu(
        self,
        compte: CompteEmail,
        message_ids: List[str],
        dossier: str = 'INBOX'
    ) -> bool:
        """Marque des emails comme lus"""
        try:
            imap = self.get_imap_connection()
            imap.select(dossier)
            
            for msg_id in message_ids:
                imap.store(msg_id.encode(), '+FLAGS', '\\Seen')
            
            return True
            
        except Exception as e:
            print(f'Erreur lors du marquage des emails: {str(e)}')
            return False
            
        finally:
            self.close_connections()
    
    def supprimer_emails(
        self,
        compte: CompteEmail,
        message_ids: List[str],
        dossier: str = 'INBOX'
    ) -> bool:
        """Supprime des emails"""
        try:
            imap = self.get_imap_connection()
            imap.select(dossier)
            
            for msg_id in message_ids:
                imap.store(msg_id.encode(), '+FLAGS', '\\Deleted')
            imap.expunge()
            
            return True
            
        except Exception as e:
            print(f'Erreur lors de la suppression des emails: {str(e)}')
            return False
            
        finally:
            self.close_connections()
    
    def deplacer_emails(
        self,
        compte: CompteEmail,
        message_ids: List[str],
        dossier_source: str,
        dossier_destination: str
    ) -> bool:
        """Déplace des emails vers un autre dossier"""
        try:
            imap = self.get_imap_connection()
            imap.select(dossier_source)
            
            for msg_id in message_ids:
                imap.copy(msg_id.encode(), dossier_destination)
                imap.store(msg_id.encode(), '+FLAGS', '\\Deleted')
            imap.expunge()
            
            return True
            
        except Exception as e:
            print(f'Erreur lors du déplacement des emails: {str(e)}')
            return False
            
        finally:
            self.close_connections()
    
    def creer_dossier(
        self,
        compte: CompteEmail,
        nom_dossier: str
    ) -> bool:
        """Crée un nouveau dossier"""
        try:
            imap = self.get_imap_connection()
            imap.create(nom_dossier)
            return True
            
        except Exception as e:
            print(f'Erreur lors de la création du dossier: {str(e)}')
            return False
            
        finally:
            self.close_connections()
    
    def supprimer_dossier(
        self,
        compte: CompteEmail,
        nom_dossier: str
    ) -> bool:
        """Supprime un dossier"""
        try:
            imap = self.get_imap_connection()
            imap.delete(nom_dossier)
            return True
            
        except Exception as e:
            print(f'Erreur lors de la suppression du dossier: {str(e)}')
            return False
            
        finally:
            self.close_connections()
    
    def lister_dossiers(
        self,
        compte: CompteEmail
    ) -> List[str]:
        """Liste tous les dossiers"""
        try:
            imap = self.get_imap_connection()
            _, dossiers = imap.list()
            
            return [
                d.decode().split('"/"')[-1].strip('"')
                for d in dossiers
            ]
            
        except Exception as e:
            print(f'Erreur lors de la liste des dossiers: {str(e)}')
            return []
            
        finally:
            self.close_connections()
    
    def verifier_quota(
        self,
        compte: CompteEmail
    ) -> Dict[str, int]:
        """Vérifie le quota utilisé"""
        try:
            imap = self.get_imap_connection()
            quota = imap.getquota('user')[1][0]
            utilise = int(quota.split()[0])
            total = int(quota.split()[1])
            
            return {
                'utilise': utilise,
                'total': total,
                'disponible': total - utilise
            }
            
        except Exception as e:
            print(f'Erreur lors de la vérification du quota: {str(e)}')
            return {
                'utilise': 0,
                'total': compte.configuration.quota_boite,
                'disponible': compte.configuration.quota_boite
            }
            
        finally:
            self.close_connections()
