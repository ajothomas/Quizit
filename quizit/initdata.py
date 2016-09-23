########################################################################################################################
# Dummy data
########################################################################################################################

from django.contrib.auth.models import User, Group
from account.models import Course, Course_Topics, Instructor_Info, Instructor_Course, Student_Info, Student_Course
from instructor.models import MCQ_Question, Recommendations
from student.models import Student_Answers, Student_Marks
import uuid
import datetime
import random
########################################################################################################################
# Course Information

Course.objects.all().delete()

Course.objects.create(
	courseName = "Introduction to Java",
	batch = "Summer'16" ,
	startDate = '2016-07-01',
	endDate = '2016-07-15' ,
	)

Course.objects.create(
	courseName = "Introduction to Algorithms",
	batch = "Summer'16" ,
	startDate = '2016-07-01',
	endDate = '2016-07-15' ,
	)

# deleting all course topics first
Course_Topics.objects.all().delete()

course = Course.objects.get(courseName = 'Introduction to Java')
courseTopics = ['Introduction to Java','Data types & Variables','Control Statements and Operators','Classes & Methods','Access specifier','Packages','Serialization','Garbage collection','Threads','Files','Strings']

for courseTopic in courseTopics :
	Course_Topics.objects.create(
			topicName = courseTopic,
			course = course,
		)

Course_Topics.objects.all().count()

########################################################################################################################
# Student_Info

# Clear Student data first
Student_Info.objects.all().delete()
Student_Course.objects.all().delete()

# dummy data
userdata = [['ajothomas','ajo','thomas','ajo.thomas24@gmail.com','ajopassword','student'] 
			,['anudeepr','anudeep','reddy','anudeepindira@gmail.com','anudeeppassword','student']
			,['bhargavir','bhargavi','rajagopalan','bhargavirajagopalan1990gmail.com','bhargavipassword','student'] 
			,['jaharshs','jaharsh','samayan','jaharsh93@gmail.com','jaharshpassword','student'] 
			,['gauravr','gaurav','ravetkar','gaurav.ravetkar@gmail.com','gauravpassword','student'] 

			,['arya','arya','stark','arya.quizit@gmail.com','aryapassword','student'] 
			,['bran','bran','stark','bran.quizit@gmail.com','branpassword','student'] 
			,['cersie','cersie','lannister','cersie.quizit@gmail.com','cersiepassword','student'] 
			,['daenerys','daenerys','targaryen','daenerys.quizit@gmail.com','daeneryspassword','student'] 
			,['eddard','eddard','stark','eddard.quizit@gmail.com','eddardpassword','student'] 
			,['frey','walder','frey','frey.quizit@gmail.com','freypassword','student'] 
			,['gregor','clegane','gregor','gregor.quizit@gmail.com','gregorpassword','student']
			,['jon','jon','snow','jon.quizit@gmail.com','jonpassword','student']
			,['jamie','jamie','lannister','jamie.quizit@gmail.com','jamiepassword','student']
			,['oberyn','oberyn','martell','oberyn.quizit@gmail.com','oberynpassword','student']
			]

# populate the data in the table
for i in range(15):
	# make a random UUID
	u = uuid.uuid4()
	Student_Info.objects.create(
		username = userdata[i][0],
		first_name = userdata[i][1],
		last_name = userdata[i][2],
		email = userdata[i][3],
		password = userdata[i][4],
		groups = userdata[i][5],
		uuid = str(u.hex),
		session_key = '',
		cookie_key = '', )
	student = Student_Info.objects.get(email = userdata[i][3])
	Student_Course.objects.create(
		course = course,
		student = student,
		enrolledDate = '2016-07-01',
	)

Instructor_Info.objects.all().delete()
u = uuid.uuid4()
Instructor_Info.objects.create(
	username = 'admin',
	first_name = 'admin',
	last_name = 'admin',
	email = 'learnjava.quiz@gmail.com',
	password = 'adminpassword',
	groups = 'admin',
	uuid = str(u.hex),
	)

course = Course.objects.get(courseName = 'Introduction to Java')
instructor = Instructor_Info.objects.get(username = 'admin')
Instructor_Course.objects.create(
	course = course,
	instructor = instructor,
	)

course = Course.objects.get(courseName = 'Introduction to Algorithms')
instructor = Instructor_Info.objects.get(username = 'admin')
Instructor_Course.objects.create(
	course = course,
	instructor = instructor,
	)

########################################################################################################################
# User [ Django user file used for authentication ]

# This command is used to delete all users
User.objects.all().delete()

# students
student = Group.objects.get_or_create(name='student')
for i in range(15):
	user = User.objects.create_user(
				username = userdata[i][0],
				first_name = userdata[i][1],
				last_name = userdata[i][2],
				email =  userdata[i][3],
				password = userdata[i][4], )
	user.groups.add(Group.objects.get(name='student'))
	user.save()

