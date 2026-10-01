

import pandas as pd
import re
import unicodedata
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def normalizar_colunas(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace(r'[^\w]', '_', regex=True)   
        .str.replace(r'_+', '_', regex=True)      
        .str.strip('_')
    )
    return df


def chave_nome(nome):
    nome = str(nome).strip().upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome


def extrair_partes_topico(df, col='t_pico_da_reuni_o'):
    df['topico'] = df[col].fillna('').astype(str).str.strip().str.replace('"', '', regex=False)
    partes = df['topico'].str.split('~', expand=True)

    df['codigo_turma'] = partes[0].str.strip().str.extract(r'^([A-Za-z0-9_-]+)')[0]
    df['nivel']        = partes[0].str.strip()
    df['professor_raw'] = ''

    mask_3 = partes[2].notna()
    df.loc[mask_3, 'professor_raw'] = partes[1].str.strip()
    df.loc[mask_3, 'horario']       = partes[2].str.strip()

    mask_2 = partes[2].isna()
    df.loc[mask_2, 'professor_raw'] = (
        partes[0].str.extract(r'(?i)(Teacher.*|Profe.*)')[0].str.strip()
    )
    df.loc[mask_2, 'horario'] = partes[1].str.strip()

    return df


def extrair_nome_professor(df, col_raw='professor_raw', col_destino='Professor'):
    df[col_destino] = df[col_raw].fillna('').astype(str).str.strip()
    df[col_destino] = df[col_destino].str.replace(
        r'(?i)^(teacher|teacger|profe|prof\.?)\s+', '', regex=True
    )
    df[col_destino] = df[col_destino].str.replace(r'\[.*?\]', '', regex=True)
    df[col_destino] = df[col_destino].str.replace(r'\s+', ' ', regex=True).str.strip()
    df[col_destino] = df[col_destino].replace({'...': '', '': ''})
    df[col_destino] = df[col_destino].fillna('').replace('', 'Professor não identificado')
    return df


def extrair_faixa_turma(total_alunos):
    n = pd.to_numeric(total_alunos, errors='coerce')
    if pd.isna(n):
        return 'Não identificado'
    if 1 <= n <= 10:
        return 'PP (1–10)'
    elif 11 <= n <= 20:
        return 'P (11–20)'
    elif 21 <= n <= 40:
        return 'M (21–40)'
    elif n >= 41:
        return 'G (41+)'
    else:
        return 'Não identificado'


ORDEM_FAIXA_TURMA = ['PP (1–10)', 'P (11–20)', 'M (21–40)', 'G (41+)', 'Não identificado']

def extrair_zoom_id_da_url(url):
    if pd.isna(url) or str(url).strip() == '':
        return None
    match = re.search(r'/j/(\d+)', str(url))
    return match.group(1) if match else None


def _encontrar_col(df, termos):
    termos = [t.lower() for t in termos]
    for col in df.columns:
        if all(t in col for t in termos):
            return col
    return None


MAPA_ESCOLA_ANALISTA = {
    'CNA Alphaville':                       'Leticia',
    'CNA Alto do Ipiranga':                 'Aline',
    'CNA Aracaju - Treze de Julho':         'Carlos',
    'CNA Barbacena':                        'Rafaela',
    'CNA Barra - Jardim Oceânico':          'Alicee',
    'CNA Bauru - Centro':                   'Leticia',
    'CNA Belém - Icoaraci':                 'Carlos',
    'CNA Belém - São Brás':                 'Aline',
    'CNA Belém - Umarizal':                 'Carlos',
    'CNA Brasilândia':                      'Aline',
    'CNA Brooklin':                         'Carlos',
    'CNA Cabreúva':                         'Carlos',
    'CNA Caieiras':                         'Leticia',
    'CNA Campina Grande - Prata':           'Leticia',
    'CNA Campinas - Guanabara':             'Carlos',
    'CNA Campinas - Sousas':                'Rafaela',
    'CNA Campos Baronesa':                  'Aline',
    'CNA Castanhal':                        'Aline',
    'CNA Curitiba - Guabirotuba':           'Carlos',
    'CNA Curitiba Boa Vista':               'Leticia',
    'CNA Fortaleza - Aldeota Costa Barros': 'Leticia',
    'CNA Fortaleza - Fátima':               'Aline',
    'CNA Fortaleza - Messejana':            'Carlos',
    'CNA Fortaleza - Parquelândia':         'Aline',
    'CNA Guaraciaba do Norte':              'Aline',
    'CNA Guarulhos - Cumbica':              'Carlos',
    'CNA Guarulhos - Taboão':               'Carlos',
    'CNA Itapecerica':                      'Carlos',
    'CNA Itapecerica da Serra':             'Aline',
    'CNA Itapetininga':                     'Carlos',
    'CNA Jacareí':                          'Alicee',
    'CNA Jaguariúna':                       'Carlos',
    'CNA Maringá Centro':                   'Rafaela',
    'CNA Mococa':                           'Carlos',
    'CNA Mogi das Cruzes - Cézar de Souza': 'Aline',
    'CNA Mongaguá':                         'Rafaela',
    'CNA Mooca':                            'Leticia',
    'CNA Natal Zona Norte':                 'Leticia',
    'CNA Osasco - Jardim Veloso':           'Carlos',
    'CNA Pampulha':                         'Carlos',
    'CNA Pedra de Guaratiba':               'Carlos',
    'CNA Presidente Prudente Centro':       'Carlos',
    'CNA Presidente Prudente Morumbi':      'Alicee',
    'CNA Quirinópolis':                     'Alicee',
    'CNA Recanto das Emas':                 'Leticia',
    'CNA Rio das Ostras':                   'Carlos',
    'CNA Salvador Pituba':                  'Carlos',
    'CNA Salvador Stiep':                   'Leticia',
    'CNA Santiago':                         'Aline',
    'CNA São Bento do Sul':                 'Aline',
    'CNA São José dos Campos - Jd. Satélite': 'Alicee',
    'CNA Sinop':                            'Aline',
    'CNA Sorocaba':                         'Carlos',
    'CNA Sorocaba Itavuvu':                 'Carlos',
    'CNA Sorriso':                          'Aline',
    'CNA Sumaré':                           'Carlos',
    'CNA Tijuca Saens Pena':                'Rafaela',
    'CNA Três Corações':                    'Aline',
    'CNA Uruguaiana':                       'Rafaela',
    'CNA Valqueire':                        'Leticia',
    'CNA Vila Maria':                       'Rafaela',
    'CNA Vila Prudente':                    'Carlos',
    'CNA Vila Velha - Praia da Costa':      'Leticia',
    'CNA Jundiaí - Anhangabaú':             'Rafaela',
    'CNA Digital School':                   'Mayara',
    'CNA Lorena':                           'Leticia',
    'CNA Ferraz de Vasconcelos':            'Rafaela',
    'CNA Cordeirópolis':                    'Alicee',
    'CNA Campinas - Taquaral':              'Alicee',
    'CNA Curitiba Capão Raso':              'Rafaela',
    'CNA Itapira':                          'Rafaela',
    'CNA Vila dos Remédios':                'Carlos',
    'CNA Santa Cruz':                       'Rafaela',
    'CNA Guarulhos - Centro':               'Leticia',
    'CNA Teresina - Centro':                'Leticia',
    'CNA Ananindeua':                       'Aline',
    'CNA Valinhos':                         'Aline',
    'CNA Várzea Paulista':                  'Leticia',
    'CNA Vila Velha - Santa Mônica':        'Rafaela',
    'CNA Vila Mariana':                     'Aline',
    'CNA Vila Guilherme':                   'Rafaela',
    'CNA Artur Alvim':                      'Leticia',
    'CNA Campo Limpo':                      'Carlos',
    'CNA Embu das Artes - Centro':          'Rafaela',
    'CNA Fortaleza - Montese':              'Aline',
    'CNA Arujá':                            'Carlos',
    'CNA Campos Ouvidor':                   'Leticia',
    'CNA Cangaíba':                         'Carlos',
    'CNA Hortolândia':                      'Carlos',
}

MAPA_IDIOMA = {
    'ESPAV': 'Espanhol', 'ESPBA': 'Espanhol', 'ESPIN': 'Espanhol',
    'ESPPA': 'Espanhol', 'ESPPI': 'Espanhol', 'ESPA':  'Espanhol',
    'TB_ESPBA': 'CNA Turbo (Espanhol)', 'TB_ESPPI': 'CNA Turbo (Espanhol)',
    'TB_ESPPA': 'CNA Turbo (Espanhol)', 'TB_ESPIN': 'CNA Turbo (Espanhol)',
    'TB_ADV':  'CNA Turbo (Inglês)', 'TB_BAS':  'CNA Turbo (Inglês)',
    'TB_INT':  'CNA Turbo (Inglês)', 'TB_MAST': 'CNA Turbo (Inglês)',
    'TB_PADV': 'CNA Turbo (Inglês)',
    'ACC': 'Inglês (Preparatório)', 'CAE': 'Inglês (Preparatório)',
    'CPE': 'Inglês (Preparatório)', 'FCE': 'Inglês (Preparatório)',
    'TKT': 'Inglês (Preparatório)',
}

MAPA_ESTAGIO = {
    'A1': 'A1', 'A2': 'A1',
    'INT1': 'Intermediário', 'INT2': 'Intermediário',
    'PADV1': 'Pré Avançado', 'PADV2': 'Pré Avançado',
    'ADV1': 'Avançado', 'ADV2': 'Avançado',
    'MAST1': 'Master In English', 'MAST2': 'Master In English',
    'PRO_L1A': 'Advanced Conversation Course',
    'ACC1': 'Advanced Conversation Course', 'ACC2': 'Advanced Conversation Course',
    'YK1': 'Young Kids', 'YK2': 'Young Kids', 'YK3': 'Young Kids',
    'KIDS1': 'Kids', 'KIDS2': 'Kids', 'KIDS3': 'Kids', 'KIDS4': 'Kids',
    'Teen_UP1': 'Teens', 'Teen_UP2': 'Teens', 'Teen_UP3': 'Teens', 'Teen_UP4': 'Teens',
    'PS1': 'Pre-school', 'PS3': 'Pre-school', 'PS4': 'Pre-school',
    'ESPBA': 'En Contacto', 'ESPPI': 'En Contacto', 'ESPIN': 'En Contacto',
    'ESPAV': 'En Contacto', 'ESPPA': 'En Contacto',
    'EJ1': 'Joven', 'EJ3': 'Joven',
    'TB_A1': 'Turbo > Básico', 'TB_BAS2': 'Turbo > Básico',
    'TB_INT1': 'Turbo > Intermediário', 'TB_INT2': 'Turbo > Intermediário',
    'TB_PADV1': 'Turbo > Pré Avançado', 'TB_PADV2': 'Turbo > Pré Avançado',
    'TB_ADV1': 'Turbo > Avançado', 'TB_ADV2': 'Turbo > Avançado',
    'TB_MAST1': 'Turbo > Master In English', 'TB_MAST2': 'Turbo > Master In English',
    'TB_ESPBA': 'Turbo > En Contacto', 'TB_ESPPI': 'Turbo > En Contacto',
    'TB_ESPIN': 'Turbo > En Contacto', 'TB_ESPAV': 'Turbo > En Contacto',
    'TB_ESPPA': 'Turbo > En Contacto',
    'CAE1': 'Cae Prep', 'CAE2': 'Cae Prep',
    'FCE': 'B2 First Prep', 'B2_F_Prep': 'B2 First Prep',
    'TKT': 'Tkt Prep',
    'CPE': 'Cpe Prep'  
}

ORDEM_ESTAGIO = [
    'Pre-school', 'Young Kids', 'Kids', 'Teens',
    'A1', 'Básico', 'Intermediário', 'Pré Avançado', 'Avançado',
    'Master In English', 'Advanced Conversation Course',
    'Turbo > Básico', 'Turbo > Intermediário', 'Turbo > Pré Avançado',
    'Turbo > Avançado', 'Turbo > Master In English',
    'En Contacto', 'Joven', 'Turbo > En Contacto',
    'Tkt Prep', 'B2 First Prep', 'Cae Prep', 'Cpe Prep',
    'Não identificado',
]

