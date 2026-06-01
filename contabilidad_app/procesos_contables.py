from django.db import connection

from cuentas_app.models import PLAN_CTAS
from hecho_economico_app.models import HECHO_ECONO
from documentos_app.models import DOCTO_CONTA
from detalle_producto_app.models import DETALLE_PROD
from detalle_economico_app.models import DETALLE_ECONO
from terceros_app.models import TERCEROS
from clientes_app.models import CLIENTES
from oficinas_app.models import OFICINAS

def saldo_anterior(id_cli, id_ofi, fec_ini, fec_fin, cta_ini, cta_fin, con_cierre, doc_ide):
        with connection.cursor() as cursor:
            query = '''
            SELECT pc.cod_cta AS cod_cta,
                pc.nom_cta AS nom_cta,
                '' AS doc_ide,
                '' AS raz_soc,
                0 AS docto,
                0 AS numero,
                DATE_SUB(%s, INTERVAL 1 DAY) AS fecha,
                'Saldo Anterior' AS detalle,
                '0' AS id_dc,
                0 AS debito,
                0 AS credito,
                SUM(de.debito - de.credito) AS sal_acu
            FROM detalle_econo de
            INNER JOIN (
                SELECT he.ID AS id,
                    he.fecha AS fecha,
                    dc.codigo AS cod_doc,
                    dc.nom_cto AS nom_doc,
                    he.numero AS numero
                FROM hecho_econo he
                INNER JOIN oficinas fi ON fi.id = %s
                INNER JOIN docto_conta dc ON dc.id = he.docto_conta_id
                                        AND dc.oficina_id = fi.id
                                        AND YEAR(he.fecha) = dc.per_con
                                        AND (%s = 'S' OR (%s = 'N' AND dc.codigo != 255))
                WHERE ((he.fecha = %s AND YEAR(he.fecha) >= YEAR(%s))
                    OR (dc.codigo = 0 AND YEAR(he.fecha) = YEAR(%s)))
                AND he.anulado = 'N' 
                AND (%s IS NULL OR te.doc_ide = %s)
            ) AS co ON co.id = de.hecho_econo_id
            INNER JOIN plan_ctas AS pc ON pc.cliente_id = %s
                                        AND pc.id = de.cuenta_id
                                        AND pc.cod_cta >= %s
                                        AND pc.cod_cta <= %s
            GROUP BY cod_cta, nom_cta
            UNION ALL
            SELECT pc.cod_cta AS cod_cta,
                pc.nom_cta AS nom_cta,
                te.doc_ide AS doc_ide,
                te.nombre AS raz_soc,
                co.cod_doc AS docto,
                co.numero AS numero,
                co.fecha AS fecha,
                de.detalle AS detalle,
                de.id_ds AS id_dc,
                de.debito AS debit0,
                de.credito AS credito,
                0.0 AS sal_acu
            FROM detalle_econo de
            INNER JOIN (
                SELECT he.ID AS id,
                    he.fecha AS fecha,
                    dc.codigo AS cod_doc,
                    dc.nom_cto AS nom_doc,
                    he.numero AS numero
                FROM hecho_econo he
                INNER JOIN oficinas fi ON fi.id = %s
                INNER JOIN docto_conta dc ON dc.id = he.docto_conta_id
                                        AND dc.oficina_id = fi.id
                                        AND YEAR(he.fecha) = dc.per_con
                                        AND (%s = 'S' OR (%s = 'N' AND dc.codigo != 255))
                WHERE he.fecha >= %s
                AND he.fecha <= %s
                AND dc.codigo != 0
                AND he.anulado = 'N'
                AND (%s IS NULL OR te.doc_ide = %s)
            ) AS co ON co.id = de.hecho_econo_id
            INNER JOIN plan_ctas AS pc ON pc.cliente_id = %s
                                        AND pc.id = de.cuenta_id
                                        AND pc.cod_cta >= %s
                                        AND pc.cod_cta <= %s
            INNER JOIN terceros te ON te.id = de.tercero_id
            AND (%s IS NULL OR te.doc_ide = %s)
            ORDER BY 1, 2, 7, 5, 6
        '''
            params = [
                fec_ini,  # %s para DATE_SUB
                id_ofi,   # %s para INNER JOIN oficinas
                con_cierre,  # %s para el primer AND en docto_conta
                con_cierre,  # %s para el segundo AND en docto_conta
                fec_ini,  # %s para el primer DATE en WHERE
                fec_ini,  # %s para el segundo DATE en WHERE
                fec_ini,  # %s para YEAR en el tercer DATE en WHERE
                id_cli,   # %s para INNER JOIN plan_ctas
                cta_ini,  # %s para AND pc.cod_cta >=
                cta_fin,  # %s para AND pc.cod_cta <=
                id_ofi,   # %s para INNER JOIN oficinas en UNION ALL
                con_cierre,  # %s para el primer AND en docto_conta en UNION ALL
                con_cierre,  # %s para el segundo AND en docto_conta en UNION ALL
                fec_ini,  # %s para el primer DATE en WHERE en UNION ALL
                fec_fin,  # %s para el segundo DATE en WHERE en UNION ALL
                id_cli,   # %s para INNER JOIN plan_ctas en UNION ALL
                cta_ini,  # %s para AND pc.cod_cta >= en UNION ALL
                cta_fin,  # %s para AND pc.cod_cta <= en UNION ALL
                doc_ide,  # %s para el filtro por te.doc_ide en ambas consultas
                doc_ide,  # %s para el filtro por te.doc_ide en UNION ALL
            ]

            cursor.execute(query, params)
            results = cursor.fetchall()
            # Define los nombres de los campos como una lista
            columns = ['cod_cta', 'nom_cta', 'doc_ide', 'raz_soc', 'docto',
                'numero', 'fecha', 'detalle', 'id_dc', 'debito', 'credito', 'sal_acu']
            results_dict = [dict(zip(columns, row)) for row in results]

        return results_dict



