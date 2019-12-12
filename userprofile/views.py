from .forms import ProfileForm
from .models import Profile
from login.models import User
from django.shortcuts import render, redirect, HttpResponse


def profile_edit(request, id):
    if not request.session.get('is_login', None):
        return HttpResponse('您尚未登陆')
    if not User.objects.filter(id=id):
        return HttpResponse('您无权修改他人profile')
    user = User.objects.get(id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)
    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.session.get('user_id', None) != user.id:
            return HttpResponse('您无权修改别人的个人信息!')
        profile_form = ProfileForm(data=request.POST, files=request.FILES)
        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            # 带参数的 redirect()
            return redirect("user_profile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
