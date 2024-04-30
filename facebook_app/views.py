from django.shortcuts import render, redirect
from .models import FaceBookUsers, PersonalInfo, Friends, Posts, SearchedUsersTable, Req_Resp_Table, Photos, Profile_Photos, Default_Photo
from .forms import RegistrationForm, LoginForm, OtherProfileForm, ChangeInfoForm, ChangeGenderForm, ChangeEmailForm,ChangePhoneForm,AddPostForm, ChangePasswordForm,ChangeUsernameForm,ChangeBirthdayForm,PhotoForm
from datetime import timedelta
from django.utils import timezone


# Registration process.
def registration(request):
    if request.method == "POST": 
        form = RegistrationForm(request.POST)
        if form.is_valid():
            phone_num = form.cleaned_data["phone_num"]
            if not Phone_Number_Is_Valid(str(phone_num)):
               text = "phone number isn't valid, format must be: 5********"
               return render(request,'facebook_app/error_message.html', {'text': text})

            username = form.cleaned_data["first_name"] + " " + form.cleaned_data["last_name"]
            user = FaceBookUsers(
                first_name = form.cleaned_data["first_name"],
                last_name = form.cleaned_data["last_name"],
                username = username,
                phone_num = form.cleaned_data["phone_num"],
                email = form.cleaned_data["email"],
                password = form.cleaned_data["password"],
                birthday = form.cleaned_data["birthday"],
                gender = form.cleaned_data["gender"],
            )
            user.save()
            user2 = Create_User(form.cleaned_data["email"])
            user2.save()
            return redirect('login')
        else:  
            text = "form isn't valid"
            return render(request, 'facebook_app/error_message.html',{'text': text})    
    else:
        form = RegistrationForm()  
        return render(request,"facebook_app/registration.html",{
            "form": form,
        })

# Login process.
def login(request):     
    if request.method == "POST": 
            emails = list(FaceBookUsers.objects.values_list('email', flat=True))
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                if email in emails:
                   password = FaceBookUsers.objects.get(email=email).password
                   inp_password = form.cleaned_data["password"]
                   if inp_password == password:
                      return redirect('main_page',email=email)
                   else:
                       text = "password isn't correct"
                       return render(request, 'facebook_app/error_message.html',{'text': text})   
                else:
                    text = "email isn't correct"
                    return render(request, 'facebook_app/error_message.html',{'text': text})
            else:  
                text = "form isn't valid"
                return render(request, 'facebook_app/error_message.html',{'text': text}) 
    else:
        form = LoginForm()  
        return render(request,"facebook_app/login.html",{
            "form": form,
        })

# Remove account process.
def remove_account(request,email):
    Remove_User_From_Every_Tables(email)
    text = "your account remove succesfully"
    return render(request,'facebook_app/message_text.html',{"text": text})

# Deletes records for the user from all tables.
def Remove_User_From_Every_Tables(email):
    Remove_User_From_FaceBookUser(email)
    Remove_User_From_PersonalInfo(email)
    Remove_User_From_Friends(email)
    Remove_User_From_Posts(email)
    Remove_User_From_Req_Resp_Table(email)
    Remove_User_From_Photos_Tables(email)

# Removes user records from the Photos and Profile_Photos tables.
def Remove_User_From_Photos_Tables(email):
    emails = list(Photos.objects.values_list('email', flat=True))
    if email in emails:
        Photos.objects.filter(email=email).delete()

    emails = list(Profile_Photos.objects.values_list('email', flat=True))
    if email in emails:
        Profile_Photos.objects.get(email=email).delete()

# Removes user records from the Req_Resp_Table table.
def Remove_User_From_Req_Resp_Table(email):
    emails = list(Req_Resp_Table.objects.values_list('req_email', flat=True))
    if email in emails:
        Req_Resp_Table.objects.filter(req_email=email).delete()
    
    emails = list(Req_Resp_Table.objects.values_list('resp_email', flat=True))
    if email in emails:
        Req_Resp_Table.objects.filter(resp_email=email).delete()
    
# Removes user records from the FaceBookUsers table.
def Remove_User_From_FaceBookUser(email):
    FaceBookUsers.objects.filter(email=email).delete()

# Removes user records from the PersonalInfo table.
def Remove_User_From_PersonalInfo(email):
    emails = list(PersonalInfo.objects.values_list('email', flat=True))
    if email in emails:
       PersonalInfo.objects.filter(email=email).delete()

