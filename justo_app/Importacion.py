import sys, fdb, csv, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Justo_proy.settings')
django.setup()
from django.shortcuts import render
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from django.db.models.query import QuerySet
from django.db.models import Q, F, Sum, Case, When, Value, FloatField, CharField, IntegerField
from django.db.models.functions import Coalesce
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP

from clientes_app.models import CLIENTES, XMOV_CRE
from terceros_app.models import TERCEROS
from oficinas_app.models import OFICINAS
from asociados_app.models import ASOCIADOS, ASO_BENEF, ASO_REFERENCIAS
from cuentas_app.models import PLAN_CTAS
from ciiu_app.models import CIIU
from localidades_app.models import LOCALIDADES
from conceptos_app.models import CONCEPTOS
from documentos_app.models import DOCTO_CONTA, XDOC_ZEP
from hecho_economico_app.models import HECHO_ECONO
from detalle_economico_app.models import DETALLE_ECONO
from detalle_producto_app.models import DETALLE_PROD
from ctas_ahorros_app.models import CTAS_AHORRO,CANJE_AHORROS
from centrocostos_app.models import CENTROCOSTOS
from contabilizacion_lineas_ahorros_app.models import IMP_CON_LIN_AHO
from contabilizacion_capital_creditos_app.models import IMP_CON_CRE,MODALIDADES
from contabilizacion_intereses_creditos_app.models import IMP_CON_CRE_INT
from lineas_ahorro_app.models import LINEAS_AHORRO
from lineas_credito_app.models import LINEAS_CREDITO
from tasas_lin_aho_app.models import TAS_LIN_AHO
from retefuente_ahorros_app.models import RET_FUE_AHO
from liquidacion_cdat_app.models import CTA_CDAT_LIQ
from cdat_app.models import CTA_CDAT
from ampliacion_cdat_app.models import CTA_CDAT_AMP
from destino_credito_app.models import DESTINO_CRE
from causacion_creditos_app.models import CREDITOS_CAUSA
from recla_carte_app.models import PE_MODE_REFE,PE_CALIF_RANGO,PE_PDI_RANGO,PE_PI_CALIF,CARTE_CAT_HIS
from aportes_app.models import PLAN_APORTES
from categorias_creditos_app.models import CAT_DES_DIA_CRE
from creditos_app.models import CREDITOS, CODEUDORES, GAR_NO_IDONEA
from cambios_creditos_app.models import CAMBIOS_CRE
#from usuarios_app.models import USUARIOS
from movimiento_caja_app.models import MOV_CAJA
from estados_financieros_app.models import ESTADOS_FIN
from cierre_mensual_app.models import CIERRE_MES
from pagadores_app.models import PAGADORES
from cxc_app.models import CTAS_X_COBRAR,CXC_DET
from recla_carte_app.models import CARTERA_CXC
from activos_fijos_app.models import ACTIVOS_FIJOS
#from recla_carte_app.models import CARTE_CAT_HIS,CARTERA_CXC,CATE_INTE,PE_CALIF_RANGO,PE_PI_CALIF,PE_CARTE_HIS,PE_MODE_REFE,PE_PDI_RANGO
from ctas_ahorros_app.models import TEMPO_AHO

def gomonth(fecha, meses):
    return fecha + relativedelta(months=meses)

def asignar_fecha(fecha_str, formato='%m/%d/%Y'):
    try:
        fecha = datetime.strptime(fecha_str, formato)
        fecha_validada = fecha.strftime('%Y-%m-%d')
        return fecha_validada
    except ValueError:
        return None

def inicio():           # inicio()  # 1. Esto es primero
    print('Inicial  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    if Cliente == None:
        Cliente = CLIENTES.objects.create(codigo = 'A')
    Cliente.doc_ide = '892000914'
    Cliente.sigla = 'COORINOQUIA'
    Cliente.nombre = 'COOPERATIVA ESPECIALIZADA DE AHORRO Y CREDITO DE LA ORINOQUIA'
    Cliente.celular = '3153275734'
    Cliente.email = 'COORINOQUIA@HOTMAIL.COM'
    Cliente.dv = "3"   
    Cliente.clase_coop = 'EAYC'
    Cliente.direccion = 'CR 33A 39 38 BRR CENTRO'
    Cliente.telefono = 6086628885
    Cliente.ciudad = 'Villavicencio'   
    Cliente.nit_ger = 40395800
    Cliente.nom_ger = 'Rubiela Pérez Castañeda'
    Cliente.nit_con = 17221322
    Cliente.nom_con = 'Wilmer Leandro Triana Bustos'
    Cliente.tp_con = '122271-T'
    Cliente.nit_rev_fis = '5944379'
    Cliente.nom_rev_fis = 'Jesús Alfredo Lombana' 
    Cliente.tp_rev_fis = '12245165'
    Cliente.age_ret = 'N'
    Cliente.ret_iva = 'N'
    Cliente.aut_ret = 'N'
    Cliente.logo = ''
    Cliente.num_lic = '001'
    Cliente.lic_act = 'S'
    # Cliente.ini_lic = "2024-01-01"
    # Cliente.fin_lic = "2024-12-31"-
    
    Cliente.save()
    Oficina = OFICINAS.objects.filter(cliente = Cliente,codigo='A0001').first()
    if Oficina == None:
        Oficina=OFICINAS.objects.create(cliente = Cliente,codigo = "A0001",
        contabiliza = 'S',
        nombre_oficina = 'Principal',
        responsable = 'Rubiela Pérez Castañeda',
        celular = '3125683606',
    )
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    if CentroCosto==None:
        CentroCosto = CENTROCOSTOS.objects.create(oficina=Oficina,codigo = 'A001')

#    with open('c:/ajusto/csv/localidades.csv', 'r', encoding='utf-8-sig') as file:
#        csv_reader = csv.DictReader(file, delimiter=',')
#        for row in csv_reader:
#            Localidad = LOCALIDADES.objects.filter(cliente=Cliente, codigo=row['CODIGO']).first()
#            if Localidad is None:
#                Localidad = LOCALIDADES.objects.create(cliente=Cliente,codigo=row['CODIGO'])
#            Localidad.nombre = row['NOMBRE']
#            Localidad.cod_pos = row['CODPOS']
#            Localidad.departamento = row['DPTO']
#            Localidad.save()
    
    with open('c:/ajusto/csv/c00documentos.csv', 'r',encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            DocZep = XDOC_ZEP.objects.filter(per_con=int(row['c00agno']),clase_zep=row['c00clase']).first()
            if DocZep == None:
                DocZep = XDOC_ZEP.objects.create(per_con=int(row['c00agno']),clase_zep=row['c00clase'])
            DocZep.doc_ds = int(row['c00docds'])    #  OJOOOOOO  ESTA ES LA CORRECTA
            DocZep.nombre =row['c00nombre']
            DocZep.descripcion =row['c00descripcion']
            DocZep.save()
    print('         ',datetime.now())


#print(row)  # Ver cada fila
    #with open("export_utf8.csv", "w", encoding="utf-8", newline='') as f:
    #    writer = csv.writer(f)
    #    writer.writerow([desc[0] for desc in cur.description])  # nombres de columnas
    #    for row in cur:
    #        writer.writerow(row)
    #return
    #with open('c:/ajusto/csv/terceros.csv', 'r',encoding='utf-8-sig') as file:
    #    csv_reader = csv.DictReader(file,delimiter=';')
    #    for row in csv_reader:


def terceros():         # terceros()  # 2
    print('Terceros....  ',datetime.now())
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='WIN1252'
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar

    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM terceros")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))
            Tercero = TERCEROS.objects.filter(cliente=Cliente,
            cla_doc = row['LL_TIP_DOC'][0],
            doc_ide = row['NIT']).first()
            if Tercero == None:
                Tercero = TERCEROS.objects.create(
                    cliente = Cliente,
                    cla_doc = row['LL_TIP_DOC'][0],
                    doc_ide = row['NIT'],
                    cod_ciu_exp = LOCALIDADES.objects.filter(cliente=Cliente,codigo=row['CO_CIU_RES']).first()

                )
            Tercero.dig_ver = row['DV']
            Tercero.nit_rap = row['NIT_RAP']
            Tercero.cod_ciu_exp = LOCALIDADES.objects.filter(cliente=Cliente,
                        codigo=row['CO_CIU_EXP']).first()
            Tercero.cod_ciu_res = LOCALIDADES.objects.filter(cliente=Cliente,
                        codigo=row['CO_CIU_RES']).first()
            Tercero.regimen = row['LL_REGIMEN']
            Tercero.fec_exp_ced = row['FEC_EXP_CED']
            Tercero.tip_ter = row['LL_TIP_TER']
            Tercero.pri_ape = row['PRI_APE'][:10]
            Tercero.seg_ape = row['SEG_APE'][:10]
            Tercero.pri_nom = row['PRI_NOM'][:10]
            Tercero.seg_nom  = row['SEG_NOM'][:10]
            Tercero.raz_soc  = row['RAZ_SOC']
            Tercero.direccion = row['DIRECCION']
            Tercero.cod_pos = row['CO_CODPOS']
            Tercero.tel_ofi  = row['TEL_OFI'][:10]
            Tercero.tel_res = row['TEL_RES'][:10]
            Tercero.celular1 = row['CELULAR1'][:10]
            Tercero.celular2 = row['CELULAR2'][:10]
            Tercero.fax = row['FAX']
            Tercero.email = row['EMAIL']
            #   fec_act = datetime.strptime("1900-01-1", "%Y-%m-%d")
            #   asignar_fecha(anteia1['flows'][idsocio]['form.date'])
            Tercero.observacion = row['OBSERVACION']
            Tercero.per_pub_exp = row['PER_PUB_EXP']
            Tercero.nit_interno = row['NIT_INTERNO']
            Tercero.id_ds = row['ID']
            Tercero.save()
    cur.close()
    conn.close()
    print('Fin Terceros  ',datetime.now())

def pagadores():        # pagadores() # 3.
    print('Pagadores..  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s07entidades1.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')    
        for row in csv_reader:
            codent = row['s07codent'].strip()

            if codent == '999':
                codigo_final = '00000'
            elif codent == '41':
                codigo_final = '00082'
            else:
                codigo_final = f'00{codent}'
                
            pagador = PAGADORES.objects.filter(cliente=Cliente, codigo=codigo_final).first()
            if pagador == None:
                pagador=PAGADORES.objects.create(cliente = Cliente, codigo = codigo_final)
            pagador.nombre = row['s07nombre']
            pagador.ciudad = LOCALIDADES.objects.filter(cliente=Cliente, nombre=row['s07ciudad']).first()
            pagador.pagador = row['s07nompag']
            pagador.tel_cel = row['s07telpag']
            pagador.nit = row['s07nit']
            pagador.save()
    print('Fin pagadores ',datetime.now())

def plan_ctas():        # plan_ctas() # 4.
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='latin1' 
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar

    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM CUENTAS WHERE PER_CON > 2014 and tip_con = 1")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        try:
        # Intenta obtener todas las filas
            rows = cur.fetchall()
        except Exception as e:
            print("Error al obtener las filas:", e)
        finally:
            # Cierra la conexión
            cur.close()
            conn.close()
        # Convertir cada fila en un diccionario
        #for row in rows:
        #    row_dict = dict(zip(columns, row))
    else:
        print("No se pudo obtener la descripción de las columnas. Puede que la consulta no haya retornado resultados.")
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))
            PlanCta = PLAN_CTAS.objects.filter(cliente=Cliente,per_con=row['PER_CON'],
                cod_cta=row['COD_CTA']).first()
            if PlanCta == None:
                PlanCta = PLAN_CTAS.objects.create(cliente=Cliente,per_con=row['PER_CON'],
            cod_cta=row['COD_CTA'])
            PlanCta.nom_cta = row['NOMBRE'][:64]
            PlanCta.tip_cta = row['TIP_CTA']
            PlanCta.dinamica = row['DINAMICA']
            PlanCta.naturaleza = row['NATURALEZA']
            PlanCta.activa = row['ACTIVA']
            PlanCta.por_tercero  = row['POR_TER']
            PlanCta.cta_act_fij  = row['CTA_ACT_FIJ']
            PlanCta.cta_pre  = row['CTA_PRE']
            PlanCta.cta_bal  = row['CTA_BAL']
            PlanCta.cta_res = row['CTA_RES']
            PlanCta.cta_ord = row['CTA_ORD']
            PlanCta.cta_ban  = row['CTA_BAN']
            PlanCta.cta_gan_per = row['CTA_GANPER']
            PlanCta.cta_per_gan = row['CTA_PERGAN']  
            PlanCta.cta_dep  = row['CTA_DEP']
            PlanCta.cta_ing_ret = row['CTA_INGRET']
            PlanCta.cta_ret_iva  = row['CTA_RETIVA']
            PlanCta.cta_rec  = row['CTA_REC']
            PlanCta.id_ds  = row['ID']
            PlanCta.save()
    cur.close()
    conn.close()
    print('Fin Cuentas ',datetime.now())
    
def ciiu():        # ciiu()) # 5.
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='latin1' 
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar

    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM CIIU")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        try:
        # Intenta obtener todas las filas
            rows = cur.fetchall()
        except Exception as e:
            print("Error al obtener las filas:", e)
        finally:
            # Cierra la conexión
            cur.close()
            conn.close()
        # Convertir cada fila en un diccionario
        #for row in rows:
        #    row_dict = dict(zip(columns, row))
    else:
        print("No se pudo obtener la descripción de las columnas. Puede que la consulta no haya retornado resultados.")
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))
            ciiu = CIIU.objects.filter(cliente=Cliente, codigo=row['CODIGO']).first()
            if ciiu == None:
                ciiu = CIIU.objects.create(cliente=Cliente)
            ciiu.codigo = row['CODIGO']
            ciiu.actividad = row['ACTIVIDAD']
            ciiu.save()
    cur.close()
    conn.close()
    print('Fin CIIU ',datetime.now())

def conceptos():        # conceptos() # 5.
    print('Conceptos Justo ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    with open('c:/ajusto/csv/c02concepto.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')  
        for row in csv_reader:
            Concepto = CONCEPTOS.objects.filter(cliente=Cliente,cod_con=row['c02codcon']).first()
            if Concepto == None:
                Concepto = CONCEPTOS.objects.create(cliente=Cliente,cod_con=row['c02codcon'])
            Concepto.con_justo = 'S' if row['c02noborra']=='T' else 'N'
            Concepto.descripcion = row['c02descripcion']
            Concepto.tip_dev_ap = 'N' if row['c02tipdevapo'] else (row['c02tipdevapo'] if len(row['c02tipdevapo']) == 1 else ('N'))       
            Concepto.tip_con = 'S' if row['c02tipcon']=='T' else 'N'
            Concepto.tip_sis = row['c02tipsis']
            Concepto.cta_con = row['c02ctacon']
            Concepto.cta_con_pas = row['c02ctapas']
            Concepto.debito = 'S' if row['c02debito'] == 'T' else 'N'
            Concepto.credito = 'S' if row['c02credito'] == 'T' else 'N'
            Concepto.por_tercero =  'S' if row['c02conporter'] == 'T' else 'N'
            Concepto.por_ret_fue =  row['c02por_ret']
            Concepto.save()
    print('Fin Conceptos    ',datetime.now())    

def docto_conta():    # docto_conta() # 6.
    print('Documentos  ',datetime.now())
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='latin1' 
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar
    cur = conn.cursor()
    try:
        cur.execute("select * from documentos where per_con > 2014")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        try:
            rows = cur.fetchall()
        except Exception as e:
            print("Error al obtener las filas:", e)
        finally:
            cur.close()
            conn.close()
    else:
        print("No se pudo obtener la descripción de las columnas. Puede que la consulta no haya retornado resultados.")
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    Oficina = OFICINAS.objects.filter(cliente = Cliente,codigo='A0001').first()
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))
            DoctoConta = DOCTO_CONTA.objects.filter(oficina=Oficina,per_con=int(float(row['PER_CON'])),
                codigo=int(float(row['COD_DOC']))).first()
            if DoctoConta == None:
                DoctoConta = DOCTO_CONTA.objects.create(oficina=Oficina,per_con=int(float(row['PER_CON'])),
                    codigo=int(float(row['COD_DOC'])))
            DoctoConta.nom_cto = row['NOM_CTO']
            DoctoConta.nombre = row['NOMBRE']
            DoctoConta.doc_admin = row['DOC_ADM']
            DoctoConta.doc_caja = row['DE_CAJA']
            DoctoConta.inicio_nuevo_per = row['INI_NUE_VIG']
            valor = row['CONSECUTIVO']  # Elimina espacios en blanco
            if valor is None:
                DoctoConta.consecutivo = 0
            else:
                DoctoConta.consecutivo = valor
            DoctoConta.id_ds = row['ID']
            xinv = 'S'
            xinv = 'N' if int(float(row['COD_DOC'])) in (126,127,130) else xinv
            DoctoConta.num_automatico = xinv
            DoctoConta.save()

    print('Fin Documentos ',datetime.now())

