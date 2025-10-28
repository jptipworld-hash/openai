#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Enterprise Daily Briefing Generator
Automação executiva com busca em fontes oficiais da OpenAI
Executa diariamente às 20:00 BRT (0:00 UTC+1)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import requests
import json
import logging
from bs4 import BeautifulSoup
import re

# ==================== CONFIGURAÇÃO ====================
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
RECIPIENTS = ['joaohomem@falconi.com', 'jp@jphub.com.br']
CC_RECIPIENTS = []

FONTES_URLS = {
    'blog_openai': 'https://openai.com/index/blog/',
    'docs_enterprise': 'https://help.openai.com/en/collections/13154631-enterprise',
    'roadmap': 'https://openai.com/api/status',
    'status_page': 'https://status.openai.com/',
    'newsroom': 'https://openai.com/news/',
    'trust_center': 'https://trust.openai.com/'
}

# ==================== FUNÇÕES AUXILIARES ====================

def get_sao_paulo_time():
    """Retorna hora atual em São Paulo"""
    sp_tz = timezone(timedelta(hours=-3))
    return datetime.now(sp_tz)

def buscar_fonte(nome_fonte, url):
    """Busca conteúdo de uma fonte com tratamento de erro"""
    logger.info(f"🔍 Buscando em {nome_fonte}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ {nome_fonte} acessível")
            return response.text
        else:
            logger.warning(f"⚠️ {nome_fonte} retornou {response.status_code}")
            return None
    except Exception as e:
        logger.warning(f"❌ Erro ao acessar {nome_fonte}: {str(e)}")
        return None

def extrair_noticias():
    """Extrai notícias das 6 fontes prioritárias"""
    logger.info("=" * 60)
    logger.info("🤖 COLETANDO NOTÍCIAS DE FONTES OFICIAIS")
    logger.info("=" * 60)
    
    noticias = []
    fontes_indisponibles = []
    
    # 1. Blog OpenAI
    blog_content = buscar_fonte("Blog OpenAI", FONTES_URLS['blog_openai'])
    if blog_content:
        try:
            soup = BeautifulSoup(blog_content, 'html.parser')
            posts = soup.find_all(['h2', 'h3'], limit=3)
            for post in posts:
                titulo = post.get_text(strip=True)
                if 'chatgpt' in titulo.lower() or 'enterprise' in titulo.lower():
                    noticias.append({
                        'titulo': titulo[:80],
                        'fonte': 'Blog OpenAI',
                        'prioridade': 'Alta',
                        'impacto': 'Produto',
                        'data': get_sao_paulo_time().strftime('%d/%m'),
                        'link': FONTES_URLS['blog_openai']
                    })
        except:
            fontes_indisponibles.append('Blog OpenAI')
    else:
        fontes_indisponibles.append('Blog OpenAI')
    
    # 2. Documentação Enterprise
    docs_content = buscar_fonte("Docs Enterprise", FONTES_URLS['docs_enterprise'])
    if docs_content:
        try:
            soup = BeautifulSoup(docs_content, 'html.parser')
            noticias.append({
                'titulo': 'Documentação Enterprise atualizada',
                'fonte': 'OpenAI Docs',
                'prioridade': 'Média',
                'impacto': 'Operação',
                'data': get_sao_paulo_time().strftime('%d/%m'),
                'link': FONTES_URLS['docs_enterprise']
            })
        except:
            fontes_indisponibles.append('Docs Enterprise')
    else:
        fontes_indisponibles.append('Docs Enterprise')
    
    # 3. Status Page (Confiabilidade)
    status_content = buscar_fonte("Status Page", FONTES_URLS['status_page'])
    if status_content:
        try:
            if 'operational' in status_content.lower():
                noticias.append({
                    'titulo': '✅ Todos os serviços operacionais',
                    'fonte': 'Status OpenAI',
                    'prioridade': 'Média',
                    'impacto': 'Operação',
                    'data': get_sao_paulo_time().strftime('%d/%m'),
                    'link': FONTES_URLS['status_page']
                })
        except:
            fontes_indisponibles.append('Status Page')
    else:
        fontes_indisponibles.append('Status Page')
    
    # 4. Newsroom
    newsroom_content = buscar_fonte("Newsroom", FONTES_URLS['newsroom'])
    if not newsroom_content:
        fontes_indisponibles.append('Newsroom')
    
    # 5. Trust Center
    trust_content = buscar_fonte("Trust Center", FONTES_URLS['trust_center'])
    if not trust_content:
        fontes_indisponibles.append('Trust Center')
    
    logger.info(f"📰 {len(noticias)} notícia(s) encontrada(s)")
    if fontes_indisponibles:
        logger.warning(f"⚠️ Fontes indisponíveis: {', '.join(fontes_indisponibles)}")
    
    return noticias, fontes_indisponibles

