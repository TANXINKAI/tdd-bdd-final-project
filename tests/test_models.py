# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)
    
    def test_add_a_product_negative(self):
        """It should not Create a product with invalid fields and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Empty product, TypeError.
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize,[])
        # Missing keys, KeyError.
        self.assertRaises(DataValidationError, product.deserialize, {'name':"Fedora"})
        # Invalid Attributes, AttributeError.
        product = ProductFactory()
        product_dict = product.serialize()
        product_dict['category'] = "Fail""abc"
        self.assertRaises(DataValidationError, product.deserialize, product_dict)
        # Invalid product.available Invalid type for boolean.
        product = ProductFactory()
        product_dict = product.serialize()
        product_dict['available'] = 8
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        # Check that it matches the original product
        found_product = Product.find(product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)
    
    def test_update_a_product(self):
        """It should update a product"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()        
        product.id = None
        app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        
        ori_id = products[0].id

        # Update op.
        product.name = 'Testing'
        product.price = 12.50
        product.description="A red hat"
        product.available=True
        product.category=Category.CLOTHS
        product.update()

        # Assert no addition to db.
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check updated.
        updated_product = products[0]
        self.assertEqual(updated_product.id, ori_id)
        self.assertEqual(updated_product.name, 'Testing')
        self.assertEqual(updated_product.price, 12.50)
        self.assertEqual(updated_product.description, "A red hat")
        self.assertEqual(updated_product.available, True)
        self.assertEqual(updated_product.category, Category.CLOTHS)
    
    def test_update_a_product_negative(self):
        """It should not update a product with no id"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()        
        product.id = None
        app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        
        # Update op.
        product.id = None
        product.name = 'Testing'

        self.assertRaises(DataValidationError, product.update)
        
    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()        
        product.id = None
        app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        self.assertEqual(len(Product.all()), 1)
        
        # Delete op.
        product.delete()
        
        # Assert deletion.
        self.assertEqual(len(Product.all()), 0)
      
    def test_list_all_product(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(products, [])
        
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
            product.create()        
        
        # Assert size is 5.
        products = Product.all()
        self.assertEqual(len(products),5)
        
    def test_find_by_name(self):
        """It should Find All products by Name"""
        products = Product.all()
        self.assertEqual(products, [])
        products = ProductFactory.create_batch(5)
        for product in products:
            product.id = None
            app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
            product.create()        
        
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        # Assert name matches expected name.
        for item in found:
            self.assertEqual(item.name, name)
    
    def test_find_by_availability(self):
        """It should Find All products by Availability"""
        products = Product.all()
        self.assertEqual(products, [])
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
            product.create()        
        
        availability = products[0].available
        count = len([product for product in products if product.available == availability])
        found = Product.find_by_availability(availability)
        self.assertEqual(found.count(), count)
        # Assert availability matches expected availability.
        for item in found:
            self.assertEqual(item.available, availability)

    def test_find_by_category(self):
        """It should Find All products by Category"""
        products = Product.all()
        self.assertEqual(products, [])
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
            product.create()        
        
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        # Assert category matches expected category.
        for item in found:
            self.assertEqual(item.category, category)
    
    def test_find_by_price(self):
        """It should Find All products by Price"""
        products = Product.all()
        self.assertEqual(products, [])
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            app.logger.info(f"id={product.id}, name={product.name}, description={product.description}, availability={product.available}, price={product.price}, category={product.category}")
            product.create()   

        price = products[0].price
        price_string = str(price)
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price_string)
        self.assertEqual(found.count(), count)
        # Assert price matches expected price.
        for item in found:
            self.assertEqual(item.price, price)