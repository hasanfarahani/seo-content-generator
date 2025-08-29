# SEO Content Generator with Entity Mapping & Schema

A powerful AI-powered SEO content generation tool that analyzes SERP data, extracts entities, and generates optimized content outlines with structured schema markup.

## 🚀 Features

- **Keyword Analysis**: Extract TF-IDF keywords and entities from top SERP results
- **Entity Mapping**: Identify and categorize key entities using NLP
- **Content Outlines**: AI-generated SEO-optimized content structures
- **Schema Generation**: Automatic JSON-LD markup for better search visibility
- **Competitor Analysis**: Analyze competitor content for unique angles
- **Modern Web Interface**: Clean, responsive dashboard with authentication

## 🏗️ Architecture

- **Backend**: FastAPI with async support
- **Frontend**: Jinja2 templates with modern CSS
- **Database**: SQLite with async support
- **NLP**: spaCy for entity extraction, scikit-learn for TF-IDF
- **AI**: OpenAI API for content generation
- **Authentication**: JWT-based secure login system

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Modern web browser

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd seo-writer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

6. Run the application:
```bash
uvicorn main:app --reload
```

## 🎯 Usage

1. **Landing Page**: Visit `/` to learn about the tool
2. **Login/Register**: Create an account or sign in
3. **Dashboard**: Enter keywords and analyze SERP data
4. **Generate Content**: Get AI-powered outlines and schema markup

## 🔧 Configuration

- `OPENAI_API_KEY`: Your OpenAI API key for content generation
- `SECRET_KEY`: JWT secret for authentication
- `DATABASE_URL`: Database connection string

## 📊 Project Structure

```
seo-writer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── seo_engine.py
│   └── utils.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── dashboard.html
├── requirements.txt
└── README.md
```

## 🚀 Deployment

The application can be deployed to:
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Docker containers

## 📈 Roadmap

- [ ] Semantic similarity search
- [ ] Competitor outline clustering
- [ ] WordPress/Webflow integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions, please open an issue on GitHub.

