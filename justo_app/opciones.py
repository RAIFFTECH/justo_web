import re

OPC_BOOL = (('S', 'Si'), ('N', 'No'))

OPC_EST_SOCIO = (
    ('A', 'Activo'),
    ('I', 'Ingresó Nuevamente'),
    ('S', 'Suspendido'),
    ('Z', 'Retirado con Crédito'),
    ('R', 'Retirado'),
    ('F', 'Fallecido'),
)

CLASE_COOP = (
    ('AS', 'Asociaciones Mutuales'),
    ('TA', 'Trabajo Asociado'),
    ('EAYC', 'Especializada de Ahorro Y Crédito'),
    ('ESSA', 'Especializada sin Sección de Ahorros'),
    ('FE', 'Fondo de Empleados'),
    ('ISSA', 'Integral Sin Sección de Ahorros'),
    ('MASSA', 'Multi Activa Sin Sección de Ahorros'),
)

OPC_CLASEDOC = (
    ('C', 'Cédula de Ciudadanía'),
    ('T', 'Tarjeta de Identidad'),
    ('N', 'Nit'),
    ('R', 'Registro Civil'),
    ('E', 'Cédula de Extranjería'),
    ('P', 'Pasaporte'),
    ('O', 'Otros'),
)

OPC_CANJE = (
    ('', '---------'),
    ('P', 'Pendiente'),
    ('C', 'Confirmado'),
    ('D', 'Devuelto'),
)


OPC_REGIMEN = (
    ('48', 'Responsable'),
    ('49', 'No Responsable'),
    ('Comun', 'Común'),
)

OPC_TIPTER = (
    ('N', 'Persona Natural'),
    ('J', 'Persona Jurídica'),
    ('O', 'Otro'),
)

OPC_EST_CIV = (
    ('N', 'No Aplica'),
    ('S', 'Soltero(a)'),
    ('C', 'Casado(a)'),
    ('U', 'Unión Libre'),
    ('V', 'Viudo(a)'),
    ('E', 'Separado(a)'),
    ('D', 'Divorciado(a)'),
)

OPC_PRODUCTO = (
    ('AP', 'Aportes'),
    ('AH', 'Ahorros'),
    ('CR', 'Créditos'),
    ('CC', 'Cuenta por Cobrar'),
    ('CP', 'Cuenta por Pagar'),
    ('CO', 'Contable'),
    ('BA', 'Bancos'),
)

OPC_EDUCACION = (
    ('0', 'No Aplica'),
    ('1', 'Primaria'),
    ('2', 'Bachiller'),
    ('3', 'Técnico'),
    ('4', 'Tecnólogo'),
    ('5', 'Profesional'),
    ('6', 'PosGrado'),
    ('7', 'Maestria'),
    ('8', 'Doctorado'),
    ('9', 'Otros'),
)

OPC_PARENTESCO = (
    ('0', 'No Aplica'),
    ('1', 'Esposo(a)'),
    ('2', 'Hijo(a)'),
    ('3', 'Padre o Madre'),
    ('4', 'Abuelo(a)'),
    ('5', 'Nieto(a)'),
    ('6', 'Hermano'),
    ('7', 'Hermana'),
    ('8', 'Primo(a)'),
    ('9', 'Otro Familiar'),
)

OPC_PARENTESCO_PEP = (
    ('0', 'No Aplica'),
    ('1', 'Esposo(a)'),
    ('2', 'Hijo(a)'),
    ('3', 'Padres'),
    ('4', 'Hermano(a)')
)

OPC_VINCULO = (
    ('0', 'No Aplica'),
    ('1', 'Proveedor'),
    ('2', 'Empleado'),
    ('3', 'Asociado')
)
OPC_REFERENCIAS = (
    ('0', 'No Aplica'),
    ('1', 'Familiar'),
    ('2', 'Personal'),
    ('3', 'Bancaria'),
    ('4', 'Comercial'),
    ('5', 'Laboral'),
)

OPC_CANALES = (
    ('EFE', 'Efectivo'),
    ('CHE', 'Cheque'),
    ('CON', 'Consignación'),
    ('TRA', 'Transferencia'),
    ('GIR', 'Giro'),
    ('ATM', 'Red de Cajeros'),
    ('POS', 'Compras en Comercios'),
    ('IVR', 'Audio Respuesta'),
    ('WEB', 'Portal Transaccional'),
    ('MOV', 'Banca Móvil'),
    ('OFI', 'Oficina'),
    ('CNB', 'Corresponsales Bancarios'),
    ('RAL', 'Redes Aliadas'),
    ('N/A', 'No Aplica')
)

