#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Enterprise Daily Briefing Generator
Dispara automaticamente via GitHub Actions Ã s 20:00 BRT
Envia via Gmail com senha de aplicativo
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('briefing_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ConfiguraÃ§Ãµes
GMAIL_SENDER = os.getenv('GMAIL_SENDER_EMAIL', 'jptipworld@gmail.com')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# DestinatÃ¡rios
RECIPIENTS = ['jp@jphub.com.br', 'joaohomem@falconi.com']
CC_RECIPIENTS = []

# Fontes de busca
SEARCH_QUERIES = [
    'ChatGPT Enterprise news latest',
    'OpenAI blog ChatGPT updates',
    'ChatGPT Enterprise release notes',
]

def get_current_time_sao_paulo():
    """Retorna horÃ¡rio atual em SÃ£o Paulo"""
    sp_tz = timezone(timedelta(hours=-3))
    return datetime.now(sp_tz)

def search_openai_news():
    """
    Busca notÃ­cias sobre ChatGPT Enterprise das Ãºltimas 24-72h
    Para agora, usa dados fictÃ­cios (vocÃª pode integrar web search depois)
    """
    logger.info("ðŸ” Buscando notÃ­cias sobre ChatGPT Enterprise...")

    # Dados de exemplo (substitua por busca real depois)
    example_news = [
        {
            'title': 'OpenAI lanÃ§a Company Knowledge para Enterprise',
            'snippet': 'Novo recurso permite buscar em Slack, SharePoint, Google Drive simultaneamente com uma Ãºnica pergunta.',
            'link': 'https://openai.com/index/introducing-company-knowledge',
            'source': 'OpenAI Blog'
        },
        {
            'title': 'GPT-5 expandido com 78% reduÃ§Ã£o em erros factuais',
            'snippet': 'Melhorias significativas em raciocÃ­nio e integraÃ§Ã£o com ferramentas corporativas.',
            'link': 'https://openai.com/index/gpt-5-enterprise-improvements',
            'source': 'OpenAI Official'
        }
    ]

    logger.info(f"âœ… Encontradas {len(example_news)} notÃ­cias para demonstraÃ§Ã£o")
    return example_news

def generate_html_briefing(news_items):
    """
    Gera HTML bonito e visual do briefing
    """
    now = get_current_time_sao_paulo()
    date_str = now.strftime('%d/%m/%Y Ã s %H:%M BRT')

    # Se sem notÃ­cias, usar fallback
    if not news_items:
        tldr = "Sem novidades relevantes hoje."
        news_html = "<p>Nenhuma notÃ­cia encontrada nas Ãºltimas 24h.</p>"
    else:
        tldr = f"Encontradas {len(news_items)} notÃ­cias sobre ChatGPT Enterprise"
        news_html = ""
        for i, item in enumerate(news_items, 1):
            title = item.get('title', 'Sem tÃ­tulo')
            snippet = item.get('snippet', '')
            link = item.get('link', '#')
            source = item.get('source', 'Fonte desconhecida')

            news_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #0066cc; background: #f5f8fa;">
                <h4 style="margin-top: 0; color: #0066cc;">{title}</h4>
                <p style="color: #333; line-height: 1.6;">{snippet}</p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                    ðŸ“Œ <strong>Fonte:</strong> {source} | 
                    <a href="{link}" style="color: #0066cc; text-decoration: none;">Ler mais â†’</a>
                </p>
            </div>
            """

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header p {{
            margin: 8px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 18px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .tldr {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .tldr-label {{
            font-weight: 600;
            color: #856404;
            margin-bottom: 8px;
        }}
        .tip {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }}
        .tip strong {{
            color: #0c5460;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        a {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>ðŸ“Š Briefing ChatGPT Enterprise</h1>
            <p>{date_str}</p>
        </div>

        <!-- CONTEÃšDO -->
        <div class="content">
            <!-- TL;DR -->
            <div class="section">
                <div class="tldr">
                    <div class="tldr-label">ðŸš€ TL;DR (RESUMO EXECUTIVO)</div>
                    <p>{tldr}</p>
                </div>
            </div>

            <!-- NOVIDADES -->
            <div class="section">
                <h2>ðŸ“° Novidades & LanÃ§amentos</h2>
                {news_html}
            </div>

            <!-- DICA -->
            <div class="section">
                <h2>ðŸ’¡ Dica de Uso</h2>
                <div class="tip">
                    <strong>Company Knowledge:</strong> Ative o recurso Company Knowledge no seu ChatGPT Enterprise 
                    para buscar automaticamente em Slack, SharePoint, Google Drive e mais, tudo em uma Ãºnica pergunta!
                </div>
            </div>

            <!-- PRÃ“XIMOS PASSOS -->
            <div class="section">
                <h2>ðŸ“ PrÃ³ximos Passos</h2>
                <ul>
                    <li>Revisar novidades e impactos para sua equipe</li>
                    <li>Explorar <a href="https://help.openai.com">documentaÃ§Ã£o oficial</a></li>
                    <li>Testar novos recursos em ambiente controlado</li>
                </ul>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            <p>
                ðŸ“§ Briefing automÃ¡tico enviado diariamente Ã s 20:00 BRT<br>
                Fontes: Blog OpenAI | DocumentaÃ§Ã£o Oficial | Release Notes<br>
                <a href="https://status.openai.com">Status OpenAI</a> | 
                <a href="https://openai.com/index/company-knowledge">Saiba mais</a>
            </p>
        </div>
    </div>
</body>
</html>
    """

    return html_body

def send_email_via_gmail(subject, html_body, to_emails, cc_emails=None):
    """
    Envia email via Gmail usando senha de aplicativo
    """
    logger.info(f"ðŸ“§ Enviando email para: {', '.join(to_emails)}")

    try:
        cc_emails = cc_emails or []

        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_SENDER
        msg['To'] = ', '.join(to_emails)
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)

        # Anexar HTML
        part = MIMEText(html_body, 'html')
        msg.attach(part)

        # Conectar ao SMTP do Gmail e enviar
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)

            # Enviar para TO + CC
            all_recipients = to_emails + cc_emails
            server.sendmail(GMAIL_SENDER, all_recipients, msg.as_string())

        logger.info("âœ… Email enviado com sucesso!")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("âŒ Erro de autenticaÃ§Ã£o: Verifique GMAIL_APP_PASSWORD")
        return False
    except Exception as e:
        logger.error(f"âŒ Erro ao enviar email: {str(e)}")
        return False