def BALANCE_DE_PRUEBA(id_cli, id_ofi, PER_CON, tip_cta, fec_ini, fec_fin, cta_ini, cta_fin, con_cierre):
        with connection.cursor() as cursor:
            query = '''
            SELECT CU.cod_cta AS cod_cta,
                CU.nom_cta AS nom_cta,
                TIP_CTA AS TIPO,
                SUM(0+COALESCE(SALDOS.SALINI,0)) AS SALINI,
                SUM(0+COALESCE(SALDOS.DEB,0)) AS DEBITOS,
                SUM(0+COALESCE(SALDOS.CRE,0)) AS CREDITOS,
                SUM(0+COALESCE(SALDOS.SALINI,0))+SUM(0+COALESCE(SALDOS.DEB,0))-SUM(0+COALESCE(SALDOS.CRE,0)) AS SALDO
            FROM PLAN_CTAS AS CU
            INNER JOIN CLIENTES AS CL ON CL.ID_CLI = %s AND CL.ID_CLI = CU.cliente_id
            LEFT JOIN (SELECT CU1.ID AS IDC,CU1.COD_CTA AS COD_CTA,
                                0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,CO.FECHA,:FEC_INI) > 0
                                OR DO.COD_DOC = 0 OR DO.COD_DOC = 100 THEN DT.DEBITO-DT.CREDITO ELSE 0 END),0) AS SALINI,
                                0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,:FEC_INI,CO.FECHA) >= 0 AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >= 0
                                    AND DO.COD_DOC <> 0 AND DO.COD_DOC <> 100 THEN DT.DEBITO ELSE 0 END),0) AS DEB,
                                0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,:FEC_INI,CO.FECHA) >= 0 AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >= 0
                                    AND DO.COD_DOC <> 0 AND DO.COD_DOC <> 100 THEN DT.CREDITO ELSE 0 END),0) AS CRE                          
                            FROM DETALLES_COM AS DT
                                INNER JOIN COMPROBANTES AS CO ON CO.ID = DT.ID_COM
                                INNER JOIN DOCUMENTOS AS DO ON DO.ID = CO.ID_DOC AND DO.PER_CON = :PER_CON
                                INNER JOIN CUENTAS AS CU1 ON CU1.ID = DT.ID_CTA  AND CU1.PER_CON = :PER_CON AND CU1.TIP_CON = :TIP_CON                     
                                INNER JOIN OFICINAS AS AG ON AG.ID_CL = %s AND AG.ID = DO.ID_AGE
                                AND ((AG.COD_AGE = :COD_AGE AND :FILIALES = 'N') 
                                    OR (:COD_AGE = SUBSTRING(AG.COD_AGE FROM 1 FOR CHAR_LENGTH(TRIM(:COD_AGE))) 
                                        AND :FILIALES = 'S'))
                            WHERE CO.ID = DT.ID_COM AND CO.ANULADO = 'N'
                                AND EXTRACT(YEAR FROM CO.FECHA) = :PER_CON
                        /*      AND DATEDIFF(DAY,:FEC_INI,CO.FECHA) >=0  */
                                AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >=0 
                                AND ((:CONCIERRE = 'S' OR (:CONCIERRE = 'N' AND DO.COD_DOC != 255)))  
                            GROUP BY CU1.ID,CU1.COD_CTA) AS SALDOS ON SALDOS.IDC = CU.ID 
            WHERE CU.PER_CON = :PER_CON AND CU.TIP_CON = :TIP_CON 
                AND CU.COD_CTA >= :CTA_INI AND CU.COD_CTA <= :CTA_FIN
            GROUP BY CU.COD_CTA,CU.TIP_CTA,CU.NOMBRE  
            ORDER BY CU.COD_CTA,CU.NOMBRE
            INTO :COD_CTA,:NOM_CTA,:TIP_CTA,:SALANT,:DEBITO,:CREDITO,:SALDO'
        '''
            params = [
                fec_ini,  # %s para DATE_SUB
                id_ofi,   # %s para INNER JOIN oficinas
                con_cierre,  # %s para el primer AND en docto_conta
                con_cierre,  # %s para el segundo AND en docto_conta
                fec_ini,  # %s para el primer DATE en WHERE
                fec_ini,  # %s para el segundo DATE en WHERE
                fec_ini,  # %s para YEAR en el tercer DATE en WHERE
                id_cli,   # %s para INNER JOIN plan_ctas
                cta_ini,  # %s para AND pc.cod_cta >=
                cta_fin,  # %s para AND pc.cod_cta <=
                id_ofi,   # %s para INNER JOIN oficinas en UNION ALL
                con_cierre,  # %s para el primer AND en docto_conta en UNION ALL
                con_cierre,  # %s para el segundo AND en docto_conta en UNION ALL
                fec_ini,  # %s para el primer DATE en WHERE en UNION ALL
                fec_fin,  # %s para el segundo DATE en WHERE en UNION ALL
                id_cli,   # %s para INNER JOIN plan_ctas en UNION ALL
                cta_ini,  # %s para AND pc.cod_cta >= en UNION ALL
                cta_fin,  # %s para AND pc.cod_cta <= en UNION ALL
                doc_ide,  # %s para el filtro por te.doc_ide en ambas consultas
                doc_ide,  # %s para el filtro por te.doc_ide en UNION ALL
            ]
            
            cursor.execute(query, params)
                results = cursor.fetchall()
                # Define los nombres de los campos como una lista
                columns = ['cod_cta', 'nom_cta', 'doc_ide', 'raz_soc', 'docto',
                'numero', 'fecha', 'detalle', 'id_dc', 'debito', 'credito', 'sal_acu']
                results_dict = [dict(zip(columns, row)) for row in results]
        return results_dict