def linaho():       #linaho() # 7.    
    print('Lineas Ahorros  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s04linaho.csv', 'r',encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            LinAho = LINEAS_AHORRO.objects.filter(cliente = Cliente,
                cod_lin_aho = row['s04tipcta']).first()
            if LinAho == None:
                LinAho = LINEAS_AHORRO.objects.create(cliente = Cliente,
                cod_lin_aho = row['s04tipcta'])
            LinAho.nombre = row['s04nombre']    
            LinAho.termino = row['s04termino']
            LinAho.per_liq_int = row['s04perliqint']
            LinAho.cta_por_pas = row['s04ctaporpag']
            LinAho.fec_ult_liq_int =  asignar_fecha(row['s04fecultliqint'],'%m/%d/%Y')
            LinAho.saldo_minimo = row['s04monminliqint']
            LinAho.save()
    print('Fin Lin Ahorros ',datetime.now())

def destino_cre():       #destino_cre () # 8. 
    print('des Creditos   ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s17descre.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            DesCre = DESTINO_CRE.objects.filter(cliente=Cliente,codigo = ord(row['s17coddescre'])).first()
            if DesCre == None:
                DesCre = DESTINO_CRE.objects.create(cliente=Cliente,codigo = ord(row['s17coddescre']))
            DesCre.descripcion = row['s17descripcion']
            DesCre.save()
    print('Fin des Creditos   ',datetime.now())    

def lineas_credito():       # lineas_credito() # 9.
    print('Lineas Credito   ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s14lincre.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            LinCre = LINEAS_CREDITO.objects.filter(cliente=Cliente,cod_lin_cre = ord(row['s14codlincre'])).first()
            if LinCre == None:
                LinCre = LINEAS_CREDITO.objects.create(cliente=Cliente,cod_lin_cre = ord(row['s14codlincre']))
            LinCre.descripcion = row['s14descripcion']
            LinCre.tas_int_anu = row['s14tasintanu']
            LinCre.tas_int_mor = row['s14tasintmor']
            LinCre.por_pol = row['s14porpol']
            LinCre.por_des_pp = row['s14pordespropag']
            LinCre.dia_con_int_mor = row['s14diaconintmor']
            LinCre.save()
    print('Fin Lineas Credito   ',datetime.now()) 

def cat_des_dia_cre():       # cat_des_dia_cre() # 10.  falta el codigo   69
    print('des Dia Creditos   ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s19catdescre.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            CatDesDiaCre = CAT_DES_DIA_CRE.objects.filter(cliente=Cliente,codigo = ord(row['s19coddescre']),categoria = row['s19codcat']).first()
            if CatDesDiaCre == None:
                CatDesDiaCre = CAT_DES_DIA_CRE.objects.create(cliente=Cliente,codigo = ord(row['s19coddescre']),categoria = row['s19codcat'])
            CatDesDiaCre.minimo_dias = row['s19diamin']
            CatDesDiaCre.maximo_dias = row['s19diamax']
            CatDesDiaCre.save()
    print('Fin ... ',datetime.now())    

def ret_fue_aho():           # ret_fue_aho() # 11.
    print('ret_fue_aho  ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s11parretfue.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            LinAho = LINEAS_AHORRO.objects.filter(cliente=Cliente,cod_lin_aho=row['s11tipcta']).first()
            if LinAho == None:
                continue
            RetFueAho = RET_FUE_AHO.objects.filter(lin_aho=LinAho,
                    fecha_inicial=asignar_fecha(row['s11fecini'],'%m/%d/%Y')).first()
            if RetFueAho == None:
                RetFueAho = RET_FUE_AHO.objects.create(lin_aho=LinAho,
                    fecha_inicial=asignar_fecha(row['s11fecini'],'%m/%d/%Y'))
            RetFueAho.fecha_final = asignar_fecha(row['s11fecfin'],'%m/%d/%Y')
            RetFueAho.bas_liq_int = row['s11basliqdia'] 
            RetFueAho.tas_liq_rf = row['s11tasintretfue']
            RetFueAho.save()
    print('Fin...',datetime.now())    

def int_lin_aho():          # int_lin_aho() # 12.
    print('int_lin_aho  ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s08intlinaho.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            LinAho = LINEAS_AHORRO.objects.filter(cliente=Cliente,cod_lin_aho=row['s08tipcta']).first()
            if LinAho == None:
                continue
            TasLinAho = TAS_LIN_AHO.objects.filter(lin_aho=LinAho,
                    fecha_inicial=asignar_fecha(row['s08fecini'],'%m/%d/%Y')).first()
            if TasLinAho == None:
                TasLinAho = TAS_LIN_AHO.objects.create(lin_aho=LinAho,
                    fecha_inicial=asignar_fecha(row['s08fecini'],'%m/%d/%Y'),tiae=0)
            TasLinAho.fecha_final = asignar_fecha(row['s08fecfin'],'%m/%d/%Y')
            TasLinAho.tiae = row['s08tasintanu']
            TasLinAho.save()
    print('Fin ...',datetime.now())    

def imp_con_lin_aho():      # imp_con_lin_aho() # 13.
    print('Imp Lin Aho     ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/S22IMPCONLINAHO.CSV', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            LinAho = LINEAS_AHORRO.objects.filter(cliente=Cliente,cod_lin_aho=row['s22tipcta']).first()
            if LinAho == None:
                continue
            Impconlinaho = IMP_CON_LIN_AHO.objects.filter(linea_ahorro=LinAho,cod_imp = row['s22codimp']).first()
            if Impconlinaho == None:
                Impconlinaho = IMP_CON_LIN_AHO.objects.create(linea_ahorro=LinAho,cod_imp = row['s22codimp'])
            Impconlinaho.descripcion = row['s22descripcion']
            Impconlinaho.ctaafeact = row['s22ctaafecap'] 
            Impconlinaho.ctaafeina = row['s22ctaafeina']
            Impconlinaho.ctaafeint = row['s22ctaafeint']
            Impconlinaho.ctaretfue = row['s22ctaaferetfue']
            Impconlinaho.save()
    print('Fin Imp Lin Aho ',datetime.now())        

def imp_con_cre():           # imp_con_cre() # 14.
    print('Imp Creditos   ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    # IMP_CON_CRE.objects.all().delete()
    with open('c:/ajusto/csv/s16impconcre.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            ImpConCre = IMP_CON_CRE.objects.filter(cliente=Cliente,cod_imp = row['s16codimp']).first()
            if ImpConCre == None:
                ImpConCre = IMP_CON_CRE.objects.create(cliente=Cliente,cod_imp = row['s16codimp'])
            xcod_mod = ' '
            if row['s16codmod'] == 'V':
                xcod_mod = 'V'
            elif row['s16codmod'] == 'D':
                if row['s16forpag'] == 'P':
                    xcod_mod = 'S'
                else:
                    xcod_mod = 'L'
            elif row['s16codmod'] == 'C':
                xcod_mod = 'C'
            elif row['s16codmod'] == 'M':
                xcod_mod = 'M'
            ImpConCre.cod_mod = xcod_mod    
            ImpConCre.descripcion = row['s16descripcion']
            ImpConCre.kpte_cap = '14433501'
            ImpConCre.kpte_ic = '14433001'
            ImpConCre.kdet_gen_adi = row['s16ctaprogenadi'] 
            ImpConCre.kdet_gen = row['s16ctaprogen']
            ImpConCre.kdet_gen_gas = row['s16ctagasprogen']
            ImpConCre.kdet_gen_rec = row['s16ctarecprogen']
            ImpConCre.kdet_ind_gas = row['s16ctagasproind']
            ImpConCre.kdet_ind_rec = row['s16ctarecproind']
            ImpConCre.kdpp_ic = ''
            ImpConCre.save()
            
    MODALIDADES.objects.all().delete()
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'V',num_rango = 1,categoria = 'A',cod_cta = '840505' ,max_dias = 60)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'V',num_rango = 2,categoria = 'B',cod_cta = '840510' ,max_dias = 150)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'V',num_rango = 3,categoria = 'C',cod_cta = '840515' ,max_dias = 360)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'V',num_rango = 4,categoria = 'D',cod_cta = '840520' ,max_dias = 540)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'V',num_rango = 5,categoria = 'E',cod_cta = '840525' ,max_dias = 9999)

    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'M',num_rango = 1,categoria = 'A',cod_cta = '842005' ,max_dias = 30)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'M',num_rango = 2,categoria = 'B',cod_cta = '842010' ,max_dias = 60)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'M',num_rango = 3,categoria = 'C',cod_cta = '842015' ,max_dias = 90)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'M',num_rango = 4,categoria = 'D',cod_cta = '842020' ,max_dias = 120)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'M',num_rango = 5,categoria = 'E',cod_cta = '842025' ,max_dias = 9999)

    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'L',num_rango = 1,categoria = 'A',cod_cta = '841005' ,max_dias = 30)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'L',num_rango = 2,categoria = 'B',cod_cta = '841010' ,max_dias = 60)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'L',num_rango = 3,categoria = 'C',cod_cta = '841015' ,max_dias = 90)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'L',num_rango = 4,categoria = 'D',cod_cta = '841020' ,max_dias = 180)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'L',num_rango = 5,categoria = 'E',cod_cta = '841025' ,max_dias = 9999)

    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'S',num_rango = 1,categoria = 'A',cod_cta = '841505' ,max_dias = 30)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'S',num_rango = 2,categoria = 'B',cod_cta = '841510' ,max_dias = 60)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'S',num_rango = 3,categoria = 'C',cod_cta = '841515' ,max_dias = 90)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'S',num_rango = 4,categoria = 'D',cod_cta = '841520' ,max_dias = 180)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'S',num_rango = 5,categoria = 'E',cod_cta = '841525' ,max_dias = 9999)

    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'C',num_rango = 1,categoria = 'A',cod_cta = '842505' ,max_dias = 30)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'C',num_rango = 2,categoria = 'B',cod_cta = '842510' ,max_dias = 90)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'C',num_rango = 3,categoria = 'C',cod_cta = '842515' ,max_dias = 120)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'C',num_rango = 4,categoria = 'D',cod_cta = '842520' ,max_dias = 150)
    MODALIDADES.objects.create(cliente = Cliente,cod_mod = 'C',num_rango = 5,categoria = 'E',cod_cta = '842525' ,max_dias = 9999)
    print('Fin ... ',datetime.now())