# Removes user records from the Friends table.
def Remove_User_From_Friends(email):
    emails = list(Friends.objects.values_list('email', flat=True))
    if email in emails:
        Friends.objects.filter(email=email).delete()
    
    emails = list(Friends.objects.values_list('friend_email', flat=True))
    if email in emails:
        Friends.objects.filter(friend_email=email).delete()

# Removes user records from the Posts table.
def Remove_User_From_Posts(email):
    emails = list(Posts.objects.values_list('email', flat=True))
    if email in emails:
       Posts.objects.filter(email=email).delete()

# Main page.
def main_page(request,email):
    if request.method == 'POST':
        view_email = request.POST.get('view')
        return redirect('view_profile', email=view_email, my_email=email)
    friends_posts = Get_Friends_Posts(email)
    friends_photos = Get_Friends_Photos(email)
    return render(request,'facebook_app/main_page.html',{
        'email': email,
        'friends_posts': friends_posts,
        'friends_photos': friends_photos,
        })

# Settings.
def settings(request,email):
    return render(request,'facebook_app/settings.html',{
        'email': email,
        })

# This method returns friends posts.
def Get_Friends_Posts(email):
    hundred_minutes_ago = timezone.now() - timedelta(minutes=100)
    exists = Posts.objects.filter(date_added__gte=hundred_minutes_ago).exists()
    if exists:
       list = []
       recent_records = Posts.objects.filter(date_added__gte=hundred_minutes_ago)
       for recent_record in recent_records:
           if Is_Friend(email, recent_record.email):
               list1 = []
               user = FaceBookUsers.objects.get(email=recent_record.email)
               list1 = [user, recent_record.post]
               list.append(list1)
       if len(list) > 0:        
          return list
       else:
           return None
    return None

# This method returns friends photos.
def Get_Friends_Photos(email):
    hundred_minutes_ago = timezone.now() - timedelta(minutes=100)
    exists = Photos.objects.filter(date_added__gte=hundred_minutes_ago).exists()
    if exists:
       list = []
       recent_records = Photos.objects.filter(date_added__gte=hundred_minutes_ago)
       for recent_record in recent_records:
           if Is_Friend(email, recent_record.email):
               list1 = []
               user = FaceBookUsers.objects.get(email=recent_record.email)
               list1 = [user, recent_record]
               list.append(list1)
       if len(list) > 0:        
          return list
       else:
           return None
    return None

# User profile page
def myProfile(request,email):
    if request.method == 'POST':
       delete = request.POST.get('delete')
       if delete is not None:
           Profile_Photos.objects.filter(email=email).delete()
           return redirect('myProfile', email=email)
       else:
           text = 'myProfile'
           return redirect('upload_photo', email=email, text=text) 
             
    exists = Profile_Photos.objects.filter(email=email).exists()
    profile_photo = Default_Photo.objects.get(id=1) 
    if exists:  
       profile_photo = Profile_Photos.objects.get(email=email)
    user = FaceBookUsers.objects.get(email=email)
    user2 = PersonalInfo.objects.get(email=email)
    num_friends = Get_Num_Friends(email)
    university = user2.university
    school = user2.school
    experience = user2.experience
    city = user2.city
    country = user2.country
    return render(request,'facebook_app/myProfile.html', {
        'username': user.username,
        'num_friends': num_friends,
        'email': email,
        'university': university,
        'experience': experience,
        'school': school,
        'city': city,
        'country': country,
        'profile_photo': profile_photo,
        'exists': exists,
    })

# When a user wants to search for someone else's profile and clicks 
# the View Other Profile button, the main page will launch this process.
def otherProfile(request,email,text):
    if request.method == 'POST':
        form = OtherProfileForm(request.POST)
        if form.is_valid():
           username = form.cleaned_data["username"]
           usernames = list(FaceBookUsers.objects.values_list('username', flat=True))
           if username in usernames:
               users_profile = FaceBookUsers.objects.filter(username=username)
               for user_profile in users_profile:
                   user = SearchedUsersTable(
                       username = user_profile.username,
                       email = user_profile.email,
                   )
                   user.save()
               return redirect('otherProfile', email=email, text='None')
           else:
               text = "User Not Found"
               return redirect('otherProfile', email=email, text=text)
        
    if text == 'None':
        text = None
    users_profile = None      
    if SearchedUsersTable.objects.exists():
        users_profile = list(SearchedUsersTable.objects.all())
        SearchedUsersTable.objects.all().delete()
        
    return render(request,'facebook_app/otherProfile.html',{
        'form': OtherProfileForm(),
        'users_profile': users_profile,
        'email': email,
        'text': text,
    })