# admin/instructor user
instructor = Group.objects.get_or_create(name='admin')
user = User.objects.create_user(
				username = 'admin',
				first_name = 'admin',
				last_name = 'admin',
				email =  'learnjava.quiz@gmail.com',
				password = 'adminpassword',
				)
user.groups.add(Group.objects.get(name='admin'))
user.save()

########################################################################################################################
# MCQ_Question

# This command is used to delete all users
MCQ_Question.objects.all().delete()

question_list = [
				['What kind of language is java', 'Introduction to Java','Procedural language','object oriented language','declarative language','Machine Language','ChoiceB','Easy']
				,['What is the range of data type short in Java','Data types & Variables','-128 to 127','-32768 to 32767','-2147483648 to 2147483647','None of the above','ChoiceB','Easy']
				,['Which of these is an incorrect Statement?','Data types & Variables','It is necessary to use new operator to initialize an array.','Array can be initialized using comma separated expressions surrounded by curly braces.','Array can be initialized when they are declared','None of the above','ChoiceA','Moderate']
				
				,['Decrement operator, –, decreases value of variable by what number','Control Statements and Operators','1','2','3','4','ChoiceA','Easy']
				,['What is the output of relational operators?','Control Statements and Operators','Integers','Boolean','character','Double','ChoiceB','Easy']

				,['What is a class?','Classes & Methods','Blueprint','Object','Variable','Instance','ChoiceA','Easy']
				,['What kind of variables a class can consist of?','Classes & Methods','Local Variables','Instance variables', 'Class Variables', 'All of the above', 'ChoiceD', 'Medium']
				,['Which of these operators is used to allocate memory for an object?','Classes & Methods','alloc','malloc','new','None of the above','ChoiceC','Difficult']
				,['What is the return type of Constructors?','Classes & Methods','int','float','void','None of the above','ChoiceC','Easy']
				,['Which of these can be overloaded?','Classes & Methods','Methods','constructors','classes','None','ChoiceA','Difficult']
				
				,['Which of these keyword must be used to inherit a class?','Inheritence & Interfaces','super','this','extend','extends','ChoiceD','Difficult']
				,['Which of the following package stores all the standard java classes?','Packages','lang','java','util','None','ChoiceB','Easy']
				,['Which of these is a process of writing the state of an object to a byte stream?','Serialization','serialization','externilization','file filtering','None','ChoiceA','Moderate']
				,['Which of these method waits for the thread to terminate?','Threads','sleep()','isAlive()','join()','stop()','ChoiceC','Moderate']
				,['How many ports of TCP/IP are reserved for specific protocols?','Networking','10','1024','2028','1052','ChoiceB','Easy']
				,['Which of these methods are used to read in from file?','Files','get()','read()','write()','scan()','ChoiceB','Moderate']
				,['Which of these methods can be used to output a sting in an applet?','Applets','display()','print()','output()','get()','ChoiceB','Moderate']
				,['Which of these method of class StringBuffer is used to get the length of sequence of characters?','Strings','length()','capacity()','Length()','distance()','ChoiceA','Easy']
				,['Which of these class is used to read and write bytes in a file?','Files','Byte streams','Filereader','filewriter','fileinputstream','ChoiceA','Difficult']
				,['Which of these selection statements test only for equality?','Control statements','if','switch','if and switch','None','ChoiceB','Easy']
				,['Which of these access specifiers must be used for main() method?','Access specifiers','private','public','protected','None','ChoiceB','Moderate']
				,['Which function is used to perform some action when the object is to be destroyed?','Garbage collection','Finalize()','Delete()','free()','None','ChoiceA','Easy']
				]


course = Course.objects.get(courseName__iexact = 'Introduction to Java')

# 'B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A','A','B','B','A'
for i in range(22):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	sentFlag = False
	if i-18 <= 0:
		sentFlag = True
MCQ_Question.objects.create(
	question = question_list[i][0],
	course =  course, 
	courseTopic = question_list[i][1],
	choiceA = question_list[i][2],
	choiceB = question_list[i][3],
	choiceC = question_list[i][4],
	choiceD = question_list[i][5],
	answer = question_list[i][6],
	level = question_list[i][7],
	datetime = dt,
	sentFlag = sentFlag,
)

########################################################################################################################
# Student_Answers

# Clear the table
Student_Answers.objects.all().delete()

# 'B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A'  ,'A','B','B','A'
# ajothomas has 16/18 in the first 10 questions
set1 = ['B','B','A','A','C','A','D','C','C','A','C','B','A','C','B','B','B','A']
student = Student_Info.objects.filter(username = 'ajothomas')[0]
	
