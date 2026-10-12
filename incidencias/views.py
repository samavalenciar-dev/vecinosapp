from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import (RegistroForm, PerfilForm, IncidenciaForm,
                    IncidenciaAdminForm, ComentarioForm)
from .models import Perfil, Incidencia, Comentario
from .utils import es_admin


# ---------- Registro y perfil ----------
class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Cuenta creada. Ya puedes iniciar sesión.')
        return super().form_valid(form)


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PerfilForm
    template_name = 'incidencias/perfil.html'
    success_url = reverse_lazy('perfil')

    def get_object(self):
        perfil, creado = Perfil.objects.get_or_create(
            usuario=self.request.user,
            defaults={'piso_puerta': '', 'edificio': ''},
        )
        return perfil

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado.')
        return super().form_valid(form)


# ---------- Incidencias ----------
class DuenoOAdminMixin(UserPassesTestMixin):
    """Deja pasar al dueño de la incidencia o al administrador."""
    def test_func(self):
        incidencia = self.get_object()
        return es_admin(self.request.user) or incidencia.usuario == self.request.user


class IncidenciaListView(LoginRequiredMixin, ListView):
    model = Incidencia
    template_name = 'incidencias/lista.html'
    context_object_name = 'incidencias'
    paginate_by = 5   # paginación (punto bonus)

    def get_queryset(self):
        incidencias = Incidencia.objects.select_related('usuario')
        if not es_admin(self.request.user):
            incidencias = incidencias.filter(usuario=self.request.user)
        return incidencias


class IncidenciaDetailView(LoginRequiredMixin, DuenoOAdminMixin, DetailView):
    model = Incidencia
    template_name = 'incidencias/detalle.html'
    context_object_name = 'incidencia'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['form_comentario'] = ComentarioForm()
        return contexto


class IncidenciaCreateView(LoginRequiredMixin, CreateView):
    model = Incidencia
    form_class = IncidenciaForm
    template_name = 'incidencias/form.html'
    success_url = reverse_lazy('lista_incidencias')

    def form_valid(self, form):
        form.instance.usuario = self.request.user   # el dueño es quien está logueado
        messages.success(self.request, 'Incidencia reportada.')
        return super().form_valid(form)


class IncidenciaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Incidencia
    template_name = 'incidencias/form.html'

    def test_func(self):
        incidencia = self.get_object()
        if es_admin(self.request.user):
            return True
        # el residente solo edita lo suyo y si está Pendiente
        return incidencia.usuario == self.request.user and incidencia.estado == 'pendiente'

    def get_form_class(self):
        if es_admin(self.request.user):
            return IncidenciaAdminForm
        return IncidenciaForm

    def get_success_url(self):
        messages.success(self.request, 'Incidencia actualizada.')
        return reverse('detalle_incidencia', args=[self.object.pk])


class IncidenciaDeleteView(LoginRequiredMixin, DuenoOAdminMixin, DeleteView):
    model = Incidencia
    template_name = 'incidencias/confirmar_eliminar.html'
    success_url = reverse_lazy('lista_incidencias')


# ---------- Comentarios ----------
class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm

    def dispatch(self, request, *args, **kwargs):
        self.incidencia = get_object_or_404(Incidencia, pk=kwargs['pk'])
        if request.user.is_authenticated:
            if not (es_admin(request.user) or self.incidencia.usuario == request.user):
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.incidencia = self.incidencia
        form.instance.autor = self.request.user
        form.save()
        return redirect('detalle_incidencia', pk=self.incidencia.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'El comentario no puede estar vacío.')
        return redirect('detalle_incidencia', pk=self.incidencia.pk)