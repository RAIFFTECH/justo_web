from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import CAJEROS
from .forms import CajerosForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from terceros_app.models import TERCEROS
import json
from django.contrib.auth.models import User
from oficinas_app.models import OFICINAS

# Crear
class CajeroCreateView(CreateView):
    model = CAJEROS
    form_class = CajerosForm
    template_name = 'cajeros_form.html'
    success_url = reverse_lazy('cajeros_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation'] = 'create'  # Definir la operación como 'create'
        return context

    def form_valid(self, form):
        # Guarda la instancia principal del modelo CAJEROS
        response = super().form_valid(form)
        
         # Manejar los campos adicionales relacionados con el modelo "tercero"
        doc_ide = form.cleaned_data.get('doc_ide')
        activo = self.request.POST.get('activo', '').strip()
        print('activo ',activo)
        if self.object.tercero and doc_ide:
             self.object.tercero.doc_ide = doc_ide
             self.object.tercero.save()  # Guarda los cambios en el modelo relacionado
        return response
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            data = json.loads(request.body)
            print('Datos recibidos:', data)
            if 'user' not in data or 'oficina' not in data:
                return JsonResponse({'error': 'Campos de usuario o oficina faltantes'}, status=400)
            try:
                user = User.objects.get(id=data['user'])
                oficina = OFICINAS.objects.get(id=data['oficina'])
            except user.DoesNotExist:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=400)
            except oficina.DoesNotExist:
                return JsonResponse({'error': 'Oficina no encontrada'}, status=400)
            tercero = TERCEROS.objects.filter(cliente_id = 1,doc_ide = data['doc_ide']).first()
            print('activo   ',data['activo'])
            if tercero == None:
                return JsonResponse({'error': 'Tercero No existe'}, status=400)
            cajero = CAJEROS(
                user=user,
                oficina=oficina,
                tercero=tercero,
                fecha_ingreso=data['fecha_ingreso'],
                fecha_retiro=data['fecha_retiro'],
                activo='S' if data['activo'] == 'on' else 'N',
                cta_con_caja=data['cta_con_caja'],
                cta_con_acre=data['cta_con_acre']
            )

            try:
                # Guardar directamente la instancia
                cajero.save()
                return JsonResponse({'success': 'Cajero registrado correctamente.'})
            except Exception as e:
                # Capturar errores y manejarlos
                print('Error al guardar el cajero:', str(e))
                return JsonResponse({'error': 'Error al guardar el cajero.', 'details': str(e)}, status=400)



# Actualizar
class CajeroUpdateView(UpdateView):
    model = CAJEROS
    form_class = CajerosForm
    template_name = 'cajeros_form.html'
    success_url = reverse_lazy('cajeros_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation'] = 'update'  # Definir la operación como 'create'
        cajero = self.object  # Instancia del modelo CAJEROS que se está editando

        # Obtenemos el tercero relacionado
        tercero = cajero.tercero
        context['doc_ide'] = tercero.doc_ide if tercero else ""
        context['nombre'] = tercero.nombre if tercero else "Tercero Inválido"
        return context

    def form_valid(self, form):
        # Actualiza la relación con el tercero basado en el `doc_ide` proporcionado
        doc_ide = self.request.POST.get('doc_ide', '').strip()
        activo = self.request.POST.get('activo', '').strip()
        try:
            tercero = TERCEROS.objects.get(doc_ide=doc_ide)
        except TERCEROS.DoesNotExist:
            tercero = None

        # Asigna el tercero al cajero y guarda
        form.instance.tercero = tercero
        return super().form_valid(form)

# Eliminar
class CajeroDeleteView(DeleteView):
    model = CAJEROS
    template_name = 'cajeros_confirm_delete.html'
    success_url = reverse_lazy('cajeros_list')

# Listar
class CajeroListView(ListView):
    model = CAJEROS
    template_name = 'cajeros_list.html'
    context_object_name = 'cajeros'
