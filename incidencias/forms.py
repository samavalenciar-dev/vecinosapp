from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Perfil, Incidencia, Comentario


class BootstrapMixin:
    """Le pone clases de Bootstrap a todos los campos."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs['class'] = 'form-select'
            else:
                campo.widget.attrs['class'] = 'form-control'


class RegistroForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=50)
    email = forms.EmailField(label='Correo')
    piso_puerta = forms.CharField(label='Piso / Puerta', max_length=20)
    edificio = forms.CharField(label='Edificio', max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'email')

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data['first_name']
        usuario.email = self.cleaned_data['email']
        usuario.save()
        # Crear el perfil
        Perfil.objects.create(
            usuario=usuario,
            piso_puerta=self.cleaned_data['piso_puerta'],
            edificio=self.cleaned_data['edificio'],
        )
        # Asignar al grupo Residente (si no existe, lo crea)
        grupo, creado = Group.objects.get_or_create(name='Residente')
        usuario.groups.add(grupo)
        return usuario


class PerfilForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['piso_puerta', 'edificio']


class IncidenciaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'categoria', 'prioridad', 'foto']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if len(titulo.strip()) < 10:
            raise forms.ValidationError('El título debe tener al menos 10 caracteres.')
        return titulo

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto and hasattr(foto, 'size') and foto.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La foto no puede pesar más de 2 MB.')
        return foto


class IncidenciaAdminForm(BootstrapMixin, forms.ModelForm):
    """Lo que ve el administrador al editar: estado, prioridad y nota interna."""
    class Meta:
        model = Incidencia
        fields = ['estado', 'prioridad', 'nota_interna']
        widgets = {'nota_interna': forms.Textarea(attrs={'rows': 3})}


class ComentarioForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escribe un comentario...'})}