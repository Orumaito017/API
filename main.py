from flask import Flask, make_response, jsonify, request
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Método GET para buscar todos os usuários
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    usuarios = data.get('usuarios', [])
    return make_response(jsonify(usuarios))

# Método GET para buscar todos os perfis
@app.route('/perfil', methods=['GET'])
def get_perfis():
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    perfis = data.get('perfis', [])
    return make_response(jsonify(perfis))

# Método POST para criação de um novo usuário
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    if not request.is_json:
        return make_response(jsonify({"mensagem": "Requisição deve ser JSON"}), 400)

    novo_usuario = request.get_json()

    # Verifica se 'matricula', 'nome' e 'profile' estão presentes
    if not novo_usuario.get('matricula') or not novo_usuario.get('nome') or not novo_usuario.get('profile'):
        return make_response(jsonify({"mensagem": "Campos 'matricula', 'nome' e 'profile' são obrigatórios"}), 400)

    # Tenta converter a matrícula para inteiro
    try:
        matricula = int(novo_usuario['matricula'])
    except ValueError:
        return make_response(jsonify({"mensagem": "A matrícula deve ser um número inteiro"}), 400)

    # Carrega dados existentes
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    usuarios = data.get('usuarios', [])
    perfis = data.get('perfis', [])

    # Verifica se a matrícula já existe
    for usuario in usuarios:
        if usuario['matricula'] == matricula:
            return make_response(jsonify({"mensagem": "Matrícula já existente"}), 400)

    perfis_existentes = [perfil['profile'] for perfil in perfis]

    # Verifica se o perfil existe
    if novo_usuario['profile'] not in perfis_existentes:
        return make_response(jsonify({"mensagem": "Perfil não existente"}), 400)

    # Gera email automaticamente se não fornecido
    if 'email' not in novo_usuario:
        nome_email = novo_usuario['nome'].replace(" ", "").lower()
        novo_usuario['email'] = f"{nome_email}.{matricula}@example.com"

    # Valida formato do email
    if 'email' in novo_usuario:
        email = novo_usuario['email']
        if '@' not in email or '.com' not in email.split('@')[1]:
            return make_response(jsonify({"mensagem": "O e-mail deve seguir o formato 'nome@dominio.com'"}), 400)

    # Define o status padrão como 'Ativo', caso não seja fornecido
    if 'status' not in novo_usuario:
        novo_usuario['status'] = 'Ativo'

    # Adiciona o novo usuário à lista e salva no arquivo
    novo_usuario['matricula'] = matricula  # Salva matrícula como inteiro
    usuarios.append(novo_usuario)
    data['usuarios'] = usuarios
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return make_response(jsonify({"mensagem": "Usuário criado com sucesso", "usuario": novo_usuario}), 201)


# Método DELETE para remover perfil de um usuário específico.
@app.route('/usuarios/perfil/remover/<int:matricula>', methods=['DELETE'])
def remove_profile(matricula):
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    usuarios = data.get('usuarios', [])
    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if usuario:
        usuario['profile'] = None
        data['usuarios'] = usuarios
        with open('db.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        
        return make_response(jsonify({"mensagem": "Perfil removido com sucesso"}), 200)
    
    return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)

# Método POST para adicionar um perfil a um usuário específico
@app.route('/usuarios/perfil/adicionar/<int:matricula>', methods=['POST'])
def update_profile(matricula):
    data = request.get_json()
    novo_perfil = data.get("profile")

    if not novo_perfil:
        return make_response(jsonify({"mensagem": "Perfil ausente"}), 400)

    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    usuarios = data.get('usuarios', [])
    perfis_existentes = data.get('perfis', [])

    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if not usuario:
        return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)

    perfis_existentes_nomes = [perfil['profile'] for perfil in perfis_existentes]
    if novo_perfil not in perfis_existentes_nomes:
        return make_response(jsonify({"mensagem": "Perfil não existente"}), 400)

    usuario['profile'] = novo_perfil
    data['usuarios'] = usuarios
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return make_response(jsonify({"mensagem": "Perfil atualizado com sucesso", "usuario": usuario}), 200)

# Método POST para criar um perfil no sistema.
@app.route('/perfil', methods=['POST'])
def criar_perfil():
    novo_perfil = request.get_json()
    nome_perfil = novo_perfil.get("profile")
    codigo_perfil = novo_perfil.get("codigo")

    if not nome_perfil or not codigo_perfil:
        return make_response(jsonify({"mensagem": "Nome e código do perfil são obrigatórios"}), 400)

    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    perfis = data.get('perfis', [])
    for perfil in perfis:
        if perfil['profile'].lower() == nome_perfil.lower():
            return make_response(jsonify({"mensagem": "Nome do perfil já existente"}), 400)
        if perfil['codigo'].lower() == codigo_perfil.lower():
            return make_response(jsonify({"mensagem": "Código do perfil já existente"}), 400)

    perfis.append({"profile": nome_perfil, "codigo": codigo_perfil})
    data['perfis'] = perfis
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return make_response(jsonify({"mensagem": "Perfil criado com sucesso", "perfil": {"profile": nome_perfil, "codigo": codigo_perfil}}), 201)