OPC_NAT = (
    ('D', 'Débito'),
    ('C', 'Crédito'),
)

OPC_TERMINO = (
    ('D', 'Definido'),
    ('I', 'Indefinido'),
)

OPC_TERMINO_AHO = (
    ('1', 'Cuenta de Ahorro'),
    ('2', 'CDAT'),
    ('3', 'Contractual'),
    ('4', 'Permanente'),
    ('5', 'Ahorro Programado Vivienda'),
)

OPC_PER_LIQ_INT = (
    ('D', 'Diario'),
    ('M', 'Mensual'),
    ('C', 'Cdat'),
    ('V', 'Vencimiento'),
)

OPC_EST_CTA_AHO = (
    ('P', 'Por Aplicar'),
    ('A', 'Activa'),
    ('I', 'Inactiva'),
    ('C', 'Cancelada'),
    ('E', 'Embargada'),
)

OPC_SEXO = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('N', 'No Aplica'),
)

OPC_LIQ_INT_AHO = (
    ('C', 'Causación Final'),
    ('D', 'Causación Diaria'),
    ('M', 'Causación Mensual'),
    ('V', 'Causación Vencimiento'),
    ('P', 'Pago'),
)

OPC_CRE_TERMINO = (
    ('D', 'Definido'),
    ('C', 'Cupo'),
    ('R', 'Rotativo'),
)

OPC_CRE_FOR_PAG = (
    ('P', 'Personal'),
    ('L', 'Libranza'),
    ('T', 'Transferencia'),
)

OPC_CRE_EST_JUR = (
    ('N', 'Normal'),
    ('P', 'Persuasivo'),
    ('J', 'Cobro Jurídico'),
    ('C', 'Condonación'),
    ('T', 'Castigado'),
)

OPC_CAMBIOS_CRE = (
    ('2', 'Ajuste Pag Ant'),
    ('3', 'Ajuste otros'),
    ('4', 'Castigo/Condonación'),
)

OPC_CRE_CATEGORIA = (
    ('A', 'Normal'),
    ('B', 'Apreciable'),
    ('C', 'En Peligro'),
    ('D', 'En Mora'),
    ('E', 'Irrecuperable'),
    ('F', 'Castigado'),
)

OPC_EST_CRE = (
    ('X', 'Por Causar'),
    ('A', 'Activo'),
    ('C', 'Cancelado'),
    ('T', 'Terminado Cupo'),
    ('D', 'Retirado con Deuda'),
)

OPC_MODALIDAD_CRE = (
    ('CCCL', 'Consumo Con Libranza'),
    ('CCSL', 'Consumo Sin Libranza'),
    ('CCPJ', 'Comercial Jurídica'),
    ('CCPN', 'Comercial Natural'),
    ('CMIC', 'MicroCrédito'),
)

OPC_GARANTIA = (
    ('1', 'No Idónea'),
    ('2', 'Hipotecaria'),
    ('15', 'Sin Garantias'),
)

OPC_ESTADO_ANTEIA = (
    ('0', 'No Anteia'),
    ('1', 'Validar'),
    ('2', 'Validado'),
    ('3', 'Denegar')
)

OPC_TIP_CTA = (
    ('C', 'Corriente'),
    ('A', 'Ahorros')
)

OPC_NOV_CTA_AHO = (
    ('A', 'Activada'),
    ('I', 'Inactivada'),
    ('C', 'Cancelada'),
    ('E', 'Embargada'),
    ('S', 'Inrtervenida'),
)

OPC_TIP_MOV_AHO = (
    ('SALINI','Saldo Inicial Justo'),
    ('DEPOSI','Depósito'),
    ('INTCTA','Interés Cuenta'),
    ('INTCDA','Interés Cdat'),
    ('CANJE','Canje por Confirmar'),
    ('CAN_OK','Canje Confirmado'),
    ('RETIRO','Retiro'),
    ('RETFUE','Rete Fuente'),
    ('RF_CDA','Rete Fuente Cdat'),
    ('CH_DEV','Cheque Devuelto')
)