ORDEM_NIVEL = [
    'A1', 'A2', 'Advanced Conversation Course', 'Avançado', 'B2 First Prep',
    'Cae Prep', 'En Contacto', 'Intermediário', 'Joven', 'Kids',
    'Master In English', 'Pré Avançado', 'Pre-school', 'PRO Live 1',
    'Teens', 'Tkt Prep', 'Turbo > A', 'Turbo > Avançado', 'Turbo > Básico',
    'Turbo > En Contacto', 'Turbo > Intermediário', 'Turbo > Master In English',
    'Turbo > Pré Avançado', 'Young Kids',
    'Não identificado - Nível',
]

DIAS_VALIDOS = ['Seg','Seg-Qua','Seg-Ter-Qua-Qui','Ter','Ter-Qui',  'Qua', 'Qui', 'Sex',  'Sab', 'Sáb',  ]
NORMALIZAR_DIA = {'Sab': 'Sáb'}

DIAS_NORMALIZADOS = list(dict.fromkeys(NORMALIZAR_DIA.get(d, d) for d in DIAS_VALIDOS))

MAPA_ESTAGIO_2_INPUT = [
    "A1-1", "Pre-advanced 1", "Nuevo CNA En Contacto 2", "Advanced 1 - NEW",
    "Nuevo CNA En Contacto 1", "Teen UP 1", "Master in English 2 - NEW",
    "Teen UP 3", "Young Kids 4", "Advanced 2 - NEW", "Pre-advanced 2",
    "Intermediate 1", "Turbo > Intermediate 1", "Nuevo CNA En Contacto 3",
    "Master in English 1 - NEW", "Intermediate 2", "Nuevo CNA En Contacto 5",
    "Kids 2", "A1-2", "Basic 2", "Turbo > Basic 2",
    "Nuevo CNA En Contacto 4", "Turbo > Nuevo CNA En Contacto 3",
    "Advanced Conversation Course 2 - 21st", "Kids 1", "Teen UP 2", "Kids 3",
    "Kids 4", "Teens 4", "Advanced Conversation Course 1 - 21st",
    "Turbo > Nuevo CNA En Contacto 1", "Turbo > Basic 1", "Turbo > Pre-Advanced 1",
    "Turbo > Advanced 1 - NEW", "Tkt Prep", "CPE Prep 2", "Español Joven 2",
    "Turbo > Advanced 2 - NEW", "CAE Prep 2", "Pre-School - Garden 3",
    "Turbo > Nuevo CNA En Contacto 4", "Pre-School - Garden 2", "B2 First Prep",
    "Turbo > Nuevo CNA En Contacto 2", "CAE Prep 1", "Turbo > Intermediate 2",
    "Young Kids 1", "Young Kids 2", "Turbo > Master in English 2 - NEW",
    "Turbo > Pre-Advanced 2"
]
ORDEM_IDIOMA = [
    'CNA Turbo (Espanhol)',
    'CNA Turbo (Inglês)',
    'Espanhol',
    'Inglês',
    'Inglês (Preparatório)',
]
MAPA_ESTAGIO_2 = {}
for item in MAPA_ESTAGIO_2_INPUT:
    normalized_key = unicodedata.normalize('NFKD', item).encode('ASCII', 'ignore').decode('ASCII')
    normalized_key = re.sub(r'[^A-Za-z0-9 >_-]', '', normalized_key)
    normalized_key = re.sub(r'\s+', ' ', normalized_key).strip().upper()
    MAPA_ESTAGIO_2[normalized_key] = item

ORDEM_ESTAGIO_2 = MAPA_ESTAGIO_2_INPUT + ['Não identificado - Estagio 2']


COL_PROFESSOR_IDIOMA         = 'seu_sua_professor_a_utiliza_apenas_o_idioma_ingl_s_espanhol_durante_as_aulas'
COL_SATISFACAO               = 'como_voc_avalia_sua_satisfa_o_geral_com_as_aulas_do_a_seu_sua_professor_a'
COL_GRAU                     = 'qual_seu_grau_de_satisfa_o_com_o_que_e_o_quanto_aprendeu_no_seu_est_gio_atual'
COL_ABRE_CAMERA              = 'voc_abre_a_sua_c_mera_durante_as_aulas'
COL_PROFESSOR_CAMERA         = 'o_seu_professor_incentiva_a_abertura_de_c_mera_dos_alunos'
COL_PROBABILIDADE_RECOMENDAR = 'em_uma_escala_de_0_a_10_qual_a_probabilidade_de_voc_recomendar_o_cna_a_amigos_ou_colegas'
COL_COMENTARIO               = 'deixe_suas_sugest_es_elogios_a_seu_sua_professor_a_e_ou_sua_experi_ncia_cna'

RENAME_BASE = {
    'Total_Turmas':            'Total de turmas',
    'Total_Alunos':            'Total de alunos',
    'Total_Respostas':         'Total de respostas',
    'Uso_L2':                  'Uso de L2 [inglês/espanhol] durante as aulas',
    'Satisfacao_Prof':         'Satisfação com as aulas do prof',
    'Satisfacao_Aprendizagem': 'Satisfação com aprendizagem',
    'Prof_Incentiva_Camera':   'Seu professor incentiva abertura da câmera?',
    'Abertura_Camera':         'Abertura de câmera',
    '(%) Abertura de câmera':  '(%) Abertura de câmera',
    'Total_Detratores':        'DETRATOR',
    'Total_Neutros':           'NEUTRO',
    'Total_Promotores':        'PROMOTOR',
    'NPS Total':               'NPS Total',
}

COLS_DISPLAY_ZERO_RESPOSTAS = [
    'Uso de L2 [inglês/espanhol] durante as aulas',
    'Satisfação com as aulas do prof',
    'Satisfação com aprendizagem',
    'Seu professor incentiva abertura da câmera?',
    'Abertura de câmera',
    '(%) Abertura de câmera',
    'NPS Total',
    'DETRATOR',
    'NEUTRO',
    'PROMOTOR',
]

TURNO_ORDEM = {'Manhã': 0, 'Tarde': 1, 'Noite': 2, 'Não identificado': 3}

ORDEM_ESTAGIO_TODOS = [
    'A1-1', 'A1-2', 'A2-1',
    'Advanced 1 - NEW', 'Advanced 2 - NEW',
    'Advanced Conversation Course 1 - 21st', 'Advanced Conversation Course 2 - 21st',
    'B2 First Prep', 'CAE Prep 1', 'CAE Prep 2', 'CNA PRO Live 1A',
    'Español Joven 1', 'Español Joven 3',
    'Intermediate 1', 'Intermediate 2',
    'Kids 1', 'Kids 2', 'Kids 3', 'Kids 4',
    'Master in English 1 - NEW', 'Master in English 2 - NEW',
    'Nuevo CNA En Contacto 1', 'Nuevo CNA En Contacto 2', 'Nuevo CNA En Contacto 3',
    'Nuevo CNA En Contacto 4', 'Nuevo CNA En Contacto 5',
    'Pre-advanced 1', 'Pre-advanced 2',
    'Pre-School - Garden 1', 'Pre-School - Garden 3', 'Pre-School - Garden 4',
    'Teen UP 1', 'Teen UP 2', 'Teen UP 3', 'Teen UP 4',
    'Tkt Prep',
    'Turbo > A1-1', 'Turbo > Advanced 1 - NEW', 'Turbo > Advanced 2 - NEW',
    'Turbo > Basic 2', 'Turbo > Intermediate 1', 'Turbo > Intermediate 2',
    'Turbo > Master in English 1 - NEW', 'Turbo > Master in English 2 - NEW',
    'Turbo > Nuevo CNA En Contacto 2', 'Turbo > Nuevo CNA En Contacto 3',
    'Turbo > Nuevo CNA En Contacto 4', 'Turbo > Nuevo CNA En Contacto 5',
    'Turbo > Pre-Advanced 1', 'Turbo > Pre-Advanced 2',
    'Young Kids 1', 'Young Kids 2', 'Young Kids 3',
    'Não identificado',
]

ORDEM_HORARIO = [
    ('07:00 - 08:00', 'Manhã'),
    ('07:30 - 08:30', 'Manhã'),
    ('07:30 - 08:45', 'Manhã'),
    ('07:30 - 09:00', 'Manhã'),
    ('08:00 - 09:15', 'Manhã'),
    ('08:00 - 09:30', 'Manhã'),
    ('09:00 - 10:00', 'Manhã'),
    ('09:30 - 10:30', 'Manhã'),
    ('09:30 - 10:45', 'Manhã'),
    ('10:00 - 11:00', 'Manhã'),
    ('10:00 - 11:15', 'Manhã'),
    ('10:00 - 11:30', 'Manhã'),
    ('10:30 - 12:00', 'Manhã'),
    ('11:00 - 12:00', 'Manhã'),
    ('11:00 - 12:15', 'Manhã'),
    ('11:00 - 12:30', 'Manhã'),
    ('12:00 - 13:15', 'Tarde'),
    ('12:00 - 13:30', 'Tarde'),
    ('12:30 - 14:00', 'Tarde'),
    ('13:30 - 14:45', 'Tarde'),
    ('14:00 - 15:15', 'Tarde'),
    ('14:15 - 15:30', 'Tarde'),
    ('15:00 - 16:00', 'Tarde'),
    ('15:00 - 16:15', 'Tarde'),
    ('15:00 - 16:30', 'Tarde'),
    ('16:30 - 17:45', 'Tarde'),
    ('17:00 - 19:00', 'Tarde'),
    ('17:45 - 18:45', 'Tarde'),
    ('17:45 - 19:00', 'Tarde'),
    ('17:45 - 19:15', 'Tarde'),
    ('18:00 - 19:00', 'Noite'),
    ('18:00 - 19:15', 'Noite'),
    ('18:45 - 20:15', 'Noite'),
    ('19:00 - 20:15', 'Noite'),
    ('19:00 - 20:30', 'Noite'),
    ('19:15 - 20:30', 'Noite'),
    ('19:15 - 20:45', 'Noite'),
    ('19:30 - 20:30', 'Noite'),
    ('19:30 - 20:45', 'Noite'),
    ('19:30 - 21:00', 'Noite'),
    ('20:00 - 21:30', 'Noite'),
    ('20:00 - 22:00', 'Noite'),
    ('20:15 - 22:15', 'Noite'),
    ('20:45 - 22:00', 'Noite'),
    ('20:45 - 22:15', 'Noite'),
    ('21:00 - 22:15', 'Noite'),
]

def _reindex_com_extras(resumo, chave, ordem):
    fixos = set(ordem)
    extras = sorted((v for v in resumo[chave].dropna().unique() if v not in fixos), key=str)
    if extras:
        print(f"   ⚠️  Fora da lista fixa ({chave}), acrescentados ao fim: {extras}")
    resumo = resumo.set_index(chave).reindex(list(ordem) + extras)
    resumo.index.name = chave
    return resumo.reset_index()
def preparar_metricas(df):
    df_copy = df.copy()
    df_copy[COL_PROFESSOR_CAMERA] = df_copy[COL_PROFESSOR_CAMERA].map(
        {'Sim': 1, 'Não': 0, 'Yes': 1, 'No': 0}
    )
    df_copy[COL_ABRE_CAMERA] = df_copy[COL_ABRE_CAMERA].map(
        {'Sim': 1, 'Não': 0, 'Yes': 1, 'No': 0}
    )
    df_copy[COL_PROFESSOR_IDIOMA] = pd.to_numeric(df_copy[COL_PROFESSOR_IDIOMA], errors='coerce')
    df_copy[COL_SATISFACAO] = pd.to_numeric(df_copy[COL_SATISFACAO], errors='coerce')
    df_copy[COL_GRAU] = pd.to_numeric(df_copy[COL_GRAU], errors='coerce')
    df_copy['_nps']     = pd.to_numeric(df_copy[COL_PROBABILIDADE_RECOMENDAR], errors='coerce')
    df_copy['PROMOTOR'] = (df_copy['_nps'] >= 9).astype(int)
    df_copy['DETRATOR'] = (df_copy['_nps'] <= 6).astype(int)
    df_copy['NEUTRO']   = ((df_copy['_nps'] >= 7) & (df_copy['_nps'] <= 8)).astype(int)
    return df_copy

