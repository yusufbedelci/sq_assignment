from functools import wraps
from tkinter import messagebox
from entities.user import User


# ======================================== #
# Authorization functions
# ======================================== #
def reset_user(app):
    is_user_logged_in = app.user is not None
    db_user = app.user_manager.get_user(app.user.username) if is_user_logged_in else None
    is_user_in_db = db_user is not None
    if is_user_logged_in and is_user_in_db:
        app.user = db_user
    return app


def is_authorized(app, allowed_roles: tuple[User.Role], password_reset_check=True):
    """
    User is authorized if:
    1. app.user is not None -> (Any user is logged in)
    2. app.user still exists in database -> (User is not deleted)
    3. app.user.reset_password is 0 and password_reset_check is True -> (User has not reset password)
    4. app.user.role is in allowed_roles -> (User has the correct role)
    """
    allowed_roles = {role.value for role in allowed_roles}
    if (
        app.user is not None
        and app.user_manager.get_user(app.user.username) is not None
        and (not password_reset_check or app.user.reset_password == 0)
        and app.user.role in allowed_roles
    ):
        return True
    return False


def handle_unauthorized(app):
    """
    Handle unauthorized access
    """
    messagebox.showerror("Unauthorized", "You are not authorized to view this page.")
    app.logout()


# ======================================== #
# Decorators
# ======================================== #
def authorized(allowed_roles: tuple[User.Role], password_reset_check=True):
    """
    Authorization decorator
    """

    def decorator(func):
        @wraps(func)
        def wrapper(app, *args, **kwargs):

            # authorize user
            app = reset_user(app)
            if is_authorized(app, allowed_roles, password_reset_check):
                return func(app, *args, **kwargs)
            return handle_unauthorized(app)

        return wrapper

    return decorator


def authorized_action(app, allowed_roles: tuple[User.Role], password_reset_check=True):
    """
    Authorization action decorator for standalone functions (like submit actions).
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # authorize user
            action_app = reset_user(app)
            if is_authorized(action_app, allowed_roles, password_reset_check):
                return func(*args, **kwargs)
            return handle_unauthorized(action_app)

        return wrapper

    return decorator