OPC_PRIMA_CREDITO = (
    ('NO','No Tiene Extra prima'),
    ('PR','Prima'),
    ('EP','Extra Prima'),
    ('OP','Otra Prima')
)

OPC_TIP_APO = (
    ('N', 'No Aplica'),
    ('O', 'Ordinarios'),
    ('E', 'Extra Ordinarios'),
    ('R', 'Revalorización'),
    ('V', 'Voluntarios'),
    ('M', 'Aporte Mínimo')    
)

OPC_ZONA = (
    ('U', 'Urbana'),
    ('R', 'Rural')
)

OPC_OCUPACION = (
    ('0', 'No aplica'),
    ('1', 'Empleado'),
    ('2', 'Independiente'),
    ('3', 'Pensionado'),
    ('4', 'Estudiante'),
    ('5', 'Hogar'),
    ('6', 'Cesante'),
    ('7', 'Menor de Edad'),
    ('8', 'Empleado Término Fijo'),
    ('9', 'Empleado Temporal'),
    ('A', 'Entidad Sin Ánimo de Lucro')
)

OPC_ESTRATO = (
    ('N', 'No Aplica'),
    ('1', 'Uno'),
    ('2', 'Dos'),
    ('3', 'Tres'),
    ('4', 'Cuatro'),
    ('5', 'Cinco'),
    ('6', 'Seis')   
)

OPC_VIVIENDA = (
    ('P', 'Propia'),
    ('F', 'Familiar'),
    ('A', 'Arrendada')
)

OPC_ACTIVIDAD_ECON = (
    ('1', 'Intermediacion Financiera'),
    ('2', 'Servicios de Ahorro y Credito'),
    ('3', 'Organismos de Representacion'),
    ('4', 'Agricola'),
    ('5', 'Pecuaria'),
    ('6', 'Silvicultura'),
    ('7', 'Pesca'),
    ('8', 'Mineria'),
    ('9', 'Educacion'),
    ('10', 'Transporte'),
    ('11', 'Vivienda'),
    ('12', 'Consumo (Comercio)'),
    ('13', 'Industria'),
    ('14', 'Servicios Funerarios'),
    ('15', 'Comunicaciones'),
    ('16', 'Obras Publicas'),
    ('17', 'Hoteles Restaurantes Bares'),
    ('18', 'Turismo'),
    ('19', 'Aseo Mantenimiento Reciclaje'),
    ('20', 'Inmobiliarias y de Alquiler'),
    ('21', 'Seguros'),
    ('22', 'Salud'),
    ('23', 'Vigilancia y seguridad'),
    ('24', 'Servicios de Credito'),
    ('99', 'Otras Actividades')
)

OPC_TIPO_PENSION = (
    ('0', 'No Aplica'),
    ('1', 'Vejez'),
    ('2', 'Invalidez'),
    ('3', 'Sobrevivientes'),
    ('4', 'Sustitución'),
    ('5', 'Menores de Edad'),
    ('6', 'Asignación de Retiro')
)

OPC_DANE = (
    ('0', 'Ninguna'),
    ('1', 'Agricultura, ganadería, caza, silvicultura y pesca'),
    ('2', 'Explotación de minas y canteras'),
    ('3', 'Industrias manufactureras'),
    ('4', 'Construcción'),
    ('5', 'Suministro de servicios públicos'),
    ('6', 'Comercio al por mayor y al por menor; Reparación de vehículos; Transporte y almacenamiento; Alojamiento y servicios de comida'),
    ('7', 'Información y comunicaciones'),
    ('8', 'Actividades financieras y de seguros'),
    ('9', 'Actividades inmobiliarias'),
    ('10', 'Actividades profesionales, científicas y técnicas; Actividades de servicios administrativos y de apoyo'),
    ('11', 'Administración pública y defensa; planes de seguridad social; Educación; Actividades de salud humana y servicios sociales'),
    ('12', 'Actividades artísticas, recreación y de servicios; Actividades de los hogares (empleadores); Actividades no diferenciadas de los hogares')
)

OPC_TIPO_SAL = (
    ('0', 'No Aplica'),
    ('1', 'Convencional'),
    ('2', 'Integral'),
    ('3', 'Por Obra'),
    ('4', 'Jornal'),
    ('5', 'Variable'),
    ('6', 'Otros')
)

