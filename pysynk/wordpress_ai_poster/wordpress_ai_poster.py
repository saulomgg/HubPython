```python
# =========================================================
# Desenvolvido por Saulomgg
# GitHub Oficial:
# https://github.com/saulomgg
#
# Projeto Open Source para automação de postagens WordPress
# utilizando IA + APIs de imagens.
#
# Este projeto foi criado para estudos, automação de conteúdo,
# SEO e integração com APIs.
# =========================================================

import requests
import base64
import re
import unidecode
import os
from datetime import datetime, timedelta

# =========================================================
# CONFIGURAÇÕES DO WORDPRESS
# =========================================================

# URL da API do WordPress
# Exemplo:
# https://seusite.com/wp-json/wp/v2/
WORDPRESS_URL = "ADICIONE_AQUI_A_URL_DA_API_WORDPRESS"

# Usuário do WordPress
USUARIO = "ADICIONE_SEU_USUARIO"

# Senha de Aplicativo do WordPress
# Gere em:
# WordPress > Usuário > Perfil > Senhas de Aplicativo
SENHA_APP = "ADICIONE_SUA_SENHA_DE_APLICATIVO"

# =========================================================
# AUTENTICAÇÃO WORDPRESS
# =========================================================

# Aqui é criada a autenticação Basic Auth para a API
credenciais = f"{USUARIO}:{SENHA_APP}"
token = base64.b64encode(credenciais.encode()).decode()

headers = {
    "Authorization": f"Basic {token}",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# =========================================================
# ARQUIVO DE FRASES/TEMAS
# =========================================================

# Arquivo TXT contendo os temas das postagens
# Uma linha = um tema/post
ARQUIVO_FRASES = "frases.txt"

# =========================================================
# FUNÇÃO: LER PRIMEIRA LINHA
# =========================================================

def ler_primeira_linha():
    """
    Lê a primeira linha do arquivo TXT.
    Cada linha representa um novo tema para postagem.
    """

    if not os.path.exists(ARQUIVO_FRASES):
        print("❌ Arquivo de frases não encontrado!")
        return None

    with open(ARQUIVO_FRASES, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    if not linhas:
        print("✅ Todas as frases foram publicadas!")
        return None

    return linhas[0].strip()

# =========================================================
# FUNÇÃO: REMOVER PRIMEIRA LINHA
# =========================================================

def remover_primeira_linha():
    """
    Remove a primeira linha do arquivo após postagem concluída.
    """

    try:
        with open(ARQUIVO_FRASES, "r", encoding="utf-8") as f:
            linhas = f.readlines()

        if len(linhas) > 1:
            with open(ARQUIVO_FRASES, "w", encoding="utf-8") as f:
                f.writelines(linhas[1:])

            print("✅ Primeira linha removida.")

        else:
            with open(ARQUIVO_FRASES, "w", encoding="utf-8") as f:
                f.write("")

            print("⚠️ Arquivo esvaziado.")

    except Exception as e:
        print(f"❌ Erro: {e}")

# =========================================================
# FUNÇÃO: GERAR CONTEÚDO COM IA
# =========================================================

def gerar_conteudo(frase):

    # =====================================================
    # ADICIONE SUA API KEY DA IA AQUI
    # =====================================================

    GEMINI_API_KEY = "ADICIONE_SUA_API_KEY"

    # Endpoint da API Gemini
    GEMINI_URL = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-1.5-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    # Prompt enviado para IA
    prompt = f"""
    Create a detailed SEO article about:
    {frase}
    """

    dados = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    resposta = requests.post(GEMINI_URL, json=dados)

    if resposta.status_code == 200:

        texto = resposta.json()["candidates"][0]["content"]["parts"][0]["text"]

        linhas = texto.split("\n", 1)

        titulo = linhas[0].strip().replace("## ", "")

        conteudo = (
            "<p>" +
            linhas[1].strip()
            .replace("\n", "</p><p>")
            .replace("*", "")
            .replace("**", "") +
            "</p>"
        )

        return titulo, conteudo

    else:
        print("❌ Erro ao gerar conteúdo")
        return None, None

# =========================================================
# FUNÇÃO: GERAR IMAGEM COM PEXELS
# =========================================================

def gerar_imagem_pexels(prompt):

    # API KEY DO PEXELS
    api_key = "ADICIONE_SUA_API_KEY_PEXELS"

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": api_key
    }

    params = {
        "query": prompt,
        "per_page": 1
    }

    try:

        resposta = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        if resposta.status_code == 200:

            resultados = resposta.json().get("photos", [])

            if resultados:
                return resultados[0]["src"]["large"]

    except Exception as e:
        print(f"❌ Erro Pexels: {e}")

    return None

# =========================================================
# FUNÇÃO: GERAR IMAGEM COM PIXABAY
# =========================================================

def gerar_imagem_pixabay(prompt):

    # API KEY DO PIXABAY
    api_key = "ADICIONE_SUA_API_KEY_PIXABAY"

    url = "https://pixabay.com/api/"

    params = {
        "key": api_key,
        "q": prompt,
        "image_type": "photo",
        "per_page": 1
    }

    try:

        resposta = requests.get(
            url,
            params=params,
            timeout=10
        )

        if resposta.status_code == 200:

            resultados = resposta.json().get("hits", [])

            if resultados:
                return resultados[0]["webformatURL"]

    except Exception as e:
        print(f"❌ Erro Pixabay: {e}")

    return None

# =========================================================
# FUNÇÃO: ENVIAR IMAGEM AO WORDPRESS
# =========================================================

def enviar_imagem_wordpress(imagem_url, titulo):

    try:

        resposta_imagem = requests.get(imagem_url, timeout=10)

        if resposta_imagem.status_code != 200:
            print("❌ Erro ao baixar imagem.")
            return None

        headers_media = {
            "Authorization": f"Basic {token}"
        }

        nome_arquivo = f"{titulo}.jpg"

        files = {
            "file": (
                nome_arquivo,
                resposta_imagem.content,
                "image/jpeg"
            )
        }

        resposta = requests.post(
            WORDPRESS_URL + "media",
            headers=headers_media,
            files=files
        )

        if resposta.status_code == 201:
            return resposta.json().get("id")

    except Exception as e:
        print(f"❌ Erro upload imagem: {e}")

    return None

# =========================================================
# FUNÇÃO: GERAR SLUG
# =========================================================

def gerar_slug(titulo):

    slug = unidecode.unidecode(titulo.lower())

    slug = re.sub(r'\s+', '-', slug)

    slug = re.sub(r'[^a-z0-9-]', '', slug)

    return slug

# =========================================================
# FUNÇÃO: CRIAR POST
# =========================================================

def criar_post(frase, agendamento=None):

    titulo, conteudo = gerar_conteudo(frase)

    if not titulo:
        print("❌ Falha ao gerar conteúdo.")
        return

    # Tenta gerar imagem pelo Pexels
    imagem_url = gerar_imagem_pexels(frase)

    # Fallback Pixabay
    if not imagem_url:

        print("⚠️ Pexels falhou. Tentando Pixabay...")

        imagem_url = gerar_imagem_pixabay(frase)

    # Imagem padrão
    if not imagem_url:

        imagem_url = (
            "ADICIONE_AQUI_UMA_IMAGEM_PADRAO"
        )

    featured_media_id = None

    if imagem_url:
        featured_media_id = enviar_imagem_wordpress(
            imagem_url,
            titulo
        )

    slug = gerar_slug(titulo)

    # IDs de tags e categorias do WordPress
    tags = [1]
    categoria = [1]

    dados = {
        "title": titulo,
        "content": conteudo,
        "status": "future",
        "date": agendamento.isoformat(),
        "slug": slug,
        "tags": tags,
        "categories": categoria
    }

    if featured_media_id:
        dados["featured_media"] = featured_media_id

    resposta = requests.post(
        WORDPRESS_URL + "posts",
        headers=headers,
        json=dados
    )

    if resposta.status_code == 201:

        print(f"✅ Post criado: {titulo}")

        remover_primeira_linha()

    else:

        print("❌ Erro ao publicar")
        print(resposta.text)

# =========================================================
# LOOP PRINCIPAL
# =========================================================

def iniciar_publicacao():

    intervalo_horas = int(input(
        "⏳ Intervalo entre postagens (horas): "
    ))

    intervalo_segundos = intervalo_horas * 3600

    agora = datetime.now()

    proxima_postagem = agora

    while True:

        frase = ler_primeira_linha()

        if not frase:
            print("✅ Todas as frases processadas.")
            break

        criar_post(
            frase,
            agendamento=proxima_postagem
        )

        proxima_postagem += timedelta(
            seconds=intervalo_segundos
        )

# =========================================================
# INICIAR SISTEMA
# =========================================================

iniciar_publicacao()
```
