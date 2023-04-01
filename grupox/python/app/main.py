##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2021/2022 ===============
## =============================================
## ================ DB Project =================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   Gonçalo Senra nº 2020213750
##   Henrique Costa nº 2020214120
##   João Coelho nº 2020235901
##

from flask import Flask, jsonify, request
import logging, psycopg2, time
import jwt
from functools import wraps
from datetime import datetime, timedelta, date
import hashlib
import uuid


import platform
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY']= '004f2af45d3a4e161a7dd2d17fdae47f'
salt = 'fe4c0bf9ce0044c79c4e41c9891ec450'


StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = "grupox",
        password = "grupox",
        host = "db",
        port = "5432",
        database = "market_place"
    )
    
    return db



##########################################################
## ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello!  <br/>
    <br/>
    Welcome to TechMarketPlace!<br/>
    <br/>
    """


def generate_token(user_id, type_user):

    payload = {
        'exp': datetime.utcnow() + timedelta(hours=1),
        'sub': str(user_id)+';'+type_user
    }
    return jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')


def verify_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if 'Token' not in request.headers or not request.headers['Token']:
            return jsonify({'status': StatusCodes['api_error'], 'errors': 'token is missing'})

        token = request.headers['Token']

        try:
            payload = jwt.decode(
                token,
                app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            sub = payload['sub']
            array = sub.split(";")
 
        except jwt.ExpiredSignatureError:
            type_user = ""
            return jsonify({'status': StatusCodes['api_error'], 'errors': 'token expired'})

        except jwt.InvalidTokenError:
            type_user = ""
            return jsonify({'status': StatusCodes['api_error'], 'errors': 'invalid token'})

        return f(array[0], array[1], *args, **kwargs)

    return decorator
    
def verify_addUser(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if 'Token' not in request.headers or not request.headers['Token']:
            type_user = ""
            user_id = 0
            return f(user_id, type_user, *args, **kwargs)

        token = request.headers['Token']

        try:

            payload = jwt.decode(
                token,
                app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            
            sub = payload['sub']
            array = sub.split(";")


        except jwt.ExpiredSignatureError:
            type_user = ""
            return jsonify({'status': StatusCodes['api_error'], 'errors': 'token expired'})

        except jwt.InvalidTokenError:
            type_user = ""
            return jsonify({'status': StatusCodes['api_error'], 'errors': 'invalid token'})

        return f(array[0], array[1], *args, **kwargs)

    return decorator




##
## Demo GET
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##

@app.route('/dbproj/users/', methods=['GET'])
@verify_token
def get_all_users(user_id, type_user):
    logger.info('GET /users')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM utilizador')
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'user_id': int(row[0]), 'username': row[1], 'password': row[3]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
@app.route('/dbproj/products/', methods=['GET'])
@verify_token
def get_all_products(user_id, type_user):
    logger.info('GET /products')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM produto WHERE hist_id IS NULL;')
        rows = cur.fetchall()

        logger.debug('GET /products - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'prod_id': int(row[0]), 'descricao': row[1], 'preco': row[2], 'stock': row[3], 'nome': row[4], 'hist_id': row[5], 'user_id': row[6]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
    
@app.route('/dbproj/notifications/', methods=['GET'])
@verify_token
def get_notifications(user_id, type_user):
    logger.info('GET /notifications')

    conn = db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(f'select not_descricao from notificacao n join notificacao_comentario c on n.not_id = c.not_id where user_id = {user_id};')
        
        rows = cur.fetchall()

        aux = []
        for row in rows:
            aux += row
            
        content = {'notificacoes comentario': aux}
           
        if type_user == 'comprador':
            cur.execute(f'select not_descricao from notificacao n join notificacao_compra c on n.not_id = c.not_id where user_id = {user_id};')
            rows = cur.fetchall()
            aux = []
            for row in rows:
                aux += row
                
            content.update({'notificacoes compra': aux})
        elif type_user == 'vendedor':
            cur.execute(f'select not_descricao from notificacao n join notificacao_venda c on n.not_id = c.not_id where user_id = {user_id};')
            rows = cur.fetchall()
            aux = []
            for row in rows:
                aux += row
                
            content.update({'notificacoes venda': aux})
   
        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
    
@app.route('/dbproj/report/year', methods=['GET'])
@verify_token
def get_month_satistics(user_id, type_user):
    logger.info('GET /notifications')

    conn = db_connection()
    cur = conn.cursor()
    
    if type_user != 'administrador':
        response = {'status': StatusCodes['api_error'], 'results': 'Only administrador has permissions to get statistics'}
        return jsonify(response)
    
    try:
        cur.execute(f"""select count(encom_id), sum(preco_total), (SELECT EXTRACT(Month FROM encom_date) AS "Month")
                        from encomenda e
                        group by "Month";""")
        
        rows = cur.fetchall()
        logger.info(rows)
        aux = []
        for row in rows:
            aux.append({"month":row[2], "total_value":row[1], "orders":row[0]})
        
        response = {'status': StatusCodes['success'], 'results': aux}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

@app.route('/dbproj/report/campaign', methods=['GET'])
@verify_token
def get_campaign_satistics(user_id, type_user):
    logger.info('GET /notifications')

    conn = db_connection()
    cur = conn.cursor()
    
    if type_user != 'administrador':
        response = {'status': StatusCodes['api_error'], 'results': 'Only administrador has permissions to get statistics'}
        return jsonify(response)
    
    try:
        cur.execute(f"""select ca.camp_id, count(cup_id) "Generated coupons",(select count(cup_id) "Used coupons"
                                     from cupao c
                                     where c.usado = 'true' and ca.camp_id =c.camp_id),
                                                                 (select (sum(coalesce(preco_total,0))) / (desconto/100) - sum(coalesce((preco_total),0)) "Total of discount"
                                                                 from campanha, encomenda, cupao
                                                                 where  campanha.camp_id = ca.camp_id and cupao.encom_id = encomenda.encom_id and cupao.usado = 'true'
                                                                 group by campanha.camp_id)
                        from cupao ca
                        group by ca.camp_id""")
        
        rows = cur.fetchall()
        logger.info(rows)
        aux = []
        for row in rows:
            aux.append({"campaign_id":row[0], "generated_coupons":row[1], "used_coupons":row[2], "total_discount_value":row[3]})
        
        response = {'status': StatusCodes['success'], 'results': aux}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


@app.route('/dbproj/product/<prod_id>', methods=['GET'])
@verify_token
def get_product_info(user_id, type_user, prod_id):
    logger.info('GET /notifications')

    conn = db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(f"""select nome, stock, preco, (select descricao from produto where prod_id = {prod_id}) ,prod_date, coalesce((select avg(classificacao)
                                                                         from rating r, produto p2
                                                                         where r.prod_id = p2.prod_id 
                                                                         and p2.stats_id = (select stats_id from produto where prod_id = {prod_id})
                                                                         group by p2.stats_id), 0)
                                                                        ,
                                                                        (select STRING_AGG(com_comentario,';')
                                                                        from comentario c, produto p3
                                                                        where c.prod_id = p3.prod_id
                                                                        and p3.stats_id = (select stats_id from produto where prod_id = {prod_id})
                                                                        )
                        from produto p
                        where p.stats_id = (select stats_id from produto where prod_id = {prod_id})""")
        
        rows = cur.fetchall()
        logger.info(rows)
        aux = {"name": rows[0][0], "stock": rows[0][1], "product_description": rows[0][3], "rating": rows[0][5]}
        comment = rows[0][6].split(';')
        aux.update({"comments": comment})
        precos = []
        for row in rows:
            precos.append(str(row[4])+' - '+str(row[2]))
        
        aux.update({"prices": precos})
        response = {'status': StatusCodes['success'], 'results': aux}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

##
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/user/ -H 'Content-Type: application/json' -d '{'localidade': 'Polo II', 'ndep': 69, 'nome': 'Seguranca'}'
##

@app.route('/dbproj/user/', methods=['POST'])
@verify_addUser
def add_user(user_id, type_user):
    logger.debug(type_user)
    logger.info('POST /user')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'username' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username value not in payload'}
        return jsonify(response)

    if 'email' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'email value not in payload'}
        return jsonify(response)

    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password value not in payload'}
        return jsonify(response)

    if 'type' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'type of user not specified in payload'}
        return jsonify(response)
    
    hashed_password = hashlib.sha512(payload['password'].encode('utf-8') + salt.encode('utf-8')).hexdigest()
    # parameterized queries, good for security and performance
    if payload['type'] == 'administrador':
        if type_user != "administrador":
            response = {'status': StatusCodes['api_error'], 'results': 'you dont have permissions to create an administrador'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into utilizador (username, email, password) values(%s, %s, %s) returning user_id into insertedID; ' \
                    'insert into administrador (user_id) values(insertedID); ' \
                    'end; ' \
                    '$$;'
        values = (payload['username'], payload['email'], hashed_password)
    elif payload['type'] == 'vendedor':
        if type_user != "administrador":
            response = {'status': StatusCodes['api_error'], 'results': 'you dont have permissions to create a vendedor'}
            return jsonify(response)
        if 'vend_morada' not in payload or 'vend_nif' not in payload or 'IBAN' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'value missing in payload'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into utilizador (username, email, password) values(%s, %s, %s) returning user_id into insertedID; ' \
                    'insert into vendedor (user_id, vend_morada, vend_nif, IBAN) values(insertedID, %s, %s, %s); ' \
                    'end; ' \
                    '$$;'
        values = (payload['username'], payload['email'], hashed_password, payload['vend_morada'], payload['vend_nif'], payload['IBAN'])
    elif payload['type'] == 'comprador':
        if type_user != "" and type_user != "administrador":
            response = {'status': StatusCodes['api_error'], 'results': 'you dont have permissions to create a comprador'}
            return jsonify(response)
        if 'compr_morada' not in payload or 'compr_nif' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'value missing in payload'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into utilizador (username, email, password) values(%s, %s, %s) returning user_id into insertedID; ' \
                    'insert into comprador (user_id, compr_morada, compr_nif) values(insertedID, %s, %s); ' \
                    'end; ' \
                    '$$;'
        values = (payload['username'], payload['email'], hashed_password, payload['compr_morada'], payload['compr_nif'])
    else:
        response = {'status': StatusCodes['api_error'], 'results': 'number of parameters doesn\'t match with any user'}
        return jsonify(response)

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted user {payload["username"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)

##
## Demo POST
##
## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/departments/ -H 'Content-Type: application/json' -d '{'localidade': 'Polo II', 'ndep': 69, 'nome': 'Seguranca'}'
##

@app.route('/dbproj/product/', methods=['POST'])
@verify_token
def add_product(user_id, type_user):
    logger.info('POST /product')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if type_user != 'vendedor':
        response = {'status': StatusCodes['api_error'], 'results': 'Only vendedor have permissions to sell products'}
        return jsonify(response)

    logger.debug(f'POST /product - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'nome' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'nome value not in payload'}
        return jsonify(response)

    if 'preco' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'preco value not in payload'}
        return jsonify(response)

    if 'stock' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'stock value not in payload'}
        return jsonify(response)

    if 'type' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'type of user not specified in payload'}
        return jsonify(response)

    if 'descricao' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'descricao value not in payload'}
        return jsonify(response)

    # parameterized queries, good for security and performance
    if payload['type'] == 'computador':
        if 'cpu' not in payload or 'ram' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'value missing in payload'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into produto (nome, preco, stock, descricao, user_id, stats_id) values(%s, %s, %s, %s, %s,(select max(stats_id)from produto) +1 ) returning prod_id into insertedID; ' \
                    'insert into computador (prod_id, cpu, ram) values(insertedID, %s, %s); ' \
                    'end; ' \
                    '$$;'
        values = (payload['nome'], payload['preco'], payload['stock'], payload['descricao'], user_id, payload['cpu'], payload['ram'])
    elif payload['type'] == 'televisao':
        if 'tamanho' not in payload or 'definicao' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'value missing in payload'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into produto (nome, preco, stock, descricao, user_id, stats_id) values(%s, %s, %s, %s, %s, (select max(stats_id)from produto) +1) returning prod_id into insertedID; ' \
                    'insert into televisao (prod_id, tamanho, definicao) values(insertedID, %s, %s); ' \
                    'end; ' \
                    '$$;'
        values = (payload['nome'], payload['preco'], payload['stock'], payload['descricao'], user_id, payload['tamanho'], payload['definicao'])
    elif payload['type'] == 'smartphone':
        if 'ecra' not in payload or 'ram' not in payload or 'bateria' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'value missing in payload'}
            return jsonify(response)
        statement = 'do $$ ' \
                    'declare ' \
                    'insertedID integer; ' \
                    'begin ' \
                    'insert into produto (nome, preco, stock, descricao, user_id, stats_id) values(%s, %s, %s, %s, %s,(select max(stats_id)from produto) +1) returning prod_id into insertedID; ' \
                    'insert into smartphone (prod_id, ecra, ram, bateria) values(insertedID, %s, %s, %s); ' \
                    'end; ' \
                    '$$;'
        values = (payload['nome'], payload['preco'], payload['stock'], payload['descricao'], user_id, payload['ecra'], payload['ram'], payload['bateria'])
    else:
        response = {'status': StatusCodes['api_error'], 'results': 'number of parameters doesn\'t match with any user'}
        return jsonify(response)

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted product {payload["nome"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


@app.route('/dbproj/product/<prod_id>', methods=['PUT'])
@verify_token
def update_product(user_id, type_user, prod_id):
    logger.info('PUT /product/<prod_id>')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /product/<prod_id> - payload: {payload}')
    logger.info(prod_id)
    try:
        details_prod = ['descricao', 'preco', 'stock']
        types = [['televisao','SELECT * FROM produto JOIN televisao ON produto.prod_id = televisao.prod_id WHERE produto.prod_id = %s'],
                 ['computador','SELECT * FROM produto JOIN computador ON produto.prod_id = computador.prod_id WHERE produto.prod_id = %s'], 
                 ['smartphone','SELECT * FROM produto JOIN smartphone ON produto.prod_id = smartphone.prod_id WHERE produto.prod_id = %s']]
        
        cur.execute(f"SELECT * FROM PRODUTO WHERE prod_id = {prod_id} AND hist_id IS NULL AND user_id = {user_id}")
        if cur.rowcount == 0:
            response = {'status': StatusCodes['api_error'], 'errors': 'this product can\'t be modified or doesn\'t exist'}
            return jsonify(response)

        row = []
        type_prod = ""
        statement = ""
        logger.debug(prod_id)
        for i in types:
            cur.execute(i[1], (prod_id,))
            logger.debug(cur.rowcount)
            if cur.rowcount == 1:
                row = cur.fetchall()
                #logger.info(row)
                type_prod = i[0]
                #logger.info(type_user)
                break
        

        details = []
        # parameterized queries, good for security and performance
        if type_prod == "smartphone":
            details = ['ecra', 'ram', 'bateria']
            statement = """
                        do $$
                        declare
                            insertedID integer;
                            c1 cursor for select ecra, ram, bateria from smartphone where prod_id = {};
                            registo smartphone%ROWTYPE;
                        begin
                            insert into produto (descricao, preco, stock, nome, user_id, stats_id) 
                            select descricao, preco, stock, nome, user_id, stats_id
                            from produto where prod_id = {} returning prod_id into insertedID;
                            update produto set hist_id = insertedID  where prod_id = {};
                            open c1;
                            fetch c1 into registo;
                            insert into smartphone (prod_id, ecra, ram, bateria) values(insertedID, registo.ecra, registo.ram, registo.bateria);
                        """.format(prod_id, prod_id, prod_id)
        elif type_prod == "computador":
            details = ['cpu', 'ram']
            statement = """
                        do $$
                        declare
                            insertedID integer;
                            c1 cursor for select cpu, ram from computador where prod_id = {};
                            registo computador%ROWTYPE;
                        begin
                            insert into produto (descricao, preco, stock, nome, user_id, stats_id) 
                            select descricao, preco, stock, nome, user_id, stats_id
                            from produto where prod_id = {} returning prod_id into insertedID;
                            update produto set hist_id = insertedID where prod_id = {};
                            open c1;
                            fetch c1 into registo;
                            insert into computador (prod_id, cpu, ram) values(insertedID, registo.cpu, registo.ram);
                        """.format(prod_id, prod_id, prod_id)
        elif type_prod == "televisao":
            details = ['tamanho', 'definicao']
            statement = """
                        do $$
                        declare
                            insertedID integer;
                            c1 cursor for select tamanho, definicao from televisao where prod_id = {};
                            registo televisao%ROWTYPE;
                        begin
                            insert into produto (descricao, preco, stock, nome, user_id, stats_id) 
                            select descricao, preco, stock, nome, user_id, stats_id
                            from produto where prod_id = {} returning prod_id into insertedID;
                            update produto set hist_id = insertedID where prod_id = {};
                            open c1;
                            fetch c1 into registo;
                            insert into televisao (prod_id, tamanho, definicao) values(insertedID, registo.tamanho, registo.definicao);
                        """.format(prod_id, prod_id, prod_id)
        
        for i in payload:
            if i not in details and i not in details_prod:
                response = {'status': StatusCodes['api_error'], 'results': f'the parameter {i} does\'t exist'}  
                return jsonify(response)
        for i in payload:
            if i in details:
                statement = statement + "update {} set {} = \'{}\' where prod_id = insertedID;".format(type_prod, i, payload[i])
            else: 
                statement = statement + "update produto set {} = \'{}\' where prod_id = insertedID;".format(i, payload[i])
        statement += """
                     end;
                     $$;
                     """
    
        res = cur.execute(statement)
        response = {'status': StatusCodes['success'], 'results': f'Product with id:{prod_id} has been updated'}

        # commit the transaction
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
@app.route("/dbproj/order/", methods=['POST'])
@verify_token
def order(user_id, type_user):
    logger.info("###              DEMO: POST /order              ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'payload: {payload}')
    #response = {}
    
    if "cart" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'cart not in payload'}
        return jsonify(response)
        
    if type_user != "comprador":
        response = {'status': StatusCodes['api_error'], 'results': f'the user type {type_user} cannot order'}
        return jsonify(response)
        
    logger.info(user_id + "--" + type_user)
    notificacao = ""
    for i in payload['cart']:
        notificacao += ' ID: ' + str(i[0]) + ' Quantity: ' + str(i[1])
    
    logger.debug(notificacao)
    statement = ""
    try:
        statement = f"""
                        do $$ 
                        declare
                            encID integer;
                            preco float(8);
                            precoTotal float(8);
                        begin
                            CREATE TEMPORARY TABLE t1 (var VARCHAR(512), id INTEGER) ON COMMIT DROP;
                            INSERT INTO t1 (var, id) values (\'{notificacao}\', {user_id});
                            precoTotal := 0;
                            INSERT INTO encomenda (preco_total, user_id) values(0, {user_id}) returning encom_id into encID;
                     """
        for i in payload['cart']:
            cur.execute(f"SELECT * FROM produto WHERE hist_id is NULL AND prod_id = {i[0]} AND stock >= {i[1]} for update;")
            
            if cur.rowcount != 1:
                response = {'status': StatusCodes['api_error'], 'results': f'the product with the ID: {i[0]} doesn\'t exist or doesn\'t have stock'}
                return jsonify(response)
            else:
                statement = statement + (f"""     
                                        INSERT INTO item (item_preco, quantidade, encom_id, prod_id) values ((SELECT p.preco FROM produto p WHERE prod_id = {i[0]})*{i[1]}, {i[1]}, encID, {i[0]}) returning item_preco into preco;
                                        precoTotal = precoTotal + preco;
                                        """)
             
        desconto = 0
        cupao = False
        if 'coupon' in payload:
        
            cur.execute(f'SELECT desconto, usado FROM campanha c, cupao cup WHERE cup_id = {payload["coupon"]} AND cup.camp_id = c.camp_id;')
            if cur.rowcount == 0:
                response = {'status': StatusCodes['api_error'], 'results': f'The coupon with ID: {payload["coupon"]} doesn\'t exist'}
                return jsonify(response)
            
            row = cur.fetchall() 
            logger.info(row)
            if row[0][1] == True:
                response = {'status': StatusCodes['api_error'], 'results': f'The coupon with ID: {payload["coupon"]} was already used'}
                return jsonify(response)
            desconto = row[0][0] / 100
            logger.info(desconto)
            cupao = True
   
        statement = statement + f"""
                                    UPDATE encomenda SET preco_total = precoTotal - (precoTotal * {desconto}) WHERE encom_id = encID;
                                    end;$$;
                                 """   
        
        cur.execute(statement)
        
        cur.execute(f'SELECT MAX(encom_id) FROM encomenda;')
        row = cur.fetchall()
        if cupao is True:
            cur.execute(f"""UPDATE cupao SET usado = TRUE WHERE cup_id = {payload["coupon"]};
                            UPDATE cupao SET encom_id = {row[0][0]} WHERE cup_id = {payload["coupon"]};
                        """)
        response = {'status': StatusCodes['success'], 'results': f'order {row[0][0]} completed'}
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
@app.route('/dbproj/rating/<prod_id>', methods=['POST'])
@verify_token
def rating(user_id, type_user, prod_id):
    logger.info('PUT /rating/<prod_id>')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    
    if type_user != "comprador":
        response = {'status': StatusCodes['api_error'], 'results': f'the user type {type_user} cannot rate a product'}
        return jsonify(response)
    
    if "rating" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'rating not in payload'}
        return jsonify(response)
        
    if payload["rating"] < 0 or payload["rating"] > 5:
        response = {'status': StatusCodes['api_error'], 'results': 'rating must be between 0 and 5'}
        return jsonify(response)
        
    if "comment" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'comment not in payload'}
        return jsonify(response)
        
    
    logger.debug(f'PUT /rating/<prod_id> - payload: {payload}')
    
    try:
        cur.execute(f'SELECT user_id FROM encomenda e JOIN item i ON e.encom_id = i.encom_id WHERE e.user_id = {user_id} AND i.prod_id = {prod_id};')
        
        if cur.rowcount >= 1:
            cur.execute(f'SELECT rank_id FROM rating WHERE user_id = {user_id} AND prod_id = {prod_id};')
            logger.info(cur.rowcount)
            if cur.rowcount == 0:
                logger.info(cur.rowcount)
                cur.execute(f'INSERT INTO rating (classificacao, rank_comentario, user_id, prod_id) VALUES ({payload["rating"]}, \'{payload["comment"]}\', {user_id}, {prod_id});')
                
                response = {'status': StatusCodes['success'], 'results': f'you rated a product successfully'}
                logger.info(cur.rowcount)
            else:
                logger.info(cur.rowcount)
                cur.execute(f'UPDATE rating SET classificacao = {payload["rating"]}, rank_comentario = \'{payload["comment"]}\' WHERE prod_id = {prod_id} AND user_id = {user_id};')
                response = {'status': StatusCodes['success'], 'results': f'the product\'s rating has been updated'}
               
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'you haven\'t bought the product yet'}
            return jsonify(response)

        conn.commit()    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    

@app.route('/dbproj/questions/<prod_id>/<parent_id>', methods=['POST'])   
@app.route('/dbproj/questions/<prod_id>', methods=['POST'])
@verify_token
def comment(user_id, type_user, prod_id, parent_id = None):
    logger.info('POST /questions/<prod_id>')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    
    if "question" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'question not in payload'}
        return jsonify(response)
    
    cur.execute(f'SELECT prod_id FROM produto WHERE prod_id = {prod_id};')
    if cur.rowcount == 0:
        response = {'status': StatusCodes['api_error'], 'results': f'There isn\'t any product with ID {prod_id}'}
        return jsonify(response)
    
    if parent_id is not None:
        cur.execute(f' SELECT com_id FROM comentario WHERE com_id = {parent_id} and prod_id = {prod_id};')
        if cur.rowcount == 0:
            response ={'status': StatusCodes['api_error'], 'results': f'The product ID inserted doens\'t match with the product ID of the parent comment'}
            return jsonify(response)
        
    
    logger.debug(f'POST /questions/<prod_id> - payload: {payload}')
    statement = ""
    logger.info(parent_id)
    try:
        if parent_id is None:
            statement = f"""
                            CREATE TEMPORARY TABLE t1 (aux INTEGER, id INTEGER) ON COMMIT DROP;
                            INSERT INTO t1 (aux, id) values(0, {prod_id});
                            INSERT INTO comentario (com_comentario, user_id, prod_id) values (\'{payload["question"]}\', {user_id}, {prod_id});
                         """
            cur.execute(statement)
            cur.execute(f'SELECT MAX(com_id) FROM comentario;')
            row = cur.fetchall()
            response = {'status': StatusCodes['success'], 'results': f'you posted a comment successfully with ID: {row[0][0]}'}
        else:
        
            cur.execute(f'SELECT com_id from comentario where com_id = {parent_id};')
            
            if cur.rowcount == 1:
                cur.execute(f"""
                                CREATE TEMPORARY TABLE t1 (aux INTEGER, id INTEGER) ON COMMIT DROP;
                                INSERT INTO t1 (aux, id) values(1, {parent_id});
                                INSERT INTO comentario (com_comentario, user_id, prev_com_id, prod_id) VALUES (\'{payload["question"]}\', {user_id}, {parent_id}, {prod_id});
                             """)                
                cur.execute(f'SELECT MAX(com_id) FROM comentario;')
                row = cur.fetchall()
                response = {'status': StatusCodes['success'], 'results': f'you answered a question successfully with ID: {row[0][0]}'}
            else:
                response = {'status': StatusCodes['api_error'], 'results': f'the comment you selected doesn\'t exist'}
                return jsonify(response)

        conn.commit()    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
    
    
@app.route('/dbproj/campaign/', methods=['POST'])
@verify_token
def add_campaign(user_id, type_user):
    logger.info('POST /campaign/')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    
    if type_user != "administrador":
        response = {'status': StatusCodes['api_error'], 'results': f'the user type {type_user} cannot create a campaign'}
        return jsonify(response)
    
    if "description" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'description not in payload'}
        return jsonify(response)
        
    if "date_start" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'date_start not in payload'}
        return jsonify(response)
    
    if "date_end" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'date_end not in payload'}
        return jsonify(response)
    
    if "coupons" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'coupons not in payload'}
        return jsonify(response)
    
    if "discount" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'discount not in payload'}
        return jsonify(response)
        
    if "duration" not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'duration not in payload'}
        return jsonify(response)
    
        
    date_start = datetime(int(payload["date_start"].split('-')[0]),int(payload["date_start"].split('-')[1]),int(payload["date_start"].split('-')[2]))
    date_end = datetime(int(payload["date_end"].split('-')[0]), int(payload["date_end"].split('-')[1]), int(payload["date_end"].split('-')[2]))
    current_date = datetime.today()
    
    logger.info(date_start)
    logger.info(current_date)
    
    if datetime.date(date_start) < datetime.date(current_date):
        response = {'status': StatusCodes['api_error'], 'results': 'Date format incorrect or invalid date (Date format: yyyy-mm-dd)'}
        return jsonify(response)
    
    if datetime.date(date_end) < datetime.date(date_start):
        response = {'status': StatusCodes['api_error'], 'results': 'Date format incorrect or invalid date (Date format: yyyy-mm-dd)'}
        return jsonify(response)
    
    if payload["coupons"] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'Number of coupons must be higher or equal to 0'}
        return jsonify(response)
        
    if payload["discount"] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'Discount can\'t be less than 0'}
        return jsonify(response)
        
    if payload["duration"] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'Duration can\'t be less than 0'}
        return jsonify(response)
        
    logger.debug(f'POST /rating/<prod_id> - payload: {payload}')
    statement=''
        
    try:
    
        statement =f'SELECT data_fim FROM campanha WHERE camp_id = (SELECT MAX(camp_id) FROM campanha);'
        cur.execute(statement)
        if cur.rowcount > 0:
            row = cur.fetchall()
            date_aux = datetime(int(str(row[0][0]).split('-')[0]),int(str(row[0][0]).split('-')[1]),int(str(row[0][0]).split('-')[2]))
            if datetime.date(date_aux) > datetime.date(date_start):
                response = {'status': StatusCodes['api_error'], 'results': 'A campaign is already running'}
                return jsonify(response)
        
        statement = f'INSERT INTO campanha (user_id, num_cupoes, data_inicio, data_fim, desconto, descricao, duracao) VALUES ({user_id}, {payload["coupons"]}, \'{payload["date_start"]}\', \'{payload["date_end"]}\', {payload["discount"]}, \'{payload["description"]}\', {payload["duration"]})'
        cur.execute(statement)
        conn.commit()
        cur.execute(f'SELECT MAX(camp_id) FROM campanha;')
        row = cur.fetchall()
        response = {'status': StatusCodes['success'], 'results': f'You created a new campaign with ID: {row[0][0]}'}    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)
   
   
@app.route('/dbproj/subscribe/<camp_id>', methods=['PUT'])
@verify_token
def subscribe_campaign(user_id, type_user, camp_id):
    logger.info('PUT /subscribe/<camp_id>')

    conn = db_connection()
    cur = conn.cursor()
    
    if type_user != "comprador":
        response = {'status': StatusCodes['api_error'], 'results': f'the user type {type_user} cannot subscribe a campaign'}
        return jsonify(response)
    
    try:
        cur.execute(f'SELECT user_id FROM cupao WHERE camp_id = {camp_id} AND user_id = {user_id};')
        if cur.rowcount != 0:
            response = {'status': StatusCodes['api_error'], 'results': f'you already subscribed this campaign'}
            return jsonify(response) 
    
        cur.execute(f'SELECT data_inicio FROM campanha WHERE camp_id = {camp_id};')
        if cur.rowcount == 0:
            response = {'status': StatusCodes['api_error'], 'results': f'there is no campaign with ID: {camp_id}'}
            return jsonify(response)
        
        row = cur.fetchall()
        date_aux = datetime(int(str(row[0][0]).split('-')[0]),int(str(row[0][0]).split('-')[1]),int(str(row[0][0]).split('-')[2]))
        if datetime.date(date_aux) < datetime.date(datetime.today()):
            response = {'status': StatusCodes['api_error'], 'results': f'this campaign hasn\'t started yet'}
            return jsonify(response) 
    
        cur.execute(f'SELECT num_cupoes FROM campanha WHERE camp_id = {camp_id} for update;')
        row = cur.fetchall()
        if row[0][0] == 0:
            response = {'status': StatusCodes['api_error'], 'results': f'there are no coupons available in the current campaign'}
            return jsonify(response) 

        cur.execute(f"""INSERT INTO cupao(camp_id, usado, exp_date, user_id) values({camp_id}, FALSE, current_date + (SELECT duracao FROM campanha WHERE camp_id = {camp_id}), {user_id});
                        UPDATE campanha SET num_cupoes = {row[0][0]} - 1 WHERE camp_id = {camp_id};
                     """)
        
        conn.commit()
        cur.execute(f'SELECT cup_id, exp_date FROM cupao WHERE cup_id = (SELECT MAX(cup_id) FROM cupao)')
        row = cur.fetchall()
        
        response = {'status': StatusCodes['success'], 'results': f'You subscribed the campaign with ID: {camp_id} successfully', 'coupon_id':f'{row[0][0]}', 'expiration date': f'{row[0][1]}'}    

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)   
   

##
## Demo PUT
##
## Update a department based on a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X PUT http://localhost:8080/departments/ -H 'Content-Type: application/json' -d '{'ndep': 69, 'localidade': 'Porto'}'
##

@app.route('/dbproj/user/', methods=['PUT'])
def login():
    logger.info('PUT /user/')
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    response = {}
    user_id = 0
    type_user = ""
    logger.debug(f'PUT /user/ - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'username' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username is required to log in'}
        return jsonify(response)

    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password is required to log in'}
        return jsonify(response)

    types = [['administrador','SELECT utilizador.user_id, username FROM utilizador JOIN administrador ON utilizador.user_id = administrador.user_id WHERE utilizador.username = %s AND utilizador.password = %s'],
             ['comprador','SELECT utilizador.user_id, username FROM utilizador JOIN comprador ON utilizador.user_id = comprador.user_id WHERE utilizador.username = %s AND utilizador.password = %s'], 
             ['vendedor','SELECT utilizador.user_id, username FROM utilizador JOIN vendedor ON utilizador.user_id = vendedor.user_id WHERE utilizador.username = %s AND utilizador.password = %s']]

    row = []

    try:
        hashed_password = hashlib.sha512(payload['password'].encode('utf-8') + salt.encode('utf-8')).hexdigest()

        for i in types:
            cur.execute(i[1], (payload['username'], hashed_password))

            if cur.rowcount == 1:
                row = cur.fetchall()
                logger.info(row)
                user_id = row[0][0]
                type_user = i[0]
                logger.info(user_id)
                logger.info(type_user)
                break

        if type_user == "":
            response = {'status': StatusCodes['api_error'], 'results': 'wrong credentials'}
            #return jsonify(response)
        else:
            token = generate_token(user_id, type_user)
            #request.headers['Token'] = token
            response = {'status': StatusCodes['success'], 'token': token}
            #return jsonify(response)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)





##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1) # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.1 online: http://localhost:8080/departments/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)



