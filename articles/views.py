import json
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from users.serializers import UsersSerializer
from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer

    queryset = Article.objects.all()

    def list(self, request):
        articles = Article.objects.filter(user=request.user)

        response = {
            'data': list(articles.values())
        }

        return JsonResponse(response)


# 01. C - 게시글 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_articles(request):
    user = request.user
    body = json.loads(request.POST["data"])

    if 'image' in request.FILES:
        article = Article(
            emotion=body['emotion'],
            location=body['location'],
            menu=body['menu'],
            weather=body['weather'],
            image=request.FILES["image"],
            song=body['song'],
            point=body['point'],
            content=body['content'],
            user=user)
    else:
        article = Article(
            emotion=body['emotion'],
            location=body['location'],
            menu=body['menu'],
            weather=body['weather'],
            song=body['song'],
            point=body['point'],
            content=body['content'],
            user=user)

    article.save()

    serializer = ArticleSerializer(article, context={'request': request})

    return JsonResponse({"success": True,  "data": serializer.data})

    # if serializer.is_valid():
    #     serializer.save()
    #     return JsonResponse(serializer.data)
    # else:
    #     return JsonResponse(serializer.error_messages())


# 02. R - 상대방 게시글 전체 목록
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_friends_articles(request, pk):
    article = Article.objects.filter(user=pk)
    serializer = ArticleSerializer(article, many=True, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 02. R - 상대방 게시글 검색해셔 가져오기
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends_articles(request, pk):
    year = int(request.data["year"])
    month = int(request.data["month"])

    article = Article.objects.filter(user=pk, created__year=year, created__month=month)
    serializer = ArticleSerializer(article, many=True, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 02. R - 내 게시글 목록(get)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_articles(request):
    year = int(request.GET['year'])
    month = int(request.GET['month'])

    articles = Article.objects.filter(user=request.user, created__year=year, created__month=month)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 02. R - 피드 일기 목록(get_all)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_allarticles(request):
    followings = UsersSerializer(request.user).data.get('followings')
    target_users = followings + [request.user]

    articles = Article.objects.filter(user__in=target_users)

    serializer = ArticleSerializer(articles, many=True, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 02. R - 게시글 한 개만 가져오기(get_single_article/<int:pk>)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_single_article(request, pk):
    article = Article.get_object(pk)
    serializer = ArticleSerializer(article, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 03. U - 게시글 수정(update/<int:pk>/)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_articles(request, pk):
    article = Article.get_object(pk)

    if article.user != request.user:
        return JsonResponse({
            'success': False,
            'message': '작성자 본인만 수정할 수 있습니다'
        })

    if 'image' in request.FILES:
        article.image = request.FILES['image']

    article.emotion = request.data['emotion']
    article.location = request.data['location']
    article.menu = request.data['menu']
    article.weather = request.data['weather']
    article.song = request.data['song']
    article.point = request.data['point']
    article.content = request.data['content']

    article.save()

    serializer = ArticleSerializer(article, context={'request': request})

    response = {
        'success': True,
        'data': serializer.data
    }

    return JsonResponse(response)


# 04. D - 게시글 삭제(delete/<int:pk>/)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_articles(request, pk):
    article = Article.get_object(pk)
    article.delete()
    serializer = ArticleSerializer(article, context={'request': request})
    return JsonResponse({'success': True, 'data': serializer.data})

#
# # 05. 게시글 하트(post/<int:pk>/like/)
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def post_like_articles(request, pk):
#     article = Article.get_object(pk)
#     article.liked = True
#     article.num_liked += 1
#     article.save()
#     serializer = ArticleSerializer(article, context={'request': request})
#     return JsonResponse({'success': True, 'data': serializer.data})
#
#
# # 06. 게시글 하트 취소(post/<int:pk>/unlike/)
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def post_unlike_articles(request, pk):
#     article = Article.get_object(pk)
#     if article.num_liked > 0:
#         article.liked = False
#         article.num_liked -= 1
#         article.save()
#         serializer = ArticleSerializer(article, context={'request': request})
#         return JsonResponse({'success': True, 'data': serializer.data})
#     else:
#         return JsonResponse({'success': False})


# 05. 게시글 하트(post/<int:pk>/like/)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like_articles(request, pk):
    article = Article.get_object(pk)
    status = 'unliked'

    if article.liked.filter(pk=request.user.pk).exists():
        article.liked.remove(request.user)
    else:
        article.liked.add(request.user)
        status = 'liked'

    article.save()

    serializer = ArticleSerializer(article, context={'request': request})

    response = serializer.data
    response.update({'status': status})

    return JsonResponse(response)