# When you go to someone else's profile, this process will start.
def view_profile(request,email,my_email):
    if request.method == 'POST':
       connection_type = request.POST.get('connection_type')
       if connection_type == 'friends':
           return redirect('remove_friend', email=email, my_email=my_email)
       elif connection_type == 'add_friend':
           Send_Request(req_email=my_email,resp_email=email)
           return redirect('view_profile', email=email, my_email=my_email)
       elif connection_type == 'remove_request':
           Remove_Requset(req_email=my_email,resp_email=email)
           return redirect('view_profile', email=email, my_email=my_email)
       else:
           text = 'view_profile'
           return redirect('response', email=email, my_email=my_email, text=text, ff_email='None')

    connection_type = '' 
    text = '' 
    if email == my_email:
        return redirect('myProfile',email=email)
    
    if Is_Friend(email,my_email):
        connection_type = 'friends'
        text = 'Friends'
    elif Is_Request(email,my_email):
        connection_type = 'remove_request'
        text = 'Remove Request'
    elif Is_Response(email,my_email):
        connection_type = 'response'
        text = 'Response'
    else:
       connection_type = 'add_friend'
       text = 'Add Friends'

    user = FaceBookUsers.objects.get(email=email)
    user2 = PersonalInfo.objects.get(email=email)
    mutual_friends = Get_Mutual_Friends(email=email,my_email=my_email)
    num_mutual_friends = 0
    if mutual_friends is not None:
       num_mutual_friends = len(mutual_friends)
    university = user2.university
    school = user2.school
    experience = user2.experience
    city = user2.city
    country = user2.country
    exists = Profile_Photos.objects.filter(email=email).exists()
    profile_photo = Default_Photo.objects.get(id=1) 
    if exists:  
       profile_photo = Profile_Photos.objects.get(email=email)
    return render(request,'facebook_app/view_profile.html',{
        'username': user.username,
        'num_mutual_friends': num_mutual_friends,
        'email': email,
        'my_email': my_email,
        'university': university,
        'experience': experience,
        'school': school,
        'city': city,
        'country': country,
        'connection_type': connection_type,
        'text': text,
        'profile_photo': profile_photo,
    })

# Sends a friend request to another user.
def Send_Request(req_email,resp_email):
    obj = Req_Resp_Table(
        req_email = req_email,
        resp_email = resp_email,
        )
    obj.save()

# When we delete a user from the list of friends, this process starts.
def remove_friend(request,email,my_email):
    if request.method == 'POST':
        Delete_Friends(email,my_email)
        return redirect('view_profile', email=email, my_email=my_email)
    return render(request,'facebook_app/remove_friend.html',{
        'email': email,
        'my_email': my_email,
    })

# When a user sends you a friend request and you press the 
# response button, this process will start.
def response(request,email,my_email,text,ff_email):
    if request.method == 'POST':
        use_email = ''
        if ff_email == 'None':
           use_email = email
        else:
           use_email = ff_email
        response = request.POST.get('response')
        if response == 'accept_request':
           Add_Friend(use_email,my_email)
        Remove_Requset(req_email=use_email,resp_email=my_email)
        if text == "find_new_friends":
           return redirect('find_new_friends', email=my_email)
        return redirect(f'{text}', email=email, my_email=my_email)
    return render(request,'facebook_app/response.html',{
        'email': email,
        'my_email': my_email,
        'ff_email': ff_email,
    })

# The function is given users' e-mails and deletes them from the friends table.
def Delete_Friends(email1,email2):
    Friends.objects.filter(email=email1, friend_email=email2).delete()
    Friends.objects.filter(email=email2, friend_email=email1).delete()