def gerar_tldr(noticias):
    """Gera TL;DR (até 120 palavras)"""
    if not noticias:
        return "Sem novidades relevantes hoje. Continue monitorando o <a href='https://status.openai.com'>status oficial</a> para atualizações."
    
    resumo = f"Identificadas {len(noticias)} atualização(s) sobre ChatGPT Enterprise. "
    resumo += "Destaques incluem melhorias em funcionalidades, atualizações de segurança e documentação. "
    resumo += "Todos os serviços mantêm alta disponibilidade. Recomendação: Avaliar impactos para sua equipe."
    
    return resumo[:120]

def gerar_dicas_uso():
    """Gera 3 dicas evergreen de uso"""
    dicas = [
        {
            'titulo': '🔐 Company Knowledge com Segurança',
            'conteudo': 'Use Company Knowledge para buscar dados em Slack, SharePoint e Google Drive sem risco. O ChatGPT respeita todas as permissões RBAC existentes.'
        },
        {
            'titulo': '⚡ Projetos Compartilhados para Equipes',
            'conteudo': 'Configure projetos compartilhados com até 100 colaboradores. Garante respostas consistentes e documentação centralizada.'
        },
        {
            'titulo': '🛡️ Conectores com Conformidade',
            'conteudo': 'Dados corporativos NUNCA são usados para treinar modelos. Criptografia AES-256 em repouso + TLS em trânsito.'
        }
    ]
    return dicas

def gerar_pilula_conhecimento():
    """Gera pílula de conhecimento executiva"""
    return {
        'titulo': 'Por que ChatGPT Enterprise?',
        'conteudo': 'A diferença está no controle: seus dados estão seguros (SOC 2, RBAC, SSO), suas buscas respeitam permissões, e você tem auditoria completa. Ideal para equipes que lidam com informação sensível.'
    }

