from .utils import es_admin


def rol_usuario(request):
    return {'es_admin': request.user.is_authenticated and es_admin(request.user)}