# When a user sees other user's friends, this process starts.
def view_other_all_friends(request,email,my_email):
    if request.method == 'POST':
        delete_email = request.POST.get('delete')
        view_email = request.POST.get('view')
        add_friend_email = request.POST.get('add_friend')
        response_email = request.POST.get('response')
        remove_request_email = request.POST.get('remove_request')
        
        if view_email is not None:
            return redirect('view_profile',email=view_email, my_email=my_email)
        elif delete_email is not None:
            Delete_Friends(my_email,delete_email)
            return redirect('view_other_all_friends', email=email, my_email=my_email)
        elif add_friend_email is not None:
            Send_Request(req_email=my_email,resp_email=add_friend_email)
            return redirect('view_other_all_friends', email=email, my_email=my_email)
        elif response_email is not None:
            text = 'view_other_all_friends'
            return redirect('response', email=email, my_email=my_email, text=text, ff_email=response_email)
        else:
            Remove_Requset(req_email=my_email,resp_email=remove_request_email)
            return redirect('view_other_all_friends', email=email, my_email=my_email)   

    emails = Friends.objects.values_list('email', flat=True)
    friends = []
    if email in emails:
       friends_obj = Friends.objects.filter(email=email)
       for i in friends_obj:
           username = FaceBookUsers.objects.get(email=i.friend_email).username
           status = Get_Status(my_email,i.friend_email)
           list = [username, i.friend_email, status]
           friends.append(list)
    if len(friends) == 0:
        friends = None
    return render(request,'facebook_app/view_other_all_friends.html', {
        'friends': friends,
        'email': email,
        'my_email': my_email,
        })

# When a user has sent a friend request to another user
# and then cancels it, this process starts
def Remove_Requset(req_email,resp_email):
    exists = Req_Resp_Table.objects.filter(req_email=req_email, resp_email=resp_email).exists
    if exists:
       Req_Resp_Table.objects.filter(req_email=req_email, resp_email=resp_email).delete()
            

# The function returns the relationship between two users,this return status
# for example: friend, no friend, request, response, myself.
def Get_Status(my_email,other_email):
    if my_email == other_email:
       return 'myself'
    status = ''
    if Is_Friend(my_email,other_email):
        status = 'friend'
    elif Is_Request(other_email,my_email):
        status = 'request'
    elif Is_Response(other_email,my_email):
        status = 'response'
    else:
        status = 'no friend'
    return status

# The function is given the email addresses of two users and checks
# whether one has sent a friend request to the other.
def Is_Request(other_email,my_email):
    exists = Req_Resp_Table.objects.filter(req_email=my_email, resp_email=other_email).exists()
    return exists


def Is_Response(other_email,my_email):
    return Is_Request(other_email=my_email,my_email=other_email)

# When the user goes to another user's profile and clicks the
# posts button, this process will be started.
def view_other_posts(request,email,my_email):
    emails = list(Posts.objects.values_list('email', flat=True))
    posts = ''
    size = 'size'
    if email in emails:
       posts = Posts.objects.filter(email=email)
    if len(posts) == 0:
        size = None
    return render(request,'facebook_app/view_other_posts.html', {
        "posts": posts,
        "email": email,
        "my_email": my_email,
        "size": size,
    })

# When the user goes to another user's profile and clicks 
# the personal info button, this process will start.
def other_personal_info(request,email,my_email):
    user = PersonalInfo.objects.get(email=email)
    user2 = FaceBookUsers.objects.get(email=email)
    university = user.university
    school = user.school
    experience = user.experience
    country = user.country
    city = user.city
    phone_num = user2.phone_num
    gender = user2.gender
    birthday = user2.birthday
    return render(request,'facebook_app/other_personal_info.html', {
        'email': email,
        'my_email': my_email,
        'university': university,
        'experience': experience,
        'school': school,
        'country': country,
        'city': city,
        'phone_num': phone_num,
        'gender': gender,
        'birthday': birthday,
    })

# When the user goes to another user's profile and clicks
# the mutual friends button, this process will start.
def view_mutual_friends(request,email,my_email):
    if request.method == 'POST':
        mutual_friend_email = request.POST.get('delete')
        if mutual_friend_email is None:
            mutual_friend_email = request.POST.get('view')
            return redirect('view_profile',email=mutual_friend_email, my_email=my_email)
        else:
            Friends.objects.filter(email=email, friend_email=mutual_friend_email).delete()
            Friends.objects.filter(email=mutual_friend_email, friend_email=email).delete()
            return redirect('view_mutual_friends', email=email, my_email=my_email)
    
    mutual_friends = Get_Mutual_Friends(email=email,my_email=my_email)
    return render(request,'facebook_app/view_mutual_friends.html', {
        'mutual_friends': mutual_friends,
        'email': email,
        'my_email': my_email,
        })

# The function is passed two users and returns their mutual friends.
def Get_Mutual_Friends(email,my_email):
    mutual_friends = []
    emails = Friends.objects.values_list('email', flat=True)
    if (email in emails) and (my_email in emails):
       friends1 = Friends.objects.filter(email=email)
       friends2 = Friends.objects.filter(email=my_email)
       for friend1 in friends1:
           for friend2 in friends2:
               if friend1.friend_email == friend2.friend_email:
                   user = FaceBookUsers.objects.get(email=friend1.friend_email)
                   mutual_friends.append(user)
                   break
    if len(mutual_friends) > 0:
        return mutual_friends
    return None

