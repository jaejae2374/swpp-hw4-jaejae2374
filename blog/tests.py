from django.test import TestCase, Client
import json
from blog.models import User, Article, Comment


class BlogTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username="testuser",
            password="password"
        )
        cls.user_data = {
            "username": "testuser",
            "password": "password"
        }
        cls.test_stranger = User.objects.create_user(
            username="teststranger",
            password="password"
        )
        cls.stranger_data = {
            "username": "teststranger",
            "password": "password"
        }
        cls.stranger_article = Article.objects.create(
            title=f"test stranger article title",
            content=f"test stranger article content",
            author=cls.test_stranger
        )

        cls.articles = []
        for i in range(10):
            cls.articles.append(
                Article.objects.create(
                    title=f"test article title..{i}",
                    content=f"test article content..{i}",
                    author=cls.test_user
            ))
        cls.comments = []
        for i in range(3):
            cls.comments.append(
                Comment.objects.create(
                    content=f"test comment content..{i}",
                    author=cls.test_user,
                    article=cls.articles[2]
            ))

        cls.stranger_comments = []
        for i in range(2):
            cls.stranger_comments.append(
                Comment.objects.create(
                    content=f"test comment content of stranger..{i}",
                    author=cls.test_stranger,
                    article=cls.articles[3]
            ))
        

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

        response = self.client.put('/api/token/')
        self.assertEqual(response.status_code, 405)
        
    def test_signup(self):
        data = {
            "username": "swpp",
            "password": "iluvswpp"
        }
        response = self.client.post(
            "/api/signup/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.put(
            "/api/signup/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 405)

    def test_signin(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)

        wrong_data = {
            "username": "wrongusername",
            "password": "wrongpassword"
        }
        response = self.client.post(
            "/api/signin/",
            data=wrong_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.put(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 405)

    def test_signout(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.put(
            "/api/signout/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 405)

    def test_create_article(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        data = {
            "title": "test create title",
            "content": "test create content"
        }
        response = self.client.post(
            "/api/article/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertIn("id", response)
        self.assertEqual(response['title'], data['title'])
        self.assertEqual(response['content'], data['content'])
        self.assertIn("author", response)

        wrong_data = {
            "title": "test create title"
        }
        response = self.client.post(
            "/api/article/",
            data=wrong_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        response = self.client.post(
            "/api/article/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_list_articles(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )

        response = self.client.get(
            "/api/article/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), len(self.articles)+1)
        for i in range(len(self.articles)):
            self.assertEqual(data[i+1]['id'], self.articles[i].id)
            self.assertEqual(data[i+1]['title'], self.articles[i].title)
            self.assertEqual(data[i+1]['content'], self.articles[i].content)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.get(
            "/api/article/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_retrieve_article(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        response = self.client.get(
            "/api/article/9999/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            f"/api/article/{self.articles[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['author'], self.articles[0].author.id)
        self.assertEqual(data['title'], self.articles[0].title)
        self.assertEqual(data['content'], self.articles[0].content)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.get(
            f"/api/article/{self.articles[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_update_article(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        data = {
            "title": "modified title !",
            "content": "modified content !"
        }

        response = self.client.put(
            "/api/article/9999/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            f"/api/article/{self.articles[0].id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['id'], self.articles[0].id)
        self.assertEqual(response['author'], self.articles[0].author.id)
        self.assertEqual(response['title'], data['title'])
        self.assertEqual(response['content'], data['content'])

        wrong_data = {
            "content": "test update content"
        }
        response = self.client.put(
            f"/api/article/{self.articles[0].id}/",
            data=wrong_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            f"/api/article/{self.stranger_article.id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )

        response = self.client.put(
            f"/api/article/{self.articles[0].id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        

    def test_delete_article(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        response = self.client.delete(
            "/api/article/9999/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(
            f"/api/article/{self.articles[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.articles[0].id, Article.objects.all())

        response = self.client.delete(
            f"/api/article/{self.stranger_article.id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.delete(
            f"/api/article/{self.articles[1].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_comment(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        data = {
            "content": "test create comment"
        }
        response = self.client.post(
            f"/api/article/{self.articles[0].id}/comment/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertIn("id", response)
        self.assertEqual(response['article'], self.articles[0].id)
        self.assertEqual(response['content'], data['content'])
        self.assertEqual(response["author"], self.test_user.id)

        response = self.client.post(
            "/api/article/9999/comment/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        wrong_data = {
            "conten": "wrong field name."
        }
        response = self.client.post(
            f"/api/article/{self.articles[0].id}/comment/",
            data=wrong_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        response = self.client.post(
            f"/api/article/{self.articles[0].id}/comment/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_list_comments(self):
        response = self.client.post(
        "/api/signin/",
        data=self.user_data,
        content_type="application/json"
        )

        response = self.client.get(
            f"/api/article/{self.articles[2].id}/comment/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), len(self.comments))
        for i in range(len(self.comments)):
            self.assertEqual(data[i]['id'], self.comments[i].id)
            self.assertEqual(data[i]['author'], self.test_user.id)
            self.assertEqual(data[i]['content'], self.comments[i].content)
            self.assertEqual(data[i]['article'], self.articles[2].id)

        response = self.client.get(
            "/api/article/9999/comment/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.get(
            f"/api/article/{self.articles[2].id}/comment/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_retrieve_comment(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        response = self.client.get(
            "/api/comment/9999/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            f"/api/comment/{self.comments[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['author'], self.comments[0].author.id)
        self.assertEqual(data['article'], self.comments[0].article.id)
        self.assertEqual(data['content'], self.comments[0].content)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.get(
            f"/api/comment/{self.comments[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_update_comment(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        data = {
            "content": "modified content !"
        }

        response = self.client.put(
            "/api/comment/9999/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            f"/api/comment/{self.comments[0].id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['id'], self.comments[0].id)
        self.assertEqual(response['author'], self.comments[0].author.id)
        self.assertEqual(response['article'], self.comments[0].article.id)
        self.assertEqual(response['content'], data['content'])

        wrong_data = {
            "conten": "wrong field name."
        }
        response = self.client.put(
            f"/api/comment/{self.comments[0].id}/",
            data=wrong_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            f"/api/comment/{self.stranger_comments[0].id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        response = self.client.put(
            f"/api/comment/{self.comments[0].id}/",
            data=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_comment(self):
        response = self.client.post(
            "/api/signin/",
            data=self.user_data,
            content_type="application/json"
        )
        response = self.client.delete(
            "/api/comment/9999/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(
            f"/api/comment/{self.comments[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.comments[0].id, Comment.objects.all())

        response = self.client.delete(
            f"/api/comment/{self.stranger_comments[0].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        self.client.delete(
            f"/api/article/{self.articles[2].id}/",
            content_type="application/json"
        )
        self.assertEqual(False, Comment.objects.filter(author=self.test_user).exists())

        response = self.client.get(
            "/api/signout/",
            content_type="application/json"
        )
        
        response = self.client.delete(
            f"/api/comment/{self.comments[1].id}/",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)


        




