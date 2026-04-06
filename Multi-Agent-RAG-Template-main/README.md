
# Multi-Agent-RAG-Template

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)


[![GitHub stars](https://img.shields.io/github/stars/The-Swarm-Corporation/Legal-Swarm-Template?style=social)](https://github.com/The-Swarm-Corporation/Legal-Swarm-Template)
[![Swarms Framework](https://img.shields.io/badge/Built%20with-Swarms-blue)](https://github.com/kyegomez/swarms)


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Swarms Framework](https://img.shields.io/badge/Built%20with-Swarms-orange)](https://swarms.xyz)

A production-ready template for building Multi-Agent RAG (Retrieval-Augmented Generation) systems using the Swarms Framework. This template demonstrates how to create a collaborative team of AI agents that work together to process, analyze, and generate insights from documents.


## 🌟 Features

- **Plug-and-Play Agent Architecture**
  - Easily swap or modify agents without disrupting the system
  - Add custom agents with specialized capabilities
  - Define your own agent interaction patterns
  - Scale from 2 to 100+ agents seamlessly
  - Any LLM can be used, this template defaults to OpenAI but you can swap in another provider if needed.

- **Adaptable Document Processing**
  - Support for any document format through custom extractors
  - Flexible document storage options (local, cloud, or hybrid)
  - Customizable chunking and embedding strategies
  - Dynamic index updates without system restart
  - Any RAG system can be used, this template uses LlamaIndexDB but you can use any other RAG system.

- **Configurable Workflows**
  - Design custom agent communication patterns
  - Implement parallel or sequential processing
  - Add conditional logic and branching workflows
  - Adjust system behavior through environment variables


## 🚀 Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/The-Swarm-Corporation/Multi-Agent-RAG-Template.git
cd Multi-Agent-RAG-Template
```

2. **Set Up Environment**
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
# Create .env file

# Edit .env file with your credentials
OPENAI_API_KEY="your-openai-api-key-here"
WORKSPACE_DIR="agent_workspace"
```

### Get your OpenAI API key

1. Create or manage your API keys at [platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys).
2. Create a new secret key and copy it when it is shown.
3. Add it to your `.env` file as `OPENAI_API_KEY="your-openai-api-key-here"`.
4. If you only have a ChatGPT subscription, set up API billing on the OpenAI Platform before testing this project. ChatGPT billing and API billing are separate.

Helpful references:
- [OpenAI API authentication docs](https://platform.openai.com/docs/api-reference/authentication)
- [OpenAI quickstart: set up your API key](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)
- [ChatGPT billing vs. API billing](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform)

4. **Run the Example**
```bash
python main.py
```

## 🏗️ Project Structure

```
Multi-Agent-RAG-Template/
├── main.py                    # Main entry point
├── multi_agent_rag/
│   ├── agents.py             # Agent definitions
│   └── memory.py             # RAG implementation
├── docs/                      # Place your documents here
├── requirements.txt           # Project dependencies
└── .env                      # Environment variables
```

## 🔧 Customization

### Adding New Agents

1. Open `multi_agent_rag/agents.py`
2. Create a new agent using the Agent class:

```python
new_agent = Agent(
    agent_name="New-Agent",
    system_prompt="Your system prompt here",
    llm=model,
    max_loops=1,
    # ... additional configuration
)
```

### Modifying the Agent Flow

In `main.py`, update the `flow` parameter in the `AgentRearrange` initialization:

```python
flow=f"{agent1.agent_name} -> {agent2.agent_name} -> {new_agent.agent_name}"
```

## Integrating RAG

- The `memory_system` parameter in the `AgentRearrange` initialization is used to configure the RAG system.
- The `memory_system` parameter is an instance of `LlamaIndexDB`, which is a database class for storing and retrieving medical documents.
- The `memory_system` class must have a `query(query: str)` method that returns a string for the agent to use it.

```python

# Import the AgentRearrange class for coordinating multiple agents
from swarms import AgentRearrange

from multi_agent_rag.agents import (
    diagnostic_specialist,
    medical_data_extractor,
    patient_care_coordinator,
    specialist_consultant,
    treatment_planner,
)

from multi_agent_rag.memory import LlamaIndexDB

router = AgentRearrange(
    name="medical-diagnosis-treatment-swarm",
    description="Collaborative medical team for comprehensive patient diagnosis and treatment planning",
    max_loops=1,
    agents=[
        medical_data_extractor,
        diagnostic_specialist,
        treatment_planner,
        specialist_consultant,
        patient_care_coordinator,
    ],
    memory_system=LlamaIndexDB(
        data_dir="docs",
        filename_as_id=True,
        recursive=True,
        similarity_top_k=10,
    ),
    flow=f"{medical_data_extractor.agent_name} -> {diagnostic_specialist.agent_name} -> {treatment_planner.agent_name} -> {specialist_consultant.agent_name} -> {patient_care_coordinator.agent_name}",
)

if __name__ == "__main__":
    router.run(
        "Analyze this Lucas Brown's medical data to provide a diagnosis and treatment plan"
    )

```


## Pinecone Example

Here is an example of how to use Pinecone as the RAG system.

- Make sure you have a Pinecone index created and the `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, and `PINECONE_ENVIRONMENT` environment variables set.
- See the `pinecone_swarm.py` file for the full example.
- The `PineconeManager` class is used to interface with the Pinecone API.

```python
import os
from swarms import AgentRearrange
from multi_agent_rag.agents import (
    diagnostic_specialist,
    medical_data_extractor,
    patient_care_coordinator,
    specialist_consultant,
    treatment_planner,
)
from multi_agent_rag.pinecone_wrapper import PineconeManager

router = AgentRearrange(
    name="medical-diagnosis-treatment-swarm",
    description="Collaborative medical team for comprehensive patient diagnosis and treatment planning",
    max_loops=1,
    agents=[
        medical_data_extractor,
        diagnostic_specialist,
        treatment_planner,
        specialist_consultant,
        patient_care_coordinator,
    ],
    memory_system=PineconeManager(
        api_key=os.getenv("PINECONE_API_KEY"),
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        environment=os.getenv("PINECONE_ENVIRONMENT"),
    ),
    flow=f"{medical_data_extractor.agent_name} -> {diagnostic_specialist.agent_name} -> {treatment_planner.agent_name} -> {specialist_consultant.agent_name} -> {patient_care_coordinator.agent_name}",
)

if __name__ == "__main__":
    router.run(
        "Analyze this Lucas Brown's medical data to provide a diagnosis and treatment plan"
    )


```


## 📚 Documentation

For detailed documentation on:
- [Swarms Framework](https://swarms.xyz)
- [LlamaIndex](https://docs.llamaindex.ai)
- [OpenAI Platform](https://platform.openai.com/docs/overview)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
g

## 🛠 Built With

- [Swarms Framework](https://github.com/kyegomez/swarms)
- Python 3.10+
- OpenAI API Key, with the option to swap to another model provider through [Swarm Models](https://github.com/The-Swarm-Corporation/swarm-models)
- LlamaIndexDB for storing and retrieving medical documents

## 📬 Contact

Questions? Reach out:
- Twitter: [@kyegomez](https://twitter.com/kyegomez)
- Email: kye@swarms.world

---

## Want Real-Time Assistance?

[Book a call with here for real-time assistance:](https://cal.com/swarms/swarms-onboarding-session)

---

⭐ Star us on GitHub if this project helped you!

Built with ♥ using [Swarms Framework](https://github.com/kyegomez/swarms)






