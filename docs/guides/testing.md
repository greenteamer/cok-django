# Testing Strategy

This document describes the testing approach for the project.

## Current State

**Status**: No tests currently implemented

This is a foundational template project. Tests should be added as business logic is implemented.

---

## Testing Philosophy

When adding tests, follow these principles:

1. **Test behavior, not implementation** - Focus on what the code does, not how
2. **Test at the right level** - Unit tests for logic, integration tests for workflows
3. **Write tests first** (TDD) or immediately after implementing features
4. **Keep tests fast** - Slow test suites don't get run
5. **Make tests readable** - Tests are documentation

---

## Testing Levels

### Unit Tests

**Purpose**: Test individual functions, methods, and models in isolation

**Scope**: Single function or method

**Speed**: Very fast (<100ms per test)

**Example** (when implemented):
```python
# myapp/tests/test_models.py
from django.test import TestCase
from myapp.models import Product

class ProductModelTest(TestCase):
    def test_product_str_representation(self):
        product = Product(name="Test Product", price=99.99)
        self.assertEqual(str(product), "Test Product")

    def test_product_discount_calculation(self):
        product = Product(price=100, discount_percent=10)
        self.assertEqual(product.discounted_price(), 90)
```

---

### Integration Tests

**Purpose**: Test interaction between components (views, models, database)

**Scope**: Multiple components working together

**Speed**: Medium (100-500ms per test)

**Example** (when implemented):
```python
# myapp/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_product_list_view(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Products")
```

---

### End-to-End Tests

**Purpose**: Test complete user workflows from browser perspective

**Scope**: Entire application stack

**Speed**: Slow (1-10s per test)

**Tools**: Selenium, Playwright, or Cypress

**Example** (when implemented):
```python
# myapp/tests/test_e2e.py
from django.test import LiveServerTestCase
from selenium import webdriver

class CheckoutE2ETest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_user_can_checkout(self):
        # User visits site
        self.browser.get(self.live_server_url)
        # User adds product to cart
        # User proceeds to checkout
        # User completes payment
        # Assert order is created
```

---

## Test Organization

Organize tests in each Django app:

```
myapp/
├── models.py
├── views.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_integration.py
```

Or use a single `tests.py` file for simple apps:

```
myapp/
├── models.py
├── views.py
└── tests.py
```

---

## Running Tests

### Run All Tests

```bash
# Via Makefile
make test

# Or directly
docker-compose exec web python manage.py test
```

---

### Run Specific Tests

```bash
# Test a specific app
docker-compose exec web python manage.py test myapp

# Test a specific test case
docker-compose exec web python manage.py test myapp.tests.test_models.ProductModelTest

# Test a specific test method
docker-compose exec web python manage.py test myapp.tests.test_models.ProductModelTest.test_product_str_representation
```

---

### Run with Coverage

Install coverage:
```bash
# Add to requirements.txt
coverage==7.3.2
```

Run tests with coverage:
```bash
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
docker-compose exec web coverage html
```

View HTML coverage report:
```bash
open htmlcov/index.html
```

---

## Test Database

Django automatically creates a test database (`test_django_db`) when running tests.

**Characteristics**:
- Created before each test run
- Destroyed after test run
- Separate from development database
- No data loss from running tests

**Configuration** (if needed):
```python
# config/settings.py
DATABASES = {
    'default': {
        # ... production config
    }
}

# Override test database name if needed
if 'test' in sys.argv:
    DATABASES['default']['NAME'] = 'test_django_db'
```

---

## Testing Patterns

### Fixtures and Factories

**Django Fixtures** (JSON/YAML data):
```python
class ProductTest(TestCase):
    fixtures = ['products.json']

    def test_product_exists(self):
        product = Product.objects.get(pk=1)
        self.assertEqual(product.name, "Test Product")
```

**Factory Boy** (recommended for complex models):
```bash
# Add to requirements.txt
factory-boy==3.3.0
```