OPC_TIPO_CONT = (
    ('0', 'No Aplica'),
    ('1', 'No Empleado'),
    ('2', 'Término Indefinido'),
    ('3', 'Término Fijo Mayor a 1 Año'),
    ('4', 'Término Fijo Menor a 1 Año'),
    ('5', 'Culmincación de Obra'),
    ('6', 'Por Cooperativa'),
    ('7', 'Orden de Prestación de Servicios'),
    ('8', 'Otros'),
)

OPC_OCUPACION_CONYUGE = (
    ('0', 'No Aplica'),
    ('1', 'Empleado'),
    ('2', 'Pensionado'),
    ('3', 'Rentista'),
    ('4', 'Trabajador Independiente'),
    ('5', 'Ama de Casa'),
    ('6', 'Independiente Informal'),
    ('7', 'Independiente Formal'),
    ('8', 'Empleado Doméstico'),
    ('9', 'Profesional Independiente'),
    ('10', 'Estudiante'),
    ('11', 'Cesante')
)

OPC_SECTOR_ECONO = (
    ('0', 'No Aplica'),
    ('1', 'Privado'),
    ('2', 'Público'),
    ('3', 'Rentista'),
    ('4', 'Trabajador Independiente'),
    ('5', 'Ama de Casa'),
    ('6', 'Independiente Informal'),
    ('7', 'Independiente Formal'),
    ('8', 'Empleado Doméstico'),
    ('9', 'Profesional Independiente'),
    ('10', 'Estudiante'),
    ('11', 'Cesante')
)

