from django.contrib import admin
from .models import FaceBookUsers, PersonalInfo, Friends, Posts, Photos, Req_Resp_Table, Profile_Photos
# Register your models here.

admin.site.register(FaceBookUsers)
admin.site.register(PersonalInfo)
admin.site.register(Friends)
admin.site.register(Posts)
admin.site.register(Photos)
admin.site.register(Profile_Photos)
admin.site.register(Req_Resp_Table)