def calcular_adesao(respostas, alunos):
    respostas = pd.to_numeric(respostas, errors='coerce')
    alunos    = pd.to_numeric(alunos, errors='coerce')

    adesao = respostas / alunos
    adesao = adesao.replace([np.inf, -np.inf], np.nan).fillna(0)
    adesao = adesao.clip(upper=1.0).round(4) 

    return adesao

def calcular_derivados(resumo):
    resumo['(%) Abertura de câmera'] = (
        resumo['Abertura_Camera'] / resumo['Total_Respostas']
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(upper=1.0).round(4)

    resumo['% Promotores'] = (
        resumo['Total_Promotores'] / resumo['Total_Respostas']
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(upper=1.0).round(4)

    resumo['% Detratores'] = (
        resumo['Total_Detratores'] / resumo['Total_Respostas']
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(upper=1.0).round(4)


    resumo['NPS Total'] = ((resumo['% Promotores'] - resumo['% Detratores']) * 100).round(1)

    return resumo

def _replace_zeros_with_dash(relatorio_df):
    mask = (relatorio_df['Total de respostas'] == 0) | (relatorio_df['Total de respostas'].isna())
    for col in COLS_DISPLAY_ZERO_RESPOSTAS:
        if col in relatorio_df.columns:
            if pd.api.types.is_numeric_dtype(relatorio_df[col]):
                relatorio_df[col] = relatorio_df[col].astype(object)
            relatorio_df.loc[mask, col] = ' - '
    return relatorio_df


def _soma_alunos_unicos(x, df, col_codigo='codigo_turma', col_alunos='alunos_por_turma'):
    return (
        df.loc[x.index, [col_codigo, col_alunos]]
        .sort_values(col_alunos, ascending=False)
        .drop_duplicates(subset=[col_codigo])[col_alunos]
        .sum()
    )


def total_alunos(df):
    return df.groupby('codigo_turma')['alunos_por_turma'].max().sum()


def _turmas_unicas(df, cols):
    return (
        df[cols]
        .sort_values('alunos_por_turma', ascending=False)
        .drop_duplicates('codigo_turma')
    )


def extrair_idioma(codigo_turma):
    codigo = str(codigo_turma).strip().upper()
    for chave in sorted(MAPA_IDIOMA.keys(), key=len, reverse=True):
        if codigo.startswith(chave):
            return MAPA_IDIOMA[chave]
    return 'Inglês'


def extrair_dia_semana(horario):
    if pd.isna(horario) or str(horario).strip() == '':
        return 'Não identificado'
    horario_str = str(horario).strip()
    dia = re.split(r'[\s\(]', horario_str)[0].strip()
    return NORMALIZAR_DIA.get(dia, dia) if dia else 'Não identificado'


def extrair_intervalo_horario(horario):
    if pd.isna(horario) or str(horario).strip() == '':
        return 'Não identificado'
    horario_str = str(horario).strip()
    match = re.search(r'\((\d{1,2}:\d{2})\s*/\s*(\d{1,2}:\d{2})\)', horario_str)
    if not match:
        return 'Não identificado'
    return f"{match.group(1)} - {match.group(2)}"


def extrair_turno(horario):
    if pd.isna(horario) or str(horario).strip() == '':
        return 'Não identificado'
    horario_str = str(horario).strip()
    match = re.search(r'\((\d{1,2}):(\d{2})\s*/', horario_str)
    if not match:
        return 'Não identificado'
    hora_inicio = int(match.group(1))
    if 6 <= hora_inicio < 12:
        return 'Manhã'
    elif 12 <= hora_inicio < 18:
        return 'Tarde'
    else:
        return 'Noite'


def extrair_estagio(codigo_turma):
    codigo = str(codigo_turma).strip()
    codigo_normalized = unicodedata.normalize('NFKD', codigo).encode('ASCII', 'ignore').decode('ASCII')
    codigo_clean = re.sub(r'[^A-Za-z0-9_-]', '', codigo_normalized)
    codigo_upper = codigo_clean.upper()

    mapa_upper_to_value = {k.upper(): v for k, v in MAPA_ESTAGIO.items()}
    sorted_keys_upper = sorted(mapa_upper_to_value.keys(), key=len, reverse=True)

    for key_upper in sorted_keys_upper:
        if codigo_upper.startswith(key_upper):
            return mapa_upper_to_value[key_upper]

    match = re.match(r'^([A-Z0-9_]+)', codigo_upper)
    if match:
        extracted_prefix = match.group(1)
        if extracted_prefix in mapa_upper_to_value:
            return mapa_upper_to_value[extracted_prefix]
        match_alpha = re.match(r'^([A-Z_]+)', extracted_prefix)
        if match_alpha:
            alpha_prefix = match_alpha.group(1)
            if alpha_prefix in mapa_upper_to_value:
                return mapa_upper_to_value[alpha_prefix]

    return 'Não identificado'

def gerar_relatorio_professor_completo(feedback):
    df = preparar_metricas(feedback)

    resumo = (
        df.groupby(['chave_match', 'escola', 'id_escola', 'analista'])
        .agg(
            Professor       = ('Professor', lambda x: x.mode()[0] if not x.mode().empty else 'Professor Não Identificado'),
            Total_Turmas    = ('codigo_turma', 'nunique'),
            Total_Alunos    = ('codigo_turma', lambda x: _soma_alunos_unicos(x, df)),
            **COLUNAS_AGG
        )
        .reset_index()
    )
    resumo = resumo.loc[:, ~resumo.columns.duplicated()]

    resumo[['Uso_L2','Satisfacao_Prof','Satisfacao_Aprendizagem','Prof_Incentiva_Camera']] = \
        resumo[['Uso_L2','Satisfacao_Prof','Satisfacao_Aprendizagem','Prof_Incentiva_Camera']].round(2)
    resumo[['Total_Respostas','Total_Turmas','Total_Promotores','Total_Detratores','Total_Neutros','Abertura_Camera']] = \
        resumo[['Total_Respostas','Total_Turmas','Total_Promotores','Total_Detratores','Total_Neutros','Abertura_Camera']].astype(int)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por professor'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    relatorio = resumo.drop(columns=['chave_match'], errors='ignore')

    relatorio = relatorio[[
        'escola', 'analista', 'id_escola', 'Professor',
        'Adesão por professor', 'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':               'Escola',
        'analista':             'Analista',
        'id_escola':            'ID Escola',
        'Adesão por professor': 'Adesão por professor',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_professor_completo.csv — {len(relatorio)} professores")
    return relatorio

def gerar_relatorio_faixa_turma(feedback):
    df = preparar_metricas(feedback)
    df['faixa_turma'] = df['alunos_por_turma'].apply(extrair_faixa_turma)

    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'faixa_turma'])
    totais = alunos_u.groupby('faixa_turma').agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby('faixa_turma').agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on='faixa_turma', how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por faixa'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    ordem_map = {f: i for i, f in enumerate(ORDEM_FAIXA_TURMA)}
    resumo['_ord'] = resumo['faixa_turma'].map(ordem_map)
    resumo = resumo.sort_values('_ord').drop(columns='_ord')

    relatorio = resumo[[
        'faixa_turma', 'Adesão por faixa',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'faixa_turma':       'Faixa de turmas',
        'Adesão por faixa':  'Adesão por faixa',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    faixas_unicas = df['faixa_turma'].nunique()
    print(f"\n✅ relatorio_faixa_turma.csv — {len(relatorio)} linhas, {faixas_unicas} faixas diferentes")

    return relatorio

def gerar_relatorio_turma(feedback):
    df = preparar_metricas(feedback)

    resumo = (
        df.groupby(['codigo_turma', 'escola', 'id_escola', 'analista'])
        .agg(
            Professor    = ('Professor', lambda x: x.mode()[0] if not x.mode().empty else 'Professor Não Identificado'),
            Total_Alunos = ('alunos_por_turma', 'max'),
            **COLUNAS_AGG
        )
        .reset_index()
    )
    resumo = resumo.loc[:, ~resumo.columns.duplicated()]

    resumo[['Uso_L2','Satisfacao_Prof','Satisfacao_Aprendizagem','Prof_Incentiva_Camera']] = \
        resumo[['Uso_L2','Satisfacao_Prof','Satisfacao_Aprendizagem','Prof_Incentiva_Camera']].round(2)
    resumo[['Total_Respostas','Total_Promotores','Total_Detratores','Total_Neutros','Abertura_Camera']] = \
        resumo[['Total_Respostas','Total_Promotores','Total_Detratores','Total_Neutros','Abertura_Camera']].astype(int)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por turma'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])


    relatorio = resumo[[
        'escola','analista', 'id_escola',  'Professor', 'codigo_turma',
        'Adesão por turma', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'analista':         'Analista',
        'id_escola':        'ID Escola',
        'escola':           'Escola',
        'codigo_turma':     'Turma',
        'Adesão por turma': 'Adesão por turma',
    }).sort_values(['Escola', 'Professor', 'Turma'])

    if col_codigo_turma_gig and col_codigo_turma_gig in gigantes_validos.columns:

        col_status_gig = next(
            (c for c in dados_gigantes.columns if 'status' in c or 'situa' in c),
            None
        )

        VALORES_CANCELADOS = ['cancelad', 'encerrad', 'finalizad', 'inativ']

        gigantes_p_relatorio = gigantes_validos.copy()

        if col_status_gig and col_status_gig in gigantes_p_relatorio.columns:
            status_norm = (
                gigantes_p_relatorio[col_status_gig]
                .fillna('')
                .astype(str)
                .str.strip()
                .str.lower()
            )
            mask_cancelada = status_norm.apply(
                lambda s: any(termo in s for termo in VALORES_CANCELADOS)
            )
            gigantes_p_relatorio = gigantes_p_relatorio[~mask_cancelada]

        turmas_no_relatorio = set(relatorio['Turma'].dropna().astype(str))

        gigantes_p_relatorio = gigantes_p_relatorio.copy()
        gigantes_p_relatorio['codigo_turma'] = gigantes_p_relatorio[col_codigo_turma_gig].astype(str).str.strip()

        turmas_sem_resposta_gig = gigantes_p_relatorio[
            ~gigantes_p_relatorio['codigo_turma'].isin(turmas_no_relatorio)
        ].drop_duplicates(subset=['codigo_turma'])

        if not turmas_sem_resposta_gig.empty:
            extras = pd.DataFrame()
            extras['Turma'] = turmas_sem_resposta_gig['codigo_turma']

            if col_escola_gig and col_escola_gig in turmas_sem_resposta_gig.columns:
                extras['Escola'] = turmas_sem_resposta_gig[col_escola_gig]
            else:
                extras['Escola'] = pd.NA

            if col_professor_gig and col_professor_gig in turmas_sem_resposta_gig.columns:
                extras['Professor'] = turmas_sem_resposta_gig[col_professor_gig]
            else:
                extras['Professor'] = 'Professor não identificado'

            if col_id_escola_gig and col_id_escola_gig in turmas_sem_resposta_gig.columns:
                extras['ID Escola'] = turmas_sem_resposta_gig[col_id_escola_gig]
            else:
                extras['ID Escola'] = ''

            extras['Analista'] = extras['Escola'].map(MAPA_ESCOLA_ANALISTA).fillna('Não atribuído')

            extras['Total de alunos'] = pd.to_numeric(
                turmas_sem_resposta_gig[col_total_alunos], errors='coerce'
            ).fillna(0)

            extras['Total de respostas'] = 0
            extras['Adesão por turma']   = 0.0

            for col in COLS_DISPLAY_ZERO_RESPOSTAS:
                if col in relatorio.columns:
                    extras[col] = ' - '

            extras = extras[relatorio.columns]

            relatorio = pd.concat([relatorio, extras], ignore_index=True)
            relatorio = relatorio.sort_values(['Escola', 'Professor', 'Turma'])

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_turma.csv — {len(relatorio)} turmas")
    return relatorio

def gerar_relatorio_idioma(feedback):
    df = preparar_metricas(feedback)
    df['idioma'] = df['codigo_turma'].apply(extrair_idioma)

    alunos_u = _turmas_unicas(df, ['codigo_turma','alunos_por_turma','escola','idioma'])
    totais = alunos_u.groupby(['escola','idioma']).agg(
        Total_Alunos  = ('alunos_por_turma', 'sum'),
        Total_Turmas  = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['escola','idioma']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['escola','idioma'], how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por Idioma'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    relatorio = resumo[[
        'escola', 'idioma', 'Adesão por Idioma', 'Total_Turmas', 'Total_Alunos',
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':             'Escola',
        'idioma':             'Idioma',
        'Adesão por Idioma':  'Adesão por Idioma',
    }).sort_values(['Escola', 'Idioma'])

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_idioma.csv — {len(relatorio)} linhas")
    return relatorio


def gerar_relatorio_dia_semana(feedback):
    df = preparar_metricas(feedback)

    if 'horario_gig' in df.columns:
        print(f"✅ Usando coluna 'horario_gig' para Dia da Semana")
        df['horario'] = df['horario_gig'].fillna('')
        print(f"   Amostra de horários do dados_gigantes: {df['horario_gig'].dropna().head(10).tolist()}")
    else:
        print("⚠️  Coluna 'horario_gig' não encontrada. Usando 'horario' extraído do tópico como fallback.")

    df['dia_semana'] = df['horario'].apply(extrair_dia_semana)

    dias_normalizados = DIAS_NORMALIZADOS
    alunos_u = _turmas_unicas(df, ['codigo_turma','alunos_por_turma','escola','dia_semana'])
    totais = alunos_u.groupby(['escola','dia_semana']).agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['escola','dia_semana']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['escola','dia_semana'], how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por dia da semana'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    ordem_map = {d: i for i, d in enumerate(dias_normalizados)}
    resumo['_ord'] = resumo['dia_semana'].map(ordem_map).fillna(99)
    resumo = resumo.sort_values(['escola','_ord']).drop(columns=['_ord'])

    relatorio = resumo[[
        'escola', 'dia_semana', 'Adesão por dia da semana',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':                  'Escola',
        'dia_semana':              'Dia da semana',
        'Adesão por dia da semana':'Adesão por dia da semana',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    dias_unicos = df['dia_semana'].nunique()
    print(f"\n✅ relatorio_dia_semana.csv — {len(relatorio)} linhas, {dias_unicos} dias diferentes")

    dias_encontrados = sorted(df['dia_semana'].unique())
    print(f"   Dias encontrados: {dias_encontrados}")

    return relatorio


def gerar_relatorio_horario(feedback):
    df = preparar_metricas(feedback)

    if 'horario_gig' in df.columns:
        print(f"✅ Usando coluna 'horario_gig' para Horário/Turno")
        df['horario'] = df['horario_gig'].fillna('')
        print(f"   Amostra de horários do dados_gigantes: {df['horario_gig'].dropna().head(10).tolist()}")
    else:
        print("⚠️  Coluna 'horario_gig' não encontrada. Usando 'horario' extraído do tópico como fallback.")

    df['horario_intervalo'] = df['horario'].apply(extrair_intervalo_horario)
    df['turno'] = df['horario'].apply(extrair_turno)

    

    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'escola', 'horario_intervalo', 'turno'])
    totais = alunos_u.groupby(['escola', 'horario_intervalo', 'turno']).agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['escola', 'horario_intervalo', 'turno']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['escola', 'horario_intervalo', 'turno'], how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por horário'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo['_ord_turno'] = resumo['turno'].map(TURNO_ORDEM)
    resumo = resumo.sort_values(['escola', '_ord_turno', 'horario_intervalo']).drop(columns=['_ord_turno'])

    relatorio = resumo[[
        'escola', 'horario_intervalo', 'turno', 'Adesão por horário',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':             'Escola',
        'horario_intervalo':  'Horário',
        'turno':              'Turno',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    horarios_unicos = df['horario_intervalo'].nunique()
    print(f"\n✅ relatorio_horario.csv — {len(relatorio)} linhas, {horarios_unicos} horários diferentes")

    turnos_encontrados = sorted(df['turno'].unique(), key=lambda t: TURNO_ORDEM.get(t, 99))
    print(f"   Turnos encontrados: {turnos_encontrados}")

    return relatorio


def gerar_relatorio_nivel(feedback):
    df = preparar_metricas(feedback)

    if 'nivel_gig' in df.columns:
        df['nivel'] = df['nivel_gig'].fillna('Não identificado - Nível')
        print(f"✅ Usando coluna 'nivel_gig' para Nível")
        print(f"   Valores únicos encontrados: {df['nivel_gig'].nunique()}")
        print(f"   Amostra: {df['nivel_gig'].dropna().head(10).tolist()}")
    else:
        print("⚠️  Coluna 'nivel_gig' não encontrada. Tentando extrair do 'codigo_turma' como fallback.")
        df['nivel'] = df['codigo_turma'].astype(str).str.extract(r'^([A-Za-z0-9_]+)')[0].fillna('Não identificado - Nível')
        df['nivel'] = df['nivel'].str.replace(r'[0-9_]', '', regex=True).fillna('Não identificado - Nível')

    df['nivel'] = df['nivel'].astype(str).str.strip().replace('', 'Não identificado - Nível')
    df['nivel'] = df['nivel'].fillna('Não identificado - Nível')

    alunos_u = _turmas_unicas(df, ['codigo_turma','alunos_por_turma','escola','nivel'])
    totais = alunos_u.groupby(['escola','nivel']).agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['escola','nivel']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['escola','nivel'], how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por Nível'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])
    resumo = resumo.sort_values(['escola', 'nivel'])

    relatorio = resumo[[
        'escola', 'nivel', 'Adesão por Nível',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':             'Escola',
        'nivel':              'Nível',
        'Adesão por Nível':   'Adesão por Nível',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    relatorio.to_csv("relatorio_nivel.csv", index=False, sep=',', encoding='utf-8-sig')

    niveis_unicos = df['nivel'].nunique()
    print(f"\n✅ relatorio_nivel.csv — {len(relatorio)} linhas, {niveis_unicos} níveis diferentes")

    niveis_encontrados = sorted(df['nivel'].unique())
    print(f"   Níveis encontrados: {niveis_encontrados[:10]}{'...' if len(niveis_encontrados) > 10 else ''}")

    return relatorio

def gerar_relatorio_estagio(feedback):
    df = preparar_metricas(feedback)

    if 'estagio_gig' in df.columns:
        df['estagio'] = df['estagio_gig'].fillna('Não identificado')
        print(f"✅ Usando coluna 'estagio_gig' para Estágio")
        print(f"   Valores únicos encontrados: {df['estagio_gig'].nunique()}")
        print(f"   Amostra: {df['estagio_gig'].dropna().head(10).tolist()}")
    else:
        print("⚠️  Coluna 'estagio_gig' não encontrada. Usando função extrair_estagio() como fallback.")
        df['estagio'] = df['codigo_turma'].apply(extrair_estagio)

    df['estagio'] = df['estagio'].astype(str).str.strip().replace('', 'Não identificado')
    df['estagio'] = df['estagio'].fillna('Não identificado')

    alunos_u = _turmas_unicas(df, ['codigo_turma','alunos_por_turma','escola','estagio'])
    totais = alunos_u.groupby(['escola','estagio']).agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['escola','estagio']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['escola','estagio'], how='left')
    resumo = calcular_derivados(resumo)
    resumo['Adesão por Estágio'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo = resumo.sort_values(['escola', 'estagio'])

    relatorio = resumo[[
        'escola', 'estagio', 'Adesão por Estágio',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'escola':             'Escola',
        'estagio':            'Estágio',
        'Adesão por Estágio': 'Adesão por Estágio',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    estagios_unicos = df['estagio'].nunique()
    print(f"\n✅ relatorio_estagio.csv — {len(relatorio)} linhas, {estagios_unicos} estágios diferentes")

    estagios_encontrados = sorted(df['estagio'].unique())
    print(f"   Estágios encontrados: {estagios_encontrados[:10]}{'...' if len(estagios_encontrados) > 10 else ''}")

    return relatorio

def gerar_relatorio_horario_todos(feedback):
    df = preparar_metricas(feedback)

    if 'horario_gig' in df.columns:
        df['horario'] = df['horario_gig'].fillna('')

    df['horario_intervalo'] = df['horario'].apply(extrair_intervalo_horario)
    df['turno'] = df['horario'].apply(extrair_turno)

    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'horario_intervalo', 'turno'])
    totais = alunos_u.groupby(['horario_intervalo', 'turno']).agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby(['horario_intervalo', 'turno']).agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on=['horario_intervalo', 'turno'], how='left')

    fixos = set(ORDEM_HORARIO)
    extras = sorted(
        {p for p in zip(resumo['horario_intervalo'], resumo['turno']) if p not in fixos},
        key=lambda p: (TURNO_ORDEM.get(p[1], 99), p[0])
    )
    if extras:
        print(f"   ⚠️  Horários fora de ORDEM_HORARIO, acrescentados ao fim: {extras}")
    idx_completo = pd.MultiIndex.from_tuples(list(ORDEM_HORARIO) + extras,
                                             names=['horario_intervalo', 'turno'])
    resumo = resumo.set_index(['horario_intervalo', 'turno']).reindex(idx_completo).reset_index()

    colunas_numericas = [
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', 'Total_Promotores',
        'Total_Detratores', 'Total_Neutros', 'Total_Alunos', 'Total_Turmas',
    ]
    resumo[colunas_numericas] = resumo[colunas_numericas].fillna(0)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por Horário'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
            'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']] = \
        resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
                'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']].astype(int)

    relatorio = resumo[[
        'horario_intervalo', 'turno', 'Adesão por Horário',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'horario_intervalo': 'Horário',
        'turno':             'Turno',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_horario_todos.csv — {len(relatorio)} linhas (todos os horários, incl. zerados)")

    return relatorio
def gerar_relatorio_escola(feedback):
    df = preparar_metricas(feedback)

    df['escola'] = df['escola'].fillna('Escola Não Identificada')

    resumo = df.groupby(['escola', 'id_escola']).agg(
        Total_Respostas       = (COL_SATISFACAO,       'count'),
        Total_Alunos          = ('codigo_turma', lambda x: _soma_alunos_unicos(x, df)),
        Total_Turmas          = ('codigo_turma',        'nunique'),
        Uso_L2                = (COL_PROFESSOR_IDIOMA,  'mean'),
        Satisfacao_Prof       = (COL_SATISFACAO,        'mean'),
        Satisfacao_Aprendizagem = (COL_GRAU,            'mean'),
        Prof_Incentiva_Camera = (COL_PROFESSOR_CAMERA,  'mean'),
        Abertura_Camera       = (COL_ABRE_CAMERA,       'sum'),
        Total_Promotores      = ('PROMOTOR',             'sum'),
        Total_Detratores      = ('DETRATOR',             'sum'),
        Total_Neutros         = ('NEUTRO',               'sum'),
    ).round(2).reset_index()

    resumo = calcular_derivados(resumo)
    resumo['Adesão por escola'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])


    todos = pd.DataFrame([{
        'escola':                  'Todos',
        'Total_Respostas':         df[COL_SATISFACAO].count(),
        'Total_Alunos':            total_alunos(df),
        'Total_Turmas':            df['codigo_turma'].nunique(),
        'Uso_L2':                  round(df[COL_PROFESSOR_IDIOMA].mean(), 2),
        'Satisfacao_Prof':         round(df[COL_SATISFACAO].mean(), 2),
        'Satisfacao_Aprendizagem': round(df[COL_GRAU].mean(), 2),
        'Prof_Incentiva_Camera':   round(df[COL_PROFESSOR_CAMERA].mean(), 2),
        'Abertura_Camera':         df[COL_ABRE_CAMERA].sum(),
        'Total_Promotores':        df['PROMOTOR'].sum(),
        'Total_Detratores':        df['DETRATOR'].sum(),
        'Total_Neutros':           df['NEUTRO'].sum(),
    }])
    todos = calcular_derivados(todos)
    todos['Adesão por escola'] = calcular_adesao(todos['Total_Respostas'], todos['Total_Alunos'])

    relatorio = pd.concat([resumo, todos], ignore_index=True)
    relatorio['_ord'] = relatorio['escola'].apply(lambda x: 0 if x == 'Todos' else 1)
    relatorio = relatorio.sort_values(['_ord', 'escola'], ascending=[False, True]).drop(columns='_ord')

    relatorio = relatorio.rename(columns={**RENAME_BASE,
        'escola':            'Escola',
        'Adesão por escola': 'Adesão por escola',
    })

    relatorio = relatorio[[
        'Escola','Adesão por escola', 'Total de turmas', 'Total de alunos', 'Total de respostas',
        'Uso de L2 [inglês/espanhol] durante as aulas', 'Satisfação com as aulas do prof', 'Satisfação com aprendizagem',
        'Seu professor incentiva abertura da câmera?', 'Abertura de câmera', '(%) Abertura de câmera',
        'DETRATOR', 'NEUTRO', 'PROMOTOR', 'NPS Total'
    ]]

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_escola.csv — {len(relatorio)} linhas")
    return relatorio


def gerar_relatorio_comentarios(feedback):
    relatorio = feedback[[
        'analista', 'escola', 'Professor', 'codigo_turma', COL_PROBABILIDADE_RECOMENDAR, COL_COMENTARIO
    ]].rename(columns={
        'escola':       'Escola',
        'analista':     'Analista',
        'codigo_turma': 'Código da turma',
        COL_PROBABILIDADE_RECOMENDAR: 'NPS',
        COL_COMENTARIO: 'Deixe suas sugestões/elogios a seu/sua professor(a) e/ou sua experiência CNA.',
    }).copy()

    relatorio['ID Escola'] = feedback.get('id_escola', '')
    relatorio = relatorio[[
        'Escola','Analista', 'ID Escola',  'Professor', 'Código da turma',
        'NPS', 'Deixe suas sugestões/elogios a seu/sua professor(a) e/ou sua experiência CNA.',
    ]]

    print(f"\n✅ relatorio_comentarios.csv — {len(relatorio)} respostas")
    return relatorio

def gerar_relatorio_turmas_sem_resposta(turmas_sem_resposta):
    if turmas_sem_resposta.empty:
        print("\nℹ️  Nenhuma turma sem resposta encontrada (ou base_pesquisa não processada).")
        return pd.DataFrame()

    colunas_base = ['zoom_id']
    colunas_opcionais = ['topico', 'codigo_turma', 'analista', 'escola', 'Professor', 'alunos_por_turma']
    colunas_presentes = colunas_base + [c for c in colunas_opcionais if c in turmas_sem_resposta.columns]

    relatorio = turmas_sem_resposta[colunas_presentes].copy().rename(columns={
        'zoom_id':          'Zoom ID',
        'topico':           'Tópico',
        'codigo_turma':     'Código da turma',
        'analista':         'Analista',
        'escola':           'Escola',
        'Professor':        'Professor',
        'alunos_por_turma': 'Total de alunos',
    })

    print(f"\n✅ relatorio_turmas_sem_resposta.csv — {len(relatorio)} turmas sem resposta")
    return relatorio

def gerar_relatorio_cna_digital_school(feedback):
    df = preparar_metricas(feedback)
    df = df[df['escola'] == 'CNA Digital School'].copy()

    if df.empty:
        print("\nℹ️  Nenhuma linha encontrada para 'CNA Digital School'.")
        return pd.DataFrame()

    resumo = pd.DataFrame([{
        'escola':                  'CNA Digital School',
        'Total_Respostas':         df[COL_SATISFACAO].count(),
        'Total_Alunos':            total_alunos(df),
        'Total_Turmas':            df['codigo_turma'].nunique(),
        'Uso_L2':                  round(df[COL_PROFESSOR_IDIOMA].mean(), 2),
        'Satisfacao_Prof':         round(df[COL_SATISFACAO].mean(), 2),
        'Satisfacao_Aprendizagem': round(df[COL_GRAU].mean(), 2),
        'Prof_Incentiva_Camera':   round(df[COL_PROFESSOR_CAMERA].mean(), 2),
        'Abertura_Camera':         df[COL_ABRE_CAMERA].sum(),
        'Total_Promotores':        df['PROMOTOR'].sum(),
        'Total_Detratores':        df['DETRATOR'].sum(),
        'Total_Neutros':           df['NEUTRO'].sum(),
    }])

    resumo = calcular_derivados(resumo)
    resumo['Adesão por escola'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    relatorio = resumo.rename(columns={**RENAME_BASE,
        'escola':            'Escola',
        'Adesão por escola': 'Adesão por escola',
    })

    relatorio = relatorio[[
        'Escola', 'Adesão por escola', 'Total de turmas', 'Total de alunos', 'Total de respostas',
        'Uso de L2 [inglês/espanhol] durante as aulas', 'Satisfação com as aulas do prof', 'Satisfação com aprendizagem',
        'Seu professor incentiva abertura da câmera?', 'Abertura de câmera', '(%) Abertura de câmera',
        'DETRATOR', 'NEUTRO', 'PROMOTOR', 'NPS Total'
    ]]

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_cna_digital_school.csv — {len(relatorio)} linha")
    return relatorio


def gerar_relatorio_dia_semana_todos(feedback):
    df = preparar_metricas(feedback)

    if 'horario_gig' in df.columns:
        df['horario'] = df['horario_gig'].fillna('')

    df['dia_semana'] = df['horario'].apply(extrair_dia_semana)

    dias_normalizados = DIAS_NORMALIZADOS
    
    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'dia_semana'])
    totais = alunos_u.groupby('dia_semana').agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby('dia_semana').agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on='dia_semana', how='left')

    resumo = _reindex_com_extras(resumo, 'dia_semana', dias_normalizados)

    colunas_numericas = [
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', 'Total_Promotores',
        'Total_Detratores', 'Total_Neutros', 'Total_Alunos', 'Total_Turmas',
    ]
    resumo[colunas_numericas] = resumo[colunas_numericas].fillna(0)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por Dia'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
            'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']] = \
        resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
                'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']].astype(int)

    relatorio = resumo[[
        'dia_semana', 'Adesão por Dia',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'dia_semana': 'Dia da Semana',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_dia_semana_todos.csv — {len(relatorio)} linhas (todos os dias válidos, incl. zerados)")
    print(relatorio)
    return relatorio

def gerar_relatorio_nivel_todos(feedback):
    df = preparar_metricas(feedback)

    if 'nivel_gig' in df.columns:
        df['nivel'] = df['nivel_gig'].fillna('Não identificado - Nível')
    else:
        df['nivel'] = df['codigo_turma'].astype(str).str.extract(r'^([A-Za-z0-9_]+)')[0].fillna('Não identificado - Nível')
        df['nivel'] = df['nivel'].str.replace(r'[0-9_]', '', regex=True).fillna('Não identificado - Nível')

    df['nivel'] = df['nivel'].astype(str).str.strip().replace('', 'Não identificado - Nível')
    df['nivel'] = df['nivel'].fillna('Não identificado - Nível')

    # --- Totais de turmas/alunos (dedupados por turma) ---
    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'nivel'])
    totais = alunos_u.groupby('nivel').agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby('nivel').agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on='nivel', how='left')

    resumo = _reindex_com_extras(resumo, 'nivel', ORDEM_NIVEL)

    colunas_numericas = [
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', 'Total_Promotores',
        'Total_Detratores', 'Total_Neutros', 'Total_Alunos', 'Total_Turmas',
    ]
    resumo[colunas_numericas] = resumo[colunas_numericas].fillna(0)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por Nível'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
            'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']] = \
        resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
                'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']].astype(int)

    relatorio = resumo[[
        'nivel', 'Adesão por Nível',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'nivel': 'Nível',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_nivel_todos.csv — {len(relatorio)} linhas (todos os níveis, incl. zerados)")

    return relatorio
def gerar_relatorio_estagio_todos(feedback):
    df = preparar_metricas(feedback)

    if 'estagio_gig' in df.columns:
        df['estagio'] = df['estagio_gig'].fillna('Não identificado')
    else:
        df['estagio'] = df['codigo_turma'].apply(extrair_estagio)

    df['estagio'] = df['estagio'].astype(str).str.strip().replace('', 'Não identificado')
    df['estagio'] = df['estagio'].fillna('Não identificado')

    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'estagio'])
    totais = alunos_u.groupby('estagio').agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby('estagio').agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on='estagio', how='left')

        
    resumo = _reindex_com_extras(resumo, 'estagio', ORDEM_ESTAGIO_TODOS)

    colunas_numericas = [
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', 'Total_Promotores',
        'Total_Detratores', 'Total_Neutros', 'Total_Alunos', 'Total_Turmas',
    ]
    resumo[colunas_numericas] = resumo[colunas_numericas].fillna(0)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por Estágio'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
            'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']] = \
        resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
                'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']].astype(int)

    relatorio = resumo[[
        'estagio', 'Adesão por Estágio',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'estagio': 'Estágio',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_estagio_todos.csv — {len(relatorio)} linhas (todos os estágios, incl. zerados)")

    return relatorio
def gerar_relatorio_idioma_todos(feedback):
    df = preparar_metricas(feedback)
    df['idioma'] = df['codigo_turma'].apply(extrair_idioma)

    alunos_u = _turmas_unicas(df, ['codigo_turma', 'alunos_por_turma', 'idioma'])
    totais = alunos_u.groupby('idioma').agg(
        Total_Alunos = ('alunos_por_turma', 'sum'),
        Total_Turmas = ('codigo_turma',     'count'),
    ).reset_index()

    resumo = df.groupby('idioma').agg(**COLUNAS_AGG).round(2).reset_index()
    resumo = resumo.merge(totais, on='idioma', how='left')

    resumo = _reindex_com_extras(resumo, 'idioma', ORDEM_IDIOMA)

    colunas_numericas = [
        'Total_Respostas', 'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', 'Total_Promotores',
        'Total_Detratores', 'Total_Neutros', 'Total_Alunos', 'Total_Turmas',
    ]
    resumo[colunas_numericas] = resumo[colunas_numericas].fillna(0)

    resumo = calcular_derivados(resumo)
    resumo['Adesão por Idioma'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])

    resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
            'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']] = \
        resumo[['Total_Respostas', 'Total_Turmas', 'Total_Promotores',
                'Total_Detratores', 'Total_Neutros', 'Abertura_Camera']].astype(int)

    relatorio = resumo[[
        'idioma', 'Adesão por Idioma',
        'Total_Turmas', 'Total_Alunos', 'Total_Respostas',
        'Uso_L2', 'Satisfacao_Prof', 'Satisfacao_Aprendizagem',
        'Prof_Incentiva_Camera', 'Abertura_Camera', '(%) Abertura de câmera',
        'Total_Detratores', 'Total_Neutros', 'Total_Promotores', 'NPS Total'
    ]].rename(columns={**RENAME_BASE,
        'idioma': 'Idioma',
    })

    relatorio = _replace_zeros_with_dash(relatorio)

    print(f"\n✅ relatorio_idioma_todos.csv — {len(relatorio)} linhas (todos os idiomas, incl. zerados)")

    return relatorio

