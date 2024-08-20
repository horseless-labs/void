# Overview
Soon to be hosted on the [Screaming Void](https://screamingvoid.com/)!

Void is an experiment in using retrieval-augmented generation (RAG) to give people more control and flexibility over the ways in which they interact with LLMs. TO that end, it currently uses a combination of the OpenAI API and [Faiss](https://github.com/facebookresearch/faiss) via LangChain.

# Main Next Steps
- [ ] Iterate on prompts to achieve desired effects. The main chat agent pulls [hwchase17/structured-chat-agent](https://smith.langchain.com/hub/hwchase17/structured-chat-agent?organizationId=6e7cb68e-d5eb-56c1-8a8a-5a32467e2996) from the Hub, and a simpler agent for querying the Faiss vector store uses [rlm/rag-prompt](rlm/rag-prompt). (see `agent_spec.py` and `vectorize.py`, respectively). Adequate, but previous work indicates that higher specificity can be achieved by manipulating these.
- [ ] Find and ingest journal-style content corpus to run similarity searches, semantic analysis, etc. (Previous work used blogs from ~2005, which will serve this purpose if need be)
    - [ ] Add vector stores that can give information about, e.g. relevant mental health services and experiment with prompts that will accurately determine when these should be deployed.
    - [ ] Determine what OpenAI's safety layers look like now.

# Little Stuff (GUI changes, feature additions, fixes, etc.)
- [ ] Add tiktoken to keep track of token usage.
    - [ ] In the interest of **parasocial relationship avoidance**, consider making this part of a feature that will steer the user away if it seems like they are making too heavy use of Void.
- [ ] Add ability to upload documents for ingestion.
- [ ] Add ability to download chats and documents in some plaintext format.
    - [ ] Consider ability to convert to Markdown.
- [ ] Finish user profile infrastructure.
- [ ] Fix user access restriction hole around query_chats.html

# Open Questions

# Resources