# When the user clicks the find new friends 
# button on the main page, this process will start.
def find_new_friends(request,email):
    if request.method == "POST":
        req_pot_friend_email = request.POST.get('response')
        if req_pot_friend_email is not None:
            text = "find_new_friends"
            return redirect('response', email=req_pot_friend_email, my_email=email, text=text, ff_email="None")
        pot_friend_email = request.POST.get('add')
        if pot_friend_email is None:
            pot_friend_email = request.POST.get('view')
            return redirect('view_profile',email=pot_friend_email, my_email=email)
        else:
            Send_Request(req_email=email, resp_email=pot_friend_email)
            return redirect('find_new_friends',email=email)
    pot_friends = Get_Pot_Friends(email)
    size = 'size'
    if len(pot_friends) == 0:
        pot_friends = Get_All_Pot_Friends(email)
        if len(pot_friends) == 0:
           size = None
    resp_pot_friends = Get_Resp_Pot_friends(email) # None, list[]
    return render(request,'facebook_app/find_new_friends.html',{
      "pot_friends": pot_friends,
      "email": email,  
      "size": size,
      "resp_pot_friends": resp_pot_friends,
    })

# The function returns the friends of the user's friends.
def Get_Pot_Friends(email):
    pot_friends = []
    user_friends = Friends.objects.filter(email=email)
    for user_friend in user_friends:
        user_friend_friends = Friends.objects.filter(email=user_friend.friend_email)
        for user_friend_friend in user_friend_friends:
            if (user_friend_friend.friend_email != email) and (user_friend_friend.friend_email not in pot_friends) and (not Is_Friend(email,user_friend_friend.friend_email)) and not Is_Request(email,user_friend_friend.friend_email) and not Is_Response(email,user_friend_friend.friend_email):
                user = FaceBookUsers.objects.get(email=user_friend_friend.friend_email) 
                pot_friends.append(user)
    return pot_friends

# The function returns all users who are not friends of the given user.
def Get_All_Pot_Friends(email):
    pot_friends = []
    users = FaceBookUsers.objects.all()
    for user in users:
        if (not Is_Friend(email,user.email)) and (email != user.email) and (not Is_Request(email,user.email)) and (not Is_Response(email,user.email)):
           pot_friends.append(user)
    return pot_friends

# The function returns all users who have sent a friend request to the given user.
def Get_Resp_Pot_friends(email):
    exists = Req_Resp_Table.objects.filter(resp_email=email).exists()
    if exists:
       resp_pot_friends = []
       user_resp_pot_friends = Req_Resp_Table.objects.filter(resp_email=email)
       for user_resp_pot_friend in user_resp_pot_friends:
           user = FaceBookUsers.objects.get(email=user_resp_pot_friend.req_email)
           resp_pot_friends.append(user)
       return resp_pot_friends
    else:
        return None

# The function is passed two users and checks if they are friends.
def Is_Friend(email,email2):
    exists = Friends.objects.filter(email=email, friend_email=email2).exists()
    if exists:
        return True
    return False
    
# The function is given two users and adds them to each other's friends
# list, i.e. locks an entry about them in the friends table.
def Add_Friend(email,friend_email):
    user = Friends(
        email = email,
        friend_email = friend_email,
    )
    user.save()

    user = Friends(
        email = friend_email,
        friend_email = email,
    )
    user.save()

# When the user is logged in to his profile and clicks
# the posts button, this process will start.
def posts(request,email):
    if request.method == 'POST':
       user_id = int(request.POST.get('remove'))
       Posts.objects.filter(id=user_id).delete()
       return redirect('posts',email=email)
    emails = list(Posts.objects.values_list('email', flat=True))
    posts = ''
    size = 'size'
    if email in emails:
       posts = Posts.objects.filter(email=email)
    if len(posts) == 0:
        size = None
    return render(request,'facebook_app/posts.html', {
        "posts": posts,
        "email": email,
        "size": size,
    })