def imp_con_cre_int():           # imp_con_cre_int() # 15.
    print('Imp Int Creditos',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s18impconcrecapcat.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            ImpConCreInt = IMP_CON_CRE_INT.objects.filter(cliente=Cliente,cod_imp = row['s18codimp'],categoria = row['s18codcat']).first()
            if ImpConCreInt == None:
                ImpConCreInt = IMP_CON_CRE_INT.objects.create(cliente=Cliente,cod_imp = row['s18codimp'],categoria = row['s18codcat'])
            ImpConCreInt.kcta_con = row['s18ctacon']
            ImpConCreInt.kcta_pro_ind = row['s18ctapro']
            ImpConCreInt.cta_pro_ind_cap = row['s18ctapro']
            ImpConCreInt.kporcentaje = row['s18porpro']
            ImpConCreInt.save()
    print('   Continua  ',datetime.now())    
    with open('c:/ajusto/csv/s34asicatint.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            if row['s34cuenta'] not in ["Ingreso","CtaPte","CxP","Error","IngRec","OrdenI"]:
                if row['s34cuenta'] == 'OrdenC':
                    xCat = 'C'
                elif row['s34cuenta'] == 'OrdenD':
                    xCat = 'D'
                elif row['s34cuenta'] == 'OrdenE':
                    xCat = 'E'
                elif row['s34cuenta'] == 'OrdenF':
                    xCat = 'F'
                else:
                    xCat = row['s34cat']
                ImpConCreInt = IMP_CON_CRE_INT.objects.filter(cliente=Cliente,cod_imp = row['s34codimpcon'],categoria = xCat).first()
                if ImpConCreInt == None:
                    ImpConCreInt = IMP_CON_CRE_INT.objects.create(cliente=Cliente,cod_imp = row['s34codimpcon'],categoria = xCat)
                if row['s34cuenta'][:3] == 'CxC':
                    ImpConCreInt.cta_pro_ind_int = row['s34ctaali']    
                    ImpConCreInt.cta_int = row['s34codcta']
                else: 
                    ImpConCreInt.cta_ord_int = row['s34codcta']
                ImpConCreInt.save()
            else:
                ImpConCre = IMP_CON_CRE.objects.filter(cliente=Cliente,cod_imp = row['s34codimpcon']).first()
                if ImpConCre == None:
                    ImpConCre = IMP_CON_CRE.objects.create(cliente=Cliente,cod_imp = row['s34codimpcon'])
                if row['s34cuenta'] == 'CtaPte':
                    ImpConCre.kpte_ic = row['s34codcta']
                elif row['s34cuenta'] == 'Ingreso':
                    ImpConCre.kcta_ingreso = row['s34codcta']
                elif row['s34cuenta'] == 'CxP':
                    ImpConCre.kic_cxp = row['s34codcta']
                elif row['s34cuenta'] == 'OrdenI':
                    ImpConCre.kic_orden_i = row['s34codcta']
                elif row['s34cuenta'] == 'IngRec':
                    ImpConCre.kic_rec_int = row['s34codcta']
                elif row['s34cuenta'] == 'Error':
                    ImpConCre.cta_val = row['s34codcta']
                ImpConCre.save()
    print('Fin ... ',datetime.now())

def usuarios():          # usuarios() # 16.    Pendiente
    print('usuarios  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    Oficina = OFICINAS.objects.filter(cliente = Cliente,codigo='A0001').first()
    with open('c:/ajusto/csv/c06cajeros.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=',')  
        for row in csv_reader:
            Usuario = USUARIOS.objects.filter(oficina=Oficina,login = row['c06usuario']).first()
            if Usuario == None:
                Usuario = USUARIOS.objects.create(oficina=Oficina,login = row['c06usuario'])
            
    #         CAJEROS(models.Model):
    # user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name='Usuario')
    # oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    # tercero = models.ForeignKey(TERCEROS, on_delete=models.SET_NULL, null=True, verbose_name='Tercero')
    # fecha_ingreso = models.DateField(null=True, blank=False,verbose_name = 'Fecha Ingreso Cajero')
    # fecha_retiro = models.DateField(null=True, blank=True,verbose_name = 'Fecha Retiro Cajero')
    # activo = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Está Activo?')
    # cta_con_caja = models.CharField(max_length=10,null=False, blank=False,verbose_name = 'Cta Contable caja')
    # cta_con_acre 
            
            Usuario.nit = ''
            Usuario.nombre = ''
            Usuario.fec_ing = asignar_fecha('01/01/1900','%M-%D-%Y')
            Usuario.es_cajero = 'S'
            Usuario.cod_caj = row['c06codcaj']
            Usuario.fec_sal = asignar_fecha('01/01/1900','%M-%D-%Y')
            Usuario.cta_con_acr = row['c06ctacon']
            Usuario.activo = 'S'
            Usuario.save()
    print('Fin Usuarios ',datetime.now())

def cierre_mes():            # cierre_mes() # 17.   Volver a Importar
    print('cierres  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    Oficina = OFICINAS.objects.filter(cliente = Cliente,codigo='A0001').first()
    with open('c:/ajusto/csv/g10cierres.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')  
        for row in csv_reader:
            CierreMes = CIERRE_MES.objects.filter(oficina=Oficina,fecha = asignar_fecha(row['g10feccie'],'%M-%D-%Y')).first()
            if CierreMes == None:
                CierreMes = CIERRE_MES.objects.create(oficina=Oficina,fecha = asignar_fecha(row['g10feccie'],'%M-%D-%Y'))
            CierreMes.protegido = row['g10protegido']
            CierreMes.tot_deb = row['g10debitos']
            CierreMes.tot_cre = row['g10creditos']
            CierreMes.fec_cie = asignar_fecha(row['g10feccie'],'%M-%D-%Y')
            CierreMes.usuario = row['g10usuario']
            CierreMes.save()
    print('Fin Cierres ',datetime.now())

def mov_caja():         # mov_caja() # 18.  penDiEnte
    print('Mov Caja   ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    Oficina = OFICINAS.objects.filter(cliente = Cliente,codigo='A0001').first()
    with open('c:/ajusto/csv/c07movcaja.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')  
        for row in csv_reader:
            MovCaja = MOV_CAJA.objects.filter(oficina=Oficina,cod_caj=row['c07codcaj'],
                    fecha=asignar_fecha(row['c07fecha'],'%M-%D-%Y'),jornada=row['c07jornada']).first()
            if MovCaja == None:
                MovCaja = MOV_CAJA.objects.create(oficina=Oficina,cod_caj=row['c07codcaj'],
                    fecha=asignar_fecha(row['c07fecha'],'%M-%D-%Y'),jornada=row['c07jornada'])
                MovCaja.saldo_ini = row['c07salant']
                MovCaja.debitos = row['c07salant']
                MovCaja.creditos = row['c07salant']
                MovCaja.val_che_dev = row['c07chedev']
                MovCaja.saldo_fin =row['c07salfin']
                MovCaja.diferencia = row['c07difer']
                MovCaja.val_cheques = row['c07cheques']
                MovCaja.val_vales = row['c07vales']
                MovCaja.cerrado = 'S'
                MovCaja.monedas = row['c07moneda'].replace(';', ',')
                MovCaja.save()
    print('Fin Mov Caja ',datetime.now())

def plan_aportes():          # plan_aportes() # 19.
    print('plan aportes     ',datetime.now())
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/S00APORTACION.CSV', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            PlanApor = PLAN_APORTES.objects.filter(
                    oficina = Oficina,
                    agno = int(row['agno'])).first()
            if PlanApor == None:
                PlanApor = PLAN_APORTES.objects.create(
                    oficina = Oficina,
                    agno = int(row['agno'])
                    )
            PlanApor.meses = row['meses']
            PlanApor.iniadu = row['s00iniadu']
            PlanApor.totadu = row['s00totadu']
            PlanApor.inichi1 = row['s00inichi1']
            PlanApor.totchi1 = row['s00totchi1']
            PlanApor.inichi2 = row['s00inichi2']
            PlanApor.totchi2 = row['s00totchi2']
            PlanApor.inijur = row['s00inijur']
            PlanApor.totjur = row['s00totjur']
            if int(row['agno']) == 1980:
                PlanApor.sal_min = 4500
            elif int(row['agno']) == 1981:
                PlanApor.sal_min = 5700
            elif int(row['agno']) == 1982:
                PlanApor.sal_min = 7410
            elif int(row['agno']) == 1983:
                PlanApor.sal_min = 9261
            elif int(row['agno']) == 1984:
                PlanApor.sal_min = 11298
            elif int(row['agno']) == 1985:
                PlanApor.sal_min = 13558
            elif int(row['agno']) == 1986:
                PlanApor.sal_min = 16811
            elif int(row['agno']) == 1987:
                PlanApor.sal_min = 20510
            elif int(row['agno']) == 1988:
                PlanApor.sal_min = 25637
            elif int(row['agno']) == 1989:
                PlanApor.sal_min = 32560
            elif int(row['agno']) == 1990:
                PlanApor.sal_min = 41025
            elif int(row['agno']) == 1991:
                PlanApor.sal_min = 51720
            elif int(row['agno']) == 1992:
                PlanApor.sal_min = 65190
            elif int(row['agno']) == 1993:
                PlanApor.sal_min = 81510
            elif int(row['agno']) == 1994:
                PlanApor.sal_min = 98700
            elif int(row['agno']) == 1995:
                PlanApor.sal_min = 118934
            elif int(row['agno']) == 1996:
                PlanApor.sal_min = 142125
            elif int(row['agno']) == 1997:
                PlanApor.sal_min = 172005
            elif int(row['agno']) == 1998:
                PlanApor.sal_min = 203826
            elif int(row['agno']) == 1999:
                PlanApor.sal_min = 236460
            elif int(row['agno']) == 2000:
                PlanApor.sal_min = 260100
            elif int(row['agno']) == 2001:
                PlanApor.sal_min = 286000
            elif int(row['agno']) == 2002:
                PlanApor.sal_min = 309000
            elif int(row['agno']) == 2003:
                PlanApor.sal_min = 332000
            elif int(row['agno']) == 2004:
                PlanApor.sal_min = 358000
            elif int(row['agno']) == 2005:
                PlanApor.sal_min = 381500
            elif int(row['agno']) == 2006:
                PlanApor.sal_min = 408000
            elif int(row['agno']) == 2007:
                PlanApor.sal_min = 433700
            elif int(row['agno']) == 2008:
                PlanApor.sal_min = 461500
            elif int(row['agno']) == 2009:
                PlanApor.sal_min = 496900
            elif int(row['agno']) == 2010:
                PlanApor.sal_min = 515000
            elif int(row['agno']) == 2011:
                PlanApor.sal_min = 535600
            elif int(row['agno']) == 2012:
                PlanApor.sal_min = 566700
            elif int(row['agno']) == 2013:
                PlanApor.sal_min = 589500
            elif int(row['agno']) == 2014:
                PlanApor.sal_min = 616000
            elif int(row['agno']) == 2015:
                PlanApor.sal_min = 644350
            elif int(row['agno']) == 2016:
                PlanApor.sal_min = 689455
            elif int(row['agno']) == 2017:
                PlanApor.sal_min = 737717
            elif int(row['agno']) == 2018:
                PlanApor.sal_min = 781242
            elif int(row['agno']) == 2019:
                PlanApor.sal_min = 828116
            elif int(row['agno']) == 2020:
                PlanApor.sal_min = 877803
            elif int(row['agno']) == 2021:
                PlanApor.sal_min = 908526
            elif int(row['agno']) == 2022:
                PlanApor.sal_min = 1000000
            elif int(row['agno']) == 2023:
                PlanApor.sal_min = 1160000
            elif int(row['agno']) == 2024:
                PlanApor.sal_min = 1300000
            elif int(row['agno']) == 2025:
                PlanApor.sal_min = 1423500
            PlanApor.save()
        
    print('Fin Plan Aportes ',datetime.now())

def socios():            # socios() # 20.
    print('Socios....  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s01socios.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            Tercero = TERCEROS.objects.filter(cliente=Cliente,doc_ide = row['s01nit']).first()
            if Tercero == None:
                #print('No Hay Tercero ',row['s01nit'])
                continue
            Socio = ASOCIADOS.objects.filter(oficina=Oficina,cod_aso = row['s01codsoc']).first()
            if Socio == None:
                Socio = ASOCIADOS.objects.create(oficina = Oficina,cod_aso = row['s01codsoc']) 
            codent =  row['s01codent'].strip()
            if  codent == '999':
                codigo_final = '00000'
            elif codent == '41':
                codigo_final = '00082'
            else:
                codigo_final = f'00{codent}'
               
            pagador = PAGADORES.objects.filter(cliente=Cliente,codigo=codigo_final).first()
            Socio.tercero = Tercero
            Socio.sexo = row['s01sexo'][:1]
            Socio.est_civ = row['s01estciv']
            Socio.fec_nac = asignar_fecha(row['s01fecnac'])
            # Socio.ciu_res = ''
            zona = row['s01rural']
            if zona == '1':
                Socio.zona = 'R'
            else:
                Socio.zona = 'U'
            
            Socio.profesion = row['s01profesi']
            Socio.ocupacion = row['s01ocupacion']
            Socio.ocupacion_cod = ''
            Socio.estrato = row['s01estrato']
            Socio.niv_est  = row['s01nivest'][:1]
            Socio.cab_fam = row['s01mujcabfam']
            Socio.id_pag = pagador
            Socio.fec_afi = asignar_fecha(row['s01fecingc'])
            Socio.fec_ret = asignar_fecha(row['s01fecretc'])
            Socio.estado = row['s01estado'][:1]
            Socio.cargo_emp = row['s01cargo']
            Socio.per_a_cargo = row['s01peracar']
            Socio.num_hij_men = 0
            Socio.num_hij_may = row['s01peracar']
            Socio.tip_viv = ''
            Socio.tie_en_ciu = '' 
            Socio.med_con = ''
            Socio.fec_ing_tra = asignar_fecha(row['s01fecinge'])
            Socio.tel_tra = ''
            Socio.tip_sal= ''
            Socio.ciu_tra = LOCALIDADES.objects.filter(cliente=Cliente,codigo=row['s01codmun']).first()
            Socio.act_eco = row['s01sececo']
            #Socio.cod_ciiu = ''
            Socio.tip_con = ''
            Socio.nom_emp = ''
            Socio.nit_emp = ''
            Socio.dir_emp = ''
            Socio.email_emp = ''
            Socio.sector_emp = ''
            Socio.empresa_ant = ''
            Socio.emp_num_emp = ''
            Socio.negocio_pro = ''
            Socio.negocio_nom = ''
            Socio.negocio_tel = ''
            Socio.negocio_loc_pro = '' 
            Socio.negocio_cam_com = ''
            Socio.negocio_ant = ''
            Socio.pension_ent = ''
            Socio.pension_tie = ''
            Socio.pension_otr = ''
            Socio.pension_ent_otr = '' 
            Socio.pep_es_fam = ''
            Socio.pep_fam_par = ''
            Socio.pep_fam_nom = ''
            Socio.pep_car_pub = ''
            Socio.pep_cargo = ''
            Socio.pep_eje_pod = '' 
            Socio.pep_adm_rec_est = '' 
            Socio.tie_gre_car = ''
            Socio.recibe_pag_ext = '' 
            Socio.recide_ext_mas_186 = '' 
            Socio.recibe_ing_ext = ''
            Socio.estado_anteia = ''
            Socio.save()
    print('Fin socios  ',datetime.now())

def ctas_aho():         # ctas_aho() # 21.  
    print('Ctas Aho     ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/S05CTAAHO.CSV', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            Socio = ASOCIADOS.objects.filter(
                oficina = Oficina,cod_aso = row['s05codsoc']).first()
            if Socio == None:
                continue
            LinAho = LINEAS_AHORRO.objects.filter(cliente = Cliente,cod_lin_aho = row['s05tipcta']).first()
            if LinAho == None:
                continue
            CtaAho = CTAS_AHORRO.objects.filter(
                oficina = Oficina,num_cta = row['s05numcta']).first()
            if CtaAho == None:
                CtaAho = CTAS_AHORRO.objects.create(
                        oficina = Oficina,num_cta = row['s05numcta'],lin_aho = LinAho,asociado = Socio)
            CtaAho.est_cta = row['s05estado']
            CtaAho.cod_imp = row['s05codimpcon']
            CtaAho.fec_apertura = asignar_fecha(row['s05fecape'],'%m/%d/%Y')
            CtaAho.fec_cancela = asignar_fecha('01/01/1900','%m/%d/%Y')
            CtaAho.exc_tas_mil = row['s05exegmf']
            CtaAho.fec_ini_exc = asignar_fecha(row['s05feciniexc'],'%m/%d/%Y')
            CtaAho.cod_imp = row['s05codimpcon']
            CtaAho.save()
    print('Fin ctas aho  ',datetime.now())    

def cta_cdat():           # cta_cdat() # 22.
    print('CDAT    ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s20cdat.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            CtaAho = CTAS_AHORRO.objects.filter(
                oficina = Oficina,num_cta = row['s20numcta']).first()
            if CtaAho == None:
                continue
            CtaCdat = CTA_CDAT.objects.filter(cta_aho = CtaAho,ampliacion=row['s20ampliacion']).first()
            if CtaCdat == None:
                CtaCdat = CTA_CDAT.objects.create(cta_aho = CtaAho,ampliacion=row['s20ampliacion']) 
            CtaCdat.valor = row['s20monto']
            CtaCdat.fecha = asignar_fecha(row['s20fecha'],'%m/%d/%Y')
            CtaCdat.plazo_mes = row['s20plazomes']
            CtaCdat.tiae = row['s20tasintanuefe']
            CtaCdat.Periodicidad = row['s20periodicidad']
            CtaCdat.cta_int_ret = row['s20ctaafeint']
            CtaCdat.aplicado = 'S' if row['s20aplicado'] == 'T' else ' '
            CtaCdat.save()
    print('Fin CDAT ',datetime.now())    

def cta_cdat_amp():         # cta_cdat_amp() # 23.
    print('CDAT AMP  ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s21liqintcda.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            CtaAho = CTAS_AHORRO.objects.filter(
                oficina = Oficina,num_cta = row['s21numcta']).first()
            if CtaAho == None:
                continue
            CtaCda = CTA_CDAT.objects.filter(cta_aho = CtaAho,ampliacion=row['s21ampliacion']).first()
            if CtaCda == None:
                CtaCda = CTA_CDAT.objects.create(cta_aho = CtaAho,ampliacion=row['s21ampliacion']) 
            if CtaCda == None:
                continue
            CtaCdaAmp = CTA_CDAT_AMP.objects.filter(cta_aho = CtaAho,cta_amp = CtaCda,fecha = asignar_fecha(row['s21fecha'],'%m/%d/%Y')).first()
            if CtaCdaAmp == None:
                CtaCdaAmp = CTA_CDAT_AMP.objects.create(cta_aho = CtaAho,cta_amp = CtaCda,fecha = asignar_fecha(row['s21fecha'],'%m/%d/%Y'))
            CtaCdaAmp.num_liq = row['s21numliqint']
            CtaCdaAmp.valor = row['s21valor']
            CtaCdaAmp.cta_aho_afe = row['s21ctaafe']
            CtaCdaAmp.clase = row['s21clase']
            CtaCdaAmp.documento = row['s21documento']
            CtaCdaAmp.aplicado = row['s21aplicado'][:1]
            CtaCdaAmp.save()
            CtaCda.aplicado = CtaCdaAmp.aplicado
            CtaCda.save()

    print('Fin Amp Cdat ',datetime.now())    

def cta_cda_liq():           # cta_cda_liq() # 24.
    print('CDAT liq   ',datetime.now())    
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s39histcdat.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader: 
            CtaAho = CTAS_AHORRO.objects.filter(
                oficina = Oficina,num_cta = row['s39numcta']).first()
            if CtaAho == None:
                continue
            CtaCda = CTA_CDAT.objects.filter(cta_aho = CtaAho,ampliacion=row['s39ampliacion']).first()
            if CtaCda == None:
                continue
            CtaCdatAmp = CTA_CDAT_AMP.objects.filter(cta_aho = CtaAho,cta_amp =CtaCda).first()
            if CtaCdatAmp == None:
                continue 
            CtaCdatLiq = CTA_CDAT_LIQ.objects.filter(cta_aho = CtaAho,cta_amp = CtaCdatAmp,
                fecha = asignar_fecha(row['s39fecha'],'%m/%d/%Y'),tip_liq = row['s39tipo']).first()
            if CtaCdatLiq == None:
                CtaCdatLiq = CTA_CDAT_LIQ.objects.create(cta_aho = CtaAho,cta_amp = CtaCdatAmp,
                    fecha = asignar_fecha(row['s39fecha'],'%m/%d/%Y'),tip_liq = row['s39tipo'])
            CtaCdatLiq.val_int = row['s39interes']
            CtaCdatLiq.val_ret = row['s39retfue']
            CtaCdatLiq.val_ret_nue = row['s39retfuenue']
            CtaCdatLiq.aplicado = row['s39aplicado']
            CtaCdatLiq.save()
    print('Fin Cdat Liq ',datetime.now())    

def creditos():         # creditos() # 25.      #  10 Min
    print('Creditos....1  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    
    with open('c:/ajusto/csv/s12creditos.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            Socio = ASOCIADOS.objects.filter(oficina=Oficina,cod_aso=row['s12codsoc']).first()
            if Socio == None:
                #print('Socio con Docto ',row['s12codsoc'], ' No existe con el credito ',row['s12codcre'])
                continue
            Credito = CREDITOS.objects.filter(oficina=Oficina,cod_cre=row['s12codcre']).first()
            if Credito == None:
                Credito = CREDITOS.objects.create(oficina=Oficina,cod_cre=row['s12codcre'],socio=Socio)
            ImpConCre = IMP_CON_CRE.objects.filter(cliente = Cliente,cod_imp = row['s12codimpcon']).first()
            if ImpConCre == None:
                ImpConCre = IMP_CON_CRE.objects.create(cliente = Cliente,cod_imp = row['s12codimpcon'])
            Credito.imputacion = ImpConCre
            linea_credito = LINEAS_CREDITO.objects.filter(cliente = Cliente,cod_lin_cre=ord(row['s12codlincre'])).first()
            Credito.cod_lin_cre = linea_credito
            Credito.cap_ini = row['s12capini'] 
            Credito.cod_des = row['s12coddescre']
            Credito.libranza = row['s12libranza']
            Credito.pagare = row['s12pagare']
            Credito.termino = row['s12termino']
            Credito.for_pag = row['s12forpag']
            Credito.fec_des = asignar_fecha(row['s12fecdes'],'%m/%d/%Y')
            Credito.fec_pag_ini = asignar_fecha(row['s12fecpagini'],'%m/%d/%Y')
            Credito.fec_ree = asignar_fecha('01/01/1900','%m/%d/%Y')
            fecha_date = datetime.strptime(Credito.fec_pag_ini, "%Y-%m-%d").date()

            Credito.num_cuo_ini = row['s12numcuo']
            Credito.fec_ven = fecha_date     + relativedelta(months=int(Credito.num_cuo_ini)-1)
            Credito.fec_ult_pag = asignar_fecha(row['s12fecultpag'],'%m/%d/%Y')
            Credito.val_cuo_ini = row['s12valcuo']
            Credito.val_cuo_act = row['s12valcuo']
            # Credito.num_cuo_ini = row['s12numcuo']
            Credito.num_cuo_act = row['s12numcuo']
            Credito.num_cuo_gra = 0
            Credito.per_ano = row['s12perano']
            Credito.tiae_ic_ini = row['s12tasintanuini']
            Credito.tiae_ic_act = row['s12tasintanu']
            Credito.tian_ic_act = row['s12tasintanu']
            Credito.tian_im = row['s12tasintmor']
            Credito.tian_pol_seg = row['s12porpol']
            Credito.por_des_pro_pag = 0
            Credito.decreciente = 'N'
            Credito.cat_eva = row['s12catevacar']
            Credito.rep_cen_rie = 'S' if row['s12repcenrie'] == 'T' else 'N'
            #if row['s12repcenrie'] == 'F': 
            #    print('Credito.rep_cen_rie ',Credito.rep_cen_rie,'   ',row['s12repcenrie'])
            Credito.not_mor = 'S' if row['s12notmor']  == 'T' else 'N'
            Credito.fec_not_mor = asignar_fecha(row['s12fecnotmor'],'%m/%d/%Y')
            est_cre = row['s12estjur'].strip()
            if est_cre == 'X':
                Credito.estado = 'X'
            elif est_cre == 'C':
                Credito.estado = 'C'
            else:
                Credito.estado = 'A' 
            
            valor = row['s12estjur'].strip()
            if valor in ['J', 'E']:
                Credito.est_jur = 'J'
            elif valor in ['K', 'R']:
                Credito.est_jur = 'T'
            elif valor == 'P':
                Credito.est_jur = 'C'
            elif valor == 'p':
                Credito.est_jur = 'P'
            else:
                Credito.est_jur = 'N'
                
            # Credito.est_jur = row['s12estjur'].strip()
            Credito.cat_nue = row['s12nvocat'].strip()
            # Credito.rep_cen_rie = row['s12repcenrie'][:0]
            Credito.val_gar_hip = row['s12valcomgarhip']
            Credito.mat_inm_gar = row['s12matinmgarhip']
            Credito.num_pol_gar_hip = row['s12numpolgh']
            Credito.figarantias = row['s12figrantias'][:0]

#   creditos.com_des  ojo A PARTIR DE S12CLASE Y S12DOCUMENTO  PARA LA SIGUIENTE MIGRACION
        
            Credito.save()
    with open('c:/ajusto/csv/s10codeudor.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            Credito = CREDITOS.objects.filter(oficina=Oficina,cod_cre=row['s10codcre']).first()
            if Credito != None:
                if Credito.socio.tercero.doc_ide == row['s10nit']:
                    continue 
                Credito.tip_gar = '15'
                if Credito.val_gar_hip != 0:
                    Credito.tip_gar = '2 '
                else:
                    Credito.tip_gar = '1 '
                Credito.save()
                GarNoIdo = GAR_NO_IDONEA.objects.filter(oficina = Oficina,credito = Credito,doc_ide = row['s10nit']).first()
                if GarNoIdo == None:
                    GarNoIdo = GAR_NO_IDONEA.objects.create(oficina = Oficina,credito = Credito,doc_ide = row['s10nit'])
                    GarNoIdo.tipo = 'C' 
                    GarNoIdo.save()
    creeli = CREDITOS.objects.filter(oficina=Oficina,cod_cre = '118140').first()
    creeli.estado = 'H'
    creeli.save()
    creeli = CREDITOS.objects.filter(oficina=Oficina,cod_cre = '120890').first()
    creeli.estado = 'H'
    creeli.save()
    print('Fin Creditos ',datetime.now())

#s24salcap,s24salcapdia,
#s24salintdia,s24intcauresmes,s24categoria,s24arrastre,s24aporte,s24proindkap,s24proindint,s24saldo1,s24saldo2,
#s24valgarhip,s24validado,s24catint,s24salcatint,s24casti,s24gasproind,s24gasprogen,s24salintali,salintcorpe,salintcontin,z,puntaje,tip_gar,
#cat_mod,cat_ree,cat_eva,cat_sel,categoria,apl_pe,pi,pdi,vea,pe,conta_ali,ali_acu,gas_ind_acu
def categorizacion():           # categorizacion() # 30.
    print('Grabar Categorizaciones  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    # reg_inicio = 379997
    with open('c:/ajusto/csv/s24catecred.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file, delimiter=',')
        for index, row in enumerate(csv_reader, start=1):
            Credito = CREDITOS.objects.filter(oficina = Oficina,cod_cre = row['s24codcre']).first()
            if Credito == None:
                continue
            CreCarHis = CARTE_CAT_HIS.objects.filter(oficina = Oficina,fecha = asignar_fecha(row['s24fecha']),cod_cre = row['s24codcre']).first()
            if CreCarHis == None:
                CreCarHis = CARTE_CAT_HIS.objects.create(oficina = Oficina,fecha = asignar_fecha(row['s24fecha']),cod_cre = row['s24codcre'])
            CreCarHis.credito = Credito
            CreCarHis.nit = row['s24nit']
            CreCarHis.cod_lin_cre = row['s24codlincre']
            CreCarHis.cod_imp_con = row['s24codimpcon']
            CreCarHis.for_pag = row['s24forpag']
            CreCarHis.plazo = row['s24plazo']
            CreCarHis.dias_mor = row['s24diamor']
            CreCarHis.cap_ini = row['s24capini']
            CreCarHis.cla_gar = row['tip_gar']
            CreCarHis.sal_cap_pe = row['s24salcap']
            CreCarHis.sal_cap_dia = row['s24salcapdia']
            CreCarHis.sal_int_dia = row['s24salintdia']
            CreCarHis.int_cau_res_per = row['s24intcauresmes']
            CreCarHis.cat_mor = row['s24categoria']
            CreCarHis.cat_arr = row['s24arrastre']
            CreCarHis.aporte = row['s24aporte']
            CreCarHis.pro_ind_kap = row['s24proindkap']
            CreCarHis.pro_ind_int = row['s24proindint']
            CreCarHis.saldo_1 = row['s24saldo1']
            CreCarHis.saldo_2 = row['s24saldo2']
            CreCarHis.val_gar_hip = row['s24valgarhip']
            CreCarHis.cat_int_mes = row['s24catint']
            CreCarHis.sal_cat_int = row['s24salcatint']
            CreCarHis.categoria = row['categoria']
            CreCarHis.castigo = row['s24casti']
            CreCarHis.gas_pro_gen = row['s24gasprogen']
            CreCarHis.zeta = row['z']
            CreCarHis.puntaje = row['puntaje']
            CreCarHis.cat_mod = row['cat_mod']
            CreCarHis.cat_ree = row['cat_ree']
            CreCarHis.cat_eva = row['cat_eva']
            CreCarHis.cat_sel = row['cat_sel']
            CreCarHis.pro_inc = row['pi']
            CreCarHis.pdi = row['pdi']
            CreCarHis.vea = row['vea']
            CreCarHis.per_esp = row['pe']
            CreCarHis.conta_ali = row['conta_ali']
            CreCarHis.ali_acu = row['ali_acu']
            CreCarHis.gas_pro_ind_acu = row['gas_ind_acu']
            
            CreCarHis.save()
    print('Fin credito CATEGO  ',datetime.now())

def est_fin():           # est_fin() # 26.
    print('Estados_fin ..  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    with open('c:/ajusto/csv/s02estfin.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')    
        for row in csv_reader:
            Tercero  = TERCEROS.objects.filter(
                cliente = Cliente,
                doc_ide = row['s02nit']).first()
            if Tercero == None:
                continue
            Estfin = ESTADOS_FIN.objects.filter(
                cliente = Cliente,
                tercero = Tercero,
                fec_inf = asignar_fecha(row['s02fecmod'].strip(),'%m/%d/%Y')).first()
            if Estfin == None:  
                Estfin = ESTADOS_FIN.objects.create(
                    cliente = Cliente,
                    tercero = Tercero,
                    fec_inf = asignar_fecha(row['s02fecmod'].strip(),'%m/%d/%Y'))
            Estfin.ing_sal_fij = row['s02ingsalfij']
            Estfin.ing_hon = row['s02inghon']
            Estfin.ing_pen = row['s02ingpen']
            Estfin.ing_arr = row['s02ingarr']
            Estfin.ing_com = row['s02ingcom']
            Estfin.ing_ext = row['s02ingext']
            Estfin.ing_otr = 'S'
            Estfin.ing_tot = row['s02ingmen']
            Estfin.egr_sec_fin = row['s02egrsecfin']
            Estfin.egr_cuo_hip = row['s02egrcuohip']
            Estfin.egr_des_nom = 'S'
            Estfin.egr_gas_fam = row['s02egrgasfam']
            Estfin.egr_otr_cre = row['s02egrotrcre']
            Estfin.egr_arr = row['s02egrarr']
            Estfin.egr_otr_gas = row['s02egrotrgas']
            Estfin.egr_tot = 0
            Estfin.act_otr_egr = 0
            Estfin.act_tip_bien = ''
            Estfin.act_vei = row['s02actveh']
            Estfin.act_otr = 'S'
            Estfin.tot_act = 0
            Estfin.act_fin_rai = row['s02actfinrai']
            Estfin.act_inv = 0
            Estfin.escritura = ''
            Estfin.pas_otr = 'S'
            Estfin.pas_tip = row['s02pasfin']
            Estfin.tot_pat = 0
            Estfin.pas_val = row['s02pasotr']
            Estfin.tot_pas = 0
            Estfin.pas_des = 0 
            Estfin.dec_ren = 'N'
            Estfin.tip_pas = ''
            Estfin.des_pas = ''
            Estfin.val_pas = 0
            Estfin.ope_mon_ext = 'N'
            Estfin.nom_ban_ext = ''
            Estfin.ope_pais_ext = 'S'
            Estfin.ope_monto_ext = 0
            Estfin.num_cta_ext = ''
            Estfin.tip_ope_ext = ''
            Estfin.mon_ope_ext = 'S'
            Estfin.prod_mon_ext = 0
            Estfin.des_prod_ext = 0
            Estfin.mon_prod_ext = 0
            Estfin.pais_prod_ext = 0
            Estfin.ciu_prod_ext = 0
            Estfin.prom_prod_ext = 0
            Estfin.save()
    print('Fin Estados_fin',datetime.now())

def bene_aso():         # bene_aso() # 27.
    print('Bene_aso  ',datetime.now())
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s01compfami.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        idocide = 1
        for row in csv_reader:
            Socio = ASOCIADOS.objects.filter(
                    oficina=Oficina,
                    cod_aso = row['s01xcodsoc']).first()
            if Socio == None:
                continue
            AsoBene = ASO_BENEF.objects.filter(asociado  = Socio,
                    doc_ide = str(idocide)).first()
            if AsoBene == None:
                AsoBene = ASO_BENEF.objects.create(asociado  = Socio,
                    doc_ide = str(idocide))
            AsoBene.nombre = row['s01xnombre']
            AsoBene.agno_nac = row['s01xagnnac']
            AsoBene.parentesco = row['s01xparentesco']
            AsoBene.porcentaje = 0
            AsoBene.save()
            idocide = idocide + 1
    print('Fin Bene ',datetime.now())

def referencias():          # referencias() # 28.
    print('Referencias  ',datetime.now())
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s02referencias.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            Socio = ASOCIADOS.objects.filter(
                    oficina = Oficina,
                    cod_aso = row['s02nit']).first()
            if Socio == None:
                continue
            Referencia = ASO_REFERENCIAS.objects.filter(asociado = Socio,nombre = row['s02nombre']).first()
            if Referencia == None:
                Referencia = ASO_REFERENCIAS.objects.create(asociado = Socio,nombre = row['s02nombre'])
            if row['s02tipref'] < '7':
                Referencia.tipo_ref = '1'
                if row['s02tipref'] == '1':
                    Referencia.parentesco = '3'
                elif row['s02tipref'] == '2':
                    Referencia.parentesco = '6' 
                elif row['s02tipref'] == '3':
                    Referencia.parentesco = '2' 
                else:
                    Referencia.parentesco = '9' 
            else:
                Referencia.parentesco = '0' 
                if row['s02tipref'] == '7':
                    Referencia.tipo_ref = '2'
                if row['s02tipref'] == '8':
                    Referencia.tipo_ref = '3'
            Referencia.ocupacion = row['s02cargo']
            Referencia.empresa = row['s02empresa']
            Referencia.direccion = row['s02direccion']
            Referencia.tel_fijo = row['s02telfij'][:10]
            Referencia.tel_cel = row['s02telcel'][:10]
            Referencia.tel_emp = row['s02telemp'][:10]
            Referencia.save()
    print('Fin Referen ',datetime.now())

def comprobantes():          # comprobantes() # 29.   59 minutos  al importar quitar ,00
    print('Comprobantes .... ',datetime.now())
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='latin1' 
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar
    cur = conn.cursor()
    try:
        cur.execute("select * from comprobantes where extract(year from fecha) > 2015")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        try:
            rows = cur.fetchall()
        except Exception as e:
            print("Error al obtener las filas:", e)
        finally:
            cur.close()
            conn.close()
    else:
        print("No se pudo obtener la descripción de las columnas. Puede que la consulta no haya retornado resultados.")
    Cliente = CLIENTES.objects.filter(codigo = 'A').first()
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))    
            Documento = DOCTO_CONTA.objects.filter(id_ds = row['ID_DOC']).first()
            if Documento == None:
                continue
            Comprobante = HECHO_ECONO.objects.filter(docto_conta=Documento,numero=int(float(row['NUMERO']))).first()
            if Comprobante == None:
                Comprobante = HECHO_ECONO.objects.create(docto_conta=Documento,numero=int(float(row['NUMERO'])))            
            Comprobante.fecha = row['FECHA']
            Comprobante.valor = row['VAL_CAJ']
            Comprobante.descripcion = row['CONCEPTO'][:64]
            Comprobante.anulado =  row['ANULADO']
            Comprobante.protegido = row['PROTEGIDO']
            Comprobante.fecha_prot = row['FEC_GRA']
            Comprobante.usuario = row['CUENTA'][:16]
            tip_doc = row['LL_TIP_DOC'].strip()

            if tip_doc in ['E', 'T']:
                Comprobante.canal = 'EFE'
            elif tip_doc == 'D':
                Comprobante.canal = 'DEP'
            elif tip_doc == 'R':
                Comprobante.canal = 'RET'
            elif tip_doc == 'C':
                Comprobante.canal = 'CHE'
            elif tip_doc == 'F':
                Comprobante.canal = 'TRA'
            elif tip_doc == 'G':
                Comprobante.canal = 'CON'
            elif tip_doc == 'P':
                Comprobante.canal = 'CNB'
            elif tip_doc == '':
                Comprobante.canal = 'N/A'
            
            banco = row['BANCO']
            if isinstance(row['FECHA'], str):
                fecha = datetime.strptime(row['FECHA'], '%d/%m/%Y')
            else:
                fecha = row['FECHA']  # ya es datetime.date o datetime.datetime
            #print('Fecha ',row['FECHA'],type(row['FECHA']))
            #fecha = datetime.strptime(row['FECHA'], '%d/%m/%Y')
            per_con = fecha.year 
            id_cuenta = PLAN_CTAS.objects.filter(cliente=1, per_con=per_con, cod_cta=banco).first()
            Comprobante.banco = id_cuenta
            Comprobante.cheque = row['CHEQUE']
            Comprobante.beneficiario = row['NIT_BEN']
            Comprobante.id_ds =  row['ID']
            Comprobante.ciudad_id = 1
            
            usuario = row['CUENTA'][:16]
            if usuario == 'LMGARCIA       S':
                Comprobante.user_id = 11
            elif usuario == 'ROGALINDO      S':
                Comprobante.user_id = 8
            elif usuario == 'EJOCAMPO       S':
                Comprobante.user_id = 18
            elif usuario in ['WTRIANA        S', 'WTRIANA']:
                Comprobante.user_id = 19
            elif usuario == 'LCLOPEZ        S':
                Comprobante.user_id = 12
            elif usuario in ['JSCAICEDO      S', 'JSCAICEDO']:
                Comprobante.user_id = 13
            elif usuario == 'IBAQUERO       S':
                Comprobante.user_id = 17
            elif usuario == 'RPEREZ         S':
                Comprobante.user_id = 20
            elif usuario == 'RHSERNA        S':
                Comprobante.user_id = 9
            elif usuario == 'CCASTRO':
                Comprobante.user_id = 15
            elif usuario == 'ESANCHEZ':
                Comprobante.user_id = 16
            elif usuario in ['', 'EVELASQUEZ     S', 'LORTEGA        S']:
                Comprobante.user_id = 1 
            elif usuario is None:
                Comprobante.user_id = 1
            elif usuario in ['CHMANOSALVA    S', 'CHMANOSALVA']:
                Comprobante.user_id = 7
            else:
                Comprobante.user_id = 1
            Comprobante.save()
    print('Fin Comprobantes.... ',datetime.now())

def importar_mov_cre():         # importar_mov_cre() # 31. 
    print('importar_mov_cre  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/xmov_cre.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            xCredito = CREDITOS.objects.filter(oficina=Oficina,cod_cre=row['codcre']).first()
            xEsta = ' '
            if xCredito == None:
                #print('Credito No Registrado ',row['codcre'])
                xEsta = 'N'
            xCredito  = XMOV_CRE.objects.create(cod_cre=row['codcre'],
                        est_jur = row['esjur'],
                        fecdes = asignar_fecha(row['fecdes'],'%m/%d/%Y'),
                        fec_ult_pag = asignar_fecha(row['fecultpag'],'%m/%d/%Y'),
                        min_fecha = asignar_fecha(row['min_fecha'],'%m/%d/%Y'),
                        max_fecha = asignar_fecha(row['max_fecha'],'%m/%d/%Y'),
                        clase = row['s13clase'],
                        docto = row['s13documen'],
                        tip_mov = row['s13tipmov'],
                        fecha = asignar_fecha(row['s13fecha'],'%m/%d/%Y'),
                        capital = row['s13capital'],
                        int_cor = row['s13intcor'],
                        int_mor = row['s13intmor'],
                        acreed = row['s13acreedo'],
                        estado = xEsta)
            xCredito.save()
    print('Fin MovCre ',datetime.now())

def catego_detalle():            # catego_detalle()  # 32
    print('Grabar Categori Detalle  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    reg_inicio = 0
    with open('c:/ajusto/csv/s31hiscatint.csv', 'r') as file:
        csv_reader = csv.DictReader(file, delimiter=',')
        for index, row in enumerate(csv_reader, start=1):
            if index < reg_inicio:
                continue  # Saltar las filas hasta alcanzar el número de registro inicial
            CatDet = CARTERA_CXC.objects.filter(oficina = Oficina,fecha = asignar_fecha(row['s31fecha']),cod_cre = row['s31codcre'],fec_ref = asignar_fecha(row['s31fecref'])).first()
            if CatDet == None:
                CatDet = CARTERA_CXC.objects.create(oficina = Oficina,fecha = asignar_fecha(row['s31fecha']),cod_cre = row['s31codcre'],fec_ref = asignar_fecha(row['s31fecref']))
            CatDet.categoria = row['s31cat']
            CatDet.valor = row['s31valor']
            CatDet.val_ali = row['s31valali']
            CatDet.clave = row['s31clave']
            Credito = CREDITOS.objects.filter(oficina = Oficina,cod_cre = row['s31codcre']).first()
            if Credito != None:
                CatDet.credito = Credito
            CatDet.save()
    print('Fin credito CATEGO  ',datetime.now())

def tablas_de_referencia():         # tablas_de_referencia()   #  33   pendiente
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    PE_CALIF_RANGO.objects.filter(cliente = Cliente).delete()
    PE_PI_CALIF.objects.filter(cliente = Cliente).delete()
    PE_PDI_RANGO.objects.filter(cliente = Cliente).delete()
    PE_MODE_REFE.objects.filter(cliente = Cliente).delete()
#  se busca la Calificacion a partir de un Puntaje Cartera de Consumo Con Libranza Entra el Puntaje y sale la Calificacion
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='A',pi_puntaje = 0.16480)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='B',pi_puntaje = 0.24810)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='C',pi_puntaje = 0.36770)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='D',pi_puntaje = 0.52300)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='E',pi_puntaje = 1.0)
#  se busca la Calificacion a partir de un Puntaje Cartera de Consumo Sin Libranza  Entra el Puntaje y sale la Calificacion
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='A',pi_puntaje = 0.07320)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='B',pi_puntaje = 0.20170)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='C',pi_puntaje = 0.38490)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='D',pi_puntaje = 0.59310)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='E',pi_puntaje = 1.0)
#  se busca la Calificacion a partir de un Puntaje Cartera Comercial Persona Natural Entra el Puntaje y sale la Calificacion
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPN',calificacion='A',pi_puntaje = 0.02080)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPN',calificacion='B',pi_puntaje = 0.17680)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPN',calificacion='C',pi_puntaje = 0.54410)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPN',calificacion='D',pi_puntaje = 0.76260)
    PE_CALIF_RANGO.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPN',calificacion='E',pi_puntaje = 1.0)

#  Cartera de Consumo Con Libranza Entra le Calificacion y sale la Porbabilidad de Incumplimieno PI en porcentaje
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='A',pi_porcent = 0.50)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='B',pi_porcent = 0.60)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='C',pi_porcent = 4.41)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='D',pi_porcent = 4.48)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='E',pi_porcent = 22.73)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCCL',calificacion='F',pi_porcent = 100.0) #Zepp no
#  Calificacion segun Puntaje  Cartera de Consumo Sin Libranza
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='A',pi_porcent = 1.50)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='B',pi_porcent = 5.95)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='C',pi_porcent = 13.82)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='D',pi_porcent = 32.77)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='E',pi_porcent= 41.71)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCSL',calificacion='F',pi_porcent = 100.0)
#  Calificacion segun Puntaje  Cartera Comercial Persona Natural
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='A',pi_porcent = 0.37)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='B',pi_porcent = 6.21)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='C',pi_porcent = 12.43)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='D',pi_porcent = 21.05)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='E',pi_porcent = 58.97)
    PE_PI_CALIF.objects.create(cliente=Cliente,clase_coop='EAYC',modalidad = 'CCPJ',calificacion='F',pi_porcent = 100.0)