# RETURNS (
#  COD_CTA   D_CODCTA,
#  NOM_CTA   D_STR128,
#  TIP_CTA   D_TIPCTA,
#  SALANT    D_MONEDA,
#  DEBITO    D_MONEDA,
#  CREDITO   D_MONEDA,
#  SALDO     D_MONEDA)
# AS 
# BEGIN
#   FOR SELECT CU.COD_CTA AS COD_CTA,
#         CU.NOMBRE AS NOM_CTA,
#         TIP_CTA AS TIPO,
#         SUM(0+COALESCE(SALDOS.SALINI,0)) AS SALINI,
#         SUM(0+COALESCE(SALDOS.DEB,0)) AS DEBITOS,
# 	    SUM(0+COALESCE(SALDOS.CRE,0)) AS CREDITOS,
#         SUM(0+COALESCE(SALDOS.SALINI,0))+SUM(0+COALESCE(SALDOS.DEB,0))-SUM(0+COALESCE(SALDOS.CRE,0)) AS SALDO
#     FROM CUENTAS AS CU
#       INNER JOIN CLIENTES AS CL ON CL.ID_CL = :ID_CL AND CL.ID_CL = CU.ID_CL
#       LEFT JOIN (SELECT CU1.ID AS IDC,CU1.COD_CTA AS COD_CTA,
#                      0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,CO.FECHA,:FEC_INI) > 0
#                        OR DO.COD_DOC = 0 OR DO.COD_DOC = 100 THEN DT.DEBITO-DT.CREDITO ELSE 0 END),0) AS SALINI,
#                      0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,:FEC_INI,CO.FECHA) >= 0 AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >= 0
#                           AND DO.COD_DOC <> 0 AND DO.COD_DOC <> 100 THEN DT.DEBITO ELSE 0 END),0) AS DEB,
#                      0+COALESCE(SUM(CASE WHEN DATEDIFF(DAY,:FEC_INI,CO.FECHA) >= 0 AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >= 0
#                           AND DO.COD_DOC <> 0 AND DO.COD_DOC <> 100 THEN DT.CREDITO ELSE 0 END),0) AS CRE                          
#                    FROM DETALLES_COM AS DT
#                      INNER JOIN COMPROBANTES AS CO ON CO.ID = DT.ID_COM
#                      INNER JOIN DOCUMENTOS AS DO ON DO.ID = CO.ID_DOC AND DO.PER_CON = :PER_CON
#                      INNER JOIN CUENTAS AS CU1 ON CU1.ID = DT.ID_CTA  AND CU1.PER_CON = :PER_CON AND CU1.TIP_CON = :TIP_CON                     
#                      INNER JOIN AGENCIAS AS AG ON AG.ID_CL = :ID_CL AND AG.ID = DO.ID_AGE
#                        AND ((AG.COD_AGE = :COD_AGE AND :FILIALES = 'N') 
#                           OR (:COD_AGE = SUBSTRING(AG.COD_AGE FROM 1 FOR CHAR_LENGTH(TRIM(:COD_AGE))) 
#                               AND :FILIALES = 'S'))
#                    WHERE CO.ID = DT.ID_COM AND CO.ANULADO = 'N'
#                      AND EXTRACT(YEAR FROM CO.FECHA) = :PER_CON
#                /*      AND DATEDIFF(DAY,:FEC_INI,CO.FECHA) >=0  */
#                      AND DATEDIFF(DAY,CO.FECHA,:FEC_COR) >=0 
#                      AND ((:CONCIERRE = 'S' OR (:CONCIERRE = 'N' AND DO.COD_DOC != 255)))  
#                    GROUP BY CU1.ID,CU1.COD_CTA) AS SALDOS ON SALDOS.IDC = CU.ID 
#    WHERE CU.PER_CON = :PER_CON AND CU.TIP_CON = :TIP_CON 
#      AND CU.COD_CTA >= :CTA_INI AND CU.COD_CTA <= :CTA_FIN
#   GROUP BY CU.COD_CTA,CU.TIP_CTA,CU.NOMBRE  
#   ORDER BY CU.COD_CTA,CU.NOMBRE
#   INTO :COD_CTA,:NOM_CTA,:TIP_CTA,:SALANT,:DEBITO,:CREDITO,:SALDO 
#   DO
#   BEGIN 
#     SUSPEND;
#   END
# END



def saldo_aportes_fecha(id_oficina, subcuenta, fecha_corte):
        with connection.cursor() as cursor:
            query = '''
            SELECT 
                MAX(he.fecha) AS fec_ult_apo
            FROM DETALLE_PROD dp
            JOIN HECHO_ECONO he ON dp.hecho_econo_id = he.id
            JOIN DOCTO_CONTA dc ON he.docto_conta_id = dc.id
            WHERE 
                dp.producto = 'AP'
                AND dp.subcuenta = %s
                AND he.fecha <= %s
                AND dc.oficina_id = %s
            GROUP BY dp.subcuenta
            LIMIT 1;
        '''
            params = [
                subcuenta,  # %s para DATE_SUB
                fecha_corte,   # %s para INNER JOIN oficinas
                id_oficina
            ]

            cursor.execute(query, params)
            resultado = cursor.fetchall()
            # Define los nombres de los campos como una lista
            columns = ['fec_ult_apo']
            resultados = [dict(zip(columns, row)) for row in resultado]

        return resultados

