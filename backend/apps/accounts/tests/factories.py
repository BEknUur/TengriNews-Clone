import factory
from apps.accounts.models import CustomUser

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@example.test")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = CustomUser.Role.USER
    is_active = True

    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        if create:
            obj.set_password("password123")
            obj.save()