# Método DELETE para remover um perfil no sistema.
@app.route('/perfil', methods=['DELETE'])
def delete_perfil():
    remove_perfil = request.get_json()
    nome_perfil = remove_perfil.get("profile")
    codigo_perfil = remove_perfil.get("codigo")

    # Verificação se o perfil e código foram passados
    if not nome_perfil or not codigo_perfil:
        return make_response(jsonify({"mensagem": "Nome e código do perfil são obrigatórios"}), 400)

    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    perfis = data.get('perfis', [])
    usuarios = data.get('usuarios', [])

    # Checa se existe algum usuário vinculado ao perfil
    matriculas_vinculadas = [
        usuario['matricula'] for usuario in usuarios if usuario['profile'] == nome_perfil
    ]

    if matriculas_vinculadas:
        return make_response(jsonify({
            "mensagem": "Não é possível remover o perfil, pois existem usuários vinculados.",
            "matriculas": matriculas_vinculadas
        }), 400)

    # Remove o perfil do arquivo 'db.json' se não houver vinculação
    perfil_encontrado = False
    for perfil in perfis:
        if perfil['profile'].lower() == nome_perfil.lower() and perfil['codigo'].lower() == codigo_perfil.lower():
            perfis.remove(perfil)
            perfil_encontrado = True
            data['perfis'] = perfis
            with open('db.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

            return make_response(jsonify({"mensagem": "Perfil removido com sucesso"}), 200)

    if not perfil_encontrado:
        return make_response(jsonify({"mensagem": "Perfil não encontrado"}), 404)

# Método GET para buscar usuário por matrícula
@app.route('/usuarios/matricula/<int:matricula>', methods=['GET'])
def get_usuario_por_matricula(matricula):
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    usuarios = data.get('usuarios', [])
    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if usuario:
        return make_response(jsonify({"usuario": usuario}), 200)

    return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)

# Método PUT para alterar atributos do usuário
@app.route('/usuario/<int:matricula>', methods=['PUT'])
def update_usuario(matricula):
    dados_atualizados = request.get_json()

    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    usuarios = data.get('usuarios', [])
    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if not usuario:
        return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)

    # Permitindo apenas a alteração de 'nome' e 'email'
    for key, value in dados_atualizados.items():
        if key in ['nome', 'email']:
            usuario[key] = value

    data['usuarios'] = usuarios
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return make_response(jsonify({"mensagem": "Usuário atualizado com sucesso", "usuario": usuario}), 200)

# Método POST para desabilitar uma matrícula
@app.route('/usuario/desabilitar/<int:matricula>', methods=['POST'])
def desabilitar_usuario(matricula):
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Lista de usuários no arquivo JSON
    usuarios = data.get('usuarios', [])
    
    # Busca pelo usuário com a matrícula fornecida
    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if not usuario:
        return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)
    
    # Verifica o status do usuário
    if usuario.get("status") == "Inativo":
        return make_response(jsonify({"mensagem": "Usuário já está desabilitado"}), 400)
    
    # Altera o status para 'Inativo'
    usuario["status"] = "Inativo"
    data['usuarios'] = usuarios

    # Salva as alterações no arquivo JSON
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    
    return make_response(jsonify({"mensagem": "Usuário desabilitado com sucesso"}), 200)

# Método POST para ativar uma matrícula
@app.route('/usuario/ativar/<int:matricula>', methods=['POST'])
def ativar_usuario(matricula):
    with open('db.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Lista de usuários no arquivo JSON
    usuarios = data.get('usuarios', [])
    
    # Busca pelo usuário com a matrícula fornecida
    usuario = next((user for user in usuarios if user['matricula'] == matricula), None)

    if not usuario:
        return make_response(jsonify({"mensagem": "Usuário não encontrado"}), 404)
    
    # Verifica o status do usuário
    if usuario.get("status") == "Ativo":
        return make_response(jsonify({"mensagem": "Usuário já está ativo"}), 400)
    
    # Altera o status para 'Ativo'
    usuario["status"] = "Ativo"
    data['usuarios'] = usuarios

    # Salva as alterações no arquivo JSON
    with open('db.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    
    return make_response(jsonify({"mensagem": "Usuário ativado com sucesso"}), 200)     

if __name__ == '__main__':
    app.run(debug=True)
