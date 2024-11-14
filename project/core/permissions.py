from django.contrib.auth.mixins import UserPassesTestMixin

class IsAdmin(UserPassesTestMixin):
    def test_func(self) -> bool:
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return True
        return False