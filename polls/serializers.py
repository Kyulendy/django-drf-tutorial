from rest_framework import serializers
from .models import Poll, Choice, Vote
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User

# >>> from rest_framework.authtoken.models import Token
# >>> user = User.objects.get(pk=pk_of_user_without_token)
# >>> Token.objects.create(user=user)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Resticting fields to the following ones
        fields = ('username', 'email', 'password')
        # We also don’t want to get back the password in response
        extra_kwargs = {'password': {'write_only': True}}

    # We have overriden the ModelSerializer method’s create() to save the User instances
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        # We want to ensure that tokens are created when user is created in UserCreate view, so we update the UserSerializer
        Token.objects.create(user=user)
        return user

# We will use ModelSerializer which will reduce code duplication by automatically determing the set of fields
# and by creating implementations of the create() and update() methods.

# is_valid(self, ..) method which can tell if the data is sufficient and valid to create/update a model instance.
# save(self, ..) method, which knows how to create or update an instance.
# create(self, validated_data, ..) method which knows how to create an instance. This method can be overriden to customize the create behaviour.
# update(self, instance, validated_data, ..) method which knows how to update an in- stance. This method can be overriden to customize the update behaviour.
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    # Had to set "read_only=True", otherwise got an error on Choice post
    # The `.create()` method does not support writable nested fields by default.
    # Write an explicit `.create()` method for serializer `polls.serializers.ChoiceSerializer`, or set `read_only=True` on nested serializer fields.
    votes = VoteSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Choice
        fields = '__all__'

class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Poll
        fields = '__all__'

# Serializer usage :

# poll_serializer = PollSerializer(data={"question": "Mojito or Caipirinha?", "created_by": 1})
# poll_serializer.is_valid()
# poll = poll_serializer.save()
# poll.pk # saved !
