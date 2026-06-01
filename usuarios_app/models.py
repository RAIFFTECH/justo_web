from django.db import models
from django.db import models
from oficinas_app.models import OFICINAS
from terceros_app.models import TERCEROS
from justo_app.opciones import OPC_BOOL
from django.contrib.auth.models import User
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oficina = models.ForeignKey(OFICINAS, on_delete=models.PROTECT, null=True, verbose_name='Oficina')
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    activo = models.CharField(max_length=1, choices=OPC_BOOL, verbose_name='Está Activo?')
    
    class Meta:
        db_table = 'user_profile' 
        
    def __str__(self):
        return self.user.username