def gerar_relatorio_escolas_2026_1(feedback, periodo='2026.2'):

    df = preparar_metricas(feedback)
    df['escola'] = df['escola'].fillna('Escola Não Identificada')
 
    resumo = df.groupby(['escola', 'id_escola']).agg(
        Total_Respostas         = (COL_SATISFACAO,        'count'),
        Total_Alunos            = ('codigo_turma', lambda x: _soma_alunos_unicos(x, df)),
        Total_Turmas            = ('codigo_turma',         'nunique'),
        Uso_L2                  = (COL_PROFESSOR_IDIOMA,   'mean'),
        Satisfacao_Prof         = (COL_SATISFACAO,         'mean'),
        Satisfacao_Aprendizagem = (COL_GRAU,               'mean'),
        Prof_Incentiva_Camera   = (COL_PROFESSOR_CAMERA,   'mean'),
        Abertura_Camera         = (COL_ABRE_CAMERA,        'sum'),
        Total_Promotores        = ('PROMOTOR',              'sum'),
        Total_Detratores        = ('DETRATOR',              'sum'),
        Total_Neutros           = ('NEUTRO',                'sum'),
    ).round(2).reset_index()
 
    resumo = calcular_derivados(resumo)
    resumo['Adesão por escola'] = calcular_adesao(resumo['Total_Respostas'], resumo['Total_Alunos'])
 
    todos = pd.DataFrame([{
        'escola':                  'Todos',
        'Total_Respostas':         df[COL_SATISFACAO].count(),
        'Total_Alunos':            total_alunos(df),
        'Total_Turmas':            df['codigo_turma'].nunique(),
        'Uso_L2':                  round(df[COL_PROFESSOR_IDIOMA].mean(), 2),
        'Satisfacao_Prof':         round(df[COL_SATISFACAO].mean(), 2),
        'Satisfacao_Aprendizagem': round(df[COL_GRAU].mean(), 2),
        'Prof_Incentiva_Camera':   round(df[COL_PROFESSOR_CAMERA].mean(), 2),
        'Abertura_Camera':         df[COL_ABRE_CAMERA].sum(),
        'Total_Promotores':        df['PROMOTOR'].sum(),
        'Total_Detratores':        df['DETRATOR'].sum(),
        'Total_Neutros':           df['NEUTRO'].sum(),
    }])
    todos = calcular_derivados(todos)
    todos['Adesão por escola'] = calcular_adesao(todos['Total_Respostas'], todos['Total_Alunos'])
 
    relatorio = pd.concat([resumo, todos], ignore_index=True)
    relatorio['_ord'] = relatorio['escola'].apply(lambda x: 0 if x == 'Todos' else 1)
    relatorio = relatorio.sort_values(['_ord', 'escola'], ascending=[False, True]).drop(columns='_ord')
 
    relatorio = relatorio.rename(columns={**RENAME_BASE,
        'escola':            'Escola',
        'Adesão por escola': 'Adesão por escola',
    })
 
    relatorio['Período'] = periodo
 
    relatorio = relatorio[[
        'Período', 'Escola', 'Adesão por escola', 'Total de turmas', 'Total de alunos', 'Total de respostas',
        'Uso de L2 [inglês/espanhol] durante as aulas', 'Satisfação com as aulas do prof', 'Satisfação com aprendizagem',
        'Seu professor incentiva abertura da câmera?', 'Abertura de câmera', '(%) Abertura de câmera',
        'DETRATOR', 'NEUTRO', 'PROMOTOR', 'NPS Total'
    ]]
 
    relatorio = _replace_zeros_with_dash(relatorio)
 
    nome_arquivo = f"relatorio_escolas_{periodo.replace('.', '_')}.csv"
    relatorio.to_csv(nome_arquivo, index=False, sep=',', encoding='utf-8-sig')
 
    print(f"\n✅ {nome_arquivo} — {len(relatorio)} linhas (resumo por escola, período {periodo})")
    return relatorio