for i in range(18):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	question = MCQ_Question.objects.filter(datetime = dt)[0]
	if ( question.answer == ''.join(['Choice',set1[i]]) ): 
	Student_Answers.objects.create(student = student, question = question, selAnswer = set1[i], answerSequence = set1[i], correctFlag = 1, numAttempts = 1, numCorrectAttempts=1 )
else:
	Student_Answers.objects.create(student = student, question = question, selAnswer = set1[i], answerSequence = set1[i], correctFlag = 0, numAttempts = 1, numCorrectAttempts=0 )


# query to check the count. there shouldnt be any duplicates
# Student_Answers.objects.filter(student = Student_Info.objects.filter(usernamCe= 'ajothomas')[0]).count()

# bhargavir has 14/18 in the first 10 questions
#correct = ['B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A']
set2 = ['B','B','A','B','B','B','D','C','B','A','D','B','A','B','B','B','B','A']
for i in range(18):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	student = Student_Info.objects.filter(username = 'bhargavir')[0]
	question = MCQ_Question.objects.filter(datetime = dt)[0]
	if ( question.answer == ''.join(['Choice',set2[i]]) ): 
	Student_Answers.objects.create(student = student, question = question, selAnswer = set2[i], answerSequence = set2[i], correctFlag = 1, numAttempts = 1, numCorrectAttempts=1 )
else:
	Student_Answers.objects.create(student = student, question = question, selAnswer = set2[i], answerSequence = set2[i], correctFlag = 0, numAttempts = 1, numCorrectAttempts=0 )

student.student_answers_set.filter(correctFlag = 0).count()
# query to check the count. there shouldnt be any duplicates
# Student_Answers.objects.filter(student = Student_Info.objects.filter(username= 'bhargavir')[0]).count()

# jaharshs has 12/18 in the first 10 questions
#correct = ['B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A']
set3 = ['B','A','B','C','B','A','D','C','D','D','D','B','A','B','B','B','B','A']
for i in range(18):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	student = Student_Info.objects.filter(username = 'jaharshs')[0]
	question = MCQ_Question.objects.filter(datetime = dt)[0]
	if ( question.answer == ''.join(['Choice',set3[i]]) ): 
	Student_Answers.objects.create(student = student, question = question, selAnswer = set3[i], answerSequence = set3[i], correctFlag = 1, numAttempts = 1, numCorrectAttempts=1 )
else:
	Student_Answers.objects.create(student = student, question = question, selAnswer = set3[i], answerSequence = set3[i], correctFlag = 0, numAttempts = 1, numCorrectAttempts=0 )

student.student_answers_set.filter(correctFlag = 0).count()
# query to check the count. there shouldnt be any duplicates
# Student_Answers.objects.filter(student = Student_Info.objects.filter(username= 'jaharshs')[0]).count()


# gauravr has 10/18 in the first 10 questions
# correct = ['B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A']
set4 = ['B','C','A','B','C','A','B','C','C','A','C','B','C','C','C','B','B','C']
for i in range(18):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	student = Student_Info.objects.filter(username = 'gauravr')[0]
	question = MCQ_Question.objects.filter(datetime = dt)[0]
	if ( question.answer == ''.join(['Choice',set4[i]]) ): 
	Student_Answers.objects.create(student = student, question = question, selAnswer = set4[i], answerSequence = set4[i], correctFlag = 1, numAttempts = 1, numCorrectAttempts=1 )
else:
	Student_Answers.objects.create(student = student, question = question, selAnswer = set4[i], answerSequence = set4[i], correctFlag = 0, numAttempts = 1, numCorrectAttempts=0 )

student.student_answers_set.filter(correctFlag = 0).count()

#
# query to check the count. there shouldnt be any duplicates
# Student_Answers.objects.filter(student = Student_Info.objects.filter(username= 'gauravr')[0]).count()

# anudeepr has 8/18 in the first 10 questions
# correct = ['B','B','A','A','B','A','D','C','C','A','D','B','A','C','B','B','B','A']
set5 = ['C','C','A','C','C','C','C','C','C','C','D','C','A','B','B','B','B','A']
for i in range(18):
	dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
	student = Student_Info.objects.filter(username = 'anudeepr')[0]
	question = MCQ_Question.objects.filter(datetime = dt)[0]
	if ( question.answer == ''.join(['Choice',set5[i]]) ): 
	Student_Answers.objects.create(student = student, question = question, selAnswer = set5[i], answerSequence = set5[i], correctFlag = 1, numAttempts = 1, numCorrectAttempts=1 )
else:
	Student_Answers.objects.create(student = student, question = question, selAnswer = set5[i], answerSequence = set5[i], correctFlag = 0, numAttempts = 1, numCorrectAttempts=0 )

student.student_answers_set.filter(correctFlag = 0).count()

# query to check the count. there shouldnt be any duplicates
# Student_Answers.objects.filter(student = Student_Info.objects.filter(username= 'anudeepr')[0]).count()

