# legacy_system.py
# Requisito 1.1.3: Sistema Legado Simulado

import xml.etree.ElementTree as ET
import uuid

# Simulação de um banco de dados interno do sistema legado
LEGACY_DATABASE = {}

def process_cadastro_xml(xml_request: str) -> str:
    """
    Simula o legado recebendo um XML de cadastro.
    Ele armazena os dados (incluindo o CPF criptografado)
    e retorna um XML de confirmação.
    """
    try:
        root = ET.fromstring(xml_request)
        
        # --- INÍCIO DA CORREÇÃO ---
        # O XML tem um nó <cliente> aninhado.
        # Precisamos encontrar esse nó primeiro.
        cliente_node = root.find('cliente')
        
        # Agora, procuramos as tags dentro do <cliente>
        nome = cliente_node.find('nome').text
        email = cliente_node.find('email').text
        cpf_criptografado = cliente_node.find('cpf').text
        # --- FIM DA CORREÇÃO ---

        # Gera um novo ID de cliente
        novo_id = str(uuid.uuid4())[:8]

        # Armazena no "banco de dados"
        LEGACY_DATABASE[novo_id] = {
            "nome": nome,
            "email": email,
            "cpf_criptografado": cpf_criptografado
        }

        # Cria a resposta XML
        xml_response = f"""
        <respostaCadastro>
            <status>SUCESSO</status>
            <idConfirmacao>{novo_id}</idConfirmacao>
        </respostaCadastro>
        """
        return xml_response

    except Exception as e:
        return f"<respostaCadastro><status>ERRO</status><mensagem>{e}</mensagem></respostaCadastro>"


def process_consulta_xml(xml_request: str) -> str:
    """
    Simula o legado recebendo um XML de consulta por ID.
    Retorna um XML com os dados do cliente (CPF ainda criptografado). 
    """
    try:
        root = ET.fromstring(xml_request)
        cliente_id = root.find('id').text

        cliente_data = LEGACY_DATABASE.get(cliente_id)

        if not cliente_data:
            return "<respostaConsulta><status>ERRO</status><mensagem>Cliente nao encontrado</mensagem></respostaConsulta>"

        # Cria a resposta XML 
        xml_response = f"""
        <respostaConsulta>
            <status>SUCESSO</status>
            <cliente>
                <id>{cliente_id}</id>
                <nome>{cliente_data['nome']}</nome>
                <email>{cliente_data['email']}</email>
                <cpf>{cliente_data['cpf_criptografado']}</cpf>
            </cliente>
        </respostaConsulta>
        """
        return xml_response

    except Exception as e:
        return f"<respostaConsulta><status>ERRO</status><mensagem>{e}</mensagem></respostaConsulta>"