def main():
    """FunÃ§Ã£o principal"""
    logger.info("=" * 60)
    logger.info("ðŸ¤– INICIANDO BRIEFING CHATGPT ENTERPRISE")
    logger.info("=" * 60)

    # Validar configuraÃ§Ãµes
    if not GMAIL_APP_PASSWORD:
        logger.error("âŒ GMAIL_APP_PASSWORD nÃ£o configurada!")
        return 1

    if not GMAIL_SENDER:
        logger.error("âŒ GMAIL_SENDER_EMAIL nÃ£o configurada!")
        return 1

    logger.info(f"ðŸ“§ Sender: {GMAIL_SENDER}")
    logger.info(f"ðŸ“¨ DestinatÃ¡rios: {', '.join(RECIPIENTS)}")

    # 1. Buscar notÃ­cias
    logger.info("\n[1/3] Coletando notÃ­cias...")
    news_items = search_openai_news()

    # 2. Gerar HTML
    logger.info("[2/3] Gerando HTML bonito...")
    html_body = generate_html_briefing(news_items)

    # 3. Enviar email
    logger.info("[3/3] Enviando email...")
    now = get_current_time_sao_paulo()
    date_str = now.strftime('%Y-%m-%d')
    subject = f"[Briefing ChatGPT Enterprise] {date_str} â€” Novidades, Roadmap, Dicas (20:00 BRT)"

    success = send_email_via_gmail(subject, html_body, RECIPIENTS, CC_RECIPIENTS)

    logger.info("\n" + "=" * 60)
    if success:
        logger.info("âœ… BRIEFING FINALIZADO COM SUCESSO!")
    else:
        logger.info("âš ï¸ BRIEFING FINALIZADO COM AVISO (verificar logs)")
    logger.info("=" * 60)

    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