def parse_data_mista(s):
    txt = s.astype(str).str.strip().str.split(' ').str[0]
    return pd.to_datetime(txt, format='%m/%d/%Y', errors='coerce')
def gerar_todos_relatorios(caminho_avaliacoes):
    global COL_PROFESSOR_IDIOMA, COL_SATISFACAO, COL_GRAU, COL_ABRE_CAMERA
    global COL_PROFESSOR_CAMERA, COL_PROBABILIDADE_RECOMENDAR, COL_COMENTARIO
    global COLUNAS_AGG
    global dados_gigantes, gigantes_validos
    global col_professor_gig, col_escola_gig, col_id_escola_gig
    global col_codigo_turma_gig, col_total_alunos

    feedback = pd.read_csv(
        caminho_avaliacoes,
        sep=',',
        encoding='utf-8'
    )
    base_pesquisa  = pd.read_csv("./files/base_pesquisa.csv",   sep=',', encoding='utf-8')
    dados_gigantes = pd.read_csv("./files/dados_gigantes.csv",  sep=',', encoding='utf-8')

    print("Dados carregados:")
    print(f"  - Feedback:        {len(feedback)} linhas")
    print(f"  - Base Pesquisa:   {len(base_pesquisa)} linhas")
    print(f"  - Dados Gigantes:  {len(dados_gigantes)} linhas")

    feedback       = normalizar_colunas(feedback)
    base_pesquisa  = normalizar_colunas(base_pesquisa)
    dados_gigantes = normalizar_colunas(dados_gigantes)

    col_topico_fb = next(
        (c for c in feedback.columns if 't' in c and 'pico' in c or 'reuni' in c),
        None
    )
    if col_topico_fb is None:
        raise ValueError(f"Coluna de tópico não encontrada. Colunas disponíveis: {list(feedback.columns)}")

    COL_PROFESSOR_IDIOMA         = _encontrar_col(feedback, ['professor', 'idioma']) or COL_PROFESSOR_IDIOMA
    COL_SATISFACAO               = _encontrar_col(feedback, ['satisfa', 'professor']) or COL_SATISFACAO
    COL_GRAU                     = _encontrar_col(feedback, ['grau', 'satisfa']) or COL_GRAU
    COL_ABRE_CAMERA              = _encontrar_col(feedback, ['abre', 'mera']) or COL_ABRE_CAMERA
    COL_PROFESSOR_CAMERA         = _encontrar_col(feedback, ['professor', 'mera']) or COL_PROFESSOR_CAMERA
    COL_PROBABILIDADE_RECOMENDAR = _encontrar_col(feedback, ['probabilidade', 'recomendar']) or COL_PROBABILIDADE_RECOMENDAR
    COL_COMENTARIO               = _encontrar_col(feedback, ['sugest', 'elogios']) or COL_COMENTARIO

    print("\nColunas do formulário detectadas:")
    for nome, val in [
        ('COL_PROFESSOR_IDIOMA', COL_PROFESSOR_IDIOMA),
        ('COL_SATISFACAO', COL_SATISFACAO),
        ('COL_GRAU', COL_GRAU),
        ('COL_ABRE_CAMERA', COL_ABRE_CAMERA),
        ('COL_PROFESSOR_CAMERA', COL_PROFESSOR_CAMERA),
        ('COL_PROBABILIDADE_RECOMENDAR', COL_PROBABILIDADE_RECOMENDAR),
        ('COL_COMENTARIO', COL_COMENTARIO),
    ]:
        status = '✅' if val in feedback.columns else '❌ NÃO ENCONTRADO'
        print(f"  {nome}: {val} {status}")


    COLUNAS_AGG = dict(
        Total_Respostas       = (COL_SATISFACAO,        'count'),
        Uso_L2                = (COL_PROFESSOR_IDIOMA,  'mean'),
        Satisfacao_Prof       = (COL_SATISFACAO,        'mean'),
        Satisfacao_Aprendizagem = (COL_GRAU,            'mean'),
        Prof_Incentiva_Camera = (COL_PROFESSOR_CAMERA,  'mean'),
        Abertura_Camera       = (COL_ABRE_CAMERA,       'sum'),
        Total_Promotores      = ('PROMOTOR',             'sum'),
        Total_Detratores      = ('DETRATOR',             'sum'),
        Total_Neutros         = ('NEUTRO',               'sum'),
    )

    feedback = extrair_partes_topico(feedback, col=col_topico_fb)
    feedback = extrair_nome_professor(feedback)
    feedback['escola']      = pd.NA   # será preenchido abaixo via join com dados_gigantes
    feedback['chave_match'] = feedback['Professor'].apply(chave_nome)

    col_zoom_fb = next(
        (c for c in feedback.columns if ('id_da_reuni' in c or 'webinar' in c) and 'id' in c),
        None
    )
    if col_zoom_fb is None:
        raise ValueError(f"Coluna de Zoom ID não encontrada no feedback. Colunas: {list(feedback.columns)}")
    feedback['zoom_id'] = feedback[col_zoom_fb].astype(str).str.strip()

    print(f"\nColuna Zoom ID no feedback: '{col_zoom_fb}'")

    col_zoom_url = next(
        (c for c in dados_gigantes.columns if 'zoom' in c and ('link' in c or 'sala' in c or 'url' in c)),
        next((c for c in dados_gigantes.columns if 'link' in c), None)
    )
    if col_zoom_url is None:
        raise ValueError(f"Coluna de link Zoom não encontrada no dados_gigantes. Colunas: {list(dados_gigantes.columns)}")

    print(f"Coluna Zoom URL no dados_gigantes: '{col_zoom_url}'")

    dados_gigantes['zoom_id'] = dados_gigantes[col_zoom_url].apply(extrair_zoom_id_da_url)

    original_len_dados_gigantes = len(dados_gigantes)

    # Diagnóstico: mostra colunas que parecem ser de data/fim para ajustar a detecção abaixo
    print("Colunas candidatas a data de fim no dados_gigantes:",
          [c for c in dados_gigantes.columns if 'data' in c or 'fim' in c])

    # OBS: a detecção abaixo exige 'data', 'fim' E 'turma' no nome — nenhuma coluna satisfazia
    # as três condições, por isso o filtro de corte nunca rodava. Ajuste o critério conforme
    # o nome real impresso acima (ex.: 'data' in c and 'fim' in c).
    col_data_fim_gig = next((c for c in dados_gigantes.columns if c.startswith('data') and 'termino' in c), None)
    APLICAR_CORTE = False   # mude para True depois de ver o diagnóstico
    cutoff_date = pd.to_datetime('2026-05-16')
    col_estagio_gig = next(
        (c for c in dados_gigantes.columns if c == 'ESTÁGIO' or c.lower() == 'estágio'),
        None
    )
    if col_estagio_gig:
        print(f"Coluna ESTÁGIO encontrada: '{col_estagio_gig}'")
    else:
        print("⚠️  Coluna ESTÁGIO NÃO encontrada no dados_gigantes. Verifique o nome da coluna.")

    col_nivel_gig = next(
        (c for c in dados_gigantes.columns if c == 'NÍVEL' or c.lower() == 'nível' or c.lower() == 'nivel'),
        None
    )
    if col_nivel_gig:
        print(f"Coluna NÍVEL encontrada: '{col_nivel_gig}'")
    else:
        print("⚠️  Coluna NÍVEL NÃO encontrada no dados_gigantes. Verifique o nome da coluna.")

    col_horario_gig = next(
        (c for c in dados_gigantes.columns if c == 'HORÁRIO' or c.lower() == 'horário' or c.lower() == 'horario'),
        None
    )
    if col_horario_gig:
        print(f"Coluna HORÁRIO encontrada: '{col_horario_gig}'")
    else:
        print("⚠️  Coluna HORÁRIO NÃO encontrada no dados_gigantes. Verifique o nome da coluna.")

    if col_data_fim_gig and col_data_fim_gig in dados_gigantes.columns:
        bruto = dados_gigantes[col_data_fim_gig]
        dados_gigantes[col_data_fim_gig] = parse_data_mista(bruto)
        falhas = bruto.notna() & dados_gigantes[col_data_fim_gig].isna()
        encerradas = dados_gigantes[col_data_fim_gig] < cutoff_date
        ativas = dados_gigantes['escola'] != 'TURMA CANCELADA'

        print(f"\nCorte por '{col_data_fim_gig}' ({cutoff_date.strftime('%d/%m/%Y')}):")
        print(f"  Datas que não consegui ler (mantidas): {falhas.sum()}")
        print(f"  Turmas com término anterior ao corte:  {(encerradas & ativas).sum()}")
        print(f"  Menor / maior data de término:         {dados_gigantes[col_data_fim_gig].min()} / {dados_gigantes[col_data_fim_gig].max()}")

        if APLICAR_CORTE:
            dados_gigantes = dados_gigantes[ativas & ~encerradas].copy()
        else:
            dados_gigantes = dados_gigantes[ativas].copy()
        print(f"Dados gigantes: {len(dados_gigantes)} de {original_len_dados_gigantes} linhas (corte aplicado: {APLICAR_CORTE})")
    else:
        print("⚠️  Coluna de data de término não encontrada. Mantendo filtro apenas por 'TURMA CANCELADA'.")
        dados_gigantes = dados_gigantes[dados_gigantes['escola'] != 'TURMA CANCELADA'].copy()
        print(f"Dados gigantes após remover turmas canceladas: {len(dados_gigantes)} de {original_len_dados_gigantes} linhas")
    col_total_alunos = next(
        (c for c in dados_gigantes.columns if 'total' in c and 'aluno' in c),
        None
    )
    if col_total_alunos is None:
        raise ValueError(f"Coluna 'total de alunos' não encontrada no dados_gigantes. Colunas: {list(dados_gigantes.columns)}")

    col_professor_gig  = next((c for c in dados_gigantes.columns if c == 'professor'), None)
    col_escola_gig     = next(
        (c for c in dados_gigantes.columns if c == 'escola'),
        next((c for c in dados_gigantes.columns if 'escola' in c and 'id' not in c), None)
    )
    col_id_escola_gig  = next((c for c in dados_gigantes.columns if c == 'id_escola' or (c.startswith('id') and 'escola' in c)), None)
    col_codigo_turma_gig = next((c for c in dados_gigantes.columns if 'codigo' in c and 'turma' in c), None)

    print("\nColunas detectadas no dados_gigantes:")
    for nome, val in [
        ('professor', col_professor_gig),
        ('escola', col_escola_gig),
        ('id escola', col_id_escola_gig),
        ('codigo turma', col_codigo_turma_gig),
        ('total alunos', col_total_alunos),
        ('estágio', col_estagio_gig),
        ('nível', col_nivel_gig),
        ('horário', col_horario_gig),
    ]:
        status = '✅' if val else '❌ NÃO ENCONTRADO'
        print(f"  {nome}: {val} {status}")

    gigantes_validos = dados_gigantes[
        dados_gigantes['zoom_id'].notna() &
        dados_gigantes['zoom_id'].astype(str).str.strip().ne('')
    ].copy()

    print(f"\ndados_gigantes com zoom_id válido: {len(gigantes_validos)} de {len(dados_gigantes)}")

    colunas_lookup = ['zoom_id']
    lookup_rename  = {}

    for col_orig, alias in [
        (col_professor_gig,    'professor_gig'),
        (col_escola_gig,       'escola_gig'),
        (col_id_escola_gig,    'id_escola_gig'),
        (col_codigo_turma_gig, 'codigo_turma_gig'),
        (col_total_alunos,     'alunos_por_turma'),
    ]:
        if col_orig and col_orig in gigantes_validos.columns:
            colunas_lookup.append(col_orig)
            lookup_rename[col_orig] = alias

    if col_estagio_gig and col_estagio_gig in gigantes_validos.columns:
        colunas_lookup.append(col_estagio_gig)
        lookup_rename[col_estagio_gig] = 'estagio_gig'
        print(f"✅ Coluna '{col_estagio_gig}' adicionada ao lookup como 'estagio_gig'")
    else:
        print("⚠️  Coluna ESTÁGIO não foi adicionada ao lookup")

    if col_nivel_gig and col_nivel_gig in gigantes_validos.columns:
        colunas_lookup.append(col_nivel_gig)
        lookup_rename[col_nivel_gig] = 'nivel_gig'
        print(f"✅ Coluna '{col_nivel_gig}' adicionada ao lookup como 'nivel_gig'")
    else:
        print("⚠️  Coluna NÍVEL não foi adicionada ao lookup")

    if col_horario_gig and col_horario_gig in gigantes_validos.columns:
        colunas_lookup.append(col_horario_gig)
        lookup_rename[col_horario_gig] = 'horario_gig'
        print(f"✅ Coluna '{col_horario_gig}' adicionada ao lookup como 'horario_gig'")
    else:
        print("⚠️  Coluna HORÁRIO não foi adicionada ao lookup")

    zoom_lookup = (
        gigantes_validos[colunas_lookup]
        .rename(columns=lookup_rename)
        .drop_duplicates(subset=['zoom_id'])
        .reset_index(drop=True)
    )

    print(f"Zoom lookup: {len(zoom_lookup)} entradas únicas")
    print(f"Colunas no zoom_lookup: {list(zoom_lookup.columns)}")
    print()

    feedback = feedback.merge(zoom_lookup, on='zoom_id', how='left')

    if 'codigo_turma_gig' in zoom_lookup.columns:
        lookup_cod = (
            zoom_lookup.dropna(subset=['codigo_turma_gig'])
            .assign(_cod=lambda d: d['codigo_turma_gig'].astype(str).str.strip())
            .drop_duplicates('_cod')
            .set_index('_cod')
        )
    else:
        print("⚠️  codigo_turma_gig ausente no lookup — fallback por código de turma desativado.")
        lookup_cod = pd.DataFrame()
    sem_match = feedback['escola_gig'].isna() if 'escola_gig' in feedback.columns else pd.Series(False, index=feedback.index)
    cod_fb = feedback.loc[sem_match, 'codigo_turma'].astype(str).str.strip()
    for c in ['professor_gig', 'escola_gig', 'id_escola_gig', 'alunos_por_turma',
              'estagio_gig', 'nivel_gig', 'horario_gig']:
        if c in feedback.columns and c in lookup_cod.columns:
            feedback.loc[sem_match, c] = feedback.loc[sem_match, c].fillna(cod_fb.map(lookup_cod[c]))
    print(f"Recuperadas por código de turma: {feedback.loc[sem_match, 'escola_gig'].notna().sum() if 'escola_gig' in feedback.columns else 0} de {sem_match.sum()}")

    if 'professor_gig' in feedback.columns:
        feedback['Professor'] = (
            feedback['professor_gig']
            .fillna(feedback['Professor'])
            .fillna('Professor não identificado')
        )
        feedback['chave_match'] = feedback['Professor'].apply(chave_nome)

    if 'escola_gig' in feedback.columns:
        feedback['escola'] = feedback['escola_gig']

    feedback['analista'] = feedback['escola'].map(MAPA_ESCOLA_ANALISTA).fillna('Não atribuído')

    feedback['id_escola'] = feedback.get('id_escola_gig', '')

    if 'alunos_por_turma' not in feedback.columns:
        feedback['alunos_por_turma'] = 0
    feedback['alunos_por_turma'] = pd.to_numeric(feedback['alunos_por_turma'], errors='coerce').fillna(0)

    if 'codigo_turma_gig' in feedback.columns:
        feedback['codigo_turma_topico'] = feedback['codigo_turma']
        feedback['codigo_turma'] = (
            feedback['codigo_turma_gig'].astype(str).str.strip()
            .where(feedback['codigo_turma_gig'].notna(), feedback['codigo_turma'])
        )
    feedback['escola']    = feedback['escola'].fillna('Escola não identificada')
    feedback['id_escola'] = feedback['id_escola'].fillna('')

    col_zoom_bp = next(
        (c for c in base_pesquisa.columns if ('id_da_reuni' in c or 'webinar' in c) and 'id' in c),
        next((c for c in base_pesquisa.columns if 'id' in c and 'reuni' in c), None)
    )
    col_topico_bp = next(
        (c for c in base_pesquisa.columns if 't' in c and ('pico' in c or 'reuni' in c)),
        None
    )

    if col_zoom_bp:
        base_pesquisa['zoom_id'] = base_pesquisa[col_zoom_bp].astype(str).str.strip()

        if col_topico_bp:
            base_pesquisa = extrair_partes_topico(base_pesquisa, col=col_topico_bp)
            base_pesquisa = extrair_nome_professor(base_pesquisa)
            base_pesquisa['escola'] = pd.NA

        base_pesquisa = base_pesquisa.merge(zoom_lookup, on='zoom_id', how='left')
        if 'codigo_turma_gig' in base_pesquisa.columns and 'codigo_turma' in base_pesquisa.columns:
            base_pesquisa['codigo_turma'] = (
                base_pesquisa['codigo_turma_gig'].astype(str).str.strip()
                .where(base_pesquisa['codigo_turma_gig'].notna(), base_pesquisa['codigo_turma'])
            )
        if 'professor_gig' in base_pesquisa.columns:
            base_pesquisa['Professor'] = (
                base_pesquisa.get('professor_gig', pd.Series(dtype=str))
                .fillna(base_pesquisa.get('Professor', ''))
                .fillna('Professor não identificado')
            )
        if 'escola_gig' in base_pesquisa.columns:
            base_pesquisa['escola'] = base_pesquisa['escola_gig']
        base_pesquisa['analista'] = base_pesquisa['escola'].map(MAPA_ESCOLA_ANALISTA).fillna('Não atribuído')

        base_pesquisa['id_escola'] = base_pesquisa.get('id_escola_gig', '')

        if 'alunos_por_turma' not in base_pesquisa.columns:
            base_pesquisa['alunos_por_turma'] = 0
        base_pesquisa['alunos_por_turma'] = pd.to_numeric(
            base_pesquisa['alunos_por_turma'], errors='coerce'
        ).fillna(0)

        zoom_ids_com_resposta = set(feedback['zoom_id'].dropna().astype(str))
        turmas_sem_resposta = base_pesquisa[
            ~base_pesquisa['zoom_id'].isin(zoom_ids_com_resposta)
        ].copy()

        print(f"\nbase_pesquisa: {len(base_pesquisa)} turmas no total")
        print(f"  Com respostas:  {len(base_pesquisa) - len(turmas_sem_resposta)}")
        print(f"  Sem respostas:  {len(turmas_sem_resposta)}")


        sem_resp_validas = turmas_sem_resposta[
            turmas_sem_resposta['zoom_id'].isin(zoom_lookup['zoom_id'])
        ].drop_duplicates('zoom_id')
        synthetic_feedback = sem_resp_validas.copy()

        turmas_sem_resposta = turmas_sem_resposta.drop_duplicates('zoom_id')

        print(f"  Sem respostas (únicas): {len(turmas_sem_resposta)} | presentes no dados_gigantes: {len(sem_resp_validas)}")

        survey_response_cols = [
            COL_PROFESSOR_IDIOMA,
            COL_SATISFACAO,
            COL_GRAU,
            COL_ABRE_CAMERA,
            COL_PROFESSOR_CAMERA,
            COL_PROBABILIDADE_RECOMENDAR,
            COL_COMENTARIO
        ]
        for col in survey_response_cols:
            if col not in synthetic_feedback.columns:
                synthetic_feedback[col] = np.nan

        all_feedback_cols = list(feedback.columns.union(synthetic_feedback.columns))
        feedback_aligned = feedback.reindex(columns=all_feedback_cols)
        synthetic_feedback_aligned = synthetic_feedback.reindex(columns=all_feedback_cols)

        feedback_for_reports = pd.concat([feedback_aligned, synthetic_feedback_aligned], ignore_index=True)

    else:
        print("⚠️  Coluna de Zoom ID não encontrada na base_pesquisa — turmas com 0 respostas não serão incluídas.")
        turmas_sem_resposta = pd.DataFrame()
        feedback_for_reports = feedback.copy()

    feedback_for_reports['escola']    = feedback_for_reports['escola'].fillna('Escola não identificada')
    feedback_for_reports['id_escola'] = feedback_for_reports['id_escola'].fillna('')

    g = gigantes_validos.rename(columns=lookup_rename).copy()
    if 'codigo_turma_gig' not in g.columns:
        g['codigo_turma_gig'] = np.nan
    tem_codigo = g['codigo_turma_gig'].notna().any()
    g['codigo_turma'] = g['codigo_turma_gig'].astype(str).str.strip()
    cols_g = [c for c in ['zoom_id', 'codigo_turma', 'professor_gig', 'escola_gig', 'id_escola_gig',
                          'alunos_por_turma', 'estagio_gig', 'nivel_gig', 'horario_gig'] if c in g.columns]
    g = g[cols_g]

    ja_turma = set(feedback_for_reports['codigo_turma'].dropna().astype(str))
    if tem_codigo:
        faltantes = g[~g['codigo_turma'].isin(ja_turma)].drop_duplicates('codigo_turma').copy()
    else:
        faltantes = g.iloc[0:0].copy()

    faltantes['Professor']        = faltantes['professor_gig'].fillna('Professor não identificado')
    faltantes['chave_match']      = faltantes['Professor'].apply(chave_nome)
    faltantes['escola']           = faltantes['escola_gig'].fillna('Escola não identificada')
    faltantes['id_escola']        = faltantes['id_escola_gig'].fillna('')
    faltantes['analista']         = faltantes['escola'].map(MAPA_ESCOLA_ANALISTA).fillna('Não atribuído')
    faltantes['alunos_por_turma'] = pd.to_numeric(faltantes['alunos_por_turma'], errors='coerce').fillna(0)

    print(f"Turmas do gigantes adicionadas sem sessão/resposta: {len(faltantes)}")
    feedback_for_reports = pd.concat([feedback_for_reports, faltantes], ignore_index=True)

    print('Re-executing BLOCO 9...')

    sem_escola    = (feedback['escola'] == 'Escola não identificada').sum()
    sem_professor = (feedback['Professor'] == 'Professor não identificado').sum()
    sem_alunos    = (feedback['alunos_por_turma'] == 0).sum()

    zoom_ids_feedback  = set(feedback['zoom_id'].dropna().astype(str))
    zoom_ids_lookup    = set(zoom_lookup['zoom_id'].dropna().astype(str))
    sem_match_no_gig   = zoom_ids_feedback - zoom_ids_lookup

    print("\n✅ Pipeline de join concluído!")
    print(f"   Total de respostas:          {len(feedback)}")
    print(f"   Sem escola após joins:       {sem_escola}")
    print(f"   Professor não identificado:  {sem_professor}")
    print(f"   Sem alunos_por_turma:        {sem_alunos}")
    print(f"   Escolas únicas:              {feedback['escola'].nunique()}")
    print(f"   Professores únicos:          {feedback['chave_match'].nunique()}")
    print(f"   Turmas únicas:               {feedback['codigo_turma'].nunique()}")

    if sem_match_no_gig:
        print(f"\n⚠️  {len(sem_match_no_gig)} zoom_ids do feedback sem match no dados_gigantes:")
        amostra = feedback[feedback['zoom_id'].isin(sem_match_no_gig)][
            ['zoom_id', 'topico', 'escola', 'Professor']
        ].drop_duplicates()
        print(amostra.to_string())
    else:
        print("\n✅ Todos os zoom_ids do feedback encontraram match no dados_gigantes!")

    print(f"Linhas antes da remoção: {len(feedback)}")

    feedback = feedback[~(
        (feedback['escola'] == 'CNA Mococa') &
        (feedback['Professor'] == 'PEDRO MASCARENHAS TOSCANO')
    )]

    print(f"Linhas após a remoção: {len(feedback)}")

    print('Re-executing BLOCO 20...')
    print('Re-executing BLOCO 20 to regenerate reports with updated data...')
    print('Re-executing BLOCO 20 to regenerate reports with updated data and fixes...')

    _dbg = preparar_metricas(feedback_for_reports)
    print("\n--- Totais de referência ---")
    print("Linhas totais:         ", len(_dbg))
    print("Respostas reais:       ", _dbg[COL_SATISFACAO].notna().sum())
    print("Turmas únicas:         ", _dbg['codigo_turma'].nunique())
    print("Alunos (máx por turma):", total_alunos(_dbg))
    _h = _dbg.copy()
    _h['horario'] = _h['horario_gig'].fillna('') if 'horario_gig' in _h.columns else _h['horario'].fillna('')
    _h['intervalo'] = _h['horario'].apply(extrair_intervalo_horario)
    _h['turno'] = _h['horario'].apply(extrair_turno)
    _h['dia'] = _h['horario'].apply(extrair_dia_semana)
    _h['resp'] = _h[COL_SATISFACAO].notna().astype(int)

    _validos = set(ORDEM_HORARIO)
    _h['par_ok'] = [(i, t) in _validos for i, t in zip(_h['intervalo'], _h['turno'])]
    _h['dia_ok'] = _h['dia'].isin(DIAS_NORMALIZADOS)

    _agg = (
        _h.groupby('codigo_turma')
        .agg(escola=('escola', 'first'), alunos=('alunos_por_turma', 'max'),
             respostas=('resp', 'sum'), horario=('horario', 'first'),
             intervalo=('intervalo', 'first'), turno=('turno', 'first'),
             dia=('dia', 'first'), par_ok=('par_ok', 'first'), dia_ok=('dia_ok', 'first'))
        .reset_index()
    )

    print("\n--- DIAGNÓSTICO: turmas fora do relatório de horário ---")
    print(_agg[~_agg['par_ok']].sort_values('alunos', ascending=False).to_string())
    print(f"\nTotal: {(~_agg['par_ok']).sum()} turmas | {_agg.loc[~_agg['par_ok'], 'alunos'].sum()} alunos | {_agg.loc[~_agg['par_ok'], 'respostas'].sum()} respostas")

    print("\n--- DIAGNÓSTICO: turmas fora do relatório de dia da semana ---")
    print(_agg[~_agg['dia_ok']].sort_values('alunos', ascending=False).to_string())

    _z = gigantes_validos.groupby('zoom_id')[col_codigo_turma_gig].nunique()
    print("\n--- DIAGNÓSTICO: zoom_ids com mais de uma turma no gigantes ---")
    print(_z[_z > 1])
    print("\nGerando todos os relatórios...\n")

    relatorio_professor       = gerar_relatorio_professor_completo(feedback_for_reports)
    relatorio_turma           = gerar_relatorio_turma(feedback_for_reports)
    relatorio_idioma          = gerar_relatorio_idioma(feedback_for_reports)
    relatorio_horario         = gerar_relatorio_horario(feedback_for_reports)
    relatorio_dia_semana      = gerar_relatorio_dia_semana(feedback_for_reports)
    relatorio_estagio         = gerar_relatorio_estagio(feedback_for_reports)
    relatorio_escola          = gerar_relatorio_escola(feedback_for_reports)
    relatorio_comentarios     = gerar_relatorio_comentarios(feedback)   # só respostas reais
    relatorio_sem_resposta    = gerar_relatorio_turmas_sem_resposta(turmas_sem_resposta)
    relatorio_faixa_turma = gerar_relatorio_faixa_turma(feedback_for_reports)
    relatorio_dia_semana_todos = gerar_relatorio_dia_semana_todos(feedback_for_reports)
    print("\n--- Amostra Professor ---")
    print("\n--- Amostra Turma ---")
    if 'codigo_turma_gig' in feedback_for_reports.columns:
        _c = feedback_for_reports.dropna(subset=['codigo_turma_gig']).copy()
        _c = _c[_c['codigo_turma'].astype(str).str.strip()
                != _c['codigo_turma_gig'].astype(str).str.strip()]
        print("\n--- DIAGNÓSTICO A: codigo_turma (tópico) ≠ codigo_turma_gig ---")
        print(_c[['zoom_id', 'topico', 'codigo_turma', 'codigo_turma_gig', 'escola']]
              .drop_duplicates().to_string())
        print(f"Total de pares distintos: {_c[['codigo_turma','codigo_turma_gig']].drop_duplicates().shape[0]}")

    print("\n--- DIAGNÓSTICO B: turmas com atributos conflitantes ---")
    for _col in ['horario_gig', 'estagio_gig', 'nivel_gig', 'escola']:
        if _col in _dbg.columns:
            _m = _dbg.groupby('codigo_turma')[_col].nunique(dropna=False)
            print(f"{_col}: {(_m > 1).sum()} turmas com >1 valor")
            if (_m > 1).any():
                print(_dbg[_dbg['codigo_turma'].isin(_m[_m > 1].index)]
                      [['codigo_turma', _col, 'alunos_por_turma']]
                      .drop_duplicates().sort_values('codigo_turma').to_string())
    relatorio_nivel = gerar_relatorio_nivel(feedback_for_reports)
    relatorio_cna_digital_school = gerar_relatorio_cna_digital_school(feedback_for_reports)
    relatorio_nivel_todos_dados = gerar_relatorio_nivel_todos(feedback_for_reports)
    relatorio_idioma_todos = gerar_relatorio_idioma_todos(feedback_for_reports)
    relatorio_estagio_todos = gerar_relatorio_estagio_todos(feedback_for_reports)
    print('Schools with 0 total responses or with "-" in their responses column:')
    relatorio_horario_todos = gerar_relatorio_horario_todos(feedback_for_reports)
    relatorio_escola_2026_1 = gerar_relatorio_escolas_2026_1(feedback_for_reports)
    def _tot(nome, df):
        if df is None or df.empty:
            print(f"{nome:<22} vazio"); return
        d = df[df['Escola'] != 'Todos'] if 'Escola' in df.columns and 'Todos' in df['Escola'].values else df
        turmas = pd.to_numeric(d['Total de turmas'], errors='coerce').sum() if 'Total de turmas' in d.columns else len(d)
        alunos = pd.to_numeric(d['Total de alunos'], errors='coerce').sum() if 'Total de alunos' in d.columns else float('nan')
        resp   = pd.to_numeric(d['Total de respostas'], errors='coerce').sum() if 'Total de respostas' in d.columns else float('nan')
        print(f"{nome:<22} turmas={turmas:>6.0f}  alunos={alunos:>8.0f}  respostas={resp:>6.0f}")

    print("\n===== RESUMO DE FECHAMENTO =====")
    for _n, _d in [
        ('turma (linhas)',       relatorio_turma),
        ('escola',               relatorio_escola),
        ('estagio',              relatorio_estagio),
        ('estagio_todos',        relatorio_estagio_todos),
        ('nivel',                relatorio_nivel),
        ('nivel_todos',          relatorio_nivel_todos_dados),
        ('idioma',               relatorio_idioma),
        ('idioma_todos',         relatorio_idioma_todos),
        ('horario',              relatorio_horario),
        ('horario_todos',        relatorio_horario_todos),
        ('dia_semana',           relatorio_dia_semana),
        ('dia_semana_todos',     relatorio_dia_semana_todos),
        ('faixa_turma',          relatorio_faixa_turma),
    ]:
        _tot(_n, _d)
    return {
        'professor_dados':        relatorio_professor,
        'turma_dados':            relatorio_turma,
        'idioma_dados':           relatorio_idioma,
        'horario_dados':          relatorio_horario,
        'dia_semana_dados':       relatorio_dia_semana,
        'estagio_dados':          relatorio_estagio,
        'escola_dados':           relatorio_escola,
        'comentarios_dados':      relatorio_comentarios,
        'sem_resposta_dados':     relatorio_sem_resposta,
        'nivel_dados':            relatorio_nivel,
        'faixa_turma_dados':      relatorio_faixa_turma,
            'cna_digital_school_dados':   relatorio_cna_digital_school,
        'dia_semana_todos_dados': relatorio_dia_semana_todos,
        'nivel_todos_dados': relatorio_nivel_todos_dados,
        'idioma_todos_dados': relatorio_idioma_todos,
        'estagio_todos_dados': relatorio_estagio_todos,
        'horario_todos_dados': relatorio_horario_todos,
        'escolas_dados_2026.1': relatorio_escola_2026_1

    }


if __name__ == "__main__":
    import sys
    caminho = sys.argv[1] if len(sys.argv) > 1 else "./files/report_survey_-_report_survey_csv.csv"
    relatorios = gerar_todos_relatorios(caminho)