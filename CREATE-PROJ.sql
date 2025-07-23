
create table pessoa (
    id_pessoa serial primary key,
    nome_completo varchar(255) not null,
    data_nasc date,
    cpf varchar(14) unique not null,
    rg varchar(20) unique,
    genero varchar(50),
    email varchar(255)unique not null,
    telefone varchar(20)
);

create table familia (
    id_familia serial primary key,
    nome_familia varchar(255) not null,
    endereco varchar(255) not null,
    bairro varchar(100),
    cidade varchar(100),
    estado varchar(50),
    cep varchar(10) not null,
    telefone varchar(20) not null,
    renda_mensal decimal(10, 2),
    data_cadastro date not null default current_date,
    status_vulnerabilidade boolean not null,
    observacoes text
);

create table membro_da_familia (
    id_membro_familia serial primary key,
    id_pessoa int not null,
    id_familia int not null,
    parentesco varchar(50) not null,
    escolaridade varchar(100),
    ocupacao varchar(100),
    situacao_saude text,
    beneficios text,
    constraint fk_membro_pessoa foreign key (id_pessoa) references pessoa(id_pessoa),
    constraint fk_membro_familia foreign key (id_familia) references familia(id_familia),
    constraint uk_pessoa_familia unique (id_pessoa, id_familia)
);

create table profissional (
    id_profissional int primary key,
    cargo varchar(100) not null,
    setor varchar(100) not null,
    constraint fk_profissional_pessoa foreign key (id_profissional) references pessoa(id_pessoa)
);

create table usuario (
    id_usuario int primary key,
    nome_usuario varchar(100) unique not null,
    senha varchar(255) not null,
    data_criacao date not null default current_date,
    status_conta varchar(50) not null,
    ultimo_login timestamp,
    constraint fk_usuario_pessoa foreign key (id_usuario) references pessoa(id_pessoa)
);

create table perfil (
    id_perfil serial primary key,
    nome_perfil varchar(100) unique not null,
    descricao_perfil text
);

create table permissao (
    id_permissao serial primary key,
    nome_permissao varchar(100) unique not null,
    descricao_permissao text
);


create table usuario_perfil (
    id_usuario int not null,
    id_perfil int not null,
    primary key (id_usuario, id_perfil),
    constraint fk_usuario_perfil_usuario foreign key (id_usuario) references usuario(id_usuario),
    constraint fk_usuario_perfil_perfil foreign key (id_perfil) references perfil(id_perfil)
);

create table perfil_permissao (
    id_perfil int not null,
    id_permissao int not null,
    primary key (id_perfil, id_permissao),
    constraint fk_perfil_permissao_perfil foreign key (id_perfil) references perfil(id_perfil),
    constraint fk_perfil_permissao_permissao foreign key (id_permissao) references permissao(id_permissao)
);

create table atendimento (
    id_atendimento serial primary key,
    data_atendimento timestamp not null,
    tipo_atendimento varchar(100) not null,
    resumo text not null,
    encaminhamentos text,
    id_familia int not null,
    id_profissional int not null,
    id_pessoa_membro int,
    constraint fk_atendimento_familia foreign key (id_familia) references familia(id_familia),
    constraint fk_atendimento_profissional foreign key (id_profissional) references profissional(id_profissional),
    constraint fk_atendimento_pessoa_membro foreign key (id_pessoa_membro) references pessoa(id_pessoa)
);

create table beneficio (
    id_beneficio serial primary key,
    tipo_beneficio varchar(100) not null,
    valor_monetario decimal(10, 2),
    data_inicio date not null,
    data_fim date,
    observacoes text,
    id_familia int not null,
    id_pessoa_membro int,
    constraint fk_beneficio_familia foreign key (id_familia) references familia(id_familia),
    constraint fk_beneficio_pessoa_membro foreign key (id_pessoa_membro) references pessoa(id_pessoa)
);

create table necessidade (
    id_necessidade serial primary key,
    tipo_necessidade varchar(100) not null,
    descricao text,
    grau_prioridade varchar(50) not null,
    status_resolucao varchar(50) not null,
    data_registro date not null default current_date,
    data_resolucao date,
    id_familia int not null,
    constraint fk_necessidade_familia foreign key (id_familia) references familia(id_familia),
    constraint ck_status_resolucao check (status_resolucao in ('Pendente', 'Em Andamento', 'Resolvido'))
);


create table ocorrencia (
    id_ocorrencia serial primary key,
    data_ocorrencia timestamp not null,
    tipo_ocorrencia varchar(100) not null,
    descricao text,
    id_profissional int,
    id_familia int not null,
    constraint fk_ocorrencia_profissional foreign key (id_profissional) references profissional(id_profissional),
    constraint fk_ocorrencia_familia foreign key (id_familia) references familia(id_familia)
);