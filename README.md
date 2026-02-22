# 🗳️ Polling System

A simple and interactive **Polling System** that allows users to create polls, cast votes, and view results.  
This project is open-source and suitable for learning, practice, and collaboration.

---

## 📌 Features

- Create polls with multiple options via the UI
- Vote on available polls (one vote per browser per poll)
- View live poll results with visual charts
- Delete polls from the UI
- Poll expiry / deadline support
- Input validation (min 2 options, non-empty question)
- Paginated polls listing
- Simple and user-friendly interface
- Lightweight and easy-to-understand codebase

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Jinja2 (Templating Engine)
- **Backend:** FastAPI, Uvicorn
- **Database:** MongoDB

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (Atlas or local)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Shiwangi3003/Polling-System.git
   cd Polling-System
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   # Copy the example file and fill in your MongoDB URL
   cp .env.example .env
   ```
   Edit `.env` and set your `MONGODB_URL`.

5. Run the server
   ```bash
   uvicorn main:app --reload
   ```

6. Open your browser at **http://127.0.0.1:8000**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page — list all polls |
| `POST` | `/create_poll` | Create a new poll |
| `GET` | `/polls` | Get all polls (JSON) |
| `GET` | `/polls/{poll_id}` | Get a single poll (voting page) |
| `PUT` | `/update_poll` | Update a poll |
| `DELETE` | `/delete_poll/{poll_id}` | Delete a poll |
| `POST` | `/submit` | Submit a vote |
| `GET` | `/poll/result/{poll_id}` | View poll results |

---

## 📸 Screenshots

Screenshots can be added here to demonstrate the UI and functionality.

---

## 🤝 Contributing

Contributions are welcome! 🎉

> **Note:** Please raise an issue before starting to contribute.

Steps to contribute:
1. Fork the repository
2. Create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit
   ```bash
   git commit -m "feat: add meaningful description"
   ```
4. Push to your branch
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request

---

## 🐞 Issues

Found a bug or have a feature request?  
Please open an issue in the GitHub repository.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🙋‍♀️ Author

**Shiwangi**  
GitHub: https://github.com/Shiwangi3003

---

⭐ If you like this project, please consider giving it a star!
