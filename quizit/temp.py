import os
print os.path.dirname(os.path.realpath(__file__))
print os.path.join( os.path.dirname(os.path.realpath(__file__)) , 'quizit_static')
