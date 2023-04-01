CREATE TABLE utilizador (
	user_id	 SERIAL,
	username VARCHAR(128) NOT NULL UNIQUE,
	email VARCHAR(128) NOT NULL UNIQUE,
	password VARCHAR(128) NOT NULL,
	PRIMARY KEY(user_id)
);

CREATE TABLE administrador (
	user_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(user_id)
);

CREATE TABLE vendedor (
	vend_nif		 NUMERIC(9) UNIQUE NOT NULL,
	vend_morada	 VARCHAR(128) UNIQUE NOT NULL,
	IBAN         VARCHAR(128) UNIQUE NOT NULL,
	user_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(user_id)
);

CREATE TABLE comprador (
	compr_nif		 NUMERIC(9) UNIQUE NOT NULL,
	compr_morada	 VARCHAR(128) UNIQUE NOT NULL,
	user_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(user_id)
);

CREATE TABLE produto (
	prod_id			 SERIAL,
	descricao		 VARCHAR(512) NOT NULL,
	preco			 FLOAT(8) NOT NULL,
	stock			 INTEGER NOT NULL,
	nome			 VARCHAR(128) NOT NULL,
	hist_id 		 INTEGER,
	user_id 		 INTEGER NOT NULL,
	prod_date		 DATE DEFAULT CURRENT_DATE,
	stats_id		 INTEGER NOT NULL,
	PRIMARY KEY(prod_id)
);

CREATE TABLE computador (
	cpu		 VARCHAR(128) NOT NULL,
	ram		 VARCHAR(128) NOT NULL,
	prod_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(prod_id)
);

CREATE TABLE televisao (
	tamanho	 FLOAT(8) NOT NULL,
	definicao	 VARCHAR(128) NOT NULL,
	prod_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(prod_id)
);

CREATE TABLE smartphone (
	ecra		 VARCHAR(128) NOT NULL,
	ram		 VARCHAR(128) NOT NULL,
	bateria	 VARCHAR(128) NOT NULL,
	prod_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(prod_id)
);

CREATE TABLE encomenda (
	encom_id			 SERIAL,
	preco_total FLOAT(8) NOT NULL,
	encom_date DATE DEFAULT CURRENT_DATE,
	user_id INTEGER NOT NULL,
	PRIMARY KEY(encom_id)
);  

CREATE TABLE rating (
	rank_id			 SERIAL,
	classificacao		 INTEGER NOT NULL,
	rank_comentario		 VARCHAR(512) NOT NULL,
	user_id INTEGER NOT NULL,
	prod_id		 INTEGER NOT NULL,
	PRIMARY KEY(rank_id)
);

CREATE TABLE campanha (
	camp_id				 SERIAL,
	num_cupoes			 INTEGER NOT NULL,
	data_inicio			 DATE UNIQUE NOT NULL,
	data_fim			 DATE UNIQUE NOT NULL,
	desconto			 FLOAT(8) NOT NULL,
	descricao			 VARCHAR(512) NOT NULL,
	duracao				 INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	PRIMARY KEY(camp_id)
);

CREATE TABLE cupao (
	cup_id     			 SERIAL,
	exp_date			 DATE NOT NULL,
	data_req			 DATE DEFAULT CURRENT_DATE,
	camp_id		 INTEGER NOT NULL,
	usado 		 BOOL NOT NULL,
	user_id INTEGER NOT NULL,
	encom_id INTEGER,		
	PRIMARY KEY(cup_id)
);

CREATE TABLE item (
	item_id		 SERIAL,
	item_preco	 FLOAT(8) NOT NULL,
	quantidade	 INTEGER NOT NULL,
	encom_id INTEGER NOT NULL ,
	prod_id	 INTEGER NOT NULL ,
	PRIMARY KEY(item_id)
);

CREATE TABLE comentario (
	com_id		 SERIAL,
	com_comentario	 VARCHAR(512) NOT NULL,
	user_id INTEGER NOT NULL,
	prev_com_id	 INTEGER,
	prod_id	 INTEGER NOT NULL,
	PRIMARY KEY(com_id)
);

CREATE TABLE notificacao (
	not_id	 SERIAL,
	not_descricao VARCHAR(512) NOT NULL,
	PRIMARY KEY(not_id)
);