OPC_NACIONALIDAD = (
    ('013', 'AFGANISTAN'),
    ('017', 'ALBANIA'),
    ('023', 'ALEMANIA'),
    ('026', 'ARMENIA'),
    ('027', 'ARUBA'),
    ('029', 'BOSNIA-HERZEGOVINA'),
    ('031', 'BURKINA FASSO'),
    ('037', 'ANDORRA'),
    ('040', 'ANGOLA'),
    ('041', 'ANGUILLA'),
    ('043', 'ANTIGUA Y BARBUDA'),
    ('047', 'ANTILLAS HOLANDESAS'),
    ('053', 'ARABIA SAUDITA'),
    ('059', 'ARGELIA'),
    ('063', 'ARGENTINA'),
    ('069', 'AUSTRALIA'),
    ('072', 'AUSTRIA'),
    ('074', 'AZERBAIJAN'),
    ('077', 'BAHAMAS'),
    ('080', 'BAHREIN'),
    ('081', 'BANGLADESH'),
    ('083', 'BARBADOS'),
    ('087', 'BELGICA'),
    ('088', 'BELICE'),
    ('090', 'BERMUDAS'),
    ('091', 'BELARUS'),
    ('093', 'BIRMANIA (MYANMAR)'),
    ('097', 'BOLIVIA'),
    ('101', 'BOTSWANA'),
    ('105', 'BRASIL'),
    ('108', 'BRUNEI DARUSSALAM'),
    ('111', 'BULGARIA'),
    ('115', 'BURUNDI'),
    ('119', 'EãTAN'),
    ('127', 'CABO VERDE'),
    ('137', 'CAIMAN, ISLAS'),
    ('141', 'CAMBOYA (KAMPUCHEA)'),
    ('145', 'CAMERUN, REPUBLICA UNIDA DEL'),
    ('149', 'CANADA'),
    ('159', 'SANTA SEDE'),
    ('165', 'COCOS (KEELING), ISLAS'),
    ('169', 'COLOMBIA'),
    ('173', 'COMORAS'),
    ('177', 'CONGO'),
    ('183', 'COOK, ISLAS'),
    ('187', 'COREA (NORTE), REPUBLICA POPULAR DEMOCRATICA DE'),
    ('190', 'COREA (SUR), REPUBLICA DE'),
    ('193', 'COSTA DE MARFIL'),
    ('196', 'COSTA RICA'),
    ('198', 'CROACIA'),
    ('199', 'CUBA'),
    ('203', 'CHAD'),
    ('211', 'CHILE'),
    ('215', 'CHINA'),
    ('218', 'TAIWAN (FORMOSA)'),
    ('221', 'CHIPRE'),
    ('229', 'BENIN'),
    ('232', 'DINAMARCA'),
    ('235', 'DOMINICA'),
    ('239', 'ECUADOR'),
    ('240', 'EGIPTO'),
    ('242', 'EL SALVADOR'),
    ('243', 'ERITREA'),
    ('244', 'EMIRATOS ARABES UNIDOS'),
    ('245', 'ESPAÑA'),
    ('246', 'ESLOVAQUIA'),
    ('247', 'ESLOVENIA'),
    ('249', 'ESTADOS UNIDOS'),
    ('251', 'ESTONIA'),
    ('253', 'ETIOPIA'),
    ('259', 'FEROE, ISLAS'),
    ('267', 'FILIPINAS'),
    ('271', 'FINLANDIA'),
    ('275', 'FRANCIA'),
    ('281', 'GABON'),
    ('285', 'GAMBIA'),
    ('287', 'GEORGIA'),
    ('289', 'GHANA'),
    ('293', 'GIBRALTAR'),
    ('297', 'GRANADA'),
    ('301', 'GRECIA'),
    ('305', 'GROENLANDIA'),
    ('309', 'GUADALUPE'),
    ('313', 'GUAM'),
    ('317', 'GUATEMALA'),
    ('325', 'GUAYANA FRANCESA'),
    ('329', 'GUINEA'),
    ('331', 'GUINEA ECUATORIAL'),
    ('334', 'GUINEA-BISSAU'),
    ('337', 'GUYANA'),
    ('341', 'HAITI'),
    ('345', 'HONDURAS'),
    ('351', 'HONG KONG'),
    ('355', 'HUNGRIA'),
    ('361', 'INDIA'),
    ('365', 'INDONESIA'),
    ('369', 'IRAK'),
    ('372', 'IRAN, REPUBLICA ISLAMICA DEL'),
    ('375', 'IRLANDA (EIRE)'),
    ('379', 'ISLANDIA'),
    ('383', 'ISRAEL'),
    ('386', 'ITALIA'),
    ('391', 'JAMAICA'),
    ('399', 'JAPON'),
    ('403', 'JORDANIA'),
    ('406', 'KAZAJSTAN'),
    ('410', 'KENIA'),
    ('411', 'KIRIBATI'),
    ('412', 'KIRGUIZISTAN'),
    ('413', 'KUWAIT'),
    ('420', 'LAOS, REPUBLICA POPULAR DEMOCRATICA DE'),
    ('426', 'LESOTHO'),
    ('429', 'LETONIA'),
    ('431', 'LIBANO'),
    ('434', 'LIBERIA'),
    ('438', 'LIBIA (INCLUYE FEZZAN)'),
    ('440', 'LIECHTENSTEIN'),
    ('443', 'LITUANIA'),
    ('445', 'LUXEMBURGO'),
    ('447', 'MACAO'),
    ('448', 'MACEDONIA'),
    ('450', 'MADAGASCAR'),
    ('455', 'MALAYSIA'),
    ('458', 'MALAWI'),
    ('461', 'MALDIVAS'),
    ('464', 'MALI'),
    ('467', 'MALTA'),
    ('469', 'MARIANAS DEL NORTE, ISLAS'),
    ('472', 'MARSHALL, ISLAS'),
    ('474', 'MARRUECOS'),
    ('477', 'MARTINICA'),
    ('485', 'MAURICIO'),
    ('488', 'MAURITANIA'),
    ('493', 'MEXICO'),
    ('494', 'MICRONESIA, ESTADOS FEDERADOS DE'),
    ('496', 'MOLDAVIA'),
    ('497', 'MONGOLIA'),
    ('498', 'MONACO'),
    ('501', 'MONSERRAT, ISLA'),
    ('505', 'MOZAMBIQUE'),
    ('507', 'NAMIBIA'),
    ('508', 'NAURU'),
    ('511', 'NAVIDAD (CHRISTMAS), ISLAS'),
    ('517', 'NEPAL'),
    ('521', 'NICARAGUA'),
    ('525', 'NIGER'),
    ('528', 'NIGERIA'),
    ('531', 'NIUE, ISLA'),
    ('535', 'NORFOLK, ISLA'),
    ('538', 'NORUEGA'),
    ('542', 'NUEVA CALEDONIA'),
    ('545', 'PAPUASIA NUEVA GUINEA'),
    ('548', 'NUEVA ZELANDIA'),
    ('551', 'VANUATU'),
    ('556', 'OMAN'),
    ('566', 'PACIFICO, ISLAS (USA)'),
    ('573', 'PAISES BAJOS (HOLANDA)'),
    ('576', 'PAKISTAN'),
    ('578', 'PALAU, ISLAS'),
    ('580', 'PANAMA'),
    ('586', 'PARAGUAY'),
    ('589', 'PERU'),
    ('593', 'PITCAIRN, ISLA'),
    ('599', 'POLINESIA FRANCESA'),
    ('603', 'POLONIA'),
    ('607', 'PORTUGAL'),
    ('611', 'PUERTO RICO'),
    ('618', 'QATAR'),
    ('628', 'REINO UNIDO'),
    ('640', 'REPUBLICA CENTROAFRICANA'),
    ('644', 'REPUBLICA CHECA'),
    ('647', 'REPUBLICA DOMINICANA'),
    ('660', 'REUNION'),
    ('665', 'ZIMBABWE'),
    ('670', 'RUMANIA'),
    ('675', 'RUANDA'),
    ('676', 'RUSIA'),
    ('677', 'SALOMON, ISLAS'),
    ('685', 'SAHARA OCCIDENTAL'),
    ('687', 'SAMOA'),
    ('690', 'SAMOA NORTEAMERICANA'),
    ('695', 'SAN CRISTOBAL Y NIEVES'),
    ('697', 'SAN MARINO'),
    ('700', 'SAN PEDRO Y MIGUELON'),
    ('705', 'SAN VICENTE Y LAS GRANADINAS'),
    ('710', 'SANTA ELENA'),
    ('715', 'SANTA LUCIA'),
    ('720', 'SANTO TOME Y PRINCIPE'),
    ('728', 'SENEGAL'),
    ('731', 'SEYCHELLES'),
    ('735', 'SIERRA LEONA'),
    ('741', 'SINGAPUR'),
    ('744', 'SIRIA, REPUBLICA ARABE DE'),
    ('748', 'SOMALIA'),
    ('750', 'SRI LANKA'),
    ('756', 'SUDAFRICA, REPUBLICA DE'),
    ('759', 'SUDAN'),
    ('764', 'SUECIA'),
    ('767', 'SUIZA'),
    ('770', 'SURINAM'),
    ('773', 'SWAZILANDIA'),
    ('774', 'TADJIKISTAN'),
    ('776', 'TAILANDIA'),
    ('780', 'TANZANIA, REPUBLICA UNIDA DE'),
    ('783', 'DJIBOUTI'),
    ('787', 'TERRITORIO BRITANICO DEL OCEANO INDICO'),
    ('788', 'TIMOR DEL ESTE'),
    ('800', 'TOGO'),
    ('805', 'TOKELAU'),
    ('810', 'TONGA'),
    ('815', 'TRINIDAD Y TOBAGO'),
    ('820', 'TUNICIA'),
    ('823', 'TURCAS Y CAICOS, ISLAS'),
    ('825', 'TURKMENISTAN'),
    ('827', 'TURQUIA'),
    ('828', 'TUVALU'),
    ('830', 'UCRANIA'),
    ('833', 'UGANDA'),
    ('845', 'URUGUAY'),
    ('847', 'UZBEKISTAN'),
    ('850', 'VENEZUELA'),
    ('855', 'VIET NAM'),
    ('863', 'VIRGENES, ISLAS (BRITANICAS)'),
    ('866', 'VIRGENES, ISLAS (NORTEAMERICANAS)'),
    ('870', 'FIJI'),
    ('875', 'WALLIS Y FORTUNA, ISLAS'),
    ('880', 'YEMEN'),
    ('885', 'YUGOSLAVIA'),
    ('888', 'ZAIRE'),
    ('890', 'ZAMBIA'),
    ('897', 'ZONA NEUTRAL PALESTINA')
)

