import os
import unittest
 
# from project1 import applicatn, udb
from applicatn import app,db
 
 
TEST_DB = 'test.db'
# class RoutingTests(unittest.TestCase):
#     # function to set up testing connection
#     def set_up():
#          app.config["TESTING"] = True
#          app.config["DEBUG"] = True
#          self.app = app.test_client()
#          self.assertEqual(app.debug,False)
#     # function to teardown connection after testing
#     def tear_down():
#          pass
    
#     def testindex(self):
#         response = self.app.get('/', follow_redirects=True)
#         self.assertEqual(response.status_code, 200)
    



 
 
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://rrdnriysxsimpz:23925e50fe33eb9d0838901dfc3f64e358e501951160b4b95b2f7a371e31a2a4@ec2-50-17-90-177.compute-1.amazonaws.com:5432/dchrk207jeq5do"
        self.app = app.test_client()
        # db.drop_all()
        # db.create_all()
 
        # Disable sending emails during unit testing
        # mail.init_app(app)
        # self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
 
 
###############
#### tests ####
###############
 
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    def test_register(self):
        response = self.app.get('/register', follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_review(self):
        review_data = Review.query.filter(and_(Review.isbn == "0441017835", Review.email == "moksh@gmail.com")).first()
        print(review_data)
        if (review_data== None):
            flag= False
        else: flag= True
        self.assertTrue(flag)
        

    
    def test_search(self):
        books_result = Book.query.filter(or_(Book.isbn.ilike('Mein kampf'), Book.title.ilike('Mein kampf'), Book.author.ilike('Mein kampf')))
        # books_result = getbooks('Mein kampf')
        print(books_result)
        if not books_result:
            flag = False
        else: flag = True 
        print(flag)
        self.assertTrue(flag)
    
    def test_bookpage(self):
        book1 = Book.query.filter(Book.isbn == "074349671X").all()
        for item in book1:
            if (item.title == "The Tenth Circle"):
                flag = True
            else: flag = False
            self.assertTrue(flag)
      

 
 
if __name__ == "__main__":
    unittest.main()
