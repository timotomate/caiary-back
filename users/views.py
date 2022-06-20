import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from json.decoder import JSONDecodeError
from users.models import User
from users.serializers import UsersSerializer


@csrf_exempt
def kakao_login(request):
    """
    카카오 로그인

    클라이언트에서 카카오 로그인 후 받아온 액세스 토큰을 헤더에 포함해서 보내주세요. (Authorization: Bearer {access_token})
    """
    if request.method == 'POST':
        """
        Check Access Token & Get Email Address
        """
        headers = {
            'Authorization': request.headers['Authorization']
        }

        user_info_req = requests.get('https://kapi.kakao.com/v2/user/me', headers=headers)
        user_info = user_info_req.json()

        error = user_info.get('error')
        if error is not None:
            raise JSONDecodeError(error)

        try:
            kakao_account = user_info['kakao_account']
        except KeyError:
            return JsonResponse({
                'success': False,
                'message': '유효하지 않은 액세스 토큰입니다'
            })

        email = kakao_account['email']
        username = kakao_account['profile']['nickname']
        profile_image_url = kakao_account['profile']['profile_image_url']

        try:
            user = User.objects.get(email=email)

            if profile_image_url != user.profile_image_url:
                user.profile_image_url = profile_image_url
                user.save()

        except User.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            user = User.objects.create_user(email)
            user.username = username
            user.profile_image_url = profile_image_url
            user.save()

        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            'success': True,
            'email': email,
            'access_token': str(refresh.access_token),
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request):
    """
    내 프로필

    내 프로필 데이터를 불러옵니다.
    """
    serializer = UsersSerializer(request.user)

    response = serializer.data

    return JsonResponse(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request, user_pk):
    """
    ID로 상대방 프로필 불러오기

    특정 유저의 ID를 이용하여 프로필 데이터를 불러옵니다.
    """
    try:
        user = User.objects.get(id=user_pk)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '해당 유저를 찾을 수 없습니다'
        })

    serializer = UsersSerializer(user)

    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_by_email(request):
    """
    이메일로 상대방 프로필 불러오기

    특정 유저의 이메일를 이용하여 프로필 데이터를 불러옵니다.
    """
    email = request.GET.get('email')

    if not email:
        return JsonResponse({
            'success': False,
            'message': '이메일을 입력해주세요'
        })

    try:
        profile = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '존재하지 않는 사용자입니다'
        })

    serializer = UsersSerializer(profile)

    return JsonResponse(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_by_username(request):
    """
    닉네임으로 유저 검색

    닉네임으로 유저를 검색합니다.
    """
    username = request.GET.get('username')

    if not username:
        return JsonResponse({
            'success': False,
            'message': '닉네임을 입력해주세요'
        })

    users = User.objects.filter(username=username)

    serializer = UsersSerializer(users, many=True)
    data = serializer.data

    response = {
        'data': data
    }

    return JsonResponse(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_pk):
    """
    유저 팔로우

    특정 유저의 ID로 팔로우합니다. 팔로우가 이미 되어 있는 상태라면 언팔로우됩니다.
    """
    try:
        target_user = User.objects.get(id=user_pk)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '팔로우하려는 유저를 찾을 수 없습니다'
        })

    serializer = UsersSerializer(target_user)

    if target_user == request.user:
        return JsonResponse({
            'success': False,
            'message': '자기 자신을 팔로우할 수 없습니다'
        })

    if target_user.followers.filter(pk=request.user.pk).exists():
        target_user.followers.remove(request.user)
        response = serializer.data
        response.update({'status': 'unfollowed'})

        return JsonResponse(response)

    target_user.followers.add(request.user)

    response = serializer.data
    response.update({'status': 'followed'})

    return JsonResponse(response)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_username(request, user_pk):
    """
    닉네임 수정

    나의 닉네임을 수정합니다.
    """
    try:
        target_user = User.objects.get(id=user_pk)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '닉네임을 설정하려는 유저를 찾을 수 없습니다'
        })

    try:
        data = json.loads(request.body)
        username = data['username']
    except JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '설정할 닉네임을 입력해주세요'
        })

    if not username:
        return JsonResponse({
            'success': False,
            'message': '설정할 닉네임을 입력해주세요'
        })

    target_user.username = username

    serializer = UsersSerializer(target_user)

    return JsonResponse(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_user_list_by_id(request):
    """
    ID 배열로 여러 유저 프로필 불러오기

    여러 유저의 프로필 데이터를 한 번에 불러올 수 있습니다.
    """

    try:
        data = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '유저 아이디 목록을 입력해주세요'
        })

    id_list = data['id_list']
    user_list = User.objects.filter(id__in=id_list)

    serializer = UsersSerializer(user_list, many=True)

    return JsonResponse({'data': serializer.data}, safe=False)