```python
# myapp/tests/factories.py
import factory
from myapp.models import Product

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)

# myapp/tests/test_models.py
from .factories import ProductFactory

class ProductTest(TestCase):
    def test_product_creation(self):
        product = ProductFactory()
        self.assertIsNotNone(product.pk)
```

---

### Mocking External Dependencies

Use `unittest.mock` for external services:

```python
from unittest.mock import patch
from django.test import TestCase

class PaymentTest(TestCase):
    @patch('myapp.services.stripe.charge')
    def test_payment_success(self, mock_charge):
        mock_charge.return_value = {'status': 'success'}

        result = process_payment(amount=100)

        self.assertEqual(result['status'], 'success')
        mock_charge.assert_called_once_with(amount=100)
```

---

### Testing Authentication

```python
from django.contrib.auth.models import User
from django.test import TestCase, Client

class AuthenticatedViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_authenticated_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/protected/')
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_redirect(self):
        response = self.client.get('/protected/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
```

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: django_db
          POSTGRES_USER: django_user
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      env:
        DB_HOST: postgres
        DB_PORT: 5432
        DB_NAME: django_db
        DB_USER: django_user
        DB_PASSWORD: password
        SECRET_KEY: test-secret-key
      run: |
        python manage.py test
```

---

## Performance Testing

For load testing (when needed):

**Tools**:
- Locust
- Apache JMeter
- k6

**Example with Locust**:
```bash
# Add to requirements.txt
locust==2.17.0
```

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def index_page(self):
        self.client.get("/")

    @task(3)
    def view_product(self):
        self.client.get("/products/1/")
```

Run:
```bash
locust -f locustfile.py --host=https://coreofkeen.com
```

---

## Testing Checklist

Before deploying to production, ensure:

- [ ] All tests pass
- [ ] Test coverage > 80% for business logic
- [ ] Integration tests cover critical workflows
- [ ] No hardcoded credentials in tests
- [ ] Tests run in CI/CD pipeline
- [ ] Performance tests show acceptable response times

---

## Test-Driven Development (TDD)

Recommended workflow:

1. **Write a failing test**
   ```python
   def test_product_has_slug(self):
       product = Product(name="Test Product")
       product.save()
       self.assertEqual(product.slug, "test-product")
   ```

2. **Write minimum code to pass**
   ```python
   from django.utils.text import slugify

   class Product(models.Model):
       name = models.CharField(max_length=200)
       slug = models.SlugField()

       def save(self, *args, **kwargs):
           if not self.slug:
               self.slug = slugify(self.name)
           super().save(*args, **kwargs)
   ```

3. **Refactor**
   - Improve code quality
   - Ensure tests still pass

4. **Repeat**

---

## Common Testing Pitfalls

### 1. Testing Implementation Details

**Bad**:
```python
def test_method_called(self):
    obj.internal_method()  # Testing how, not what
```

**Good**:
```python
def test_result_is_correct(self):
    result = obj.public_method()
    self.assertEqual(result, expected_value)  # Testing what
```

---

### 2. Slow Tests

**Bad**:
```python
def test_email_sent(self):
    send_email()  # Actually sends email, slow
```

**Good**:
```python
@patch('myapp.utils.send_email')
def test_email_sent(self, mock_send):
    send_email()
    mock_send.assert_called_once()  # Fast mock
```

---

### 3. Brittle Tests

**Bad**:
```python
def test_page_content(self):
    response = self.client.get('/')
    self.assertContains(response, '<div class="container">')  # Breaks if HTML changes
```

**Good**:
```python
def test_page_content(self):
    response = self.client.get('/')
    self.assertContains(response, 'Welcome')  # Tests content, not structure
```

---

## Next Steps

When adding tests:

1. Start with models (easiest to test)
2. Add view tests for critical workflows
3. Add integration tests for user journeys
4. Set up CI/CD to run tests automatically
5. Aim for >80% coverage on business logic

See Django documentation: https://docs.djangoproject.com/en/5.0/topics/testing/

---

Last Updated: 2025-12-21
