from rest_framework.permissions import BasePermission, SAFE_METHODS, exceptions


class IsGuestUser(BasePermission):
    """
    Permite acesso apenas a usuários autenticados do tipo GUEST.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_guest", False)
            and getattr(user, "role", None) == "GUEST"
        )


class IsNotGuest(BasePermission):
    """
    Bloqueia acesso de usuários guest.
    Permite apenas usuários autenticados que NÃO são guests.
    Útil para endpoints como logout, atualização de perfil, etc.
    """
    message = "Usuários convidados não têm permissão para realizar esta ação."

    def has_permission(self, request, view):
        user = request.user
        
        if not user or not user.is_authenticated:
            # A verificação de autenticação principal deve ser feita por IsAuthenticated
            return False
        
        # Bloqueia guests
        if getattr(user, "is_guest", False):
            raise exceptions.PermissionDenied(self.message)
        
        if getattr(user, "role", None) == "GUEST":
            raise exceptions.PermissionDenied(self.message)
        
        return True


class RolePermission(BasePermission):
    """
    Permite acesso apenas a usuários autenticados cujo role esteja
    explicitamente listado em view.allowed_roles
    """
    def has_permission(self, request, view):
        user = request.user
        required_roles = getattr(view, "allowed_roles", [])
        
        if not user or not user.is_authenticated:
            return False
        
        return getattr(user, "role", None) in required_roles


class IsAuthenticatedOrGuestReadOnly(BasePermission):
    """
    - SAFE_METHODS (GET, HEAD, OPTIONS):
        Permitido para qualquer usuário (inclusive guest ou anônimo)
    - Métodos de escrita (POST, PUT, PATCH, DELETE):
        Permitido apenas para usuários autenticados que NÃO sejam guest
    """
    def has_permission(self, request, view):
        user = request.user
        
        # Leitura sempre permitida (inclusive anônimo e guest)
        if request.method in SAFE_METHODS:
            return True
        
        # Escrita exige autenticação
        if not user or not user.is_authenticated:
            return False
        
        # Guest nunca pode escrever
        if getattr(user, "is_guest", False):
            return False
        
        if getattr(user, "role", None) == "GUEST":
            return False
        
        return True


class IsGuestOrReadOnly(BasePermission):
    """
    - GET/HEAD/OPTIONS: Permitido para todos (incluindo guests)
    - POST/PUT/PATCH/DELETE: Bloqueado para guests, permitido para usuários autenticados
    
    Diferença para IsAuthenticatedOrGuestReadOnly:
    - Esta permite que guests autenticados façam GET
    - Bloqueia apenas métodos de escrita para guests
    """
    def has_permission(self, request, view):
        # Leitura permitida para todos
        if request.method in SAFE_METHODS:
            return True
        
        user = request.user
        
        # Escrita requer autenticação E não ser guest
        return (
            user and 
            user.is_authenticated and 
            not getattr(user, 'is_guest', False) and
            getattr(user, 'role', None) != 'GUEST'
        )