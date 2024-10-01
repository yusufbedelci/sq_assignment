from functools import wraps
from tkinter import messagebox
from entities.user import User


def is_authorized(app, allowed_roles: tuple[User.Role]) -> bool:
    """
    User is authorized if:
    1. app.user is not None
    2. app.user still exists in database
    3. app.user.role is still same as in database
    4. app.user.role is in allowed_roles
    """
    allowed_roles = (role.value for role in allowed_roles)
    if (
        app.user is not None
        and app.user_manager.get_user(app.user.username) is not None
        and app.user_manager.get_user(app.user.username).role == app.user.role
        and app.user.role in allowed_roles
        and app.user.reset_password == 0
    ):
        return True
    return False


def is_authorized_without_password_reset(app, allowed_roles: tuple[User.Role]) -> bool:
    allowed_roles = (role.value for role in allowed_roles)
    if (
        app.user is not None
        and app.user_manager.get_user(app.user.username) is not None
        and app.user_manager.get_user(app.user.username).role == app.user.role
        and app.user.role in allowed_roles
    ):
        return True
    return False


def handle_unauthorized(app, allowed_roles: tuple[User.Role]):
    """
    Handle unauthorized access
    """
    if app.user.role not in allowed_roles:
        messagebox.showerror(
            "Unauthorized", "You are not authorized to view this page."
        )
        # send to default page
        if app.user.role == User.Role.SUPER_ADMIN.value:
            app.view_users()
        elif app.user.role == User.Role.SYSTEM_ADMIN.value:
            app.view_users()
        elif app.user.role == User.Role.CONSULTANT.value:
            app.view_members()
    else:
        messagebox.showerror("Something went wrong", "Please log in again.")
        app.logout()


def authorized(allowed_roles: tuple[User.Role], without_password_reset=False):
    """
    Authorization decorator
    """

    def decorator(func):
        @wraps(func)
        def wrapper(app, *args, **kwargs):
            user_is_authorized = (
                is_authorized_without_password_reset(app, allowed_roles)
                if without_password_reset
                else is_authorized(app, allowed_roles)
            )
            if not user_is_authorized:
                handle_unauthorized(app, allowed_roles)
                return None
            return func(app, *args, **kwargs)

        return wrapper

    return decorator


def authorized_action(
    app, allowed_roles: tuple[User.Role], without_password_reset=False
):
    """
    Authorization action decorator for standalone functions (like submit actions).
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_is_authorized = (
                is_authorized_without_password_reset(app, allowed_roles)
                if without_password_reset
                else is_authorized(app, allowed_roles)
            )
            if not user_is_authorized:
                handle_unauthorized(app, allowed_roles)
                return None
            return func(*args, **kwargs)  # Only execute if authorized

        return wrapper

    return decorator
