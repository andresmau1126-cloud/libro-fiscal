import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP


def generar_codigo_otp(length=6):
    """Genera un código OTP de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=length))


def crear_otp(usuario, tipo='login'):
    """Crea un nuevo OTP para el usuario"""
    # Eliminar OTPs anteriores para este usuario
    OTP.objects.filter(usuario=usuario, tipo=tipo, usado=False).delete()
    
    codigo = generar_codigo_otp()
    expires_at = timezone.now() + timedelta(minutes=5)  # OTP válido por 5 minutos
    
    otp = OTP.objects.create(
        usuario=usuario,
        codigo=codigo,
        tipo=tipo,
        expires_at=expires_at
    )
    
    return otp


def enviar_otp_email(usuario, codigo_otp):
    """Envía el código OTP al email del usuario"""
    try:
        asunto = "Tu código de verificación - Libro Fiscal"
        mensaje = f"""
        Hola {usuario.nombre},
        
        Tu código de verificación es: {codigo_otp}
        
        Este código es válido por 5 minutos.
        No compartas este código con nadie.
        
        Si no solicitaste este código, ignora este mensaje.
        
        Saludos,
        Equipo Libro Fiscal
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [usuario.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False


def verificar_otp(usuario, codigo, tipo='login'):
    """Verifica el código OTP del usuario"""
    try:
        otp = OTP.objects.get(
            usuario=usuario,
            codigo=codigo,
            tipo=tipo,
            usado=False
        )
        
        # Verificar que no haya expirado
        if otp.expires_at < timezone.now():
            otp.delete()
            return False, "Código expirado"
        
        # Marcar como usado
        otp.usado = True
        otp.save()
        
        return True, "Código verificado correctamente"
    except OTP.DoesNotExist:
        return False, "Código inválido"
