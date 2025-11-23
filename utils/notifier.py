# Nome do arquivo: src/utils/notifier.py

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

import requests

from src.config import Config
from src.utils.logger import logger


class Notifier:
    """Sistema de notificações via Email e Telegram"""

    def __init__(self):
        self.email_enabled = Config.EMAIL_ENABLED
        self.telegram_enabled = Config.TELEGRAM_ENABLED

    def send_email(self, subject: str, body: str, to_email: str = None) -> bool:
        """Envia email de notificação"""
        if not self.email_enabled:
            logger.debug("Email desabilitado")
            return False

        to_email = to_email or Config.NOTIFY_EMAIL

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = Config.EMAIL_USER
            msg["To"] = to_email
            msg["Subject"] = f"[Scout Pro] {subject}"

            # Adiciona timestamp
            footer = (
                f"\n\n---\nEnviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
            )
            body_with_footer = body + footer

            # Versão texto e HTML
            text_part = MIMEText(body_with_footer, "plain", "utf-8")
            html_part = MIMEText(
                body_with_footer.replace("\n", "<br>"), "html", "utf-8"
            )

            msg.attach(text_part)
            msg.attach(html_part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info(f"📧 Email enviado: {subject}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False

    def send_telegram(self, message: str, parse_mode: str = "HTML") -> bool:
        """Envia mensagem via Telegram"""
        if not self.telegram_enabled:
            logger.debug("Telegram desabilitado")
            return False

        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info("📱 Mensagem Telegram enviada")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar Telegram: {e}")
            return False

    def notify(self, subject: str, message: str):
        """Envia notificação por todos os canais habilitados"""
        results = []

        if self.email_enabled:
            results.append(self.send_email(subject, message))

        if self.telegram_enabled:
            telegram_msg = f"<b>{subject}</b>\n\n{message}"
            results.append(self.send_telegram(telegram_msg))

        return any(results)

    def notify_contracts_expiring(self, players: List[Dict]) -> bool:
        """Notifica sobre contratos expirando"""
        if not players:
            return False

        # Agrupa por dias restantes
        by_days = {}
        for player in players:
            days = player.get("dias_restantes", 999)
            if days not in by_days:
                by_days[days] = []
            by_days[days].append(player)

        # Monta mensagem
        subject = f"⚠️ {len(players)} Contrato(s) Expirando"

        message = "📋 ALERTAS DE CONTRATOS\n\n"

        for days in sorted(by_days.keys()):
            players_list = by_days[days]
            message += f"🔴 VENCE EM {days} DIAS:\n"
            for p in players_list:
                message += f"  • {p['nome']} - {p.get('clube', 'N/A')}\n"
            message += "\n"

        return self.notify(subject, message)

    def notify_sync_complete(self, stats: Dict) -> bool:
        """Notifica sobre conclusão de sincronização"""
        subject = "✅ Sincronização Concluída"

        message = f"""
📊 SINCRONIZAÇÃO COMPLETA

Jogadores: {stats.get('total', 0)}
Novos: {stats.get('novos', 0)}
Atualizados: {stats.get('atualizados', 0)}
Fotos baixadas: {stats.get('fotos', 0)}

Tempo: {stats.get('tempo', 'N/A')}s
        """

        return self.notify(subject, message.strip())


# Instância global
notifier = Notifier()
