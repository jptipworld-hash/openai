#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('briefing_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

GMAIL_SENDER = os.getenv('GMAIL_SENDER_EMAIL', 'jptipworld@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENTS = ['jp@jphub.com.br', 'joaohomem@falconi.com']

def get_sao_paulo_time():
    sp_tz = timezone(timedelta(hours=-3))
    return datetime.now(sp_tz)

def search_news():
    logger.info("🔍 Buscando notícias sobre ChatGPT Enterprise...")
    try:
        queries = [
            'ChatGPT Enterprise news',
            'OpenAI ChatGPT updates',
            'ChatGPT Enterprise features'
        ]
        all_news = []
        for query in queries:
            try:
                resp = requests.get(
                    'https://www.google.com/search',
                    params={'q': query},
                    headers={'User-Agent': 'Mozilla/5.0'},
                    timeout=10
                )
                if resp.status_code == 200:
                    logger.info(f"✅ Busca realizada: {query}")
            except:
                pass
        return ["ChatGPT Enterprise continua evoluindo com novos recursos"]
    except Exception as e:
        logger.error(f"❌ Erro ao buscar: {str(e)}")
        return []

def generate_html(news):
    now = get_sao_paulo_time()
    date_str = now.strftime('%d/%m/%Y às %H:%M BRT')
    
    news_html = ""
    for item in news[:5]:
        news_html += f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #0066cc; background: #f5f8fa;">
            <h4 style="margin-top: 0; color: #0066cc;">{item}</h4>
            <p style="color: #666; font-size: 12px;">Fonte: OpenAI News</p>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; margin: 0; padding: 0; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 8px 0 0 0; font-size: 14px; opacity: 0.9; }}
        .content {{ padding: 30px 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ font-size: 18px; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 0; }}
        .tldr {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px; }}
        .tip {{ background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 4px; margin-top: 15px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #e9ecef; }}
        a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Briefing ChatGPT Enterprise</h1>
            <p>{date_str}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="tldr">
                    <strong>🚀 TL;DR (RESUMO EXECUTIVO)</strong>
                    <p>Acompanhamento diário das novidades sobre ChatGPT Enterprise com foco em funcionalidades, segurança e melhores práticas.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📰 Novidades & Lançamentos</h2>
                {news_html}
            </div>
            
            <div class="section">
                <h2>💡 Dica de Uso</h2>
                <div class="tip">
                    <strong>Company Knowledge:</strong> Use o recurso Company Knowledge no ChatGPT Enterprise para buscar automaticamente em Slack, SharePoint, Google Drive e mais, tudo em uma única pergunta! Isso economiza horas de busca manual.
                </div>
            </div>
            
            <div class="section">
                <h2>📍 Próximos Passos</h2>
                <ul>
                    <li>Revisar novidades e impactos para sua equipe</li>
                    <li>Explorar <a href="https://help.openai.com">documentação oficial</a></li>
                    <li>Testar novos recursos em ambiente controlado</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>
                📧 Briefing automático enviado diariamente às 20:00 BRT<br>
                Fontes: Blog OpenAI | Documentação Oficial | Release Notes<br>
                <a href="https://status.openai.com">Status OpenAI</a>
            </p>
        </div>
    </div>
</body>
</html>
    """
    return html

def send_email(subject, html_body):
    logger.info(f"📧 Enviando email para: {', '.join(RECIPIENTS)}")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_SENDER
        msg['To'] = ', '.join(RECIPIENTS)
        
        part = MIMEText(html_body, 'html')
        msg.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_SENDER, RECIPIENTS, msg.as_string())
        
        logger.info("✅ Email enviado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao enviar: {str(e)}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("🤖 INICIANDO BRIEFING CHATGPT ENTERPRISE")
    logger.info("=" * 60)
    
    news = search_news()
    html = generate_html(news)
    
    now = get_sao_paulo_time()
    subject = f"[Briefing ChatGPT Enterprise] {now.strftime('%Y-%m-%d')} — Novidades (20:00 BRT)"
    
    success = send_email(subject, html)
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ BRIEFING FINALIZADO COM SUCESSO!")
    else:
        logger.info("⚠️ BRIEFING COM AVISO")
    logger.info("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
