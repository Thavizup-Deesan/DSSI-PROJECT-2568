from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import render


class PotmsAccountAdapter(DefaultAccountAdapter):
    """ปิด non-social signup — อนุญาตเฉพาะ Google login เท่านั้น"""

    def is_open_for_signup(self, request):
        return False


class PotmsSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter สำหรับ POTMS
    - ตรวจ @ubu.ac.th server-side
    - Auto-create/sync api.models.User หลัง social login
    """

    def is_open_for_signup(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        """ตรวจ @ubu.ac.th ก่อน login จริง"""
        email = sociallogin.account.extra_data.get('email', '')

        if not email.endswith('@ubu.ac.th'):
            raise ImmediateHttpResponse(
                render(request, 'login.html', {
                    'error': 'กรุณาใช้อีเมล @ubu.ac.th เท่านั้น',
                })
            )

        # เชื่อม auth.User ที่มีอยู่แล้ว (ถ้ามี) กับ social account
        if not sociallogin.is_existing:
            from django.contrib.auth import get_user_model
            DjangoUser = get_user_model()
            try:
                existing_user = DjangoUser.objects.get(email=email)
                sociallogin.connect(request, existing_user)
            except DjangoUser.DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        """สร้าง auth.User แล้ว sync ไปยัง api.models.User"""
        user = super().save_user(request, sociallogin, form)
        self._sync_api_user(sociallogin)
        return user

    def _sync_api_user(self, sociallogin):
        """สร้างหรืออัปเดต api.models.User"""
        from api.models import User as ApiUser

        email = sociallogin.account.extra_data.get('email', '')
        full_name = sociallogin.account.extra_data.get('name', '')

        api_user, created = ApiUser.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
            }
        )

        if not created and api_user.full_name != full_name and full_name:
            api_user.full_name = full_name
            api_user.save(update_fields=['full_name'])

        return api_user