# When the user is logged in to his profile and presses the
# personal info button, this process will start.
def personal_info(request,email):
    if request.method == 'POST':
       user = PersonalInfo.objects.get(email=email)
       detail = request.POST.get('remove')

       if detail == "experience":
           user.experience = None
       elif detail == "university":
           user.university = None
       elif detail == "school":
           user.school = None
       elif detail == "city":
           user.city = None
       elif detail == "country":
           user.country = None
       else:
           user.city = None
           user.country = None
       user.save()

       return redirect('personal_info',email=email)

    user = PersonalInfo.objects.get(email=email)
    user2 = FaceBookUsers.objects.get(email=email)
    university = user.university
    school = user.school
    experience = user.experience
    country = user.country
    city = user.city
    phone_num = user2.phone_num
    gender = user2.gender
    birthday = user2.birthday
    return render(request,'facebook_app/personal_info.html', {
        'email': email,
        'university': university,
        'experience': experience,
        'school': school,
        'country': country,
        'city': city,
        'phone_num': phone_num,
        'gender': gender,
        'birthday': birthday,
    })

# When the user is logged in to his profile and presses the 
# view all friends button, this process will start.
def view_all_friends(request,email):
    if request.method == 'POST':
        friend_email = request.POST.get('delete')
        if friend_email is None:
            friend_email = request.POST.get('view')
            return redirect('view_profile',email=friend_email, my_email=email)
        else:
            Friends.objects.filter(email=email, friend_email=friend_email).delete()
            Friends.objects.filter(email=friend_email, friend_email=email).delete()
            return redirect('view_all_friends',email=email)
    emails = Friends.objects.values_list('email', flat=True)
    friends = []
    if email in emails:
       friends_obj = Friends.objects.filter(email=email)
       for i in friends_obj:
           username = FaceBookUsers.objects.get(email=i.friend_email).username
           list = [username, i.friend_email]
           friends.append(list)
    if len(friends) == 0:
        friends = None
    return render(request,'facebook_app/view_all_friends.html', {
        'friends': friends,
        'email': email,
        })

# This process allows the user to add their work experience in personal info.
def add_experience(request,email):
    if request.method == 'POST':
        form = ChangeInfoForm(request.POST)
        if form.is_valid():
           experience = form.cleaned_data["change_info"]  
           emails = list(PersonalInfo.objects.values_list('email', flat=True))
           if email in emails:
              user = PersonalInfo.objects.get(email=email)
              user.experience = experience
              user.save()
           else:
               user = Create_User(email)
               user.experience = experience
               user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeInfoForm()
    })


# This process allows the user to add their university personal info.
def add_university(request,email):
    if request.method == 'POST':
        form = ChangeInfoForm(request.POST)
        if form.is_valid():
           university = form.cleaned_data["change_info"]  
           emails = list(PersonalInfo.objects.values_list('email', flat=True))
           if email in emails:
              user = PersonalInfo.objects.get(email=email)
              user.university = university
              user.save()
           else:
               user = Create_User(email)
               user.university = university
               user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeInfoForm()
    })

# This process allows the user to add their school in personal info.
def add_school(request,email):
    if request.method == 'POST':
        form = ChangeInfoForm(request.POST)
        if form.is_valid():
           school = form.cleaned_data["change_info"]  
           emails = list(PersonalInfo.objects.values_list('email', flat=True))
           if email in emails:
              user = PersonalInfo.objects.get(email=email)
              user.school = school
              user.save()
           else:
               user = Create_User(email)
               user.school = school
               user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeInfoForm()
    })

# This process allows the user to add country in personal info.
def add_country(request,email):
    if request.method == 'POST':
        form = ChangeInfoForm(request.POST)
        if form.is_valid():
           country = form.cleaned_data["change_info"]  
           emails = list(PersonalInfo.objects.values_list('email', flat=True))
           if email in emails:
              user = PersonalInfo.objects.get(email=email)
              user.country = country
              user.save()
           else:
               user = Create_User(email)
               user.country = country
               user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeInfoForm()
    })

# This process allows the user to add city in personal info.
def add_city(request,email):
    if request.method == 'POST':
        form = ChangeInfoForm(request.POST)
        if form.is_valid():
           city = form.cleaned_data["change_info"]  
           emails = list(PersonalInfo.objects.values_list('email', flat=True))
           if email in emails:
              user = PersonalInfo.objects.get(email=email)
              user.city = city
              user.save()
           else:
               user = Create_User(email)
               user.city = city
               user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeInfoForm()
    })