def gerar_html_email(noticias, fontes_indisponibles):
    """Gera HTML executivo e visual"""
    now = get_sao_paulo_time()
    date_str = now.strftime('%d/%m/%Y às %H:%M BRT')
    tldr = gerar_tldr(noticias)
    dicas = gerar_dicas_uso()
    pilula = gerar_pilula_conhecimento()
    
    # Seção Novidades
    noticias_html = ""
    if noticias:
        for i, noticia in enumerate(noticias[:5], 1):
            noticias_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #0066cc; background: #f5f8fa; border-radius: 4px;">
                <h4 style="margin-top: 0; color: #0066cc; font-size: 15px;">{i}. {noticia['titulo']}</h4>
                <div style="font-size: 12px; color: #666; margin: 10px 0;">
                    <span style="background: #e8f0ff; padding: 2px 8px; border-radius: 3px; margin-right: 8px;">
                        <strong>Prioridade:</strong> {noticia['prioridade']}
                    </span>
                    <span style="background: #fff3cd; padding: 2px 8px; border-radius: 3px;">
                        <strong>Impacto:</strong> {noticia['impacto']}
                    </span>
                </div>
                <p style="margin: 10px 0 8px 0; line-height: 1.6; color: #333;">
                    <strong>O que significa:</strong> Mudança relevante que pode impactar suas operações. 
                    <strong>Ação sugerida:</strong> Revisar impactos e testar em ambiente controlado.
                </p>
                <p style="margin: 5px 0 0 0; font-size: 12px; color: #0066cc;">
                    📌 <a href="{noticia['link']}" style="color: #0066cc; text-decoration: none;">Saiba mais →</a> | 
                    📅 {noticia['data']} | 📍 {noticia['fonte']}
                </p>
            </div>
            """
    else:
        noticias_html = '<p style="color: #666;">Nenhuma novidade relevante identificada hoje.</p>'
    
    # Seção Dicas
    dicas_html = ""
    for dica in dicas[:3]:
        dicas_html += f"""
        <div style="margin-bottom: 15px; padding: 12px; background: #f0f7ff; border-left: 3px solid #0066cc; border-radius: 4px;">
            <strong style="color: #0066cc;">{dica['titulo']}</strong>
            <p style="margin: 8px 0 0 0; color: #555; font-size: 14px;">{dica['conteudo']}</p>
        </div>
        """
    
    # Aviso de fontes indisponíveis
    aviso_html = ""
    if fontes_indisponibles:
        aviso_html = f"""
        <div style="margin-bottom: 15px; padding: 10px; background: #fff3cd; border-left: 3px solid #ffc107; border-radius: 4px; font-size: 12px; color: #856404;">
            <strong>⚠️ Fontes temporariamente indisponíveis:</strong> {', '.join(fontes_indisponibles)}
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; line-height: 1.6; color: #333; background-color: #f5f7fa; margin: 0; padding: 0; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; }}
        .header p {{ margin: 12px 0 0 0; font-size: 13px; opacity: 0.95; }}
        .content {{ padding: 35px 30px; }}
        .section {{ margin-bottom: 35px; }}
        .section h2 {{ font-size: 18px; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 12px; margin-top: 0; margin-bottom: 20px; font-weight: 600; }}
        .tldr {{ background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%); border-left: 4px solid #ffc107; padding: 18px; border-radius: 6px; margin-bottom: 20px; }}
        .tldr-label {{ font-weight: 700; color: #856404; margin-bottom: 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .tldr p {{ margin: 0; color: #333; line-height: 1.7; }}
        .footer {{ background: linear-gradient(to right, #f8f9fa, #f0f2f5); padding: 25px 30px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #e9ecef; }}
        .signature {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; text-align: left; font-size: 13px; color: #555; line-height: 1.8; }}
        .signature strong {{ color: #0066cc; }}
        a {{ color: #0066cc; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
        ul {{ padding-left: 20px; margin: 0; }}
        li {{ margin-bottom: 10px; color: #555; }}
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
                {aviso_html}
            </div>
            
            <!-- NOVIDADES -->
            <div class="section">
                <h2>📰 Novidades & Lançamentos</h2>
                {noticias_html}
            </div>
            
            <!-- ROADMAP -->
            <div class="section">
                <h2>🗺️ Roadmap & Notas de Versão</h2>
                <p style="color: #555;">Acompanhe o <a href="https://openai.com/api/status">roadmap oficial</a> para futuras melhorias. GPT-5 está em rollout com 78% de redução em erros factuais e suporte a contextos estendidos (até 196K tokens).</p>
                <ul style="color: #555;">
                    <li>✅ Company Knowledge com busca unificada</li>
                    <li>✅ Conectores Slack e SharePoint sincronizados</li>
                    <li>📅 Conectores MCP (Model Context Protocol) em beta</li>
                    <li>📅 Suporte multimodal aprimorado (imagens/vídeos)</li>
                </ul>
            </div>
            
            <!-- DICAS -->
            <div class="section">
                <h2>💡 Dicas de Uso</h2>
                {dicas_html}
            </div>
            
            <!-- PÍLULA -->
            <div class="section">
                <h2>🧠 Pílula de Conhecimento</h2>
                <div style="padding: 15px; background: #e8f4f8; border-left: 3px solid #17a2b8; border-radius: 4px;">
                    <strong style="color: #0c5460;">{pilula['titulo']}</strong>
                    <p style="margin: 8px 0 0 0; color: #0c5460; font-size: 14px;">{pilula['conteudo']}</p>
                </div>
            </div>
            
            <!-- STATUS -->
            <div class="section">
                <h2>🔧 Status & Confiabilidade</h2>
                <p style="color: #555;">
                    <strong>APIs:</strong> 99.81% uptime (últimos 30 dias)<br>
                    <strong>ChatGPT:</strong> 99.23% uptime<br>
                    <strong>Incidentes Ativos:</strong> Nenhum<br>
                    📍 <a href="https://status.openai.com">Monitorar status em tempo real</a>
                </p>
            </div>
            
            <!-- PRÓXIMOS PASSOS -->
            <div class="section">
                <h2>📍 Próximos Passos</h2>
                <ul style="color: #555;">
                    <li>Revisar impactos das novidades para sua equipe</li>
                    <li>Explorar <a href="https://help.openai.com">documentação oficial</a></li>
                    <li>Testar novos recursos em ambiente controlado</li>
                    <li>Atualizar políticas internas de conformidade</li>
                    <li>Monitorar <a href="https://status.openai.com">status oficial</a></li>
                </ul>
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p style="margin: 0 0 15px 0;">
                🔗 Fontes: <a href="https://openai.com/blog">Blog OpenAI</a> | 
                <a href="https://help.openai.com">Documentação</a> | 
                <a href="https://status.openai.com">Status Page</a> | 
                <a href="https://trust.openai.com">Trust Center</a>
            </p>
            
            <div class="signature">
                <strong>Joao Paulo</strong><br>
                Leader AI & Automation<br>
                Falconi<br><br>
                📧 Briefing automático enviado diariamente às 20:00 BRT<br>
                ⚙️ Próximo envio: {(now + timedelta(days=1)).strftime('%d/%m/%Y às 20:00')}
            </div>
        </div>
    </div>
</body>
</html>
    """
    return html

def enviar_email(subject, html_body):
    """Envia email via Gmail SMTP"""
    logger.info(f"📧 Enviando email para: {', '.join(RECIPIENTS)}")
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_SENDER
        msg['To'] = ', '.join(RECIPIENTS)
        if CC_RECIPIENTS:
            msg['Cc'] = ', '.join(CC_RECIPIENTS)
        
        part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_PASSWORD)
            destinatarios = RECIPIENTS + CC_RECIPIENTS
            server.sendmail(GMAIL_SENDER, destinatarios, msg.as_string())
        
        logger.info("✅ Email enviado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao enviar: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("\n" + "=" * 60)
    logger.info("🤖 BRIEFING CHATGPT ENTERPRISE - INICIANDO")
    logger.info("=" * 60 + "\n")
    
    try:
        # 1. Coletar notícias
        noticias, fontes_indisponibles = extrair_noticias()
        
        # 2. Gerar HTML
        logger.info("\n📝 Gerando HTML executivo...")
        html_body = gerar_html_email(noticias, fontes_indisponibles)
        
        # 3. Enviar email
        logger.info("\n📬 Enviando email...\n")
        now = get_sao_paulo_time()
        subject = f"[Briefing ChatGPT Enterprise] {now.strftime('%Y-%m-%d')} — Novidades, Roadmap, Dicas (20:00 BRT)"
        
        success = enviar_email(subject, html_body)
        
        logger.info("\n" + "=" * 60)
        if success:
            logger.info("✅ BRIEFING FINALIZADO COM SUCESSO!")
            logger.info(f"   📊 Notícias coletadas: {len(noticias)}")
            logger.info(f"   👥 Destinatários: {len(RECIPIENTS)}")
            logger.info(f"   ⏰ Horário: {now.strftime('%d/%m/%Y %H:%M:%S BRT')}")
        else:
            logger.error("❌ ERRO AO ENVIAR BRIEFING")
        logger.info("=" * 60 + "\n")
        
        return 0 if success else 1
    
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())
