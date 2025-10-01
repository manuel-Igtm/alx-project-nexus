from rest_framework_simplejwt.tokens import RefreshToken

def get_auth_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        },
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    }