# This process allows the user to change the phone number.
def change_phone(request,email):
    if request.method == 'POST':
        form = ChangePhoneForm(request.POST)
        if form.is_valid():
           phone_num = form.cleaned_data["phone"]  
           if not Phone_Number_Is_Valid(str(phone_num)):
               text = "phone number isn't valid, format must be: 5********"
               return render(request,'facebook_app/error_message.html', {'text': text})
           if Phone_Number_Exists(phone_num):
               text = 'A user with such a number already exists in the database'
               return render(request,'facebook_app/error_message.html', {'text': text})
           user = FaceBookUsers.objects.get(email=email)
           new_user = FaceBookUsers(
                first_name = user.first_name,
                last_name = user.last_name,
                username = user.username,
                phone_num = phone_num,
                email = user.email,
                password = user.password,
                birthday = user.birthday,
                gender = user.gender,
           )
           user.delete()
           new_user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangePhoneForm()
    })

# The function checks whether there is a user with the 
# given phone number in the database.
def Phone_Number_Exists(phone_num):
    phone_numbers = list(FaceBookUsers.objects.values_list('phone_num', flat=True))
    if phone_num in phone_numbers:
        return True
    return False

# Checks if the phone number has the following format: 5********.
def Phone_Number_Is_Valid(phone_num):
    if phone_num[0] == '5' and len(phone_num) == 9:
        return True
    return False

# This process allows the user to change the email.
def change_email(request,email):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
           new_email = form.cleaned_data["email"]  
           if Email_Exists(new_email):
               text = 'A user with such a email already exists in the database'
               return render(request,'facebook_app/error_message.html', {'text': text})
           Update_PersonalInfo(email,new_email)
           Update_FaceBookUsers(email,new_email)
           Update_Friends(email,new_email)
           Update_Posts(email,new_email)   
           Update_Photos(email,new_email)
           Update_Profile_Photos(email,new_email)   
           Update_Req_Resp_Table(email,new_email)

           return redirect('personal_info',email=new_email)
            
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeEmailForm()
    })

# The function checks whether there is a user with the 
# given email in the database.
def Email_Exists(email):
    emails = list(FaceBookUsers.objects.values_list('email', flat=True))
    if email in emails:
        return True
    return False

# This process allows the user to change the password.
def change_password(request, email):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
           new_password = form.cleaned_data["password"]  
           user = FaceBookUsers.objects.get(email=email)
           user.password = new_password
           user.save()    
           return redirect('settings',email=email)
    return render(request,'facebook_app/change_password.html',{
        'form': ChangePasswordForm()
    })

# This process allows the user to change the username.
def change_username(request, email):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
           new_username = form.cleaned_data["username"]  
           user = FaceBookUsers.objects.get(email=email)
           user.username = new_username
           user.save()    
           return redirect('settings',email=email)
    return render(request,'facebook_app/change_username.html',{
        'form': ChangeUsernameForm()
    })

# When the user changes the email, the records will be updated in the Photos table.
def Update_Photos(email,new_email):
    emails = list(Photos.objects.values_list('email', flat=True))
    if email in emails:
        objs = Photos.objects.filter(email=email)
        for obj in objs:
           obj.email = new_email
           obj.save()

# When the user changes the email, the record will be updated in the Profile_Photos table.
def Update_Profile_Photos(email,new_email):
    emails = list(Profile_Photos.objects.values_list('email', flat=True))
    if email in emails:
        obj = Profile_Photos.objects.get(email=email)
        obj.email = new_email
        obj.save()

# When the user changes the email, the records will be updated in the Req_Resp_Table table.
def Update_Req_Resp_Table(email,new_email):
    emails = list(Req_Resp_Table.objects.values_list('req_email', flat=True))
    if email in emails:
        objs = Req_Resp_Table.objects.filter(req_email=email)
        for obj in objs:
            obj.req_email = new_email
            obj.save()
    
    emails = list(Req_Resp_Table.objects.values_list('resp_email', flat=True))
    if email in emails:
        objs = Req_Resp_Table.objects.filter(resp_email=email)
        for obj in objs:
            obj.resp_email = new_email
            obj.save()


# When the user changes the email, the records will be updated in the Posts table.
def Update_Posts(email,new_email):
    emails = list(Posts.objects.values_list('email', flat=True))
    if email in emails:
       objs = Posts.objects.filter(email=email)
       for obj in objs:
           obj.email = new_email
           obj.save()

# When the user changes the email, the records will be updated in the Friends table.
def Update_Friends(email,new_email):
    emails = list(Friends.objects.values_list('email', flat=True))
    if email in emails:
        objs = Friends.objects.filter(email=email)
        for obj in objs:
            obj.email = new_email
            obj.save()
    
    emails = list(Friends.objects.values_list('friend_email', flat=True))
    if email in emails:
        objs = Friends.objects.filter(friend_email=email)
        for obj in objs:
            obj.friend_email = new_email
            obj.save()
    