OPC_GRUPO_ESPECIAL = (
    ('0', 'No Aplica'),
    ('1', 'Niños, niñas y adolescentes'),
    ('2', 'Mayores de 60 años'),
    ('3', 'Persona con discapacidad física, mental o sensorial'),
    ('4', 'Mujer cabeza de familia'),
    ('5', 'Víctima del conflicto armado'),
    ('6', 'Persona en condición de pobreza extrema'),
    ('7', 'Pueblos indígenas'),
    ('8', 'Población diversa / LGBTIQ+'),
    ('9', 'Población Afrocolombiana')
)

OPC_ASESORIA = (
    ('1', 'Oficina'),
    ('2', 'Externa'),
    ('3', 'Telefónica'),
    ('4', 'Virtual')
)

OPC_TIPO_OPERACION = (
    ('0', 'No Aplica'),
    ('1', 'Envío o recepción de giros y remesas'),
    ('2', 'Exportación'),
    ('3', 'Importación'),
    ('4', 'Inversiones'),
    ('5', 'Préstamos'),
    ('6', 'Pago de servicios'),
)

OPC_PENSION = (
    ('1', 'COLPENSIONES'),
    ('2', 'PROTECCION'),
    ('3', 'PORVENIR'),
    ('4', 'COLFONDOS'),
    ('5', 'CASUR'),
    ('6', 'ESCANDIA'),
    ('7', 'OTRA'),
)

