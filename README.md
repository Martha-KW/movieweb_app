# Movie Database Web Application
As my first project combining web development with AI capabilities, this represents a major step forward in my programming journey. The process taught me valuable lessons about API integration, error handling, and creating seamless user experiences.

Feedback and contributions are welcome as I continue to grow as a developer!

![Project Screenshot](./Screenshot.png) 

Credit for the background image: Thank you to Jamie Matociños (jamievalmat) on unsplash.com
[Cinema Picture](https://unsplash.com/de/fotos/passende-weiss-schwarze-schnursneaker-IAs0Odki5YQ)

## 🎓 Educational Project

This web application was developed as a **learning project** at Masterschool  to master:
- Full-stack web development with Python/Flask
- Database management with SQLAlchemy
- Modern web interfaces with Bootstrap
- API integrations (OMDb and DeepSeek)
- AI feature implementation

## 🌟 Special Achievement

I'm particularly proud of successfully implementing the **DeepSeek API** - my first real AI integration in a web application! This milestone represents significant growth in my development skills.

## 🎬 Features

- User-friendly web interface
- Movie database management
- OMDb API integration for movie data
- **AI-powered features** via DeepSeek
- Responsive design (works on all devices)

## ⚙️ Setup Requirements

To run this project locally, you'll need:

1. **Free OMDb API Key**:
   - Get yours at [OMDb API](http://www.omdbapi.com/apikey.aspx)

2. **DeepSeek API Key** (paid):
   - Required for AI features
   - Obtain at [DeepSeek](https://platform.deepseek.com/)

3. Python 3.8+ environment

create your .env file with your own keys

OMDB_API_KEY=your_omdb_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
SECRET_KEY=your_secret_key_here
## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/movie-web-app.git

# Navigate to project directory
cd movie-web-app

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
