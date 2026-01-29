from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Inquiry

@receiver(post_save, sender=Inquiry)
def notify_admin_new_lead(sender, instance, created, **kwargs):
    if created:
        # This only runs when a NEW inquiry is created
        subject = f"🚨 NEW LEAD: {instance.property.title}"
        message = (
            f"You have a new lead!\n\n"
            f"Property: {instance.property.title}\n"
            f"Price: {instance.property.price}\n"
            f"Inquirer Phone: {instance.user.phone}\n"
            f"Inquirer Name: {instance.user.full_name}\n\n"
            f"Log in to the Admin Dashboard to act as the middleman."
        )
        
        # In production, replace with your actual admin email
        try:
            send_mail(
                subject,
                message,
                'noreply@yourstartup.com',
                ['admin@yourstartup.com'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email failed: {e}")