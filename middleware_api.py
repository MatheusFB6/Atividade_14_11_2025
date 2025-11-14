# middleware_api.py
# Requisito 1.1.2: Middleware REST/RESTful (API a ser desenvolvida)

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, EmailStr
import xml.etree.ElementTree as ET

# Importa nossos módulos locais
import crypto_utils
import legacy_system

app = FastAPI(
    title="Middleware Legado API",
    description="Implementação do exercício de Web Service com Criptografia."
)

# ---
# Requisito 5.2: Implementar mecanismo simples de autenticação 
# Usaremos um API Token simples no cabeçalho. 
# ---
API_KEY_NAME = "Authorization"
API_KEY = "MEU_TOKEN_SECRETO_123"  # Token fixo para o exercício
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Valida o API Key enviado no header."""
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido ou ausente",
        )

# ---
# Modelos de Dados (Pydantic) para validação 
# ---
class ClienteInput(BaseModel):
    nome: str
    email: EmailStr
    cpf: str # Recebe o CPF em texto plano do cliente 

class ClienteOutput(BaseModel):
    id: str
    nome: str
    email: str
    cpf: str # Devolve o CPF em texto plano para o cliente 

class CadastroResponse(BaseModel):
    mensagem: str
    id_confirmacao: str

# ---
# Requisito 5.1: Configurar HTTPS 
#
# Em um ambiente de produção, o FastAPI não rodaria sozinho.
# Usaríamos um servidor ASGI como Uvicorn ou Gunicorn
# por trás de um Reverse Proxy (como Nginx ou Caddy).
# O Nginx/Caddy seria responsável por lidar com o HTTPS,
# gerenciando os certificados SSL (ex: via Let's Encrypt).
# A comunicação entre o Nginx (público) e o Uvicorn (interno)
# poderia ser HTTP, pois estaria dentro de uma rede privada.
# ---


# ---
# Requisito 2: Funcionalidades Obrigatórias
# ---

@app.post("/api/clientes", response_model=CadastroResponse, tags=["Clientes"])
async def cadastrar_cliente(
    cliente: ClienteInput,
    api_key: str = Depends(get_api_key)
):
    """
    Requisito 2.1: POST /api/clientes 
    Recebe JSON, criptografa o CPF, monta XML e envia ao legado.
    """
    # 1. Validar dados (Feito automaticamente pelo Pydantic/FastAPI) 

    # 2. Criptografar dados sensíveis 
    try:
        cpf_criptografado = crypto_utils.encrypt_data(cliente.cpf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criptografar dados: {e}")

    # 3. Montar XML para o legado 
    xml_request = f"""
    <requisicaoCadastro>
        <cliente>
            <nome>{cliente.nome}</nome>
            <email>{cliente.email}</email>
            <cpf>{cpf_criptografado}</cpf>
        </cliente>
    </requisicaoCadastro>
    """

    # 4. Enviar XML para o sistema legado simulado 
    xml_response_str = legacy_system.process_cadastro_xml(xml_request)

    # 5. Tratar resposta do legado e retornar JSON ao cliente 
    try:
        root = ET.fromstring(xml_response_str)
        status_legado = root.find('status').text
        
        if status_legado == "SUCESSO":
            id_confirmacao = root.find('idConfirmacao').text
            return CadastroResponse(
                mensagem="Cliente cadastrado com sucesso",
                id_confirmacao=id_confirmacao
            )
        else:
            raise HTTPException(status_code=400, detail="Erro no sistema legado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar resposta do legado: {e}")


@app.get("/api/clientes/{id}", response_model=ClienteOutput, tags=["Clientes"])
async def consultar_cliente(
    id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Requisito 2.2: GET /api/clientes/{id} 
    Recebe ID, consulta legado via XML, recebe XML criptografado,
    descriptografa e retorna JSON.
    """
    # 1. Gerar XML de requisição ao legado 
    xml_request = f"<requisicaoConsulta><id>{id}</id></requisicaoConsulta>"

    # 2. Enviar requisição ao "sistema legado" 
    xml_response_str = legacy_system.process_consulta_xml(xml_request)

    # 3. Receber XML de resposta 
    try:
        root = ET.fromstring(xml_response_str)
        status_legado = root.find('status').text
        
        if status_legado != "SUCESSO":
            mensagem_erro = root.find('mensagem').text
            raise HTTPException(status_code=404, detail=f"Erro no legado: {mensagem_erro}")

        # 4. Extrair e Descriptografar os dados 
        cliente_data = root.find('cliente')
        cpf_criptografado = cliente_data.find('cpf').text
        
        try:
            cpf_descriptografado = crypto_utils.decrypt_data(cpf_criptografado)
        except Exception:
            raise HTTPException(status_code=500, detail="Erro: Falha ao descriptografar dados do legado.")

        # 5. Converter para JSON e devolver ao cliente 
        return ClienteOutput(
            id=cliente_data.find('id').text,
            nome=cliente_data.find('nome').text,
            email=cliente_data.find('email').text,
            cpf=cpf_descriptografado # Retorna o CPF descriptografado
        )

    except ET.ParseError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parsear resposta do legado: {e}")