# When the user changes the email, the record will be updated in the FaceBookUsers table.
def Update_FaceBookUsers(email,new_email):
    emails = list(FaceBookUsers.objects.values_list('email', flat=True))
    if email in emails:
        user2 = FaceBookUsers.objects.get(email=email)
        user2.email = new_email
        user2.save()

# When the user changes the email, the records will be updated in the PersonalInfo table.
def Update_PersonalInfo(email,new_email):
    emails = list(PersonalInfo.objects.values_list('email', flat=True))
    if email in emails:
        user = PersonalInfo.objects.get(email=email)
        user.email = new_email
        user.save()
    else:
        user = Create_User(email)
        user.email = new_email
        user.save()

# This process allows the user to change the gender.
def change_gender(request,email):
    if request.method == 'POST':
        form = ChangeGenderForm(request.POST)
        if form.is_valid():
           gender = form.cleaned_data["gender"]  
           user = FaceBookUsers.objects.get(email=email)
           user.gender = gender
           user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeGenderForm()
    })

# This process allows the user to change the birhday.
def change_birhday(request,email):
    if request.method == 'POST':
        form = ChangeBirthdayForm(request.POST)
        if form.is_valid():
           birthday = form.cleaned_data["birthday"]  
           user = FaceBookUsers.objects.get(email=email)
           user.birthday = birthday
           user.save()
           return redirect('personal_info',email=email)
    return render(request,'facebook_app/add_or_change_info.html',{
        'form': ChangeBirthdayForm()
    })

# Creates a PersonalInfo type object and return it.
def Create_User(email):
    user = PersonalInfo(
        email = email,
        experience = None,
        university = None,
        school = None,
        city = None,
        country = None,
    )
    return user

# Allows the user to upload a photo.
def upload_photo(request,email,text):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            if text == 'myProfile':
               exists = Profile_Photos.objects.filter(email=email).exists()
               if exists:
                   Profile_Photos.objects.get(email=email).delete()
               else:
                   photo = Photos(
                       image = form.cleaned_data["image"],
                       email = email,
                   )
                   photo.save()
               profile_photo = Profile_Photos(
                       image = form.cleaned_data["image"],
                       email = email,
                   )
               profile_photo.save()
               return redirect('myProfile',email=email)
            else:
                photo = Photos(
                    image = form.cleaned_data["image"],
                    email = email,
                )
                photo.save()
                return redirect('view_my_photos',email=email)
    else:
        form = PhotoForm()
    return render(request, 'facebook_app/upload_photo.html', {'form': form})

# When the user is logged in to their profile and clicks
# on the photos button, this process will start.
def view_my_photos(request,email):
    if request.method == 'POST':
       delete_id = request.POST.get('delete')
       if delete_id is not None:
          Photos.objects.get(id=int(delete_id)).delete()  
          return redirect('view_my_photos',email=email)
       else:
           set_profile = int(request.POST.get('set_profile'))
           image = Photos.objects.get(id=set_profile).image
           exists = Profile_Photos.objects.filter(email=email).exists()
           if exists:
              Profile_Photos.objects.get(email=email).delete()
           profile_photo = Profile_Photos(
               email = email,
               image = image,
           )
           profile_photo.save()
           photo = Photos(
               email = email,
               image = image,
           )
           photo.save()
           Photos.objects.get(id=set_profile).delete()
           return redirect('myProfile',email=email)
               
    exists = Photos.objects.filter(email=email).exists()
    photos = None
    if exists:
        photos = Photos.objects.filter(email=email)
    return render(request, 'facebook_app/view_my_photos.html', {
        'photos': photos,
        'email': email,
        })
    
# Allows users to add a post.
def add_post(request,email):
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
           post = form.cleaned_data["post"]
           obj = Posts(
               email = email,
               post = post,
           )
           obj.save()
           return redirect('posts',email=email)
    return render(request,'facebook_app/add_post.html', {
        'form': AddPostForm(),
    })

# The function is given the user's email address and 
# returns the number of his friends.
def Get_Num_Friends(email):
    return len(Friends.objects.filter(email=email))

# When the user is logged in to another user's profile 
# and clicks the photos button, this process will start.
def view_other_photos(request,email,my_email):
    exists = Photos.objects.filter(email=email).exists()
    photos = None
    if exists:
        photos = Photos.objects.filter(email=email)
    return render(request, 'facebook_app/view_other_photos.html', {
        'photos': photos,
        'email': email,
        'my_email': my_email,
        })


