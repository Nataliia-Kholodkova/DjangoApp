from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from api.serializers import PostSerializer, CommentSerializer
from myapp.models import Post, Comment


class AuthorModelTest(APITestCase):
    client = APIClient()

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(first_name='Test_First_Name', last_name='Test_Last_Name',
                                         email='Test_Email@ukr.net', password='test12345', username='test1',
                                         is_active=True)
        user2 = User.objects.create_user(first_name='Test_First_Name_2', last_name='Test_Last_Name_2',
                                         email='Test_Email_2@ukr.net', password='test12345', username='test2',
                                         is_active=True)
        user1.save()
        user2.save()
        post = Post.objects.create(title='Test1', text='Text for test1', user=user1)
        post.save()
        comment = Comment.objects.create(user=user2, post=post, text='Some test Comment from user2')
        comment.save()

    def test_login_valid_user(self):
        response = self.client.post("/api/token/get/", {"username": "test1", "password": "test12345"}, format='json')
        self.assertIn("access", response.data)
        self.assertEquals(response.status_code, 200)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer' + token)
        response = self.client.login(username="test1", password="test12345")
        self.assertEquals(response, True)

    def test_login_invalid_user(self):
        response = self.client.post("/api/token/get/", {"username": "not_a_user", "password": "some"},
                                    format='json')
        self.assertEquals(response.status_code, 401)
        token = 'ajdnjndnaldnlkdnlknljnljbnlNBKlnDlnlnljzdngaljnzmk;dzjfngjkzdnfjkzdnkakdbnjkadgbjkganjknjkgn'
        self.client.credentials(HTTP_AUTHORIZATION='Token Bearer' + token)
        response = self.client.login(username="not_a_user", password="some")
        self.assertEquals(response, False)

    def test_register(self):
        response = self.client.post('/api/register/',
                                    {'username': 'test3', 'password1': 'test12345', 'password2': 'test12345',
                                     'email': 'TestEmail3@ukr.net'})

        self.assertEquals(response.status_code, 201)
        response = self.client.post("/api/token/get/", {"username": "test3", "password": "test12345"}, format='json')

        self.assertIn("access", response.data)
        self.assertEquals(response.status_code, 200)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Token Bearer' + token)
        response = self.client.login(username="test1", password="test12345")
        self.assertEquals(response, True)

    def test_get_posts(self):
        response = self.client.post("/api/token/get/", {"username": "test1", "password": "test12345"},
                                    format='json', follow=True)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/api/posts/', format='json')
        self.assertEquals(response.status_code, 200)
        posts = PostSerializer(Post.objects.all(), many=True)

        self.assertEqual(posts.data, response.data)

    def test_get_posts_unregistered_user(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        self.assertEquals(response.status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/posts/')
        self.assertEquals(response.status_code, 401)
        #

    def test_get_posts_own(self):
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/api/posts/own/', format='json')
        self.assertEquals(response.status_code, 200)

        posts = PostSerializer(Post.objects.filter(user__username='test1').all(), many=True)
        self.assertEqual(posts.data, response.data)

    def test_get_posts_own_unregistered(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        self.assertEquals(response.status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/posts/own/')
        self.assertEquals(response.status_code, 401)

    def test_add_post(self):
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post('/api/posts/add/', {"title": "Posttest1", "text": "test1_post"}, format='json')
        self.assertEquals(response.status_code, 201)

        post_last = PostSerializer(Post.objects.filter(user__username='test1').order_by('-created_date').all()[0])
        post_created = PostSerializer(
            Post.objects.filter(user__username='test1').filter(title='Posttest1').filter(text='test1_post').get())
        self.assertEqual(post_created.data, post_last.data)

    def test_add_post_unregisterd(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        self.assertEquals(response.status_code, 401)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/post/add/', {"title": "Posttest1", "text": "test1_post"}, format='json')
        self.assertEquals(response.status_code, 404)

    def test_delete_post(self):
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        posts_before_delete = Post.objects.filter(user__username='test1').all()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post('/api/posts/delete/1/')
        self.assertEquals(response.status_code, 200)

        posts_after_delete = Post.objects.filter(user__username='test1').all()

        self.assertNotEqual(posts_before_delete, posts_after_delete)

    def test_delete_post_unregisterd(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        posts_before_delete = Post.objects.filter(user__username='test1')
        self.assertEquals(response.status_code, 401)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/posts/delete/1/')
        self.assertEquals(response.status_code, 401)
        posts_after_delete = Post.objects.filter(user__username='test1')
        self.assertEqual(len(posts_before_delete), len(posts_after_delete))

    def test_add_like(self):
        post_before_like = Post.objects.get(id=1)
        self.assertEqual(post_before_like.likes, 0)
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post('/api/posts/like/1/',
                                    format='json')
        self.assertEquals(response.status_code, 201)
        post_after_like = Post.objects.get(id=1)

        self.assertEqual(post_after_like.likes, 1)

    def test_add_like_unregisterd(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        self.assertEquals(response.status_code, 401)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/post/like/1/', {"title": "Posttest1", "text": "test1_post"},
                                    format='json')
        self.assertEquals(response.status_code, 404)

    def test_add_dislike(self):
        post_before_dislike = Post.objects.get(id=1)
        self.assertEqual(post_before_dislike.dislikes, 0)
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post('/api/posts/dislike/1/',
                                    format='json')
        self.assertEquals(response.status_code, 201)
        post_after_dislike = Post.objects.get(id=1)

        self.assertEqual(post_after_dislike.dislikes, 1)

    def test_add_dislike_unregisterd(self):
        response = self.client.post('/api/token/get/', {'username': 'notuser', 'password': 'test12345'})
        self.assertEquals(response.status_code, 401)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer' + 'agiuHGIJISFJFGjfdnskjgnadkjnjkdnjndjkanddasbghjbasgbka')
        response = self.client.post('/api/post/dislike/1/', {"title": "Posttest1", "text": "test1_post"},
                                    format='json')
        self.assertEquals(response.status_code, 404)

    def test_add_comment(self):
        comments_before_add = Comment.objects.filter(post__pk=1).all()
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post('/api/posts/comments/add/1/', {"text": "NEW COMMENT"},
                                    format='json')
        comments_after_add = Comment.objects.filter(post__pk=1).all()
        self.assertEquals(response.status_code, 201)

        self.assertNotEqual(comments_before_add, comments_after_add)

    def test_get_comments(self):
        response = self.client.post('/api/token/get/', {'username': 'test1', 'password': 'test12345'})
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/api/posts/comments/get/1/', format='json')
        self.assertEquals(response.status_code, 200)

        posts = CommentSerializer(Comment.objects.filter(post__id='1').all(), many=True)
        self.assertEqual(posts.data, response.data)