#  Determina la PDI a partir de el tipo de garantia y los dias de incumplimiento
    PE_PDI_RANGO.objects.create(cliente=Cliente,garantia='1',pdi_0=60.0,dias_inc_1=210,pdi_1=70.0,dias_inc_2=420,pdi_2=100)
    PE_PDI_RANGO.objects.create(cliente=Cliente,garantia='2',pdi_0=40.0,dias_inc_1=360,pdi_1=70.0,dias_inc_2=720,pdi_2=100)
    PE_PDI_RANGO.objects.create(cliente=Cliente,garantia='15',pdi_0=75.0,dias_inc_1=30,pdi_1=85.0,dias_inc_2=90,pdi_2=100)

#  Se introducen los coeficientes de los modelos
    PE_MODE_REFE.objects.create(cliente = Cliente,modalidad = 'CCCL',constante = -1.52300,coe_ea = -2.08100,coe_fe = -0.91600,
        coe_valcuota = -0.16500, coe_fondplazo = -0.63200,coe_mora1230 = 2.49500,coe_mora1260 = 3.06200,coe_mora2430 = 0.31900,
        coe_sinmora = -0.57500,coe_mora3660 = 1.61500,coe_mora315 = 0.0 ) #Falta Mora315  0.0
    PE_MODE_REFE.objects.create(cliente = Cliente,modalidad = 'CCSL',constante = -2.18900,coe_ea = -1.18900,coe_fe =  0.0,
        coe_valcuota =  0.0, coe_fondplazo =  0.0,coe_mora1230 = 1.99900,coe_mora1260 = 2.90600,coe_mora2430 = 0.18000,
        coe_sinmora = -0.35000,coe_mora3660 = 0.0,coe_mora315 = 0.624 ) #Falta Mora315 =0.62400
    return

import csv
import sys
from datetime import datetime
from ctas_ahorros_app.models import xTempo02

