from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    piso_puerta = models.CharField(max_length=20, verbose_name='Piso / Puerta')
    edificio = models.CharField(max_length=100, verbose_name='Edificio')

    def __str__(self):
        return f'{self.usuario.username} - {self.edificio}'


class Incidencia(models.Model):
    CATEGORIAS = [
        ('agua', 'Agua'),
        ('electricidad', 'Electricidad'),
        ('limpieza', 'Limpieza'),
        ('seguridad', 'Seguridad'),
        ('otros', 'Otros'),
    ]
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelta', 'Resuelta'),
        ('cerrada', 'Cerrada'),
    ]

    titulo = models.CharField(max_length=150, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, verbose_name='Categoría')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    foto = models.ImageField(upload_to='incidencias/', blank=True, null=True)
    nota_interna = models.TextField(blank=True, verbose_name='Nota interna (solo admin)')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidencias')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    @property
    def color_estado(self):
        colores = {
            'pendiente': 'warning',
            'en_proceso': 'info',
            'resuelta': 'success',
            'cerrada': 'secondary',
        }
        return colores[self.estado]

    
    def delete(self, *args, **kwargs):
        if self.foto:
            self.foto.delete(save=False)
        super().delete(*args, **kwargs)


class Comentario(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(verbose_name='Comentario')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'{self.autor.username}: {self.texto[:30]}'