CREATE TABLE notificacao_compra (
	user_id INTEGER NOT NULL,
	not_id		 INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(not_id)
);

CREATE TABLE notificacao_comentario (
	user_id INTEGER NOT NULL,
	not_id INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(not_id)
);

CREATE TABLE notificacao_venda (
	user_id INTEGER NOT NULL,
	not_id	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(not_id)
);

ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (user_id) REFERENCES utilizador(user_id);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (user_id) REFERENCES utilizador(user_id);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (user_id) REFERENCES utilizador(user_id);

ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (user_id) REFERENCES vendedor(user_id);
ALTER TABLE produto ADD CONSTRAINT produto_fk2 FOREIGN KEY (hist_id) REFERENCES produto(prod_id);

ALTER TABLE computador ADD CONSTRAINT computador_fk1 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);
ALTER TABLE televisao ADD CONSTRAINT televisao_fk1 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);
ALTER TABLE smartphone ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);

ALTER TABLE encomenda ADD CONSTRAINT encomenda_fk1 FOREIGN KEY (user_id) REFERENCES comprador(user_id);

ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (user_id) REFERENCES comprador(user_id);
ALTER TABLE rating ADD CONSTRAINT rating_fk2 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);


ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (user_id) REFERENCES utilizador(user_id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (prev_com_id) REFERENCES comentario(com_id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk3 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);

ALTER TABLE campanha ADD CONSTRAINT campanha_fk1 FOREIGN KEY (user_id) REFERENCES administrador(user_id);

ALTER TABLE cupao ADD CONSTRAINT cupao_fk1 FOREIGN KEY (camp_id) REFERENCES campanha(camp_id);
ALTER TABLE cupao ADD CONSTRAINT cupao_fk2 FOREIGN KEY (user_id) REFERENCES comprador(user_id);

ALTER TABLE item ADD CONSTRAINT item_fk1 FOREIGN KEY (encom_id) REFERENCES encomenda(encom_id);
ALTER TABLE item ADD CONSTRAINT item_fk2 FOREIGN KEY (prod_id) REFERENCES produto(prod_id);

ALTER TABLE notificacao_compra ADD CONSTRAINT notificacao_compra_fk1 FOREIGN KEY (user_id) REFERENCES comprador(user_id);
ALTER TABLE notificacao_compra ADD CONSTRAINT notificacao_compra_fk2 FOREIGN KEY (not_id) REFERENCES notificacao(not_id);

ALTER TABLE notificacao_comentario ADD CONSTRAINT notificacao_comentario_fk1 FOREIGN KEY (user_id) REFERENCES utilizador(user_id);
ALTER TABLE notificacao_comentario ADD CONSTRAINT notificacao_comentario_fk2 FOREIGN KEY (not_id) REFERENCES notificacao(not_id);

ALTER TABLE notificacao_venda ADD CONSTRAINT notificacao_venda_fk1 FOREIGN KEY (user_id) REFERENCES vendedor(user_id);
ALTER TABLE notificacao_venda ADD CONSTRAINT notificacao_venda_fk2 FOREIGN KEY (not_id) REFERENCES notificacao(not_id);

DROP FUNCTION IF EXISTS update_stock CASCADE;
CREATE OR REPLACE FUNCTION update_stock()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$$
BEGIN
	update produto set stock = stock - (select quantidade from item where item_id = new.item_id) where prod_id = new.prod_id;
    RETURN NEW;
END;
$$;


CREATE OR REPLACE TRIGGER stock_trigger
  	AFTER INSERT
  	ON item
  	FOR EACH ROW
	EXECUTE PROCEDURE update_stock();
	
	
DROP FUNCTION IF EXISTS notificacao_venda CASCADE;
CREATE OR REPLACE FUNCTION notificacao_venda()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$$
DECLARE
	insertedID integer;
BEGIN
	insert into notificacao(not_descricao) values(concat(new.quantidade,' products were purchased with id: ', new.prod_id)) returning not_id into insertedID;
	insert into notificacao_venda(not_id, user_id) values(insertedID,(select user_id from produto where prod_id = new.prod_id));
	RETURN NEW;
END;
$$;


CREATE OR REPLACE TRIGGER notificacao_venda_trigger
  	AFTER INSERT
  	ON item
  	FOR EACH ROW
	EXECUTE PROCEDURE notificacao_venda();
	
	
DROP FUNCTION IF EXISTS notificacao_compra CASCADE;
CREATE OR REPLACE FUNCTION notificacao_compra()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$$
declare
	insertedID integer;
begin

	insert into notificacao(not_descricao) values((select var from t1)) returning not_id into insertedID;
	insert into notificacao_compra(not_id, user_id) values(insertedID, (select id from t1));
	
	RETURN NEW;
end;$$;

CREATE OR REPLACE TRIGGER notificacao_compra_trigger
  	AFTER INSERT
  	ON encomenda
  	FOR EACH ROW
	EXECUTE PROCEDURE notificacao_compra();
	
	
DROP FUNCTION IF EXISTS notificacao_comentario CASCADE;
CREATE OR REPLACE FUNCTION notificacao_comentario()
  RETURNS trigger
  LANGUAGE plpgsql
AS
$$
declare
	insertedID integer;
    s varchar(128) := '';
begin
    if (select aux from t1) = 0 then
        s := concat('The product with id: ', (select id from t1), ' received a comment');
        insert into notificacao(not_descricao) values(s) returning not_id into insertedID;
        insert into notificacao_comentario(not_id, user_id) values(insertedID, (select user_id from produto where prod_id = (select id from t1)));
	else
        s := concat('Your comment with id: ', (select id from t1), ' received an answer');
        insert into notificacao(not_descricao) values(s) returning not_id into insertedID;
        insert into notificacao_comentario(not_id, user_id) values(insertedID, (select user_id from comentario where com_id = (select id from t1)));
    end if;
    RETURN NEW;
end;$$;

CREATE OR REPLACE TRIGGER notificacao_comentario_trigger
  	AFTER INSERT
  	ON comentario
  	FOR EACH ROW
	EXECUTE PROCEDURE notificacao_comentario();

insert into utilizador (username, email, password) values('admin', 'admin@admin', '4d8c221cfddd779948a81b22192ce1af25acb5dc6057a40c520b9dfd7d2679705b42069f561250eab80155dc0f410ce9e900c2e8ec5cc414556ee9fd77842716');
insert into administrador (user_id) values(1);

insert into utilizador (username, email, password) values('vend', 'vend@vend', '03a9bedc1caf5211ee1a51101f546cde5b9404d659952120b147d6333fbcca521bce0edf1a00db08bbf6e1c84407d258e82bf4cde9c907818dac9434102bf155');
insert into vendedor (user_id, vend_morada, vend_nif, IBAN) values(2, 'rua do vendedor', 23629132, 'PT50 3742943');

insert into utilizador (username, email, password) values('vend2', 'vend2@vend2', 'f7d6058970c651419b12192a11aa229b9d7b3c8776d6a823c6b6336ead4f7887df210d383d5d559af731cbcd18e3c7aff0fc308b231167e7e4ed50d6bfa92ce3');
insert into vendedor (user_id, vend_morada, vend_nif, IBAN) values(3, 'rua do vendedor2', 23629999, 'PT50 3742999');

insert into produto (nome, preco, descricao, stock, user_id, stats_id) values('LENOVO', 999.99, 'descricao teste', 100, 2, 1);
insert into computador (prod_id, cpu, ram) values(1, 'intel i7', 16);

insert into produto (nome, preco, descricao, stock, user_id, stats_id) values('SAMSUNG', 1200, 'descricao teste 2', 100, 3, 2);
insert into smartphone (prod_id, ecra, ram, bateria) values(2, 'AMOLED', 12, '4500 mAh');

/*
select avg(classificacao), descricao, com_comentario, preco, prod_date, p.prod_id, p.stats_id
from produto p, comentario c, rating r
where (p.prod_id = c.prod_id and p.prod_id = r.prod_id) and (p.stats_id = (select stats_id from produto where prod_id = 3)) 
group by p.prod_id, com_id;

select count(encom_id), sum(preco_total), (SELECT EXTRACT(Month FROM encom_date) AS "Month")
from encomenda e
group by "Month";

select camp_id, count(c.cup_id) --, sum(preco_total)
from  cupao c, encomenda e
where (c.encom_id = e.encom_id) and c.camp_id = 5
group by camp_id;


delete from item;
delete from encomenda;
delete from comentario;
delete from notificacao_compra;
delete from notificacao_venda;
delete from notificacao_comentario;
delete from notificacao;*/