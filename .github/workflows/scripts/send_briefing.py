#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Enterprise Daily Briefing Generator
Dispara automaticamente via GitHub Actions às 20:00 BRT
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
import logging

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

# Configurações
RUBE_BASE_URL = os.getenv('RUBE_BASE_URL', 'https://rube-api.composio.dev')
RUBE_API_KEY = os.getenv('RUBE_API_KEY')
RUBE_SESSION_ID = os.getenv('RUBE_SESSION_ID', 'chatgpt-briefing-automation')

# Destinatários
RECIPIENTS = ['jp@jphub.com.br', 'joaohomem@falconi.com']
CC_RECIPIENTS = []

# Fontes de busca
SEARCH_QUERIES = [
    'ChatGPT Enterprise news latest',
    'OpenAI blog ChatGPT updates',
    'ChatGPT Enterprise release notes',
]

def get_current_time_sao_paulo():
    """Retorna horário atual em São Paulo"""
    from datetime import datetime, timezone, timedelta
    sp_tz = timezone(timedelta(hours=-3))
    return datetime.now(sp_tz)

def search_openai_news():
    """
    Busca notícias sobre ChatGPT Enterprise das últimas 24-72h
    Usa COMPOSIO_SEARCH_NEWS
    """
    logger.info("🔍 Buscando notícias sobre ChatGPT Enterprise...")
    
    all_results = []
    
    for query in SEARCH_QUERIES:
        try:
            # Chama via Rube API
            response = requests.post(
                f'{RUBE_BASE_URL}/api/execute',
                headers={
                    'Authorization': f'Bearer {RUBE_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'session_id': RUBE_SESSION_ID,
                    'tool_slug': 'COMPOSIO_SEARCH_NEWS',
                    'arguments': {
                        'query': query,
                        'when': 'd',  # Últimas 24h
                        'gl': 'br',
                        'hl': 'pt'
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', {}).get('results', [])
                all_results.extend(results)
                logger.info(f"✅ Encontradas {len(results)} notícias para: {query}")
            else:
                logger.warning(f"⚠️ Erro na busca: {response.status_code} - {query}")
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar notícias: {str(e)}")
    
    return all_results[:10]  # Limitar a 10 melhores resultados

def generate_html_briefing(news_items):
    """
    Gera HTML bonito e visual do briefing
    """
    now = get_current_time_sao_paulo()
    date_str = now.strftime('%d/%m/%Y às %H:%M BRT')
    
    # Se sem notícias, usar fallback
    if not news_items:
        tldr = "Sem novidades relevantes hoje."
        news_html = "<p>Nenhuma notícia encontrada nas últimas 24h.</p>"
    else:
        tldr = f"Encontradas {len(news_items)} notícias sobre ChatGPT Enterprise"
        news_html = ""
        for i, item in enumerate(news_items, 1):
            title = item.get('title', 'Sem título')
            snippet = item.get('snippet', '')
            link = item.get('link', '#')
            source = item.get('source', 'Fonte desconhecida')
            
            news_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #0066cc; background: #f5f8fa;">
                <h4 style="margin-top: 0; color: #0066cc;">{title}</h4>
                <p style="color: #333; line-height: 1.6;">{snippet}</p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                    📌 <strong>Fonte:</strong> {source} | 
                    <a href="{link}" style="color: #0066cc; text-decoration: none;">Ler mais →</a>
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
            <h1>📊 Briefing ChatGPT Enterprise</h1>
            <p>{date_str}</p>
        </div>
        
        <!-- CONTEÚDO -->
        <div class="content">
            <!-- TL;DR -->
            <div class="section">
                <div class="tldr">
                    <div class="tldr-label">🚀 TL;DR (RESUMO EXECUTIVO)</div>
                    <p>{tldr}</p>
                </div>
            </div>
            
            <!-- NOVIDADES -->
            <div class="section">
                <h2>📰 Novidades & Lançamentos</h2>
                {news_html}
            </div>
            
            <!-- DICA -->
            <div class="section">
                <h2>💡 Dica de Uso</h2>
                <div class="tip">
                    <strong>Company Knowledge:</strong> Ative o recurso Company Knowledge no seu ChatGPT Enterprise 
                    para buscar automaticamente em Slack, SharePoint, Google Drive e mais, tudo em uma única pergunta!
                </div>
            </div>
            
            <!-- PRÓXIMOS PASSOS -->
            <div class="section">
                <h2>📍 Próximos Passos</h2>
                <ul>
                    <li>Revisar novidades e impactos para sua equipe</li>
                    <li>Explorar <a href="https://help.openai.com">documentação oficial</a></li>
                    <li>Testar novos recursos em ambiente controlado</li>
                </ul>
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>
                📧 Briefing automático enviado diariamente às 20:00 BRT<br>
                Fontes: Blog OpenAI | Documentação Oficial | Release Notes<br>
                <a href="https://status.openai.com">Status OpenAI</a> | 
                <a href="https://openai.com/index/company-knowledge">Saiba mais</a>
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_body

def send_email_via_rube(subject, html_body, to_emails, cc_emails=None):
    """
    Envia email via Outlook através do Rube
    """
    logger.info(f"📧 Enviando email para: {', '.join(to_emails)}")
    
    try:
        cc_emails = cc_emails or []
        
        response = requests.post(
            f'{RUBE_BASE_URL}/api/execute',
            headers={
                'Authorization': f'Bearer {RUBE_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'session_id': RUBE_SESSION_ID,
                'tool_slug': 'OUTLOOK_SEND_EMAIL',
                'arguments': {
                    'subject': subject,
                    'body': html_body,
                    'to_email': ', '.join(to_emails),
                    'cc_emails': cc_emails,
                    'is_html': True,
                    'user_id': 'me'
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info("✅ Email enviado com sucesso!")
            return True
        else:
            logger.error(f"❌ Erro ao enviar email: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Exceção ao enviar email: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("🤖 INICIANDO BRIEFING CHATGPT ENTERPRISE")
    logger.info("=" * 60)
    
    # 1. Buscar notícias
    logger.info("\n[1/3] Coletando notícias...")
    news_items = search_openai_news()
    
    # 2. Gerar HTML
    logger.info("[2/3] Gerando HTML bonito...")
    html_body = generate_html_briefing(news_items)
    
    # 3. Enviar email
    logger.info("[3/3] Enviando email...")
    now = get_current_time_sao_paulo()
    date_str = now.strftime('%Y-%m-%d')
    subject = f"[Briefing ChatGPT Enterprise] {date_str} — Novidades, Roadmap, Dicas (20:00 BRT)"
    
    success = send_email_via_rube(subject, html_body, RECIPIENTS, CC_RECIPIENTS)
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ BRIEFING FINALIZADO COM SUCESSO!")
    else:
        logger.info("⚠️ BRIEFING FINALIZADO COM AVISO (verificar logs)")
    logger.info("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
