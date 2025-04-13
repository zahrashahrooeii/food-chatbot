# Food Chatbot API

A sophisticated Django REST API that leverages OpenAI's GPT models to provide personalized food recommendations and analytics. This project demonstrates modern API development practices, AI integration, and data analysis capabilities.

## 🌟 Features

- **AI-Powered Conversations**: Utilizes OpenAI's GPT-3.5 for natural food preference discussions
- **User Authentication**: Secure JWT-based authentication system
- **Food Analytics Dashboard**: Comprehensive analytics on food preferences and dietary trends
- **Health Analysis**: Nutritional insights and health scores for foods
- **Personalized Recommendations**: AI-driven food recommendations based on user preferences
- **Data Export**: CSV export functionality for data analysis
- **Dietary Preference Tracking**: Support for vegetarian and vegan preferences
- **Comprehensive Testing**: 95%+ test coverage with pytest
- **API Documentation**: Full Swagger/OpenAPI documentation
- **Security Features**: Rate limiting, CORS protection, and secure headers

## 🚀 Technology Stack

- **Backend**: Django 5.0 / Django REST Framework
- **Database**: SQLite (easily configurable for PostgreSQL)
- **AI Integration**: OpenAI GPT-3.5
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Testing**: pytest, factory-boy
- **Deployment**: Docker / Gunicorn
- **Security**: django-secure, django-csp

## 📋 Prerequisites

- Python 3.12+
- OpenAI API Key
- Docker (optional)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/zahrashahrooeii/food-chatbot-task.git
cd food-chatbot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## 🐳 Docker Deployment

1. Build the Docker image:
```bash
docker build -t food-chatbot .
```

2. Run the container:
```bash
docker run -p 8000:8000 food-chatbot
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=food_api
```

## 📚 API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/
- ReDoc: http://localhost:8000/redoc/

## 🔒 Security Features

- Token-based authentication
- Rate limiting on API endpoints
- CORS protection
- Content Security Policy headers
- Secure cookie configuration
- XSS protection headers

## 📊 Analytics Features

- Food preference trends
- Dietary preference statistics
- Health score analysis
- Popular food combinations
- User interaction metrics

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- Real-time chat using WebSockets
- Machine learning for better food recommendations
- Mobile app integration
- Social sharing features
- Advanced analytics dashboard

## 👨‍💻 Author

Zahra Shahrooeii
- GitHub: [zahrashahrooeii](https://github.com/zahrashahrooeii)
