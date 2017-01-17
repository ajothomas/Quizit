from rest_framework import serializers
from instructor.models import MCQ_Question

class MCQ_QuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = MCQ_Question
		fields = ('question','courseTopic','datetime')