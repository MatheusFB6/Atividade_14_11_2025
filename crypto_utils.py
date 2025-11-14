# crypto_utils.py

from cryptography.fernet import Fernet

# ---
# Requisito 4.2: Definir uma chave de criptografia (pode ser fixa para o exercício).
# Em um sistema real, isso viria de uma variável de ambiente ou cofre de segredos.
# Para gerar uma nova chave, use: Fernet.generate_key()
# ---
CHAVE_FIXA = b'Y06CgC2LpxBKj1jYqjHNVf-PjGfu19k2iFDoNitOoNI='  # Chave fixa para o exercício
cipher_suite = Fernet(CHAVE_FIXA)

# ---
# Requisito 4.3: Explicação
#
# 1. Qual algoritmo foi usado? 
#    - Fernet, que é uma implementação de alto nível de criptografia
#      simétrica autenticada, usando AES-128-CBC com HMAC-SHA256.
#
# 2. Como a chave é armazenada/utilizada? 
#    - A chave está hardcoded (fixa) neste módulo (CHAVE_FIXA).
#      Em produção, seria carregada de forma segura (ex: env vars, vault).
#
# 3. Quais dados do XML são criptografados? 
#    - Conforme a especificação, o dado sensível (CPF) é criptografado.
# ---


def encrypt_data(data_str: str) -> str:
    """
    Requisito 4.2: Criptografar dados sensíveis. 
    Criptografa uma string e retorna a versão em bytes (codificada em utf-8).
    """
    data_bytes = data_str.encode('utf-8')
    encrypted_bytes = cipher_suite.encrypt(data_bytes)
    return encrypted_bytes.decode('utf-8')  # Retorna como string para por no XML

def decrypt_data(encrypted_str: str) -> str:
    """
    Requisito 4.2: Descriptografar os dados. 
    Descriptografa e retorna a string original.
    """
    encrypted_bytes = encrypted_str.encode('utf-8')
    decrypted_bytes = cipher_suite.decrypt(encrypted_bytes)
    return decrypted_bytes.decode('utf-8')