OPC_BANCOS = (
    ('1059', 'BANCAMIA S.A'),
    ('1040', 'BANCO AGRARIO'),
    ('1052', 'BANCO AV VILLAS'),
    ('1805', 'BANCO BTG PACTUAL'),
    ('1032', 'BANCO CAJA SOCIAL BCSC SA'),
    ('1819', 'BANCO CONTACTAR S.A.'),
    ('1066', 'BANCO COOPERATIVO COOPCENTRAL'),
    ('1558', 'BANCO CREDIFINANCIERA SA.'),
    ('1051', 'BANCO DAVIVIENDA SA'),
    ('1001', 'BANCO DE BOGOTA'),
    ('1023', 'BANCO DE OCCIDENTE'),
    ('1062', 'BANCO FALABELLA S.A.'),
    ('1063', 'BANCO FINANDINA S.A.'),
    ('1012', 'BANCO GNB SUDAMERIS'),
    ('1071', 'BANCO J.P. MORGAN COLOMBIA S.A'),
    ('1047', 'BANCO MUNDO MUJER'),
    ('1060', 'BANCO PICHINCHA'),
    ('1002', 'BANCO POPULAR'),
    ('1065', 'BANCO SANTANDER DE NEGOCIOS CO'),
    ('1069', 'BANCO SERFINANZA S.A'),
    ('1303', 'BANCO UNION S.A'),
    ('1053', 'BANCO W S.A'),
    ('1031', 'BANCOLDEX S.A.'),
    ('1007', 'BANCOLOMBIA'),
    ('1061', 'BANCOOMEVA'),
    ('1013', 'BBVA COLOMBIA'),
    ('1808', 'BOLD CF'),
    ('1009', 'CITIBANK'),
    ('1812', 'COINK'),
    ('1370', 'COLTEFINANCIERA S.A'),
    ('1292', 'CONFIAR COOPERATIVA FINANCIERA'),
    ('1283', 'COOPERATIVA FINANCIERA DE ANTI'),
    ('1289', 'COOTRAFA COOPERATIVA FINANCIER'),
    ('1117', 'CREDIFAMILIA'),
    ('1816', 'CREZCAMOS S.A.'),
    ('1019', 'DAVIbank S.A.'),
    ('1802', 'DING TECNIPAGOS SA'),
    ('1121', 'FINANCIERA JURISCOOP S.A. COMP'),
    ('1814', 'GLOBAL66'),
    ('1637', 'IRIS'),
    ('1014', 'ITAU'),
    ('1006', 'ITAU antes Corpbanca'),
    ('1286', 'JFK COOPERATIVA FINANCIERA'),
    ('1807', 'KOA C.F'),
    ('1070', 'LULO BANK S.A.'),
    ('1067', 'MIBANCO S.A.'),
    ('1507', 'NEQUI'),
    ('1809', 'NU'),
    ('1560', 'PIBANK'),
    ('1803', 'POWWI'),
    ('1811', 'RAPPIPAY'),
    ('1804', 'Ualá'),
)

OPC_UNIDAD_MEDIDA = (
    ('HORA', 'HORA'),
    ('KG', 'KG'),
)