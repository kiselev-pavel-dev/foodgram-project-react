from django.contrib.auth.base_user import BaseUserManager

USERNAME_ERROR_MESSAGE = 'Имя пользователя не может быть пустым!'
EMAIL_ERROR_MESSAGE = 'Поле e-mail не может быть пустым!'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, username, **extra_fields):
        if not username:
            raise ValueError(USERNAME_ERROR_MESSAGE)
        if not email:
            raise ValueError(EMAIL_ERROR_MESSAGE)
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