choices_arr = ['A','B','C','D']
# for users 5-15 (other users)
start = Student_Info.objects.filter(username='arya')[0].id
for us in range(start,start+10):
	student = Student_Info.objects.filter(id = us)[0]
	# for all the questions, choose random choices
	for i in range(18):
		dt = datetime.datetime.now().date() + datetime.timedelta(days = i-18)
		question = MCQ_Question.objects.filter(datetime = dt)[0]
		choice = random.randint(0,3)
		correctFlag = 0
		numCorrectAttempts=0
		if question.answer == ''.join(['Choice',choices_arr[choice]]):
			correctFlag = 1
			numCorrectAttempts = 1
		Student_Answers.objects.create(
			student = student,
			question = question,
			selAnswer = choices_arr[choice],
			correctFlag = correctFlag,
			answerSequence = choices_arr[choice],
			numAttempts = 1,
			numCorrectAttempts = numCorrectAttempts,
			)

########################################################################################################################
# Recommendations

Recommendations.objects.all().delete()

question = MCQ_Question.objects.filter(question = 'Decrement operator, –, decreases value of variable by what number')[0]
Recommendations.objects.create( question = question, text = 'Rec11', rank=1)
Recommendations.objects.create( question = question, text = 'Rec12', rank=2)
Recommendations.objects.create( question = question, text = 'Rec13', rank=3)
Recommendations.objects.create( question = question, text = 'Rec14', rank=4)
Recommendations.objects.create( question = question, text = 'Rec15', rank=5)

question = MCQ_Question.objects.filter(question = 'What is the output of relational operators?')[0]
Recommendations.objects.create( question = question, text = 'Rec21', rank=1)
Recommendations.objects.create( question = question, text = 'Rec22', rank=2)
Recommendations.objects.create( question = question, text = 'Rec23', rank=3)
Recommendations.objects.create( question = question, text = 'Rec24', rank=4)
Recommendations.objects.create( question = question, text = 'Rec25', rank=5)

question = MCQ_Question.objects.filter(question = 'What is a class?')[0]
Recommendations.objects.create( question = question, text = 'Rec31', rank=1)
Recommendations.objects.create( question = question, text = 'Rec32', rank=2)
Recommendations.objects.create( question = question, text = 'Rec33', rank=3)
Recommendations.objects.create( question = question, text = 'Rec34', rank=4)
Recommendations.objects.create( question = question, text = 'Rec35', rank=5)

question = MCQ_Question.objects.filter(question = 'What kind of variables a class can consist of?')[0]
Recommendations.objects.create( question = question, text = 'Rec41', rank=1)
Recommendations.objects.create( question = question, text = 'Rec42', rank=2)
Recommendations.objects.create( question = question, text = 'Rec43', rank=3)
Recommendations.objects.create( question = question, text = 'Rec44', rank=4)
Recommendations.objects.create( question = question, text = 'Rec45', rank=5)

question = MCQ_Question.objects.filter(question = 'Which of these operators is used to allocate memory for an object?')[0]
Recommendations.objects.create( question = question, text = 'Rec51', rank=1)
Recommendations.objects.create( question = question, text = 'Rec52', rank=2)
Recommendations.objects.create( question = question, text = 'Rec53', rank=3)
Recommendations.objects.create( question = question, text = 'Rec54', rank=4)
Recommendations.objects.create( question = question, text = 'Rec55', rank=5)

question = MCQ_Question.objects.filter(question = 'What is the return type of Constructors?')[0]
Recommendations.objects.create( question = question, text = 'Rec61', rank=1)
Recommendations.objects.create( question = question, text = 'Rec62', rank=2)
Recommendations.objects.create( question = question, text = 'Rec63', rank=3)
Recommendations.objects.create( question = question, text = 'Rec64', rank=4)
Recommendations.objects.create( question = question, text = 'Rec65', rank=5)

question = MCQ_Question.objects.filter(question = 'Which of these can be overloaded?')[0]
Recommendations.objects.create( question = question, text = 'Rec71', rank=1)
Recommendations.objects.create( question = question, text = 'Rec72', rank=2)
Recommendations.objects.create( question = question, text = 'Rec73', rank=3)
Recommendations.objects.create( question = question, text = 'Rec74', rank=4)
Recommendations.objects.create( question = question, text = 'Rec75', rank=5)

question = MCQ_Question.objects.filter(question = 'Which of these method of class StringBuffer is used to get the length of sequence of characters?')[0]
Recommendations.objects.create( question = question, text = 'Rec81', rank=1)
Recommendations.objects.create( question = question, text = 'Rec82', rank=2)
Recommendations.objects.create( question = question, text = 'Rec83', rank=3)
Recommendations.objects.create( question = question, text = 'Rec84', rank=4)
Recommendations.objects.create( question = question, text = 'Rec85', rank=5)