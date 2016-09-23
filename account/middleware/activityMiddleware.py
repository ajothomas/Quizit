# from datetime import datetime
# from django.http import HttpResponseRedirect
# from django.shortcuts import render, get_object_or_404, redirect
# from django.core.urlresolvers import reverse

# class SessionExpiredMiddleware(object):
# 	def process_request(self, request):
# 		if "last_activity" in request.session:
# 			last_activity = request.session['last_activity']
# 			now = datetime.now()

# 			if (now - last_activity).minutes > 10:
# 				return redirect(reverse('account:notAllowed'))
# 			if not request.is_ajax():
# 				request.session['last_activity'] = now
# 		else:
# 			return redirect(reverse('account:login_view'))