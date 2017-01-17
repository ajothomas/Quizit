from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from instructor.models import MCQ_Question
from .serializers import MCQ_QuestionSerializer

# Create your views here.
class MCQ_QuestionList(APIView):
	def get(self, request):
		questions = MCQ_Question.objects.all()
	 	serializer = MCQ_QuestionSerializer(questions, many=True)
	 	return Response(serializer.data)
