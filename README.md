# SmartTaskAI

SmartTaskAI is an intelligent application that leverages the power of AI to help you manage your tasks efficiently. Whether you need to create a to-do list, plan your week, or simply chat with an AI assistant, SmartTaskAI has got you covered.

## Features

- **AI-Powered Chat**: Interact with an AI assistant to get responses to your queries.
- **To-Do List Creation**: Automatically generate to-do lists based on your input, such as creating a 7-day gym split or planning your tasks for the week.
- **Rate Limiting**: Ensures fair usage by limiting the number of requests per minute.

## Getting Started

### Prerequisites

- Python 3.7+
- Flask
- GEMINI API credentials

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/SmartTaskAI.git
    cd SmartTaskAI
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your GEMINI API credentials in the `config.py` file.

### Running the Application

To start the Flask application, run:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

### Running Tests

To run the tests for this project, use the following command:
```bash
pytest tests/
```

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000`.
2. Use the chat interface to interact with the AI assistant.
3. To create a to-do list, input a request such as "Create a 7-day gym split" or "Plan my tasks for the week".
4. The generated to-do list will appear in the To-Do List section.

## Contributing

We welcome contributions to SmartTaskAI. To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [GEMINI](https://gemini.com) for providing the AI API.
- The open-source community for their invaluable contributions.
