from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, username, **extra_fields):
        if not username:
            raise ValueError('Имя пользователя не может быть пустым!')
        if not email:
            raise ValueError('Поле e-mail не может быть пустым!')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username, **extra_fields):
        user = self.create_user(
            email, password=password, username=username, **extra_fields
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user