def detalle_econo(doctos):             #  34      20 min X 5
    print('Detalles Comp ... ', datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    #  log_file_path = 'c:/ajusto/detalle_com_log1.txt'
    num = 0
    err_com = 0
    err_ter = 0
    err_cta = 0
    with open(doctos, 'r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            num = num + 1
            Comprobante = HECHO_ECONO.objects.filter(id_ds=row['ID_COM']).first()
            if Comprobante is None:
                print('No_Comprob. ID_COM ', row['ID_COM'], '  Compr.', row['COD_DOC'], '-', row['NUMERO'])
                err_com = err_com + 1
                continue
            Tercero = TERCEROS.objects.filter(id_ds=row['ID_TER']).first()
            if Tercero is None:
                err_ter = err_ter + 1
                print('No_Tercero  ID_TER ', row['ID_TER'], '  Compr.', row['COD_DOC'], '-', row['NUMERO'])
                continue
            Cuenta = PLAN_CTAS.objects.filter(id_ds=row['ID_CTA']).first()
            if Cuenta is None:
                err_cta = err_cta + 1
                print('No_Cuenta  ID_CTA  ', row['ID_CTA'], '  Compr.', row['COD_DOC'], '-', row['NUMERO'])
                continue

            DetalleEcono = DETALLE_ECONO.objects.create(
                hecho_econo=Comprobante, cuenta=Cuenta, tercero=Tercero
            )
            DetalleEcono.item_concepto = row['ID_DC']
            DetalleEcono.detalle = row['DETALLE']
            DetalleEcono.referencia = row['REFERENCIA']
            DetalleEcono.debito = row['DEBITO']
            DetalleEcono.credito = row['CREDITO']
            DetalleEcono.id_ds = row['ID']
            DetalleEcono.save()
    print('Fin ...           ', datetime.now())
    print(num)
    print(err_com)
    print(err_ter)
    print(err_cta)

def grabar_causa_cre():          #   35  42 Min
    print('Grabar Causa_cre  ',datetime.now())
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    xMovCaus = XMOV_CRE.objects.filter(tip_mov='2')
    for xMovCau in xMovCaus:
        xCuota = int(float(xMovCau.docto[1:8]))
        CreditoCausa = CREDITOS_CAUSA.objects.filter(oficina=Oficina,cod_cre = xMovCau.cod_cre,
            comprobante=None,cuota=xCuota).first()
        if CreditoCausa == None:
            CreditoCausa = CREDITOS_CAUSA.objects.create(oficina=Oficina,cod_cre = xMovCau.cod_cre,
            comprobante=None,cuota=xCuota)
        CreditoCausa.fecha = xMovCau.fecha 
        CreditoCausa.capital = xMovCau.capital
        CreditoCausa.int_cor = xMovCau.int_cor
        CreditoCausa.int_mor = xMovCau.int_mor
        CreditoCausa.pol_seg = 0
        CreditoCausa.save()
        xMovCau.estado= 'V'
        xMovCau.save()
    print('Grabar...           ',datetime.now())

def detalle_prod():         # 36  28 Min
    print('Detalle_prod ... ',datetime.now())
    # log_file_path = 'c:/ajusto/detalle_prod_log.txt'
    # with open(log_file_path, 'w') as log_file:
    #original_stdout = sys.stdout
    #sys.stdout = log_file
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    with open('c:/ajusto/csv/xc05movite.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            if (row['c05clase'] == '7' or row['c05clase'] == 'C' or row['c05clase'] == 'T') and int(row['c05fecha']) < 2015 :
                continue
            DocZep = XDOC_ZEP.objects.filter(per_con=row['c05fecha'],clase_zep=row['c05clase']).first()
            if DocZep == None:
                print('No Doc Zep',row['c05fecha'],row['c05clase'],row['c05documen'],row['c05concept'])
                continue
            if row['c05clase'] == '7':      # Cambio por AHOCH 
                xCodDoc = 6
            else:
                xCodDoc = DocZep.doc_ds
            DocCon = DOCTO_CONTA.objects.filter(oficina=Oficina,per_con=DocZep.per_con,
            codigo=xCodDoc).first()
            if DocCon == None:
                print('No Doc Justo',row['c05fecha'],row['c05clase'],row['c05documen'],row['c05concept'])
                continue
            HechEco = HECHO_ECONO.objects.filter(docto_conta=DocCon,numero=int(row['c05documen'])).first()
            if HechEco == None:
                DocCon = DOCTO_CONTA.objects.filter(oficina=Oficina,per_con=DocZep.per_con,codigo=10).first()
                HechEco = HECHO_ECONO.objects.filter(docto_conta=DocCon,numero=int(row['c05documen'])).first()
                if HechEco == None:
                    print('No Comp Justo',row['c05fecha'],row['c05clase'],row['c05documen'],row['c05concept'])
                    continue
                else:
                    print('Corregido ',row['c05fecha'],row['c05clase'],row['c05documen'],row['c05concept'])
            xPro = '  '
            if row['c05concept'] == 'AHO' or row['c05concept'] == 'AHOCH':
                xPro = 'AH'
            elif row['c05concept'] == 'APOR' or row['c05concept'] == 'APORE' or row['c05concept'] == 'APORO':
                xPro = 'AP'
            elif row['c05concept'] == 'CUOTA' or row['c05concept'] == 'ABOCA' or row['c05concept'] == 'ABOCU'  or row['c05concept'] == 'DESEM'  or row['c05concept'] == 'CASTI'  or row['c05concept'] == 'CONDO':
                xPro = 'CR'
            else:
                xPro = 'OT'
            DetProd = DETALLE_PROD.objects.filter(hecho_econo=HechEco,producto=xPro,
            concepto = row['c05concept'],subcuenta=row['c05subcuen']).first()
            if DetProd == None:
                DetProd = DETALLE_PROD.objects.create(hecho_econo=HechEco,producto=xPro,
                    concepto = row['c05concept'],subcuenta=row['c05subcuen'])
            DetProd.oficina = Oficina       # para mejorar la velocidad
            DetProd.valor = row['c05valor']
            DetProd.centro_costo = CentroCosto
            DetProd.save()
        # sys.stdout = original_stdout
    print('Fin ... ',datetime.now())

def deta_eco_aho():          #   38  70 Min   es s06movaho    queda en duda    
    print('Detalles Comp ... ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    mi_tempo = TEMPO_AHO.objects.all()
    mi_tempo.delete()
    log_file_path = 'c:/ajusto/s06Aho_com_log.txt'
    with open('c:/ajusto/csv/s06movaho.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            fecha = datetime.strptime(row['s06fecha'],'%m/%d/%Y')
            if fecha.year < 2019: 
                continue
            if row['s06clase'] == '4' or row['s06clase'] == '5' :
                tem_aho = TEMPO_AHO.objects.filter(num_cta = row['s06numcta'],agno = fecha.year,mes=fecha.month).first()
                if tem_aho == None:
                    tem_aho = TEMPO_AHO.objects.create(num_cta = row['s06numcta'],agno = fecha.year,mes=fecha.month,valor=0)
                tem_aho.valor = tem_aho.valor + 1
                tem_aho.save()
                continue 
            DocZep = XDOC_ZEP.objects.filter(per_con = fecha.year,clase_zep = row['s06clase']).first()
            if DocZep == None:     # No Hay Doc Zep
                print('No Doc_zep ',row['s06numcta'],'  ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                continue
            Doc = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = fecha.year,codigo = DocZep.doc_ds).first()
            if Doc == None:         # No Hay Documento
                print('No Docto   ',row['s06numcta'],'  ',DocZep.doc_ds,'   ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                continue
            Com = HECHO_ECONO.objects.filter(docto_conta = Doc,numero = int(row['s06documento'])).first()
            if Com == None:         # No Hay Comprobante
                print('No Comprob ',row['s06numcta'],'  ',DocZep.doc_ds,'   ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                continue 
            Prod = DETALLE_PROD.objects.filter(oficina = Oficina,hecho_econo = Com,concepto = 'AHO',subcuenta = row['s06numcta']).first()
            if Prod == None:        # No Hay Detalle Prod
                print('No det_pro ',row['s06numcta'],'  ',DocZep.doc_ds,'   ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                continue
            CtaAho = CTAS_AHORRO.objects.filter(oficina=Oficina,num_cta = row['s06numcta']).first()
            Ter = CtaAho.asociado.tercero
            ImpCon = IMP_CON_LIN_AHO.objects.filter(linea_ahorro = CtaAho.lin_aho,cod_imp = CtaAho.cod_imp).first()
            if ImpCon == None:
                print('No CtaAho  ',CtaAho.lin_aho,' Cod Imp ',CtaAho.cod_imp)
                continue
            CtaCon1 = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = fecha.year,cod_cta =ImpCon.ctaafeact).first()
            CtaCon2 = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = fecha.year,cod_cta =ImpCon.ctaafeina).first()
            Ctas = [CtaCon1,CtaCon2]
            DetComs = DETALLE_ECONO.objects.filter(hecho_econo = Com,tercero = Ter,cuenta__in = Ctas)
            xMov = ''
            if row['s06tipmov'] == '0':
                xMov = 'SalIni'
            elif row['s06tipmov'] == '1':
                xMov = 'Deposi'
            elif row['s06tipmov'] == '2':
                xMov = 'IntCta'
            elif row['s06tipmov'] == '3':
                xMov = 'IntCda'
            elif row['s06tipmov'] == '4':
                xMov = 'Canje'
            elif row['s06tipmov'] == '5':
                xMov = 'Can_OK'
            elif row['s06tipmov'] == '6':
                xMov = 'Retiro'
            elif row['s06tipmov'] == '7':
                xMov = 'RetFue'
            elif row['s06tipmov'] == '8':
                xMov = 'RF_CDA'
            elif row['s06tipmov'] == '9':
                xMov = 'CH_DEV'
            for DetCom in DetComs:
                DetCom.detalle_prod = Prod
                DetCom.item_concepto = xMov
                DetCom.save()
        print('Fin Detalles ... ',datetime.now())
        return

def int_mensual_aho():          #   nuevo    
    print('Int_men_aho ... ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    with open('c:/ajusto/csv/s06movaho.csv', 'r',encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            fecha = datetime.strptime(row['s06fecha'],'%m/%d/%Y')
            if fecha.year < 2019: 
                continue
            if (row['s06clase'] == '4' or row['s06clase'] == '5') and (row['s06numcta'].startswith(('01','02','06','07'))):
                DocZep = XDOC_ZEP.objects.filter(per_con = fecha.year,clase_zep = 'F').first()
                if DocZep == None:     # No Hay Doc Zep
                    print('No Doc_zep ',row['s06numcta'],'  ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                    continue
                Doc = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = fecha.year,codigo = DocZep.doc_ds).first()
                if Doc == None:         # No Hay Documento
                    print('No Docto   ',row['s06numcta'],'  ',DocZep.doc_ds,'   ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                    continue
                Com = HECHO_ECONO.objects.filter(docto_conta = Doc,numero = fecha.month).first()
                if Com == None:         # No Hay Comprobante
                    print('No Comprob ',row['s06numcta'],'  ',DocZep.doc_ds,'   ',row['s06fecha'],'  ',row['s06clase'],' ',row['s06tipmov'])
                    continue 
                Prod = DETALLE_PROD.objects.filter(oficina = Oficina,hecho_econo = Com,producto='AH',concepto = 'AHO',subcuenta = row['s06numcta']).first()
                if Prod == None:        # No Hay Detalle Prod
                    Prod = DETALLE_PROD.objects.create(oficina = Oficina,hecho_econo = Com,producto = 'AH',concepto = 'AHO',subcuenta = row['s06numcta'])
                CtaAho = CTAS_AHORRO.objects.filter(oficina=Oficina,num_cta = row['s06numcta']).first()
                Ter = CtaAho.asociado.tercero
                ImpCon = IMP_CON_LIN_AHO.objects.filter(linea_ahorro = CtaAho.lin_aho,cod_imp = CtaAho.cod_imp).first()
                if ImpCon == None:
                    print('No CtaAho  ',CtaAho.lin_aho,' Cod Imp ',CtaAho.cod_imp)
                    continue
                CtaCon1 = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = fecha.year,cod_cta =ImpCon.ctaafeact).first()
                CtaCon2 = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = fecha.year,cod_cta =ImpCon.ctaafeina).first()
                Ctas = [CtaCon1,CtaCon2]
                DetComs = DETALLE_ECONO.objects.filter(hecho_econo = Com,tercero = Ter,cuenta__in = Ctas)
                xMov = 'IntCta'
                xValor = 0
                for DetCom in DetComs:
                    DetCom.detalle_prod = Prod
                    DetCom.detalle = "Interes Mensual"
                    DetCom.item_concepto = xMov
                    xValor = xValor + DetCom.debito - DetCom.credito
                    DetCom.save()
                Prod.valor = xValor
                Prod.save()                
    print('Fin Interes Mensual ... ',datetime.now())
    return

def ImpIntDiaAho():          # 37   90 minutos  queda en suspenso
    print('IntCtaAho ... ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    #xTempo02.objects.filter().delete()   #   para comenzar de nuevo
    DETALLE_ECONO.objects.filter(hecho_econo__docto_conta__codigo = 13).delete()
    DETALLE_ECONO.objects.filter(hecho_econo__docto_conta__codigo = 131).delete()
    DETALLE_PROD.objects.filter(hecho_econo__docto_conta__codigo = 13).delete()
    DETALLE_PROD.objects.filter(hecho_econo__docto_conta__codigo = 131).delete()  

    #with open('c:/ajusto/csv/xTempo02.csv', 'r',encoding='latin-1') as file:
    #    csv_reader = csv.DictReader(file,delimiter=',')
    #    for row in csv_reader:
    #        agno = int(row['agno'])
    #        if agno < 2019: 
    #            continue
    #        xTemp02 = xTempo02.objects.create(doc_ide = row['s01nit'],
    #                    num_cta = row['numcta'],
    #                    agno = row['agno'],
    #                    mes = int(row['mes']),
    #                    valor =  row['valor'],
    #                    retfue =  row['retfue'],
    #                    valor_apl = 0)  
    
    with open('c:/ajusto/csv/xMovIntCtaAho.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=';')
        for row in csv_reader:
            #if row['NIT'].strip() != '41306473':
            #    continue
            if int(row['PER_CON']) < 2019:
                continue
            if  row['DEBITO'] == 0 and row['CREDITO'] == 0:
                continue
            Tercero = TERCEROS.objects.filter(cliente=Cliente,doc_ide=row['NIT']).first()
            if Tercero == None:
                print('Tercero No Existe  ',row['NIT'])
                continue
            Socio = ASOCIADOS.objects.filter(oficina=Oficina,tercero=Tercero).first()
            if Socio == None:
                print('Asociado No Existe  ',row['NIT'])
                continue
            CtaCon = PLAN_CTAS.objects.filter(cliente=1,per_con=row['PER_CON'],cod_cta=row['COD_CTA']).first()
            if CtaCon == None:
                print('No Existe Cta Con ',row['COD_CTA'],'  en el Periodo  ',row['PER_CON'])
                continue
            Docto = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = row['PER_CON'],codigo = row['COD_DOC']).first()
            HecEco = HECHO_ECONO.objects.filter(docto_conta = Docto,numero = row['NUMERO']).first()
            if HecEco == None:
                print('No Existe heCho econo ',row)
                continue
            DetEco = DETALLE_ECONO.objects.filter(hecho_econo = HecEco,cuenta = CtaCon,tercero = Socio.tercero).first()
            if DetEco == None:
                DetEco = DETALLE_ECONO.objects.create(hecho_econo = HecEco,cuenta = CtaCon,tercero = Socio.tercero)
                DetEco.debito = 0
                DetEco.credito = 0
                DetEco.valor_1 = 0
                DetEco.valor_2 = 0
            
            if row['COD_CTA'][:1] != '2':
                DetEco.detalle = 'Anexo IntCta Periodo'    
                DetEco.debito = DetEco.debito + float(row['DEBITO'] or 0)
                DetEco.credito = DetEco.credito + float(row['CREDITO'] or 0)
                DetEco.item_concepto = 'AneInt'
                DetEco.save()
            else:
                ImpCon = IMP_CON_LIN_AHO.objects.filter(Q(ctaafeact=row['COD_CTA']) | Q(ctaafeina=row['COD_CTA'])).first()
                if ImpCon == None:  # es una cuenta 2 pero de interes o retenfuente
                    DetEco.detalle = 'IntoRetFue'
                    DetEco.debito = DetEco.debito + float(row['DEBITO'] or 0)
                    DetEco.credito = DetEco.credito + float(row['CREDITO'] or 0)
                    DetEco.save()
                else:
                # print('Imp con Encontrada ',row['PER_CON'],row['COD_CTA'],row['NIT'])
                    CtaAhos = CTAS_AHORRO.objects.filter(oficina = Oficina,asociado = Socio,
                        lin_aho = ImpCon.linea_ahorro,cod_imp = ImpCon.cod_imp)
                    hay = 0
                    for CtaAho in CtaAhos:
                        ctamesExi = xTempo02.objects.filter(agno = row['PER_CON'],mes = row['MES'],num_cta = CtaAho.num_cta).first()
                        if ctamesExi == None:  
                            continue
                        hay = 1
                        DetPro = DETALLE_PROD.objects.filter(hecho_econo = HecEco,producto = 'AH',concepto = 'INTCA',subcuenta = CtaAho.num_cta,centro_costo = CentroCosto).first()
                        if DetPro == None:
                            DetPro = DETALLE_PROD.objects.create(hecho_econo = HecEco,producto = 'AH',concepto = 'INTCA',subcuenta = CtaAho.num_cta,centro_costo = CentroCosto)
                            DetPro.valor = 0
                        DetPro.valor = DetPro.valor + ctamesExi.valor + ctamesExi.retfue
                        DetPro.oficina = Oficina
                        DetPro.save()
                        DetEco.detalle = (DetEco.detalle.strip() if DetEco.detalle else '') + ' Int Cta Aho = ' + CtaAho.num_cta
                        DetEco.detalle_prod = DetPro
                        DetEco.item_concepto = 'IntCta'
                        DetEco.valor_1 = DetEco.valor_2 + ctamesExi.retfue
                        DetEco.valor_2 = DetEco.valor_2 - ctamesExi.valor
                        DetEco.debito = DetEco.debito + float(row['DEBITO'] or 0)
                        DetEco.credito = DetEco.credito + float(row['CREDITO'] or 0)
                        DetEco.save()
                    if hay == 0 : 
                        print('No Hay CtaAho Asociada con ',row['PER_CON'],' Mes ',row['MES'],'  Tercero  ',Tercero.doc_ide)

    print('Fin... ',datetime.now())

def grabar_credito_mod():            #   39   240 min en el servidir  actualiza cambios_cre CMBIO PROFUNDO
    print('Grabar credito Mod  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    xMovCams = XMOV_CRE.objects.filter(tip_mov__in=  ['3','4','5'])
    for xMovCam in xMovCams:
        try:
            numero = int(xMovCam.docto)  # Intenta convertir la cadena a un entero
        except ValueError:
            xMovCam.estado = '1'
            xMovCam.save()
            continue
        xper_con = xMovCam.fecha.year
        Comprobs = HECHO_ECONO.objects.filter(numero = int(xMovCam.docto),fecha = xMovCam.fecha)
        if not Comprobs.exists():
            xMovCam.estado = '2'
            xMovCam.save()
            continue
        for Comprob in Comprobs:
            if Comprob.docto_conta.oficina != Oficina:
                continue
            DetProd = DETALLE_PROD.objects.filter(hecho_econo=Comprob,producto='CR',subcuenta=xMovCam.cod_cre,
                    concepto__in = ['CUOTA','ABOCA','ABOCU','CASTI','CONDO']).first()
            if DetProd != None:
                xMovCam.estado = 'K'
                xMovCam.save()
                CamCre = CAMBIOS_CRE.objects.filter(det_pro = DetProd).first()
                if CamCre == None:
                    CamCre = CAMBIOS_CRE.objects.create(det_pro = DetProd)
                if DetProd.concepto in ['CUOTA','ABOCA','ABOCU']:
                    if xMovCam.tip_mov == '3': 
                        CamCre.tip_cam = '3'
                    elif xMovCam.tip_mov == '4':  
                        CamCre.tip_cam = '2'
                    elif xMovCam.tip_mov == '5':  
                        CamCre.tip_cam = '4'
                elif DetProd.concepto in ['CASTI']:
                    CamCre.tip_cam = '4'
                elif DetProd.concepto in ['CONDO']:
                    CamCre.tip_cam = '4'
                CamCre.fecha = xMovCam.fecha   
                CamCre.capital = xMovCam.capital
                CamCre.int_cor = xMovCam.int_cor
                CamCre.int_mor = xMovCam.int_mor
                CamCre.pol_seg = 0
                CamCre.acreedor = xMovCam.acreed
                CamCre.save()
                break
        if xMovCam.estado != 'K':
            xMovCam.estado = '3'
            xMovCam.save()
    print('Fin credito Mod  ',datetime.now())

def grabar_credito_mod2():            #   40   24 min   actualiza cambios_cre  
    print('Grabar credito Mod2  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    xMovCams = XMOV_CRE.objects.filter(clase = '6' ,estado = '2')
    for xMovCam in xMovCams:
        try:
            numero = int(xMovCam.docto)  # Intenta convertir la cadena a un entero
        except ValueError:
            xMovCam.estado = '1'
            xMovCam.save()
            continue
        xper_con = xMovCam.fecha.year
        xFecFin = xMovCam.fecha + timedelta(days=31)
        query = Q(numero=int(xMovCam.docto)) & Q(fecha__range=(xMovCam.fecha,xFecFin))
        Comprobs = HECHO_ECONO.objects.filter(query)
        if not Comprobs.exists():
            xMovCam.estado = '2'
            xMovCam.save()
            continue
        for Comprob in Comprobs:
            if Comprob.docto_conta.oficina != Oficina:
                continue
            DetProd = DETALLE_PROD.objects.filter(hecho_econo=Comprob,producto='CR',subcuenta=xMovCam.cod_cre,
                    concepto__in = ['CUOTA','ABOCA','ABOCU','CASTI','CONDO']).first()
            if DetProd != None:
                xMovCam.estado = 'Z'
                xMovCam.save()
                CamCre = CAMBIOS_CRE.objects.filter(det_pro = DetProd).first()
                if CamCre == None:
                    CamCre = CAMBIOS_CRE.objects.create(det_pro = DetProd)
                if DetProd.concepto in ['CUOTA','ABOCA','ABOCU']:
                    if xMovCam.tip_mov == '3': 
                        CamCre.tip_cam = '3'
                    elif xMovCam.tip_mov == '4':  
                        CamCre.tip_cam = '2'
                    elif xMovCam.tip_mov == '5':  
                        CamCre.tip_cam = '4'
                    CamCre.tip_cam = '2' 
                elif DetProd.concepto in ['CASTI']:
                    CamCre.tip_cam = '4'
                elif DetProd.concepto in ['CONDO']:
                    CamCre.tip_cam = '4'
                CamCre.fecha = xMovCam.fecha   
                CamCre.capital = xMovCam.capital
                CamCre.int_cor = xMovCam.int_cor
                CamCre.int_mor = xMovCam.int_mor
                CamCre.pol_seg = 0
                CamCre.acreedor = xMovCam.acreed
                CamCre.save()
                break
        if xMovCam.estado != 'Z':
            xMovCam.estado = '3'
            xMovCam.save()
    print('Fin credito Mod  ',datetime.now())

def asigna_con_cre():         #   41 SELECT COUNT(*) FROM detalle_econo WHERE Detalle NOT LIKE 'Nuevo%' update detalle_econo SET valor_2 = 0 WHERE valor_2 IS NULL  
    print('Recorrido...  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    xMovCres = XMOV_CRE.objects.filter(tip_mov__in = ['6','7','8','9','A'])   #,cod_cre = '132258',docto = '397335')
    for xMovCre in xMovCres:
        xFecha = xMovCre.fecha
        xDocto = xMovCre.docto
        xPercon = xMovCre.fecha.year
        xDocZep = XDOC_ZEP.objects.filter(per_con=xPercon,clase_zep = xMovCre.clase).first()
        if xDocZep == None:
            xMovCre.estado = '1'
            xMovCre.save()
            continue
        xDocConta = DOCTO_CONTA.objects.filter(oficina=Oficina,per_con=xPercon,codigo=xDocZep.doc_ds).first()
        if xDocConta == None:
            xMovCre.estado = '2'
            xMovCre.save()
            continue
        xHechoEco = HECHO_ECONO.objects.filter(docto_conta=xDocConta,numero=xDocto).first()
        if xHechoEco == None:
            xMovCre.estado = '3'
            xMovCre.save()
            continue
        if xMovCre.tip_mov == '9':
            xConcepto = 'CUOTA'
        elif xMovCre.tip_mov == '8':
            xConcepto = 'ABOCA'
        elif xMovCre.tip_mov  == '7':
            xConcepto = 'CONDO'    
        elif xMovCre.tip_mov  == '6':
            xConcepto = 'CASTI'
        elif xMovCre.tip_mov  == 'A':
            xConcepto = 'ABOCU'
        DetProd = DETALLE_PROD.objects.filter(hecho_econo = xHechoEco, concepto = xConcepto,
                            subcuenta = xMovCre.cod_cre).first()
        if DetProd == None:
            xMovCre.estado = '4'
            xMovCre.save()
            continue #
        Credito = CREDITOS.objects.filter(oficina = Oficina,cod_cre = xMovCre.cod_cre).first()    
        if Credito == None:
            xMovCre.estado = '5'
            xMovCre.save()
            continue
        Tercero = Credito.socio.tercero
        if Tercero == None:
            xMovCre.estado = '6'
            xMovCre.save()
            continue

        if xMovCre.capital != 0: 
            Cuenta = PLAN_CTAS.objects.filter(cliente=Cliente,per_con=xPercon,cod_cta='14433501').first()
            if Cuenta == None:
                xMovCre.estado = '7'
                xMovCre.save()
                continue
#  si Todo esto se cumple debe haber un asiento que refleje el movimiento del credito en capital
            HalDetEco = DETALLE_ECONO.objects.filter(hecho_econo = xHechoEco,cuenta=Cuenta,
                tercero = Tercero,detalle_prod = None).first()
            if HalDetEco == None:       # fALTA VER QUE PASA SI NO PAGO CAPITAL
                NvoDetEco = DETALLE_ECONO.objects.create(hecho_econo = xHechoEco,cuenta=Cuenta,
                    tercero = Tercero,detalle_prod = DetProd)
                NvoDetEco.item_concepto = 'Kapita'
                NvoDetEco.detalle = 'NuevoCr ' + xMovCre.cod_cre
                NvoDetEco.debito = 0
                NvoDetEco.credito = 0
                NvoDetEco.valor_1 = xMovCre.capital if xMovCre.capital > 0 else 0
                NvoDetEco.valor_2 = -xMovCre.capital if xMovCre.capital < 0 else 0
                NvoDetEco.save()
            else:
                HalDetEco.detalle_prod = DetProd
                HalDetEco.item_concepto = 'Kapita'
                HalDetEco.detalle = 'Ok ' + xMovCre.cod_cre
                HalDetEco.valor_1 = xMovCre.capital if xMovCre.capital > 0 else 0
                HalDetEco.valor_2 = -xMovCre.capital if xMovCre.capital < 0 else 0
                HalDetEco.save()

        if xMovCre.int_cor != 0: 
            Cuenta = PLAN_CTAS.objects.filter(cliente=Cliente,per_con=xPercon,cod_cta ='14433001').first()
            if Cuenta == None:
                xMovCre.estado = '8'
                xMovCre.save()
                continue
#  si Todo esto se cumple debe haber un asiento que refleje el movimiento del credito en IntCor
            HalDetEco = DETALLE_ECONO.objects.filter(hecho_econo = xHechoEco,cuenta=Cuenta,
                tercero = Tercero,detalle_prod = None).first()
            if HalDetEco == None:
                NvoDetEco  = DETALLE_ECONO.objects.create(hecho_econo = xHechoEco,cuenta=Cuenta,
                    tercero = Tercero,detalle_prod = DetProd)
                NvoDetEco.item_concepto = 'IntCor'
                NvoDetEco.detalle = 'NuevoCr ' + xMovCre.cod_cre
                NvoDetEco.debito = 0
                NvoDetEco.credito = 0
                NvoDetEco.valor_1 = xMovCre.int_cor if xMovCre.int_cor > 0 else 0
                NvoDetEco.valor_2 = -xMovCre.int_cor if xMovCre.int_cor < 0 else 0
                NvoDetEco.save()
            else:    
                HalDetEco.detalle_prod = DetProd
                HalDetEco.item_concepto = 'IntCor'
                HalDetEco.detalle = 'Ok ' + xMovCre.cod_cre
                HalDetEco.valor_1 = xMovCre.int_cor if xMovCre.int_cor > 0 else 0
                HalDetEco.valor_2 = -xMovCre.int_cor if xMovCre.int_cor < 0 else 0
                HalDetEco.save()
                
        if xMovCre.int_mor != 0: 
            Cuentas = PLAN_CTAS.objects.filter(cliente=Cliente,per_con=xPercon,cod_cta__in = ['41504001','41503501'])
            HalDetEco = None
            for Cuenta in Cuentas:
                HalDetEco = DETALLE_ECONO.objects.filter(hecho_econo = xHechoEco,cuenta=Cuenta,
                                tercero = Tercero).first()
                if HalDetEco != None:
                    break
            if HalDetEco == None:
                xMovCre.estado = '8'
                xMovCre.save()
                continue
            if HalDetEco.detalle_prod != None:
                NvoDetEco = DETALLE_ECONO.objects.create(hecho_econo = xHechoEco,cuenta=HalDetEco.cuenta,
                    tercero = Tercero,detalle_prod = DetProd)
                NvoDetEco.item_concepto = 'IntMor'
                NvoDetEco.detalle = 'NuevoCr ' + xMovCre.cod_cre
                NvoDetEco.debito = 0
                NvoDetEco.credito = 0
                NvoDetEco.valor_1 = xMovCre.int_mor if xMovCre.int_mor > 0 else 0
                NvoDetEco.valor_2 = -xMovCre.int_mor if xMovCre.int_mor < 0 else 0
                NvoDetEco.save()
            else:    
                HalDetEco.detalle_prod = DetProd
                HalDetEco.item_concepto = 'IntMor'
                HalDetEco.detalle = 'Ok ' + xMovCre.cod_cre
                HalDetEco.valor_1 = xMovCre.int_mor if xMovCre.int_mor > 0 else 0
                HalDetEco.valor_2 = -xMovCre.int_mor if xMovCre.int_mor < 0 else 0
                HalDetEco.save()
        
        if xMovCre.acreed != 0: 
            Cuenta = PLAN_CTAS.objects.filter(cliente=Cliente,per_con=xPercon,cod_cta = '24459501').first()
            if Cuenta == None:
                xMovCre.estado = '7'
                xMovCre.save()
                continue
            HalDetEco = DETALLE_ECONO.objects.filter(hecho_econo = xHechoEco,cuenta=Cuenta,
                tercero = Tercero,detalle_prod = None).first()
            if HalDetEco == None:
                NvoDetEco = DETALLE_ECONO.objects.create(hecho_econo = xHechoEco,cuenta=Cuenta,
                    tercero = Tercero,detalle_prod = DetProd)
                NvoDetEco.item_concepto = 'Acreed'
                NvoDetEco.detalle = 'NuevoCr ' + xMovCre.cod_cre
                NvoDetEco.debito = 0
                NvoDetEco.credito = 0
                NvoDetEco.valor_1 = xMovCre.acreed if xMovCre.acreed > 0 else 0
                NvoDetEco.valor_2 = -xMovCre.acreed if xMovCre.acreed < 0 else 0
                NvoDetEco.save()
            else:    
                HalDetEco.detalle_prod = DetProd
                HalDetEco.item_concepto = 'Acreed'
                HalDetEco.detalle = 'Ok ' + xMovCre.cod_cre
                HalDetEco.valor_1 = xMovCre.acreed if xMovCre.acreed > 0 else 0
                HalDetEco.valor_2 = -xMovCre.acreed if xMovCre.acreed < 0 else 0
                HalDetEco.save()
        xMovCre.estado = 'V'
        xMovCre.save()
    print('Fin Recorrido...  ',datetime.now())

def asigna_com_cre():        #   42
    print('Recorrido...  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    DetallesProSel = DETALLE_PROD.objects.filter(concepto='CUOTA').all()
    ya = 0
    for oDP in DetallesProSel:
        if ya == 0:
            print('Recorrido...  ',datetime.now())
        ya = ya + 1
        oHE = oDP.hecho_econo
        oCtaCon = PLAN_CTAS.objects.filter(cliente=Cliente,per_con= oHE.fecha.year,cod_cta='14433501').first()
        if oCtaCon == None:
            print('No hay Cta Con ',oDP.subcuenta)
        Credito = CREDITOS.objects.filter(oficina=Oficina,cod_cre = oDP.subcuenta).first()
        if Credito == None:
            print('No hay Credito ',oDP.subcuenta)
            continue
        oTer = Credito.socio.tercero
        oHallado = DETALLE_ECONO.objects.filter(hecho_econo=oHE,tercero=oTer,cuenta=oCtaCon).first()
        if oHallado == None:
            print('No hay Detalle Cr =',oDP.subcuenta,'  Comp=',oHE.docto_conta.codigo,oHE.numero,oHE.fecha)
            continue
        oHallado.item_concepto = 'Kapita'
        oHallado.detalle_prod = oDP
        oHallado.detalle = oHallado.detalle.strip()+','+oDP.subcuenta if len(oHallado.detalle.strip())>0 else oDP.subcuenta
        oHallado.save()    
    print('Fin Recorrido ... ',datetime.now(),ya)

def vMov_cre():           #   44
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    print('Creditos  ',datetime.now())
    Creditos = CREDITOS.objects.filter(oficina=Oficina,estado = 'A')
    xTotSal = 0
    xNumCre = 0
    for Credito in Creditos:
        icod_cre = Credito.cod_cre
        if Credito == None:
            print('No Hay credito')
            exit()
        xNumCre = xNumCre + 1
        CreCaus = CREDITOS_CAUSA.objects.filter(oficina=Oficina,cod_cre = Credito.cod_cre,comprobante=None)
        mov_cre = []
        for CreCau in CreCaus:
            mov_cre.append({
                'Fecha' : CreCau.fecha,
                'Tipo'  : '1',
                'Cuota' : CreCau.cuota,
                'KapTal': CreCau.capital,
                'IntCor': CreCau.int_cor,
                'IntMor': 0,
                'PolSeg': 0,
                'Acreed': 0
            })
        DetPros = DETALLE_PROD.objects.filter(oficina=Oficina,producto='CR',subcuenta = Credito.cod_cre)
        for DetPro in DetPros:
            HecEco = HECHO_ECONO.objects.filter(id=DetPro.hecho_econo.id).first()
            DetEcos = DETALLE_ECONO.objects.filter(detalle_prod=DetPro)
            xKap,xIntCor,xIntMor,xPolSeg,xAcre = 0,0,0,0,0
            xTipMov = ' '
            if DetPro.concepto == 'CUOTA':
                xTipMov = '8'
            elif DetPro.concepto == 'ABOCA':
                xTipMov = '7'
            elif DetPro.concepto == 'ABOCU':
                xTipMov = '9'
            elif DetPro.concepto == 'CONDO':
                xTipMov = '6'
            elif DetPro.concepto == 'GASTI':
                xTipMov = '5'
            for DetEco in DetEcos:
                if DetEco.item_concepto == 'Kapita':
                    xKap = 0 if DetEco.valor_2 is None  else -DetEco.valor_2 
                elif DetEco.item_concepto == 'IntCor':
                    xIntCor = 0 if DetEco.valor_2 is None  else -DetEco.valor_2
                elif DetEco.item_concepto == 'IntMor':
                    xIntMor = 0 if DetEco.valor_2 is None  else -DetEco.valor_2
                elif DetEco.item_concepto == 'PolSeg':
                    xPolSeg = 0 if DetEco.valor_2 is None  else -DetEco.valor_2
                elif DetEco.item_concepto == 'Acreed':
                    xAcre = 0 if DetEco.valor_2 is None  else -DetEco.valor_2
            mov_cre.append({
                'Fecha' : HecEco.fecha,
                'Tipo'  : xTipMov,
                'Cuota' : 99,
                'KapTal': xKap,
                'IntCor': xIntCor,
                'IntMor': xIntMor,
                'PolSeg': xPolSeg,
                'Acreed': xAcre
            })
            ModCre = CAMBIOS_CRE.objects.filter(det_pro = DetPro).first()
            if ModCre != None:
                mov_cre.append({
                    'Fecha' : HecEco.fecha,
                    'Tipo'  : ModCre.tip_cam,
                    'Cuota' : 99,
                    'KapTal': ModCre.capital,
                    'IntCor': ModCre.int_cor,
                    'IntMor': ModCre.int_mor,
                    'PolSeg': ModCre.pol_seg,
                    'Acreed': ModCre.acreedor
                })
        

        mov_cre = sorted(mov_cre, key=lambda x: (x['Fecha'],x['Cuota']))
        saldo = sum(elem['KapTal'] for elem in mov_cre )
        xTotSal += saldo
        print(icod_cre,' Saldo ',saldo)
    print('Total Saldo',xTotSal,'  Numero de Creditos ',xNumCre)
    print('Finaliza ',datetime.now())

def prueba():                 #   45
    TIPOS_MOV_CRE = {
        'DESEM': '0',
        'CAUSA': '1',
        'AJUST': '2',
        'DESPP': '3',
        'KASCO': '4',
        'CASTI': '5',
        'CONDO': '6',
        'ABOCA': '7',
        'ABOCU': '8',
        'CUOTA': '9'
    }
    print('Duracion  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    Creditos = CREDITOS.objects.filter(oficina=Oficina,estado = 'A')
    xTotSal = 0
    xNumCre = 0
    for Credito in Creditos:
        queryset1 = CREDITOS_CAUSA.objects.values('fecha', 'cuota') \
            .filter(oficina=Oficina, cod_cre=Credito.cod_cre) \
            .annotate(
                tipmov=Value('1'),
            kapital=F('capital'),
            intcor=F('int_cor'),
            intmor=Value(0, output_field=IntegerField()),
            polseg=Value(0, output_field=IntegerField()),
            despp=Value(0, output_field=IntegerField()),
            acreed=Value(0, output_field=IntegerField())
        )

        #for lista in queryset1:
        #    print(lista)
        #    break
        queryset2 = DETALLE_PROD.objects.filter(oficina=Oficina, producto='CR', subcuenta=Credito.cod_cre) \
            .values(fecha=F('hecho_econo__fecha')) \
            .annotate(
                cuota=Value(0),
                tipmov=Case(
                    *[When(concepto=concept, then=Value(value)) for concept, value in TIPOS_MOV_CRE.items()],
                    output_field=CharField()
                ),
                kapital=Coalesce(Sum(Case(When(detalle_econo__item_concepto='Kapita', then=-F('detalle_econo__valor_2')))), Value(0.0)),
                intcor=Coalesce(Sum(Case(When(detalle_econo__item_concepto='IntCor', then=-F('detalle_econo__valor_2')))), Value(0.0)),
                intmor=Coalesce(Sum(Case(When(detalle_econo__item_concepto='IntMor', then=-F('detalle_econo__valor_2')))), Value(0.0)),
                polseg=Coalesce(Sum(Case(When(detalle_econo__item_concepto='PolSeg', then=-F('detalle_econo__valor_2')))), Value(0.0)),
                despp=Coalesce(Sum(Case(When(detalle_econo__item_concepto='DesPP', then=-F('detalle_econo__valor_2')))), Value(0.0)),
                acreed=Coalesce(Sum(Case(When(detalle_econo__item_concepto='Acreed', then=-F('detalle_econo__valor_2')))), Value(0.0)) 
            )
        #for lista in queryset2:
        #    print(lista)
        #    break

        queryset3 = CAMBIOS_CRE.objects.filter(det_pro__oficina=Oficina, det_pro__producto='CR', det_pro__subcuenta=Credito.cod_cre) \
            .values(fecha=F('det_pro__hecho_econo__fecha')) \
            .annotate(
                cuota=Value(0, output_field=IntegerField()),
                tipmov=F('tip_cam'),
                kapital=F('capital'),
                intcor=F('int_cor'),
                intmor=F('int_mor'),
                polseg=F('pol_seg'),
                despp=Value(0, output_field=IntegerField()),
                acreed=F('acreedor')
            )
        tab_liq = list(queryset1) + list(queryset2) + list(queryset3)
        tab_liq = sorted(tab_liq, key = itemgetter('fecha', 'tipmov'))
        nr = 0
        saldo = sum(objeto['kapital'] for objeto in tab_liq if objeto['tipmov'] != '0')
        #print(Credito.cod_cre,' ', saldo)
        xTotSal = xTotSal + saldo
        xNumCre = xNumCre + 1
    print('Creditos  ',xNumCre,'   ',xTotSal)
    print('Fin       ',datetime.now())

def asigna_desem():
    print('Inicio Asigna Desem  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    det_pro_dess = DETALLE_PROD.objects.filter(concepto='DESEM').all()
    for det_des in det_pro_dess:
        credito = CREDITOS.objects.filter(oficina = Oficina,cod_cre = det_des.subcuenta).first()
        if credito == None:
            print('No Existe Credito ',det_des.subcuenta)
            continue
        print('fec_des ',credito.cod_cre,'  ',credito.fec_des)
        per_con = credito.fec_des.year
        imp_con_cre = IMP_CON_CRE.objects.filter(id = credito.imputacion_id ).first()
        if imp_con_cre == None:
            print('No Se Encontro Imputacion Contable ',credito.cod_cre)
            continue 
        plan_ctas = PLAN_CTAS.objects.filter(cliente = Cliente,per_con = per_con,cod_cta = '14433501').first()
        if plan_ctas == None:
            print('credito ',credito.cod_cre,'  No se encontro Cuenta Contable')
            continue
        detalle_econo = DETALLE_ECONO.objects.filter(hecho_econo_id = det_des.hecho_econo_id,
            tercero_id = credito.socio.tercero_id,
            cuenta_id = plan_ctas.id).first()
        if detalle_econo == None:
            print('credito ',credito.cod_cre,'  No se encontro detalle Econo')
            continue
        detalle_econo.item_concepto = 'Kapita'
        detalle_econo.detalle_prod_id = det_des.id
        detalle_econo.detalle = 'Desem Encontrado '+credito.cod_cre
        detalle_econo.valor_1 = credito.cap_ini
        detalle_econo.valor_2 = 0
        detalle_econo.save()
    print('Fin    Asigna Desem  ',datetime.now())

def asigna_sal_ini_apor():
    print('Inicia asigna_sal_ini_apor ',datetime.now())
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    cta_con = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = 2015,cod_cta = '31050501').first()
    if cta_con == None:
        print('no hay cuenta contable aportes en 2015')
        return
    hec_eco = HECHO_ECONO.objects.filter(docto_conta_id = 50, numero = 1,fecha = asignar_fecha('31/12/2015','%d/%m/%Y')).first()
    if hec_eco == None:
        hec_eco = HECHO_ECONO.objects.create(docto_conta_id = 50, numero = 1,fecha = asignar_fecha('31/12/2015','%d/%m/%Y'))
    hec_eco.descripcion = 'Saldos Iniciales Aportes para Justo'
    hec_eco.anulado = 'N'
    hec_eco.protegido = 'S'
    hec_eco.save()
    with open('c:/ajusto/csv/xAP_2015.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=';')
        for row in csv_reader:
            socio = ASOCIADOS.objects.filter(oficina = Oficina,cod_aso = row['codsoc']).first()
            if socio == None:
                print('Asociado no existe ',row['codsoc'])
                continue
            det_pro = DETALLE_PROD.objects.filter(hecho_econo_id = hec_eco.id,producto = 'AP',concepto = 'SalIni',subcuenta = row['codsoc'] ).first()
            if det_pro == None:
                det_pro = DETALLE_PROD.objects.create(hecho_econo_id = hec_eco.id,producto = 'AP',concepto = 'SalIni',subcuenta = row['codsoc'] )
            det_pro.valor = -float(int(row['valor']))
            det_pro.concepto = 'SalIni'
            det_pro.centro_costo_id = 1
            det_pro.oficina_id = 1
            det_pro.save()
            det_eco = DETALLE_ECONO.objects.filter(hecho_econo_id =  hec_eco.id,detalle_prod_id = det_pro.id,cuenta_id = cta_con.id,tercero_id = socio.tercero.id).first()
            if det_eco == None:
                det_eco = DETALLE_ECONO.objects.create(hecho_econo_id =  hec_eco.id,detalle_prod_id = det_pro.id,cuenta_id = cta_con.id,tercero_id = socio.tercero.id)
            det_eco.item_concepto = 'SalIni'
            det_eco.debito = 0
            det_eco.credito = float(int(row['valor']))
            det_eco.save()


    print('Final  asigna_sal_ini_apor ',datetime.now())

def asigna_rev_aportes(): 
    print('Inicio Asigna reVal apoRtes  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    det_prod_revs = DETALLE_PROD.objects.filter(concepto='APREV').all()
    for det_pro_rev in det_prod_revs:
        #print('deta ',det_pro_rev.hecho_econo.fecha,'  ',det_pro_rev.hecho_econo.numero,det_pro_rev.concepto,' ',det_pro_rev.subcuenta)
        asociado = ASOCIADOS.objects.filter(oficina = Oficina,cod_aso = det_pro_rev.subcuenta).first()
        if asociado == None:
            print('No Existe Asociado con Docto ',det_pro_rev.subcuenta,'  eN ',det_pro_rev.hecho_econo.fecha)
            continue
        det_eco_rev = DETALLE_ECONO.objects.filter(hecho_econo_id = det_pro_rev.hecho_econo_id,tercero_id = asociado.tercero.id).first()
        if det_eco_rev == None:
            print('No Existe dEt_ECo ',det_pro_rev.subcuenta,'  eN ',det_pro_rev.hecho_econo.fecha)
            continue
        det_eco_rev.item_concepto = 'Reval' 
        det_eco_rev.detalle_prod_id = det_pro_rev.id
        det_eco_rev.save()
        det_pro_rev.producto = 'AP'
        det_pro_rev.save()
         
    print('Final  Asigna reVal apoRtes  ',datetime.now())

def ajuste_mov_aho():
    print('Inicia Ajuste desde 2019 en ahorros')
 #   SELECT * FROM HECHO_ECONO WHERE ID  IN (65088,65328,101951,130863,154147,177415,198943,222731) AND PRODUCTO = 'OA'

from ctas_ahorros_app.models import XAJU_SAL_AHO

#UPDATE detalle_prod SET PRODUCTO = 'AH' WHERE HECHO_ECONO_ID  IN (101951) AND PRODUCTO = 'OA' 

#SELECT he.id,HE.FECHA,DP.* FROM detalle_prod DP
#  INNER JOIN hecho_econo HE ON HE.ID = DP.HECHO_ECONO_ID
#  where PRODUCTO= 'AH'  AND YEAR(HE.fecha) <= 2018
#ORDER BY HE.FECHA

#UPDATE detalle_prod DP
#INNER JOIN hecho_econo HE ON HE.ID = DP.HECHO_ECONO_ID
#SET DP.PRODUCTO = 'AX'
#WHERE DP.PRODUCTO = 'AH' 
#  AND YEAR(HE.fecha) <= 2018;

import os
import django
from django.db.models.functions import Substr

def sal_ini_aho():
    print('Iniciar Saldo Inicial Ahorros  ',datetime.now())
    fecha_limite = datetime(2019, 12, 31)
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    docto_conta = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = 2019,codigo = 0).first()
    if docto_conta == None:
        print('No Existe Docto')
        return
    hec_eco = HECHO_ECONO.objects.filter(docto_conta_id = docto_conta.id,numero = 1).first()
    det_ecos = DETALLE_ECONO.objects.filter(hecho_econo = hec_eco) 
    for det_eco in det_ecos:
        cta_con = PLAN_CTAS.objects.filter(id = det_eco.cuenta_id).first()
        if cta_con.cod_cta[:2] == '21':
            socio = ASOCIADOS.objects.filter(tercero_id = det_eco.tercero_id).first()
            if socio == None:
                print('Tercero ',det_eco.tercero.nombre,'  No Aparece como Asociado')
                continue
            cta_ahos = CTAS_AHORRO.objects.filter(asociado = socio,fec_apertura__lte = fecha_limite)
            for cta_aho in cta_ahos :
                imp_con =IMP_CON_LIN_AHO.objects.filter(cod_imp = cta_aho.cod_imp,linea_ahorro_id = cta_aho.lin_aho_id).first()
                if imp_con == None:
                    print('la cuenta ',cta_aho.num_cta, '  No Tiene Imputacion ')
                    continue
                if imp_con.ctaafeact == cta_con.cod_cta or  imp_con.ctaafeina == cta_con.cod_cta:
                    det_pro = DETALLE_PROD.objects.filter(hecho_econo = hec_eco,producto = 'AH',subcuenta = cta_aho.num_cta).first()
                    if det_pro == None:
                        det_pro = DETALLE_PROD.objects.create(hecho_econo = hec_eco,producto = 'AH',subcuenta = cta_aho.num_cta)
                    
                    det_pro.concepto = 'SalIni'
                    det_pro.valor = det_eco.debito - det_eco.credito 
                    det_pro.centro_costo_id = 1
                    det_pro.oficina_id = 1
                    det_pro.save()
                    det_eco.detalle_prod = det_pro
                    det_eco.item_concepto = 'SalIni'
                    det_eco.detalle = 'Saldo Inicial Cta de Ahorros '+cta_aho.num_cta
                    det_eco.save()

#UPDATE detalle_prod DP
#  INNER JOIN hecho_econo HE ON HE.ID = DP.HECHO_ECONO_ID
#  SET DP.PRODUCTO = 'AX'
# WHERE DP.PRODUCTO = 'AH' 
#   AND YEAR(HE.fecha) <= 2018;
            
    print('Finaliz Saldo Inicial Ahorros  ',datetime.now())

def huerfanos_aho():          #   47
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
    django.setup()
    terceros = TERCEROS.objects.all()
    for tercero in terceros:
        # Guarda cada registro para actualizar el campo 'nombre'
        tercero.save()
        print(f"Actualizado: {tercero.id} - {tercero.nombre}")
    return
    print('Huerfanos Ahorros ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    ctas_aho = ['21100501','21100501','21101001','21101001','21101501','21101501','21102001','21102001','21050501','21051001',
			    '21250501','21050502','21051002','21050503','21051003','21250501','21251501','21050504','21051004']
    DetHues = DETALLE_ECONO.objects.filter(cuenta__cod_cta__in=ctas_aho,detalle_prod__isnull=True
            ).select_related('cuenta', 'hecho_econo')
    print(DetHues.count())
    for DetHue in DetHues:
        Tercero = DetHue.tercero
        ImpCon = IMP_CON_LIN_AHO.objects.filter(Q(ctaafeact=DetHue.cuenta.cod_cta) | Q(ctaafeina=DetHue.cuenta.cod_cta)).first()
        if ImpCon == None:
            continue
        Socio = ASOCIADOS.objects.filter(oficina = Oficina,tercero = Tercero).first()
        if Socio == None:
            print('No Existe Asociado',Tercero.doc_ide)
            continue
        CtaAho = CTAS_AHORRO.objects.filter(oficina = Oficina,asociado = Socio,lin_aho = ImpCon.linea_ahorro,cod_imp = ImpCon.cod_imp).first()
        if CtaAho == None:
            print('Asociado ',Tercero.doc_ide,' No tiene cuenta de ahorro')
            continue
        DetPro = DETALLE_PROD.objects.filter(hecho_econo = DetHue.hecho_econo,producto = 'AH',concepto = 'AHO',subcuenta = CtaAho.num_cta,centro_costo = CentroCosto).first()
        if DetPro == None:
            DetPro = DETALLE_PROD.objects.create(hecho_econo = DetHue.hecho_econo,producto = 'AH',concepto = 'AHO',subcuenta = CtaAho.num_cta,centro_costo = CentroCosto)
        DetPro.valor = DetHue.debito - DetHue.credito
        DetPro.save()
        DetHue.detalle = 'Int Cta Aho = '+CtaAho.num_cta
        DetHue.detalle_prod = DetPro
        DetHue.item_concepto = 'SalIni' if DetHue.hecho_econo.numero == 1 else ('Deposi' if DetPro.valor < 0 else 'Retiro')
        DetHue.save()
    print('Fin   Huerfanos  ',datetime.now())        
    return

def cargue_ajuste_saldos_ahorros():
    print('Inicia Cargue Ajuste Ahorros  ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    with open('c:/ajusto/csv/xaju_sal_aho.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=';')
        for row in csv_reader:
            xajusal = XAJU_SAL_AHO.objects.filter(agno = row['agno'],num_cta = row['numcta']).first()
            if xajusal == None:
                xajusal = XAJU_SAL_AHO.objects.create(agno = row['agno'],num_cta = row['numcta'],valor = 0)
            xajusal.est_cta =  row['estcta']
            xajusal.valor =  row['valor']
            xajusal.save()
    print('Final Cargue Ajuste Ahorros ..',datetime.now())

def saldo_ctaaho_fecha(oficina_id, fecha_limite):
    # Ejecutar una sola consulta y devolver un diccionario {cod_aso: total}
    resultado = (
        DETALLE_PROD.objects
        .filter(
            hecho_econo__docto_conta__oficina_id=oficina_id,
            producto='AH',
            hecho_econo__fecha__lte= fecha_limite
        )
        .values('subcuenta')
        .annotate(saldo=Sum('valor') * -1) 
    )
    return {item["subcuenta"]: item["saldo"] for item in resultado}

from datetime import date
from django.db.models import Subquery, OuterRef

def ajustar_saldo_ahorros():
    print('Inicia Ajustas Saldos Ahorros ..',datetime.now())

    DETALLE_PROD.objects.filter(
        producto='AH',
        hecho_econo__fecha__year__lte=2018  # borra lo anterior a 2019
    ).update(producto='AX')

    subquery = HECHO_ECONO.objects.filter(
        docto_conta__codigo=128,numero = 1
    ).values('id')
    
    DETALLE_ECONO.objects.filter(hecho_econo_id__in=Subquery(subquery)).delete()
    DETALLE_PROD.objects.filter(hecho_econo_id__in=Subquery(subquery)).delete()
    xbuenas = 0
    xajustar = 0
    for xano in range(2019,2025):  # Itera de 2019 a 2024
        agno = xano # Tu variable de año
        fecha_ultimo_dia = date(agno, 12, 31)
        miDoctoConta = DOCTO_CONTA.objects.filter(oficina_id=1, codigo=128, per_con=agno).first()
        miHecEco = HECHO_ECONO.objects.filter(docto_conta=miDoctoConta,numero = 1).first()
        if miHecEco == None:
            miHecEco = HECHO_ECONO.objects.create(docto_conta=miDoctoConta,numero = 1)
        miHecEco.fecha = fecha_ultimo_dia
        miHecEco.descripcion = 'Ajuste saldos de cuentas de ahorros por importacion de Zeppelin'
        miHecEco.save()
        DETALLE_PROD.objects.filter(hecho_econo=miHecEco).delete()
        saldos_fecha = saldo_ctaaho_fecha(1,fecha_ultimo_dia)
        ctassalrea = XAJU_SAL_AHO.objects.filter(agno = agno)
        for ctasalrea in ctassalrea:
            saldojusto = saldos_fecha.get(ctasalrea.num_cta,0)
            saldoreal = ctasalrea.valor
            if saldoreal == saldojusto:
                xbuenas = xbuenas + 1
            else:
                det_pro = DETALLE_PROD.objects.create(hecho_econo=miHecEco,producto='AH',concepto = 'Ajuste',
                    subcuenta = ctasalrea.num_cta,valor=-int(saldoreal-saldojusto))
                xajustar = xajustar + 1
        for subcuenta, saldo in saldos_fecha.items():
            ctaExiste = XAJU_SAL_AHO.objects.filter(agno = agno,num_cta = subcuenta).first()
            if ctaExiste == None and int(saldo) != 0:
                det_pro = DETALLE_PROD.objects.create(hecho_econo=miHecEco,producto='AH',concepto = 'Retiro',
                    subcuenta = subcuenta,valor=int(saldo))
    print('Buenas ',xbuenas)        
    print('Ajustar ',xajustar)
    print('Finaliza Ajustas Saldos Ahorros ',datetime.now())    
    return

def ajustar_saldo_aportes():
    print('Inicia Ajustas Saldos Aportes ..',datetime.now())

    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    doc = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = 2019, codigo = 128).first()
    CentroCosto = CENTROCOSTOS.objects.filter(oficina=Oficina,codigo = 'A001').first()
    hec = HECHO_ECONO.objects.filter(docto_conta = doc,numero = 1).first()
    if hec == None:
        print('No Hay Hecho Econo ')
        return
    print(hec)
    DETALLE_ECONO.objects.filter(hecho_econo = hec,item_concepto = 'AjuApo').delete()
    DETALLE_PROD.objects.filter(hecho_econo = hec,producto = 'AP').delete()
    cta = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = 2019,cod_cta = '31050501').first()
    with open('c:/ajusto/csv/xaju_apor_19.csv', 'r') as file:
        csv_reader = csv.DictReader(file,delimiter=';')
        for row in csv_reader:
            aso = ASOCIADOS.objects.filter(oficina = Oficina,cod_aso = row['codsoc']).first()
            detpro = DETALLE_PROD.objects.create(hecho_econo = hec,oficina = Oficina,centro_costo = CentroCosto,
                producto = 'AP',concepto = 'AJUAPO',subcuenta = aso.cod_aso,valor = -int(row['val_aju']))
            if detpro == None:
                print('No Grabo deppro')
            deteco = DETALLE_ECONO.objects.create(hecho_econo = hec,detalle_prod = detpro,item_concepto = 'AjuApo',
                detalle = 'Ajuste Aportes = '+aso.cod_aso,debito = 0,credito = 0,valor_1 = 0 ,valor_2 = int(row['val_aju']),
                cuenta = cta,tercero = aso.tercero)
            if deteco == None:
                print('No Grabo deteco')
            print('Socio ',row['codsoc'],'  Valor ',row['val_aju'],' nombre ',aso.tercero.nombre)

    print('Finaliza Ajustas Saldos Aportes ',datetime.now())    
    return

def CuentasXCobrar():         # creditos() # 25.      #  10 Min
    print('Cuantas X Cobrar ..',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()

    with open('c:/ajusto/csv/s50CxC.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            terce = TERCEROS.objects.filter(cliente = Cliente,doc_ide = row['s50nit']).first()
            if terce == None:
                continue
            concep = CONCEPTOS.objects.filter(cliente = Cliente,cod_con = row['s50codcon']).first()
            if concep == None:
                continue
            cxc = CTAS_X_COBRAR.objects.filter(oficina = Oficina,cod_cxc=row['s50codcxc']).first()
            if cxc == None:
                cxc = CTAS_X_COBRAR.objects.create(oficina = Oficina,cod_cxc=row['s50codcxc'])
            cxc.concepto = concep
            cxc.tercero = terce
            cxc.fecha_des = asignar_fecha(row['s50fecdes'],'%m/%d/%Y')
            cxc.fecha_exi = asignar_fecha(row['s50fecexi'],'%m/%d/%Y')
            cxc.valor = row['s50valor']
            cxc.aplicado = row['s50estado']
            cxc.save()

    with open('c:/ajusto/csv/s51movcxc.csv', 'r', encoding='latin-1') as file:
        csv_reader = csv.DictReader(file,delimiter=',')
        for row in csv_reader:
            cta_x_cob = CTAS_X_COBRAR.objects.filter(oficina = Oficina,cod_cxc=row['s51codcxc']).first()
            if cta_x_cob == None:
                continue
            xfecha = datetime.strptime(asignar_fecha(row['s51fecha'],'%m/%d/%Y'), "%Y-%m-%d")
            miDocConta = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = xfecha.year,codigo = 20 if row['s51clase'] == 'N' else int(row['s51clase'])).first()
            if miDocConta == None:
                print('No Hay Doc conta',cta_x_cob.cod_cxc)
                continue
            miHecEco = HECHO_ECONO.objects.filter(docto_conta = miDocConta,numero = row['s51documento']).first()
            if miHecEco == None:
                print('No Hay Hecho',cta_x_cob.cod_cxc)
                continue
            miDetCxc = CXC_DET.objects.filter(cuenta_x_cobrar = cta_x_cob,fecha = xfecha).first()
            if miDetCxc == None:
                miDetCxc = CXC_DET.objects.create(cuenta_x_cobrar = cta_x_cob,fecha = xfecha)
            
            miDetCxc.hecho_econo = miHecEco   
            miDetCxc.tip_mov = row['s51tipmov']
            miDetCxc.valor = row['s51capital']
            miDetCxc.save()

    print('Final   X Cobrar ..',datetime.now())

def activos_fijos():          # comprobantes() # 29.   59 minutos  al importar quitar ,00
    print('Activos Fijos.... ',datetime.now())
    try:
        conn = fdb.connect(
            dsn='C:\\Dinamica_solidaria\\DS_WEB\\DINSOL_WEB.FDB',  # Asegúrate de que la ruta sea correcta
            user='SYSDBA',
            password='masterkey',
            charset='latin1' 
        )
        print("Conexión establecida correctamente.")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return  # Salir si no se puede conectar
    cur = conn.cursor()
    try:
        cur.execute("select * from activosfijos")
        print("Consulta ejecutada correctamente.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        try:
            rows = cur.fetchall()
        except Exception as e:
            print("Error al obtener las filas:", e)
        finally:
            cur.close()
            conn.close()
    else:
        print("No se pudo obtener la descripción de las columnas. Puede que la consulta no haya retornado resultados.")
    if rows:
        for rownat in rows:
            row = dict(zip(columns, rownat))
            act_fij = ACTIVOS_FIJOS.objects.filter(oficina_id = 1,codigo = row['CODIGO'] ).first()
            if act_fij == None:
                act_fij = ACTIVOS_FIJOS.objects.create(oficina_id = 1,codigo = row['CODIGO'])
            act_fij.descripcion = row['DESCRIPCION']
            act_fij.fecha_de_alta = row['FEC_ALT']
            #deta_eco = row['codigo']
            act_fij.valor_elem = row['VALOR']
            act_fij.meses_dep = row['MES_DEP']
            act_fij.valor_salva = row['VAL_SAL'] 
            act_fij.dep_acu_vig_ant = row['DEPACUVIGANT']
            act_fij.det_acu_vig_ant = row['DETACUVIGANT']
            act_fij.val_acu_vig_ant = row['VALACUVIGANT']
            Cta = PLAN_CTAS.objects.filter(id_ds = row['ID_CTADEP']).first()
            if Cta != None:
                act_fij.cod_cta_dep = Cta.cod_cta
            Cta = PLAN_CTAS.objects.filter(id_ds = row['ID_CTADEPGAS']).first()
            if Cta != None:
                act_fij.cod_cta_dep_gas = Cta.cod_cta
            Cta = PLAN_CTAS.objects.filter(id_ds = row['ID_CTADET']).first()
            if Cta != None:
                act_fij.cod_cta_det = Cta.cod_cta
            Cta = PLAN_CTAS.objects.filter(id_ds = row['ID_CTADETGAS']).first()
            if Cta != None:
                act_fij.cod_cta_det_gas = Cta.cod_cta

            act_fij.de_baja = row['DE_BAJA']
            act_fij.save()

    print('Fin Act. Fijos ',datetime.now())

def ajstes_creditos():
    ctakap = '14433501'
    ctaint = '14433001'
    ctamor = '41504001'
    print('Ajustes Creditos.. ',datetime.now())
    registros = [
        {"cod_cre": "124382","cod_docto": 2,"numero": 128268,"fecha": date(2020,7,21),"Kap": 327337,"IntCor": 0,"IntMor": 0,"NitTer": "35262442"},
        {"cod_cre": "124382","cod_docto": 3,"numero": 54104,"fecha": date(2020,11,23),"Kap": 341197,"IntCor": 0,"IntMor": 0,"NitTer": "35262442"},
        {"cod_cre": "64042","cod_docto": 3,"numero": 70367,"fecha": date(2023,3,23),"Kap": 278328,"IntCor": 220338,"IntMor":1334,"NitTer": "40421432"},
        {"cod_cre": "129488","cod_docto": 3,"numero": 69805,"fecha": date(2023,5,28),"Kap": 505122,"IntCor": 590312,"IntMor":4586,"NitTer": "20440200"},
        {"cod_cre": "130428","cod_docto": 2,"numero": 133402,"fecha": date(2022,12,9),"Kap": 289655,"IntCor": 286459,"IntMor":3886,"NitTer": "1121876934"},
        {"cod_cre": "130821","cod_docto": 2,"numero": 134424,"fecha": date(2023,2,9),"Kap": 249622,"IntCor": 298163,"IntMor":2215,"NitTer": "21239886"},
        {"cod_cre": "131357","cod_docto": 2,"numero": 135728,"fecha": date(2023,9,21),"Kap": 283261,"IntCor": 215382,"IntMor":1357,"NitTer": "21176969"},
        {"cod_cre": "133930","cod_docto": 2,"numero": 134342,"fecha": date(2023,1,31),"Kap": 176585,"IntCor": 123164,"IntMor": 251,"NitTer": "1121922139"},
        {"cod_cre": "134050","cod_docto": 3,"numero": 75335,"fecha": date(2023,10,27),"Kap": 207414,"IntCor": 391269,"IntMor": 1317,"NitTer": "35262078"}
    ]
    for reg in registros:
        dcto = DOCTO_CONTA.objects.filter(oficina_id =1,per_con = reg['fecha'].year,codigo = reg['cod_docto']).first()
        comp = HECHO_ECONO.objects.filter(docto_conta = dcto,numero = reg['numero']).first()
        if comp == None:
            comp = HECHO_ECONO.objects.create(docto_conta = dcto,numero = reg['numero'])
        comp.fecha = reg['fecha']
        comp.save()
        detpro = DETALLE_PROD.objects.filter(hecho_econo = comp,producto = 'CR',concepto = 'CUOTA',subcuenta = reg['cod_cre']).first()
        if detpro == None:
            detpro = DETALLE_PROD.objects.create(hecho_econo = comp,producto = 'CR',concepto = 'CUOTA',subcuenta = reg['cod_cre'])
        detpro.valor = -reg['Kap']-reg['IntCor']-reg['IntMor']
        detpro.save()
        ter = TERCEROS.objects.filter(cliente_id = 1,doc_ide = reg['NitTer']).first()
        if ter == None:
            print('terce no existe',reg['NitTer'])
        ctaKap = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = reg['fecha'].year,cod_cta = ctakap).first()
        ctaIntCor = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = reg['fecha'].year,cod_cta = ctaint).first()
        ctaIntMor = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = reg['fecha'].year,cod_cta = ctamor).first()
        if reg['Kap'] == 0:
            continue
        detecok = DETALLE_ECONO.objects.filter(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'Kapita',tercero = ter,cuenta = ctaKap).first()
        if detecok == None:
            detecok = DETALLE_ECONO.objects.create(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'Kapita',tercero = ter,cuenta = ctaKap)
            detecok.debito = 0
            detecok.credito = 0
        print('Kap ',reg['Kap'])
        detecok.valor_2 = reg['Kap']
        detecok.detalle = 'xCred='+reg['cod_cre']
        detecok.save()
        print('Que da ',detecok.id)
        if reg['IntCor'] == 0:
            continue
        detecoi = DETALLE_ECONO.objects.filter(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'IntCor',tercero = ter,cuenta = ctaIntCor).first()
        if detecoi == None:
            detecoi = DETALLE_ECONO.objects.create(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'IntCor',tercero = ter,cuenta = ctaIntCor)
            detecoi.debito = 0
            detecoi.credito = 0
        detecoi.valor_2 = reg['IntCor']
        detecoi.detalle = 'xCred='+reg['cod_cre']
        detecoi.save()
        if reg['IntMor'] == 0:
            continue
        detecom = DETALLE_ECONO.objects.filter(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'IntMor',tercero = ter,cuenta = ctaIntMor).first()
        if detecom == None:
            detecom = DETALLE_ECONO.objects.create(hecho_econo = comp,detalle_prod = detpro,item_concepto = 'IntMor',tercero = ter,cuenta = ctaIntMor)
            detecom.debito = 0
            detecom.credito = 0
        detecom.valor_2 = reg['IntMor']
        detecom.detalle = 'xCred='+reg['cod_cre']
        detecom.save()
    print('Fin Ajuste Creditos',datetime.now())

from datetime import datetime

def canje_ahorros():
    print('Grabar Canje Ahorros   ',datetime.now())
    Cliente = CLIENTES.objects.filter(codigo='A').first()
    Oficina = OFICINAS.objects.filter(codigo='A0001').first()
    CANJE_AHORROS.objects.all().delete()
    with open('c:/ajusto/csv/s32cangeaho.csv', 'r') as file:
        csv_reader = csv.DictReader(file, delimiter=',')
        for row in csv_reader:
            fecha1 = datetime.strptime(row['s32fecha1'], '%m/%d/%Y').date()
            if fecha1.year<2019:
                continue
            valor2 = row['s32fecha2'].strip()
            if valor2 and valor2 != '/  /':
                try:
                    fecha2 = datetime.strptime(valor2, '%m/%d/%Y').date()
                except ValueError:
                    fecha2 = None  # o maneja el error como desees
            else:
                fecha2 = None
            xdc = XDOC_ZEP.objects.filter(per_con = fecha1.year,clase_zep = row['s32clase']).first()
            if xdc == None:
                print(' clase no aparece ',row['s32clase'])
                continue
            xdoc = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = fecha1.year,codigo = xdc.doc_ds).first()
            if xdoc == None:
                print('codigo documentono existe ',xdc.doc_ds)
                continue
            xhec_eco1 = HECHO_ECONO.objects.filter(docto_conta = xdoc,numero = int(row['s32documento'])).first()
            if xhec_eco1 == None:
                print('No hay Hecho Economico ','doc ',xdoc.codigo,'   ',int(row['s32documento'])) 
                continue
            xcta_aho = CTAS_AHORRO.objects.filter(oficina = Oficina,num_cta = row['s32numcta']).first()
            if xcta_aho == None:
                print('No hay cuenta de ahorros ',row['s32numcta']) 
                continue
            print('hecho econo ',xhec_eco1)
            xcan_aho = CANJE_AHORROS.objects.create(oficina = Oficina, hec_eco_1 = xhec_eco1,num_cta = row['s32numcta'],cta_aho = xcta_aho,fecha_1 = fecha1)
            xcan_aho.valor_1 = int(row['s32valor'])
            xcan_aho.fecha_2 = fecha2
            xcan_aho.valor_2 = int(row['s32valor'])
            xcan_aho.estado = row['s32estado']
            if fecha2 != None:
                xdc1 = XDOC_ZEP.objects.filter(per_con = fecha2.year,clase_zep = row['s32nvoclase']).first()
                if xdc1 == None:
                    print(' clase1 no aparece ',row['s32nvoclase'])
                    xcan_aho.save()
                    continue
                xdoc1 = DOCTO_CONTA.objects.filter(oficina = Oficina,per_con = fecha2.year,codigo = xdc1.doc_ds).first()
                if xdoc == None:
                    print('codigo documentono 2 no existe ',xdc1.doc_ds)
                    xcan_aho.save()
                    continue
                xhec_eco2 = HECHO_ECONO.objects.filter(docto_conta = xdoc1,numero = int(row['s32nvodcto'])).first()
                if xhec_eco2 == None:
                    print('No hay Hecho Economico 2') 
                xcan_aho.hec_eco_2 = xhec_eco2
            xcan_aho.save()

            #print(row['s32clase'])
            #print(row['s32documento'])
            #print(row['s32numcta'])
            #print(row['s32fecha1'])
            #print(row['s32fecha2'])
            #print(row['s32valor'])
            #print(row['s32estado'])
            #print(row['s32nvoclase'])
            #print(row['s32nvodcto'])
            #print(row['s32clase'])
            
    print('Terrmina Canje Ahorros ',datetime.now())

from django.db.models import Max

def ctas_ahorro_cancela():
    print('ctas_ahorro_cancela ',datetime.now())
    cuentas = CTAS_AHORRO.objects.filter(oficina_id=1, est_cta='C')
    for cuenta in cuentas:
        movimientos = DETALLE_PROD.objects.filter(
            subcuenta=cuenta.num_cta,
            producto='AH',
            concepto='AHO',
            hecho_econo__docto_conta__oficina_id=1
        ).annotate(
            fecha_hecho=F('hecho_econo__fecha')
        ).order_by('-hecho_econo__fecha')
        if movimientos.exists():
            fecha_max = movimientos.aggregate(ultima_fecha=Max('hecho_econo__fecha'))['ultima_fecha']
            cuenta.fec_cancela = fecha_max
            cuenta.save()
    
from django.db.models import F, Sum, Count, ExpressionWrapper, FloatField, Q
from django.db.models.functions import Cast

def ajus_mov_cre_fin():
    print('ctas_ahorro_cancela ',datetime.now())
    
    resultados = DETALLE_PROD.objects.filter(producto='CR').annotate(
        numero=F('hecho_econo__numero'),
        fecha=F('hecho_econo__fecha'),
        count_de=Count('detalle_econo'),
        sum_dp_valor=Sum('valor'),
        sum_de_dif=Sum(F('detalle_econo__valor_1') - F('detalle_econo__valor_2')),
    ).annotate(
        avg_dp_valor=ExpressionWrapper(
            F('sum_dp_valor') / Cast(F('count_de'), FloatField()), output_field=FloatField()
        )
    ).filter(
        ~Q(avg_dp_valor=F('sum_de_dif'))  # HAVING SUM(dp.valor)/COUNT(*) <> SUM(de.valor_1 - de.valor_2)
    ).values(
        'numero', 'id', 'subcuenta', 'concepto', 'fecha', 
        'avg_dp_valor', 'sum_de_dif', 'count_de'
    )
    i = 0
    for fila in resultados:
        i = i +1  
        if fila['subcuenta'] == '124382':
            continue
        xAgno = fila['fecha'].year
        CtaPteKap = PLAN_CTAS.objects.filter(cliente_id = 1,per_con = xAgno,cod_cta = '14433501').first()
        if CtaPteKap == None:
            continue
        mi_dep_pro = DETALLE_PROD.objects.filter(id = fila['id']).first()
        if mi_dep_pro == None:
            continue
        mi_cre = CREDITOS.objects.filter(oficina_id = 1,cod_cre = fila['subcuenta']).first()
        if mi_cre == None:
            continue
        val_apl_kap = -mi_dep_pro.valor + fila['sum_de_dif']
        print(fila['subcuenta'],'  ',mi_dep_pro.valor ,'  ',fila['sum_de_dif'],val_apl_kap)
        DETALLE_ECONO.objects.create(hecho_econo_id = mi_dep_pro.hecho_econo_id,detalle_prod_id = mi_dep_pro.id,
            cuenta_id =  CtaPteKap.id,item_concepto = 'Kapita',detalle = 'NueKap'+fila['subcuenta'],
            tercero_id = mi_cre.socio.tercero.id, debito=0,credito=0,valor_1=0,valor_2=val_apl_kap) 


    print('I ',i)


def init():
    print('Entro')
    #inicio()  # 1. Esto es primero
    #terceros()  # 2.           Paso directo de firebird a maria db   general
    #pagadores() # 3.                                   **YA** (encoding='latin-1')    general
    #plan_ctas() # 4.           Paso directo de firebird a maria db        general
    #ciiu()      #  general                 
    #conceptos() # 5.      general                             **YA**
    #docto_conta() # 6.         Paso directo de firebird a maria db   general
    #linaho() # 7.              ahorros                         **YA**
    #destino_cre() # 8.         creditos                         **YA**
    #lineas_credito() # 9.      creditos                        
    #cat_des_dia_cre() # 10.    creditos
    #ret_fue_aho() # 11.        ahorros 
    #int_lin_aho() # 12.        ahorros
    #imp_con_lin_aho() # 13.    ahorros
    #imp_con_cre() # 14.        creditos
    #imp_con_cre_int() # 15.    creditos
         #usuarios() # 16.    Pendiente
    #cierre_mes() # 17.       cierres
           #mov_caja() # 18.  penDiEnte
    #plan_aportes() # 19.     aportes
    #socios() # 20.           socios
    #ctas_aho() # 21.         ahorros 

    cta_cdat() # 22.         ahorros 
    cta_cdat_amp() # 23.     ahorros
    cta_cda_liq() # 24.      ahorros
    #creditos() # 25. NO EXPORTA DE FOXPRO TOCA MANUALMENTE     #  10 Min   creditos
    #categorizacion() # 26.  24 min       creditos
    #est_fin() # 27.          socios
    #bene_aso() # 28.         socios
    #referencias() # 29.      socios 
    #comprobantes() # 30.     contabilidad
    #importar_mov_cre() # 31.      #  36 Min   creditos
    #catego_detalle()  # 32  tabla encontrada cxc_creditos  creditos
    #tablas_de_referencia()   #  33   per_esp
    detalle_econo('c:/ajusto/csv/doctos_16_19.csv')     #  34  contabilidad    33 minutos   abril 20 2025
    #detalle_econo('c:/ajusto/csv/doctos_20_25.csv')  # doctos_20_25  contabilidad  #  cambiar , po .  33 minutos   abril 20 2025
    #grabar_causa_cre()    #   35  42 Min  creditos se debe importar completamente 
    detalle_prod()          #  36  28 Min     #   ?????  37   90 minutos  queda en suspenso
    deta_eco_aho()      #   38  70 Min   es s06movaho  ahorros
    #grabar_credito_mod()        #   39   py manaGe.Py 55 min  creditos en el servidir  actualiza cambios_cre
    #grabar_credito_mod2()    #   40   24 min   actualiza cambios_cre  creditos  cuando no encontro en grabar_credito_mod
    #asigna_con_cre()  #   41  creditos SELECT COUNT(*) FROM detalle_econo WHERE Detalle NOT LIKE 'Nuevo%' update detalle_econo SET valor_2 = 0 WHERE valor_2 IS NULL
    #                    #asigna_com_cre()   #   debe retirarse
# #vMov_cre()              #   44  RAPIDO  pero no es necesario
    #asigna_sal_ini_apor()  #  aportes 
    #asigna_rev_aportes()    # aportes
                 #huerfanos_aho()  #   46  RAPIDO
    #asigna_desem()   #  creditos
    sal_ini_aho()
    ImpIntDiaAho()       #  ahorros  xMovIntCtaAho.csv cambiar , por .  demora 70 min
    
    int_mensual_aho()  #  ahorros la ultima por que faltaba interes mensual ctas 01 y otras
    cargue_ajuste_saldos_ahorros()   #  ahorros
    canje_ahorros()    #  ahorros
    ajustar_saldo_ahorros()   #  ahorros
    #CuentasXCobrar()
        #prueba()                #   45  RAPIDO  no es necesario
    #activos_fijos()    #  46  nuevo
    #ajstes_creditos()   #  creditos
    #ajustar_saldo_aportes()   #  aportes
    ctas_ahorro_cancela()     #  ahorros
    #ters = TERCEROS.objects.filter(cliente_id = 1)
    #for ter in ters:
    #    ter.save()
    #probar_redis()
    #ajus_mov_cre_fin()   # creditos
    print('Final Migracion   ',datetime.now())


import redis

def probar_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("Redis está disponible ✅")
    except redis.exceptions.ConnectionError as e:
        print("No se pudo conectar a Redis ❌")
        print(e)

init()