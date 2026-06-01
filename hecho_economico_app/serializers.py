from .models import HECHO_ECONO
from detalle_economico_app.models import DETALLE_ECONO
from terceros_app.models import TERCEROS
from cuentas_app.models import PLAN_CTAS
from detalle_producto_app.models import DETALLE_PROD
from rest_framework import serializers

class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLAN_CTAS
        fields = ['per_con','cod_cta','nom_cta','tip_cta']

class TerceroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TERCEROS
        fields = ['cla_doc','doc_ide','dig_ver','nit_rap','cod_ciu_exp','cod_ciu_res','regimen','fec_exp_ced','tip_ter',
            'pri_ape','seg_ape','pri_nom','seg_nom','raz_soc','direccion','cod_pos','tel_ofi','tel_res','celular1','celular2',
            'fax','email','nombre','fec_act','observacion','per_pub_exp','nit_interno']

class DetalleEconoSerializer(serializers.ModelSerializer):
    cuenta = CuentaSerializer()
    tercero = TerceroSerializer()
    class Meta:
        model = DETALLE_ECONO
        fields = '__all__'


class DetalleProdSerializer(serializers.ModelSerializer):
    detalles_econo = DetalleEconoSerializer(many=True, read_only=True)
    class Meta:
        model = DETALLE_PROD
        fields = '__all__'

class HechoEconoListadoSerializer(serializers.ModelSerializer):
    detalles_prod = DetalleProdSerializer(many=True, read_only=True)
    detalles_econo = DetalleProdSerializer(many=True, read_only=True)
    docto_conta_codigo = serializers.CharField(source='docto_conta.codigo', read_only=True)
    docto_conta_nom_cto = serializers.CharField(source='docto_conta.nom_cto', read_only=True)
    docto_conta_nombre = serializers.CharField(source='docto_conta.nombre', read_only=True)
    docto_conta_consecutivo = serializers.CharField(source='docto_conta.consecutivo', read_only=True)

    class Meta:
        model = HECHO_ECONO
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

class DetalleEcoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DETALLE_ECONO
        fields = ['id', 'debito', 'credito']


class DetalleProSerializer(serializers.ModelSerializer):
    class Meta:
        model = DETALLE_PROD
        fields = ['id', 'producto', 'concepto','valor']

class HecoEcono(serializers.ModelSerializer):
    items = DetalleProSerializer(many=True, read_only=True)
    class Meta:
        model = HECHO_ECONO
        fields = ['id', 'numero', 'fecha','descripcion','anulado','protegido','canal','docto_conta_id']
